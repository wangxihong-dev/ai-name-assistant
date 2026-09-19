"""对话版的门面：把「会话持久化」和「agent 循环」串起来。

为什么要有这一层：
  本项目的规矩是「router 不写业务逻辑」，router 只做「收 -> 调 -> return」。
  那「开会话 / 取历史 / 跑 agent / 存这一轮」这套编排就得有人做，就是这里。

依赖方向（单向，没有环）：
  chat_service ──> conversation_service ──> conversation_repo ──> models
       └─────────> core.chat_agent  ──> law / trademark / risk_merge service

注意 chat_agent 不知道 conversation_service 的存在，反过来也是。
两边只通过「一个消息列表」说话——这就是它们之间唯一的接口。
"""
import asyncio
import logging
from typing import AsyncIterator, Callable, Awaitable

from langchain_core.messages import BaseMessage

from core.chat_agent import AgentRunResult, run_agent
from models import AsyncSession
from schemas.conversation import DISCLAIMER, ChatResponse, HistoryOut, StageCode
from service.conversation_service import ConversationService

logger = logging.getLogger(__name__)

# 流已经开始（HTTP 200 和响应头都发出去了）之后再出错，状态码就改不了了，
# 只能把错误当成一个事件发出去。所以这句话必须能独立看懂。
STREAM_ERROR_TEXT = "这次没能生成结果，请重试一次"

# 队列的收尾哨兵。用一个独一无二的对象，这样它不可能跟任何事件字典撞上。
_DONE = object()

StageEmitter = Callable[[StageCode, str], Awaitable[None]]


class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.conversation_service = ConversationService(session)

    # ══════════════════════════════════════════════════════
    # 会话
    # ══════════════════════════════════════════════════════

    async def open_conversation(self, conversation_id: int | None, user_id: int) -> int:
        """把「确定会话」单独拎出来。

        流式接口必须在发出响应头之前调它——一旦开始流，状态码就改不了，
        会话不存在就只能塞进事件里，前端就拿不到 404 了。
        """
        async with self.session.begin():
            return await self.conversation_service.open_or_get(conversation_id, user_id)

    # ══════════════════════════════════════════════════════
    # 普通接口：一次请求一个完整响应
    # ══════════════════════════════════════════════════════

    async def chat(self, user_input: str, user_id: int,
                   conversation_id: int | None = None) -> ChatResponse:
        cid = await self.open_conversation(conversation_id, user_id)
        return await self._run_round(user_input, cid, user_id, on_event=None)

    # ══════════════════════════════════════════════════════
    # 流式接口：先吐进度事件，最后吐一个 result（或 error）
    # ══════════════════════════════════════════════════════

    async def chat_stream(self, user_input: str, conversation_id: int,
                          user_id: int) -> AsyncIterator[dict]:
        """异步生成器，产出的是「事件字典」，不是 SSE 文本。

        SSE 的线上格式是传输层的事，归 router 拼——这一层不该知道自己
        最终是走 SSE 还是走别的什么推送方式。
        """
        queue: asyncio.Queue = asyncio.Queue()

        async def on_event(code: StageCode, text: str) -> None:
            await queue.put({"event": "stage", "code": code, "text": text})

        async def runner() -> None:
            try:
                response = await self._run_round(user_input, conversation_id, user_id, on_event)
                await queue.put({"event": "result", "data": response.model_dump()})
            except Exception:
                logger.exception("流式对话出错，会话 %s", conversation_id)
                await queue.put({"event": "error", "text": STREAM_ERROR_TEXT})
            finally:
                await queue.put(_DONE)

        task = asyncio.create_task(runner())
        try:
            while True:
                item = await queue.get()
                if item is _DONE:
                    break
                yield item
        finally:
            # 客户端中途断开（浏览器关页面）时，生成器会被 GeneratorExit 关掉，
            # 这个 finally 就会跑到。此时必须把后台任务掐掉——
            # 否则它会把整个 agent 循环跑完，继续烧模型调用的钱，
            # 而且它跑完还会往一个没人读的队列里塞东西。
            if not task.done():
                logger.info("客户端断开，取消会话 %s 的后台任务", conversation_id)
                task.cancel()

    # ══════════════════════════════════════════════════════
    # 一轮对话：普通接口和流式接口共用这一段
    # ══════════════════════════════════════════════════════

    async def _run_round(self, user_input: str, cid: int, user_id: int,
                         on_event: StageEmitter | None) -> ChatResponse:
        # ── 取历史（短事务）──
        async with self.session.begin():
            history: list[BaseMessage] = await self.conversation_service.load_history(cid)

        # ── 跑 agent ──
        # 故意放在事务外面。这一步会打模型、可能十几秒，
        # 把数据库连接攥在手里等外部 API 是浪费，也会拖长锁的持有时间。
        result: AgentRunResult = await run_agent(user_input, history, self.session, on_event)

        # ⚠️ 下面这个 if 是必须的，而且很不明显：
        # run_agent 里那些只读查询（查法条版本、扫名录、回表）会让 SQLAlchemy
        # 「自动开一个事务」。不先把它结束掉，接下来的 session.begin()
        # 会当场报 InvalidRequestError: A transaction is already begun。
        if self.session.in_transaction():
            await self.session.commit()

        # ── 存这一轮（又一个短事务）──
        # new_messages 里已经排除了系统提示词和历史，所以整份存进去不会重复。
        # payload 是「给人看的」那一份：AgentSchema 去掉 status（单独存一列）、
        # 去掉耗时和工具调用次数（运行时指标，历史里没人看）。
        payload = result.schema.model_dump(
            exclude={"status", "duration_seconds", "tool_call_count"})
        async with self.session.begin():
            saved = await self.conversation_service.save_round(
                cid, result.new_messages, result.schema.status, payload)

        # 免责措辞由代码填，不由模型写。只在真的给出了名字时出现——
        # 失败和澄清中时没有「以上」，挂一句免责反而是废话。
        # 忘了填不会静默通过：ChatResponse 那条 validator 会当场报错。
        disclaimer = DISCLAIMER if result.schema.status in ("正常", "降级") else None

        logger.info("会话 %s 这一轮存了 %s 条消息，status=%s", cid, saved, result.schema.status)
        return ChatResponse(conversation_id=cid, result=result.schema, disclaimer=disclaimer)

    # ══════════════════════════════════════════════════════
    # 历史
    # ══════════════════════════════════════════════════════

    async def get_history(self, conversation_id: int, user_id: int) -> HistoryOut:
        """前端刷新页面后重画消息列表用。只读，所以一个事务包住就够了。"""
        async with self.session.begin():
            cid = await self.conversation_service.open_or_get(conversation_id, user_id)
            rounds = await self.conversation_service.load_visible_rounds(cid)
        logger.info("会话 %s 取历史，共 %s 轮", cid, len(rounds))
        return HistoryOut(conversation_id=cid, rounds=rounds)
