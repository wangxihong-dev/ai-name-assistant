"""品牌／产品取名 · 对话版 agent。

与旧表单版（core/agent.py）并行存在、互不影响：旧接口已上线、简历上写着、面试要讲，所以一个字不动，新功能全走这条新路。

两个架构事实是实测出来的，不是猜的：
1. with_structured_output 和 bind_tools 不能共存：三种 method 都会把真工具挤掉
   （function_calling / json_schema 把 tools 换成 [ModelOutput]，json_mode 直接丢掉 tools）。
   而且请求 json_schema 会被静默降级成 function_calling，不报错。
2. 所以把 ModelOutput 当成第二个工具一起绑，让模型自己选「调诗词」还是「交答案」。
   出口 = 模型调了 ModelOutput。实测：模型会先调两轮诗词、第三轮交答案。
"""
import json
import logging
import time
from dataclasses import dataclass
from datetime import date
from typing import Annotated

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from pydantic import Field, ValidationError

from core.milvus import milvus_client
from errors import ClauseIdHallucinatedError, TrademarkDataError
from models import AsyncSession
from repository.law_repository import LawRepo
from repository.milvus_repository import MilvusRepo
from schemas.agent import AgentSchema, Candidate, ModelOutput
from service.embedding_service import EmbeddingService
from service.law_service import LawService
from service.risk_merge_service import RiskMergeService
from service.trademark_service import TrademarkService
from settings import api_key

# 模块里只取 logger，不配置日志。
# basicConfig 配的是根 logger，谁先 import 谁定全局格式——那是应用入口的事。
logger = logging.getLogger(__name__)

MAX_ROUNDS = 6          # 保险丝，不是次数目标
ANSWER_TOOL = "ModelOutput"
DATA_ERROR_MSG = "系统的法条数据出了点问题，暂时给不出结果，请稍后再试"
FAIL_MSG = "这次没能生成结果，请重试一次"


# ══════════════════════════════════════════════════════════════
# 系统提示词：静态三块是常量，法条段运行时拼
#
# 故意不写在这里的东西（写了就是第二个来源）：
#   输出字段说明 / 什么时候反问 / intent 怎么判 → 在 ModelOutput 的 description 里
#   诗词工具什么时候调 → 在 poetry_tool 的 docstring 里
#   免责措辞「仅供参考，最终以商标局审查为准」 → 代码在 router 层拼
# ══════════════════════════════════════════════════════════════

ROLE_AND_TASK = """你是一位品牌／产品命名顾问，同时熟悉《商标法》里关于注册和使用的禁区。
你的工作是取名和合规检查：根据用户给的品类、调性、目标人群提出候选品牌名并说清思路；
或者评估用户自己提出的名字能不能作为商标注册和使用。

信息不足时不许猜——不许自己替用户补品类、调性、目标人群，也不许替用户决定他想要什么风格。"""

CLAUSE_RULES = """引用条款时只填每行开头【】里的数字，并且必须填最具体的那一项。
原文以「：」结尾的那几行是引导语，它们只是后面各项的前提，本身不是可命中的条款，不要填它们。"""

WORDING_RULES = """你写的每一条理由都会原样显示给用户，所以你只做风险提示、不下结论：
说「存在被驳回风险」「可能构成…」，不说「违反第X条」「不得注册」——最终判断权在商标局。"""


ANSWER_RULES = """你唯一的回复方式是提交 ModelOutput 这个工具。
不要用普通文本回复——普通文本系统收不到，等于白说一轮。
要追问用户时也一样：提交 ModelOutput，把追问的话写进 user_message。"""

def build_system_prompt(clause_block: str) -> str:
    """纯函数：不查库、不吃 session，所以可以拿一段假法条直接测。"""
    line_count = clause_block.count("\n") + 1
    clause_section = (
        f"以下是当前生效的法条，共 {line_count} 条。"
        f"每行开头【】里的数字是这条条款的编号：\n\n{clause_block}"
    )
    return "\n\n".join([ROLE_AND_TASK, clause_section, CLAUSE_RULES, WORDING_RULES,
                        ANSWER_RULES])


# ══════════════════════════════════════════════════════════════
# 工具：诗词检索。可选——模型自己决定调不调，这个「要不要调」就是路由决策。
# ══════════════════════════════════════════════════════════════

@tool()
def poetry_tool(meaning: Annotated[str, Field(...,
                      description="要检索的寓意或意象，例如：清远、山间云雾、君子之德")]) -> list[dict]:
    """检索诗词素材，给品牌名找文化出处。

    只在品类适合从诗词里取意象时调用（茶叶、白酒、文创、餐饮这类）。
    科技、SaaS、工业品这类品类不要调用。
    不调用是合法的——大多数成功的品牌名跟诗词没有关系。"""
    repo = MilvusRepo(milvus_client())
    vector = EmbeddingService().embed_text(meaning)
    result = repo.search(collection_name="poetry_vectors", data=[vector], limit=5)
    poems = []
    for hit in result[0]:
        meta = hit["entity"]["metadata"]
        poems.append({
            "title": meta["title"],
            "author": meta["author"],
            "dynasty": meta["dynasty"],
            "content": hit["entity"]["text"],
        })
    return poems


# ══════════════════════════════════════════════════════════════
# 循环
# ══════════════════════════════════════════════════════════════

async def _run_loop(bound, messages: list, tool_call_count: int):
    """跑到模型调 ModelOutput 交答案为止。

    返回 (model_output | None, tool_call_count)。None = 轮次耗尽，交给降级路径。
    """
    for round_no in range(1, MAX_ROUNDS + 1):
        logger.info("===== 第 %d 轮调用模型 =====", round_no)
        ai_msg = await bound.ainvoke(messages)
        messages.append(ai_msg)                       # 铁律一：模型回复先 append

        tool_calls = ai_msg.tool_calls or []
        answer = None

        for tc in tool_calls:                         # 铁律二：N 个意图回 N 条消息，id 一一对应
            tool_call_count += 1                      # 失败的调用也计入，所以 0 只剩一个含义

            if tc["name"] == ANSWER_TOOL:
                try:
                    answer = ModelOutput(**tc["args"])
                    feedback = json.dumps({"accepted": True}, ensure_ascii=False)
                except ValidationError as e:
                    # 结构不合法不是终点：把错误喂回去让它重交，跟工具失败同一个处理法
                    answer = None
                    feedback = json.dumps(
                        {"accepted": False,
                         "errors": e.errors(include_url=False)},
                        ensure_ascii=False, default=str)
                    logger.warning("ModelOutput 校验失败：%s", feedback[:400])
            else:
                try:
                    result = await poetry_tool.ainvoke(tc["args"])
                    logger.info("poetry_tool 返回 %s 首", len(result))
                    feedback = json.dumps(result, ensure_ascii=False)
                except Exception as e:                # 铁律三：工具失败也造 ToolMessage
                    logger.exception("poetry_tool 调用失败，参数 %s", tc["args"])
                    feedback = json.dumps({"error": "诗词检索失败", "reason": str(e)},
                                          ensure_ascii=False)

            messages.append(ToolMessage(content=feedback, tool_call_id=tc["id"]))

        if answer is not None:
            return answer, tool_call_count

        if not tool_calls:
            logger.warning("第 %d 轮模型既没调工具也没交答案", round_no)

    return None, tool_call_count


async def _force_answer(llm, messages: list):
    """降级路径：只留一个工具、并且强制调它。

    用原始 llm 重新绑，而不是拿循环里那个 bound 再绑一次。实测两种写法的绑定结果
    一样（langchain 是替换不是叠加），但从原始 llm 绑不依赖那个合并语义——
    哪天它改成叠加，降级路径会静默多出一个 poetry_tool，而 tool_choice 又被强制成
    ModelOutput，模型从此再也调不了诗词，而且不报错。
    """
    forced = llm.bind_tools(tools=[ModelOutput], tool_choice=ANSWER_TOOL)
    ai_msg = await forced.ainvoke(messages)
    messages.append(ai_msg)

    # ⚠️ 这里必须给每个 tool_call 回一条 ToolMessage，跟 _run_loop 里一样。
    # 少一条的后果不是「这次请求出错」，而是：这条带 tool_calls 的 assistant 消息
    # 会被存进库，下一次请求把历史发出去时接口直接 400。实测报错原文：
    #   An assistant message with 'tool_calls' must be followed by tool messages
    #   responding to each 'tool_call_id'
    # 一旦落库，残缺的消息列表就是永久的地雷——这个会话从此再也聊不下去。
    answer = None
    for tc in (ai_msg.tool_calls or []):
        if tc["name"] == ANSWER_TOOL:
            try:
                answer = ModelOutput(**tc["args"])
                feedback = json.dumps({"accepted": True}, ensure_ascii=False)
            except ValidationError as e:
                logger.warning("强制交答案时校验失败：%s", str(e)[:400])
                feedback = json.dumps({"accepted": False,
                                       "errors": e.errors(include_url=False)},
                                      ensure_ascii=False, default=str)
        else:
            feedback = json.dumps({"error": "这一轮只允许提交 ModelOutput"}, ensure_ascii=False)
        messages.append(ToolMessage(content=feedback, tool_call_id=tc["id"]))

    return answer


async def _merge_all(model_output, version, trademark_service, merge_service) -> list[Candidate]:
    """每个候选名：扫一遍名录，再把两侧理由按条款聚合。"""
    out = []
    for c in model_output.candidates:
        hits = await trademark_service.scan_name(c.name, version)
        risks = await merge_service.merge_risks(c.name, hits, version, c.risks)
        out.append(Candidate(name=c.name, origin=c.origin, meaning=c.meaning,
                             source=c.source, risks=risks))
    return out


def _drop_bad_risk(model_output, candidate_name: str, bad_id: int) -> None:
    """重判之后还是幻觉：把那一条剔掉。剔掉不算静默错，因为 status 会变成降级。"""
    for c in model_output.candidates:
        if c.name == candidate_name:
            c.risks = [r for r in c.risks if r.clause_id != bad_id]


# ══════════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════════

@dataclass
class AgentRunResult:
    """一次 agent 运行的两样产出。

    为什么用带名字的结构而不是裸元组：
    裸元组在这里也不会静默出错（两样东西类型差得远，写反当场崩），
    但调用方得写 result[0] / result[1]，读的人要回头数位置。
    带名字之后 chat_service 里写的是 result.schema 和 result.new_messages。
    """

    schema: AgentSchema

    # 这一轮新产生的消息：用户那句 + 循环里所有 assistant / tool 消息。
    # 不含系统提示词（它每次请求重新装配，不落库），也不含历史（本来就在库里）。
    # chat_service 拿这一份去写消息表，所以这里多一条少一条都会直接体现在库里。
    new_messages: list


async def run_agent(user_input: str, history: list, session: AsyncSession) -> AgentRunResult:
    """纯 agent：吃「历史消息 + 用户这句新话」，吐「结果 + 这一轮新增的消息」。

    它不知道会话表的存在——存不存、存哪张表、怎么还原，
    是 chat_service 和 conversation_service 的事。这一层只负责跑循环。
    """
    started = time.monotonic()
    tool_call_count = 0

    # messages 的前 persisted_before 条是「系统提示词 + 历史」，它们不该被重复存。
    # 从这个下标切下去，才是这一轮新产生的。
    persisted_before = 1 + len(history)
    messages: list = []

    def _new_messages() -> list:
        # 早退的情况（连提示词都装配不出来）messages 还是空的，
        # 但用户这句话必须记下来——不然这一轮在会话里等于没发生过，
        # 前端刷新之后会看到一段凭空少了一句的对话。
        return messages[persisted_before:] or [HumanMessage(user_input)]

    def _finish(schema: AgentSchema) -> AgentRunResult:
        return AgentRunResult(schema=schema, new_messages=_new_messages())

    def _fail(text: str) -> AgentRunResult:
        return _finish(AgentSchema(status="失败", intent=None, candidates=None, user_message=text,
                                   duration_seconds=time.monotonic() - started,
                                   tool_call_count=tool_call_count))

    llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key, temperature=0.6)
    bound = llm.bind_tools(tools=[poetry_tool, ModelOutput], tool_choice="auto")

    law_repo = LawRepo(session)
    law_service = LawService(session)
    trademark_service = TrademarkService(session)
    merge_service = RiskMergeService(session)

    try:
        # 版本在这一层查一次，提示词／扫描／卡片三处共用同一个对象。
        # 跨午夜也不会出现「扫描按旧版判、卡片显示新版」。
        version = await law_repo.get_law_version_by_date(date.today())
        clause_block = await law_service.build_clause_block(version)
    except TrademarkDataError:
        logger.exception("法条数据故障，装配不出提示词")
        return _fail(DATA_ERROR_MSG)

    # 系统提示词每次重新装配（这就是它不落库的原因）；
    # 历史用 list() 拷一份——不改调用方那个列表，
    # 否则 chat_service 手里的 history 会在它不知道的情况下被改动，那是最难查的一类 bug。
    messages = ([SystemMessage(build_system_prompt(clause_block))]
                + list(history)
                + [HumanMessage(user_input)])
    degraded = False

    try:
        model_output, tool_call_count = await _run_loop(bound, messages, tool_call_count)
        if model_output is None:
            logger.warning("达到最大轮次 %s，强制交答案（降级）", MAX_ROUNDS)
            model_output = await _force_answer(llm, messages)
            tool_call_count += 1
            degraded = True
            if model_output is None:
                return _fail(FAIL_MSG)
    except TrademarkDataError:
        logger.exception("法条／名录数据故障")
        return _fail(DATA_ERROR_MSG)
    except Exception:
        logger.exception("agent 循环出现未预期的异常")
        return _fail(FAIL_MSG)

    # 澄清中：模型判定信息不足。这一格由代码看结构推出来，不是模型自己声明的
    if model_output.candidates is None:
        ask = model_output.user_message
        if not ask:
            logger.warning("模型没给候选名也没给追问内容，用兜底追问")
            ask = "能再说一点吗？比如这是什么品类、想要什么调性、面向什么人群。"
        return _finish(AgentSchema(status="澄清中", intent=None, candidates=None, user_message=ask,
                                   duration_seconds=time.monotonic() - started,
                                   tool_call_count=tool_call_count))

    # 扫描 + 合并。模型编了假 id 就喂回去重判一次
    attempts = 0
    while True:
        try:
            candidates = await _merge_all(model_output, version, trademark_service, merge_service)
            break
        except ClauseIdHallucinatedError as e:
            attempts += 1
            if attempts == 1:
                logger.warning("模型引用了不存在的条款 id=%s（候选名『%s』），喂回错误重判一次",
                               e.bad_clause_id, e.candidate_name)
                messages.append(HumanMessage(
                    f"你刚才给『{e.candidate_name}』引用的条款编号 {e.bad_clause_id} 不存在。"
                    f"当前版本可用的编号是：{e.valid_ids}。请重新提交完整答案。"))
                try:
                    model_output, tool_call_count = await _run_loop(bound, messages, tool_call_count)
                except Exception:
                    logger.exception("重判时出现异常")
                    return _fail(FAIL_MSG)
                if model_output is None or model_output.candidates is None:
                    return _fail("重试之后还是没给出结果，请再说得具体一点")
            elif attempts == 2:
                logger.warning("重判后仍引用不存在的条款 id=%s（候选名『%s』），丢掉这一条并标记降级",
                               e.bad_clause_id, e.candidate_name)
                _drop_bad_risk(model_output, e.candidate_name, e.bad_clause_id)
                degraded = True
            else:
                logger.error("丢掉一条之后仍有幻觉 id=%s，判失败", e.bad_clause_id)
                return _fail(FAIL_MSG)
        except TrademarkDataError:
            logger.exception("名录／法条数据故障")
            return _fail(DATA_ERROR_MSG)

    try:
        return _finish(AgentSchema(status="降级" if degraded else "正常",
                                   intent=model_output.intent, candidates=candidates,
                                   user_message=None,
                                   duration_seconds=time.monotonic() - started,
                                   tool_call_count=tool_call_count))
    except ValidationError:
        logger.exception("拼不出合法的 AgentSchema（模型给的 intent／origin／meaning 组合不合法）")
        return _fail(FAIL_MSG)


if __name__ == "__main__":
    import asyncio
    from models import AsyncSessionFactory

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    async def _main():
        # 这里传空历史，等于「单轮、不持久化」地测 agent 本身。
        # 要测持久化，跑 service/chat_service.py。
        async with AsyncSessionFactory() as s:
            result = await run_agent("『中国红』这个名字用在茶叶上能不能用", [], s)
            print(result.schema.status, "|", result.schema.intent,
                  "| 工具调用", result.schema.tool_call_count, "次 |",
                  round(result.schema.duration_seconds, 1), "秒")
            print("这一轮新增消息条数:", len(result.new_messages),
                  "| 角色:", [type(m).__name__ for m in result.new_messages])
            for c in (result.schema.candidates or []):
                print(" ", c.name, "|", c.origin, "| source=", c.source,
                      "| risks=", [(r.clause_number, [x.judged_by for x in r.reasons])
                                   for r in c.risks])

    asyncio.run(_main())
