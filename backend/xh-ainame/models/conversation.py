"""对话版的两张表：会话 + 消息。

为什么不叫 session：SQLAlchemy 里数据库连接也叫 session，
一个项目里出现两个 session 会让人分不清，所以这条线统一叫 conversation。

为什么是两张表：一个会话有很多条消息，一对多。
跟当初拆 law_version / law_clause 是同一个判据。
"""
from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from datetime import datetime
from typing import Literal


# ── 两个封闭枚举 ────────────────────────────────────────────────
# 消息角色只有三个值。system 故意不在里面：
# 系统提示词是「代码」不是「数据」，每次请求重新装配。
# 落库的后果是——改了提示词之后老会话的行为跟新会话不一致，
# 而且事后查不出当时用的是哪一版。
MessageRole = Literal["user", "assistant", "tool"]

# 一轮对话的结局，取值跟 AgentSchema.status 完全一致。
# 前端靠它决定画什么（名字卡片 / 反问气泡 / 失败提示），
# 不用去读消息正文猜——「靠状态字段区分，不靠内容猜」。
#
# ⚠️ 已知重复：这四个值在 schemas/agent.py 的 AgentSchema.status 里也写了一遍。
# 项目里 risk_grade 那三个值也是同样的重复（models/law_clause.py 和
# schemas/agent.py 各一份）。要收敛就抽一个 constants.py，两处都从那儿 import——
# 那是个独立的小重构，别混在这一格里做。
RoundStatus = Literal["正常", "降级", "失败", "澄清中"]


class Conversation(Base):
    """一次对话。前端拿着它的 id 来找回历史。"""

    __tablename__ = 'conversation'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # NOT NULL：对话版要求登录（已裁决）。
    # 判据是「可空性要有业务含义才给」——既然每个会话都必然属于某个用户，
    # 可空就没有业务含义，只是少了一道防线。
    # 它同时是权限边界：查历史、接着聊之前都要核对这一列等不等于当前用户。
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('user.id'), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    # 会话列表要按「最近聊过的」排序，所以这一列必须有，而且每轮都要更新
    last_active_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)


class ConversationMessage(Base):
    """一条消息一行。

    为什么不把整段历史存成一个 JSON 大字段：
      那样每轮都要「读出来 → 改 → 写回去」，并发时后写覆盖先写，
      而且没法按角色统计、没法只取最近 N 轮。

    为什么一条消息内部的 tool_calls 反而存成 JSON 文本：
      判据是「会不会需要单独查它」。
      整段历史会（要按会话取、要排序），所以拆成行；
      tool_calls 不会——它只是这条消息的一个零件，永远跟着消息一起进出。
    """

    __tablename__ = 'conversation_message'

    # 自增主键顺便解决两件事：
    #   ① 会话内消息的顺序（按 id 升序就是时间序）
    #   ② 同一时刻插两行时的排序打平
    # ⚠️ 不能拿 conversation_id 当主键：一个会话有 N 条消息，
    #    会话 id 会重复，插第二条就主键冲突。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('conversation.id'), nullable=False, index=True)

    role: Mapped[MessageRole] = mapped_column(String(10), nullable=False)

    # 正文。assistant 决定调工具那一轮，正文是空的，所以必须可空。
    # 这里的可空有业务含义（「这一条本来就没有正文」），不是偷懒。
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # assistant 专属：这一条要调哪些工具。
    # JSON 文本，形如 [{"name":"poetry_tool","args":{...},"id":"call_xxx","type":"tool_call"}]
    # ⚠️ 模型的原始答案也在这里面——但那是「加工前」的，见下面 round_payload。
    tool_calls: Mapped[str | None] = mapped_column(Text, nullable=True)

    # tool 消息专属：它回的是哪一次调用。
    # 跟上面 tool_calls 里的 id 一一对应，少一条接口直接 400。
    tool_call_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # ── 下面两列只在「一轮的最后一条消息」上写，其余行是 NULL ──
    # 前端按「round_status 非空」切分轮次。

    round_status: Mapped[RoundStatus | None] = mapped_column(String(10), nullable=True)

    # 这一轮「给用户看的」可见结果，JSON 文本：intent / candidates / user_message。
    #
    # 为什么必须单独存，不能从上面 tool_calls 里现算：
    #   tool_calls 里那个 ModelOutput 是「模型的原始产出」——risks 里只有 clause_id
    #   和模型自己写的那句理由。而用户看到的是「加工后」的：条款号、条款原文、
    #   风险等级、法条版本，还有名录扫描那一侧合并进来的理由。
    #   那些都是代码回表拼出来的，库里没有第二份，所以必须落下来。
    round_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
