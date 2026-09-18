"""会话这一层的业务逻辑，外加「数据库行 <-> langchain 消息对象」的双向翻译。

翻译为什么放这一层、不放 core/chat_agent.py：
  存储形状（哪一列装什么）只应该有一个地方知道。
  如果让 agent 去读 tool_calls 那个 JSON 字符串，存储细节就漏到编排层了。
  这一层对外只说 langchain 的消息对象——chat_agent 完全不知道库里有几张表。

这一层同时管两件事，不要混：
  ① 给模型用的上下文  -> load_history / save_round
  ② 给人看的历史      -> load_visible_rounds
  两者数据源相同，形状完全不同。

依赖方向（单向，没有环）：
  conversation_service -> conversation_repo -> models
"""
import json
import logging
from datetime import datetime

from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage, ToolMessage)

from errors import ConversationError
from models import AsyncSession
from models.conversation import Conversation, ConversationMessage
from repository.conversation_repo import ConversationRepo
from schemas.conversation import AgentReply, RoundOut

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ConversationRepo(session)

    # ══════════════════════════════════════════════════════
    # 会话
    # ══════════════════════════════════════════════════════

    async def open_or_get(self, conversation_id: int | None, user_id: int) -> int:
        """传 None 就新建一个会话；传了 id 就核对它存在、并且属于这个用户。

        ⚠️ 本方法不开事务，调用方负责 begin()。
        """
        if conversation_id is None:
            conversation = await self.repo.insert_conversation(
                Conversation(user_id=user_id))
            logger.info("新建会话 id=%s user_id=%s", conversation.id, user_id)
            return conversation.id

        conversation = await self.repo.get_conversation(conversation_id)

        # 权限边界：不核对归属就等于「谁猜到 id 就能读别人的对话」。
        # 而且抛出的消息故意不区分「不存在」和「不属于当前用户」——
        # 区分了别人就能拿它来枚举库里有哪些会话 id。
        if conversation is None or conversation.user_id != user_id:
            raise ConversationError(f"会话 id={conversation_id} 不存在或不属于 user_id={user_id}")
        return conversation.id

    # ══════════════════════════════════════════════════════
    # ① 给模型用的上下文
    # ══════════════════════════════════════════════════════

    async def load_history(self, conversation_id: int) -> list[BaseMessage]:
        """把库里的行还原成 langchain 消息对象，按时间顺序。

        注意这里不含系统提示词——它不落库，每次请求由 chat_agent 重新装配。

        将来的「只带最近 N 轮」就加在这里（token 的大头是历史，不是法条）。
        N 是多少还没定，所以这一版先全量取。
        """
        rows = await self.repo.get_messages(conversation_id)
        return [self._to_message(row) for row in rows]

    async def save_round(self, conversation_id: int, messages: list[BaseMessage],
                         status: str, payload: dict | None) -> int:
        """把这一轮新增的消息写库，status 和可见结果挂在最后一条上。

        ⚠️ 本方法不开事务，调用方负责 begin()。返回写进去的条数。
        """
        if not messages:
            # 走到这里说明调用方切片切错了，不是业务情况。宁可当场崩。
            raise ConversationError("这一轮没有任何消息要存，调用方的切片算错了")

        now = datetime.now()
        rows = [self._to_row(m, conversation_id, now) for m in messages]

        # 只挂最后一条：前端按「round_status 非空」切分轮次。
        # 挂每一条是冗余（同一轮的值全一样），挂第一条则前端要往后找。
        rows[-1].round_status = status
        rows[-1].round_payload = (json.dumps(payload, ensure_ascii=False)
                                  if payload is not None else None)

        conversation = await self.repo.get_conversation(conversation_id)
        if conversation is None:
            raise ConversationError(f"会话 id={conversation_id} 不存在，无法写入消息")
        conversation.last_active_at = now

        await self.repo.insert_messages(rows)
        return len(rows)

    # ══════════════════════════════════════════════════════
    # ② 给人看的历史
    # ══════════════════════════════════════════════════════

    async def load_visible_rounds(self, conversation_id: int) -> list[RoundOut]:
        """按轮次取出「给用户看的」历史，前端刷新页面后靠它重画消息列表。

        切分办法：顺着消息走，遇到 round_status 非空的那条就是一轮的结尾。
        """
        rows = await self.repo.get_messages(conversation_id)
        rounds: list[RoundOut] = []
        user_text: str | None = None

        for row in rows:
            if row.role == "user" and user_text is None:
                user_text = row.content

            if row.round_status is None:
                continue

            reply = (AgentReply.model_validate(json.loads(row.round_payload))
                     if row.round_payload else None)
            rounds.append(RoundOut(user_input=user_text or "",
                                   status=row.round_status,
                                   reply=reply,
                                   created_at=row.created_at))
            user_text = None

        if user_text is not None:
            # 有用户消息、却没有一条带 round_status 收尾 —— 说明上一次请求存到一半崩了。
            # 不静默丢掉，也不假装它是一轮：记一条日志。
            logger.warning("会话 %s 有一条没被任何一轮收尾的用户消息，上一次请求可能中途崩了",
                           conversation_id)
        return rounds

    # ══════════════════════════════════════════════════════
    # 双向翻译：这是整个文件唯一「知道存储形状」的地方
    # ══════════════════════════════════════════════════════

    @staticmethod
    def _to_message(row: ConversationMessage) -> BaseMessage:
        """数据库行 -> langchain 消息对象。"""
        if row.role == "user":
            return HumanMessage(content=row.content or "")

        if row.role == "tool":
            if not row.tool_call_id:
                # 少了这个 id，发给模型时接口直接 400。
                # 宁可当场崩，不要静默错——静默错的形状是「模型收不到工具结果」。
                raise ConversationError(f"消息 id={row.id} 是 tool 角色但没有 tool_call_id")
            return ToolMessage(content=row.content or "", tool_call_id=row.tool_call_id)

        if row.role == "assistant":
            # tool_calls 存的是 JSON 文本；没有工具调用时那一列是 NULL，
            # 还原成空列表而不是 None——AIMessage 要的是列表。
            tool_calls = json.loads(row.tool_calls) if row.tool_calls else []
            return AIMessage(content=row.content or "", tool_calls=tool_calls)

        raise ConversationError(f"消息 id={row.id} 的角色是 {row.role!r}，不在封闭三值里")

    @staticmethod
    def _to_row(message: BaseMessage, conversation_id: int,
                created_at: datetime) -> ConversationMessage:
        """langchain 消息对象 -> 数据库行。"""
        # system 故意不支持：系统提示词是代码不是数据。
        # 这里崩掉比静默存下去好——存下去就意味着改了提示词后老会话行为不一致。
        if isinstance(message, SystemMessage):
            raise ConversationError("system 消息不允许落库，它应该每次请求重新装配")

        content = message.content
        if content is not None and not isinstance(content, str):
            # 多模态模型的 content 可能是列表。这一版只接纯文本模型，
            # 遇到列表就当场报错，别 str() 硬转——那会存进去一段没法还原的东西。
            raise ConversationError(
                f"消息正文是 {type(content).__name__} 不是 str，这一版只支持纯文本模型")

        if isinstance(message, ToolMessage):
            return ConversationMessage(
                conversation_id=conversation_id, role="tool",
                content=content, tool_call_id=message.tool_call_id, created_at=created_at)

        if isinstance(message, AIMessage):
            # msg.tool_calls 是 langchain 已经解析好的列表，直接 dumps 就能存；
            # 还原时 AIMessage(tool_calls=[...]) 能吃回去。
            # ensure_ascii=False：不然中文会被转成 \uXXXX，库里没法看。
            tool_calls = (json.dumps(message.tool_calls, ensure_ascii=False)
                          if message.tool_calls else None)
            return ConversationMessage(
                conversation_id=conversation_id, role="assistant",
                content=content, tool_calls=tool_calls, created_at=created_at)

        if isinstance(message, HumanMessage):
            return ConversationMessage(
                conversation_id=conversation_id, role="user",
                content=content, created_at=created_at)

        raise ConversationError(f"不认识的消息类型 {type(message).__name__}")
