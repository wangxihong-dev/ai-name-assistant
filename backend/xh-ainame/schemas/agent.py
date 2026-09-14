from typing import Annotated, List, Literal
from pydantic import BaseModel, Field, model_validator


# ══════════════════════════════════════════════════════════════════
# 旧表单版（人名取名）在用的两个类。
# 被 core/agent.py 和 schemas/name.py 引用着，方案 A 说好旧接口一个字不动，
# 所以不要改它们。
# ══════════════════════════════════════════════════════════════════
class NameSchema(BaseModel):
    name: Annotated[str,Field(...,description="姓名")]
    reference:Annotated[str,Field(...,description="出处")]
    #author:Annotated[str,Field(...,description="作者")]
    #dynasty:Annotated[str,Field(...,description="朝代")]
    moral:Annotated[str,Field(...,description="寓意")]


class NameResultSchema(BaseModel):
    names:List[NameSchema]


# ══════════════════════════════════════════════════════════════════
# 品牌版 · 第一组：模型产出的结构
#
# 模型只填它自己知道的东西。条款原文、条款号、风险等级、法条版本
# 它一概碰不到——那些由代码拿着 clause_id 回 law_clause / law_version
# 表查出来再拼上。这样模型没有机会复述法条原文，也就不可能篡改它。
# ══════════════════════════════════════════════════════════════════
class RiskFromModel(BaseModel):
    clause_id: Annotated[int, Field(...,
        description="law_clause 表的主键 id，必须是系统提示词里列出来的那些 id 之一。"
                    "填数字，不要填条款号字符串。代码会拿它回表核对：查不到就报错，不会静默通过")]
    reason: Annotated[str, Field(...,
        description="为什么这个名字命中了这一条。要写事实依据"
                    "（名字里哪几个字、用在什么商品上、为什么构成欺骗性），"
                    "不要抄条款原文——原文由代码回表补")]


class CandidateFromModel(BaseModel):
    name: Annotated[str, Field(..., description="候选品牌名")]
    origin: Annotated[Literal["系统生成","用户提供"], Field(...,
        description="这个名字是谁出的。系统生成＝模型根据用户需求想出来的；"
                    "用户提供＝用户消息里已经写出来的那个名字，模型只是拿它去查")]
    meaning: Annotated[str | None, Field(
        description="为什么推荐这个名字（取名思路）。"
                    "仅当 origin＝系统生成时有值；origin＝用户提供时必须是 null——"
                    "用户自己起的名字，系统没有『推荐理由』，硬编一个就是撒谎")]
    source: Annotated[str | None, Field(
        description="诗词出处，例如《诗经·小雅·鹤鸣》：他山之石，可以攻玉。"
                    "仅当模型调用过诗词检索工具、并且真的采用了检索结果时有值；"
                    "没调工具、或调了但没用上，都填 null")]
    risks: Annotated[List[RiskFromModel], Field(...,
        description="这个名字命中的商标法条款。一条都没命中就传空列表 []，不要传 null——"
                    "空列表是『查过了，没问题』，null 是『我没查』，两个意思完全不同")]


class ModelOutput(BaseModel):
    """模型的结构化输出（response_format 用这个）。
    代码拿它加上自己测的东西，拼成下面的 AgentSchema。"""

    intent: Annotated[Literal["取名","合规检查","两者都有"] | None, Field(
        description="模型判断出来的用户意图。判断标准："
                    "用户消息里出现了一个具体的、要被评估的名字（如「『云栖』这个能用吗」）→ 合规检查；"
                    "用户只给了需求、没给具体名字（如「帮我想几个茶叶品牌名」）→ 取名；"
                    "两件事同时要（如「帮我想几个名字，另外『云栖』能不能用」）→ 两者都有。"
                    "如果信息不足、这次要追问用户，传 null")]
    candidates: Annotated[List[CandidateFromModel] | None, Field(
        description="候选名列表。仅当这次真的产出了候选名时有值；"
                    "信息不足需要追问用户时传 null，并把追问写进 user_message")]
    user_message: Annotated[str | None, Field(
        description="要对用户说的话。信息不足需要追问时，这里写追问内容；"
                    "正常产出候选名时传 null")]


# ══════════════════════════════════════════════════════════════════
# 品牌版 · 第二组：接口返回的结构
#
# 代码把 ModelOutput、自己测的耗时和调用次数、以及回表查到的法条信息，
# 拼成 AgentSchema 返回给前端。前端只认这一个结构。
# ══════════════════════════════════════════════════════════════════
class RiskDetail(BaseModel):
    clause_number: Annotated[str, Field(..., description="条款号，代码回 law_clause 表取。给人看的")]
    clause_original: Annotated[str, Field(..., description="条款原文，代码回 law_clause 表取。模型碰不到这一格")]
    risk_grade: Annotated[Literal["禁止使用","不予注册","例外规定"], Field(...,
        description="法律后果，代码回 law_clause 表取")]
    law_name: Annotated[str, Field(..., description="法律名称，代码回 law_version 表取，例如 商标法")]
    law_version_name: Annotated[str, Field(...,
        description="法条版本，代码回 law_version 表取，例如 2019修正版。"
                    "这一格是诚信线的落地点：界面和简历口径都要能说出依据的是哪一版")]
    reason: Annotated[str, Field(..., description="命中理由，模型产出，代码原样透传，不改写")]


class Candidate(BaseModel):
    name: Annotated[str, Field(..., description="候选品牌名")]
    origin: Annotated[Literal["系统生成","用户提供"], Field(...,
        description="这个名字是谁出的。前端靠它区分显示")]
    meaning: Annotated[str | None, Field(
        description="推荐理由。origin＝系统生成时必有值；origin＝用户提供时必为 null")]
    source: Annotated[str | None, Field(
        description="诗词出处，没调诗词工具或没用上检索结果时为 null")]
    risks: Annotated[List[RiskDetail], Field(...,
        description="命中的条款列表。没命中就是空列表 []，不是 null")]


class AgentSchema(BaseModel):
    status: Annotated[Literal["正常","降级","失败","澄清中"], Field(...,
        description="本次请求的处理结果，由代码判定，模型不填。"
                    "正常＝完整生成候选名；降级＝达到最大轮次后用现有信息强行生成；"
                    "失败＝系统异常未能生成；澄清中＝用户信息不足，正在追问")]
    intent: Annotated[Literal["取名","合规检查","两者都有"] | None, Field(
        description="模型判断出来的用户意图，由模型产出、代码原样透传。"
                    "仅当 status 为正常或降级时有值，其余情况为 null。"
                    "判断标准写在 ModelOutput.intent 里，这里不重复")]
    candidates: Annotated[List[Candidate] | None, Field(
        description="候选名列表。仅当 status 为正常或降级时有值，其余情况为 null")]
    user_message: Annotated[str | None, Field(
        description="要对用户说的话。仅当 status 为失败或澄清中有值，其余情况为 null")]
    duration_seconds: Annotated[float, Field(
        description="从请求开始到返回的总耗时，单位秒。")]
    tool_call_count: Annotated[int, Field(
        description="永远有值 模型判断这次不需要检索时为0 失败的调用也计入")]

    @model_validator(mode="after")
    def check_combination(self):
        # ── 第一组规则：status 和载荷必须对得上 ──
        if self.status in ("正常", "降级"):
            if not self.candidates:
                raise ValueError(f"status={self.status} 但 candidates 是空的：产出了结果就必须有候选名")
            if self.intent is None:
                raise ValueError(f"status={self.status} 但 intent 是 null：产出了候选名就必须知道是哪种请求")
            if self.user_message is not None:
                raise ValueError(f"status={self.status} 但 user_message 有值：正常和降级状态下不该有追问或提示")
        else:
            if self.user_message is None:
                raise ValueError(f"status={self.status} 但 user_message 是 null：失败和澄清中必须给用户一句话")
            if self.candidates is not None:
                raise ValueError(f"status={self.status} 但 candidates 有值：失败和澄清中不该有候选名")
            if self.intent is not None:
                raise ValueError(f"status={self.status} 但 intent 有值：没产出候选名就不该有意图")

        # ── 第二组规则：intent 和每个候选名的 origin 必须对得上 ──
        if self.candidates:
            origins = {c.origin for c in self.candidates}
            if self.intent == "取名" and origins != {"系统生成"}:
                raise ValueError(f"intent=取名 但候选名里出现了 {origins}：取名模式下必须全部是系统生成")
            if self.intent == "合规检查" and origins != {"用户提供"}:
                raise ValueError(f"intent=合规检查 但候选名里出现了 {origins}：合规检查模式下必须全部是用户提供")
            if self.intent == "两者都有" and len(origins) < 2:
                raise ValueError(f"intent=两者都有 但候选名只有 {origins} 一种来源：两种都要至少有一个")

            # ── 第三组规则：寓意的有无由 origin 决定 ──
            for c in self.candidates:
                if c.origin == "系统生成" and not c.meaning:
                    raise ValueError(f"候选名「{c.name}」是系统生成的，但 meaning 是空的：取名就必须说清为什么推荐它")
                if c.origin == "用户提供" and c.meaning is not None:
                    raise ValueError(f"候选名「{c.name}」是用户提供的，但 meaning 有值：用户自己起的名字不该有『推荐理由』")
        return self
