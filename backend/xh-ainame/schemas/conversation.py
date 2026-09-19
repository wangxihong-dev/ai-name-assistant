"""对话版接口的请求／返回结构。

为什么不直接把 conversation_id 塞进 AgentSchema：
  AgentSchema 是「这一轮 agent 跑出了什么」，会话编号是「这轮属于哪次对话」，
  两件事。塞进去的话，纯 agent 那一层就得知道自己被谁存着——那是耦合。
  嵌套一层，chat_agent 就可以完全不知道会话表存在。
"""
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from models.conversation import RoundStatus
from schemas.agent import AgentSchema, Candidate

# 免责措辞由代码拼、不由模型写：提示词保障不了它，模型也可能漏。
# 它是「整个响应级别」的一句话，所以挂在响应上，不是每条 risk 里各加一遍。
DISCLAIMER = "以上为风险提示，仅供参考，最终以商标局审查为准。"


class ChatIn(BaseModel):
    user_input: Annotated[str, Field(..., min_length=1, max_length=500,
        description="用户这一轮说的话。上限 500 字：一次请求要打 3~6 次模型，"
                    "不设上限等于把 token 预算交给陌生人。"
                    "注意这跟限流是两件事——限流管次数，这里管单次成本")]
    conversation_id: Annotated[int | None, Field(None,
        description="会话编号。不传＝开一段新对话；传了＝接着聊")]


class AgentReply(BaseModel):
    """一轮对话里「给用户看的那部分」。

    形状 = AgentSchema 去掉三格：
      status        单独存一列（前端要按它切分轮次、决定画什么，不该埋在 JSON 里）
      duration_seconds / tool_call_count  运行时指标，历史里没人看
    """

    intent: Annotated[Literal["取名", "合规检查", "两者都有"] | None, Field(...,
        description="这一轮判出来的意图")]
    candidates: Annotated[list[Candidate] | None, Field(...,
        description="候选名（已经回表补全过的）。失败和澄清中时是 null")]
    user_message: Annotated[str | None, Field(...,
        description="要对用户说的话。正常和降级时是 null")]


class ChatResponse(BaseModel):
    conversation_id: Annotated[int, Field(...,
        description="这次对话的编号。前端下次请求要原样带回来："
                    "带了就是继续聊，不带就是开一段新对话")]
    result: Annotated[AgentSchema, Field(...,
        description="这一轮的结果。前端看 result.status 决定画什么："
                    "正常／降级画名字卡片，澄清中画反问气泡，失败画重试提示")]
    disclaimer: Annotated[str | None, Field(None,
        description="免责措辞，由代码填。只在真的给出了名字时出现——"
                    "失败和澄清中时没有『以上』，挂一句免责反而是废话")]

    @model_validator(mode="after")
    def check_disclaimer(self):
        # 手法跟 AgentSchema 那个 check_combination 一样：
        # 把「记得加免责」从一条口头约定变成一条可执行规则，结构上没法漏。
        gave_names = self.result.status in ("正常", "降级")
        if gave_names and not self.disclaimer:
            raise ValueError("给出了候选名却没带免责措辞：这一格必须由代码填，不能靠记得")
        if not gave_names and self.disclaimer:
            raise ValueError(f"status={self.result.status} 时不该有免责措辞：没有结论可免责")
        return self


class RoundOut(BaseModel):
    """前端刷新页面后重画历史用的一轮。

    中间那些 tool 消息、assistant 的工具调用都不在这里——
    那是给模型看的上下文，不是给人看的。
    """

    user_input: Annotated[str, Field(..., description="这一轮用户说的话")]
    status: Annotated[RoundStatus, Field(..., description="这一轮的结局，前端靠它决定画什么")]
    reply: Annotated[AgentReply | None, Field(..., description="agent 的可见产出")]
    created_at: Annotated[datetime, Field(..., description="这一轮结束的时间")]


class HistoryOut(BaseModel):
    conversation_id: Annotated[int, Field(..., description="会话编号")]
    rounds: Annotated[list[RoundOut], Field(..., description="按时间正序的全部轮次")]
    disclaimer: Annotated[str, Field(DISCLAIMER,
        description="免责措辞。给了默认值，所以构造时不填也会有——结构上没法漏")]


# ══════════════════════════════════════════════════════════════
# 流式进度事件
#
# 为什么流的是「系统正在做什么」而不是「模型正在说什么」：
#   ① 最终答案是以「模型调 ModelOutput 这个工具」的形式来的，args 是一整坨
#      结构化 JSON，逐字吐给用户看没有意义
#   ② risks 是模型说完之后，代码扫名录、回表、按条款聚合才产生的，
#      它根本不存在于模型的输出流里
#   ③ 一次请求有 3~6 次模型调用，前面那些轮（检索诗词）没有任何可流的东西
#
# 事件的线上形状（SSE）：
#   event: stage   data: {"code": "retrieve_poetry", "text": "正在检索诗词素材…"}
#   event: result  data: {"data": {…ChatResponse…}}
#   event: error   data: {"text": "…"}
# code 是封闭选项（前端靠它切换图标／文案），text 是给人看的，
# 改文案不用前端发版。
# ══════════════════════════════════════════════════════════════

StageCode = Literal["load_law", "thinking", "retrieve_poetry", "scan_trademark", "retry"]
