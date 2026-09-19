"""对话版的三个接口。

跟 name_router 一个形状：收 -> 调 -> return，零业务逻辑。
编排全在 ChatService 里，异常到状态码的映射在 main.py 的 exception handler 里
（那也算业务逻辑，所以不放这里）。
"""
import json
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from core.auth import AuthHandler
from dependencies import get_chat_service
from schemas.conversation import ChatIn, ChatResponse, HistoryOut
from service.chat_service import ChatService

authhandler = AuthHandler()

router = APIRouter(prefix="/chat")


def _sse(payload: dict) -> str:
    """把一个事件字典拼成 SSE 的线上格式。

    格式是固定的：event 一行、data 一行、再来一个空行表示这条事件结束。
    data 必须是单行——json.dumps 会把字符串里的换行转义成 \\n，所以安全。
    """
    event = payload["event"]
    body = {k: v for k, v in payload.items() if k != "event"}
    return f"event: {event}\ndata: {json.dumps(body, ensure_ascii=False)}\n\n"


@router.post("/", response_model=ChatResponse)
async def chat(
        data: ChatIn,
        user_id: int = Depends(authhandler.auth_access_dependency),
        service: ChatService = Depends(get_chat_service),
):
    return await service.chat(user_input=data.user_input,
                              conversation_id=data.conversation_id,
                              user_id=user_id)


@router.post("/stream")
async def chat_stream(
        data: ChatIn,
        user_id: int = Depends(authhandler.auth_access_dependency),
        service: ChatService = Depends(get_chat_service),
):
    """流式版：推进度事件，最后推一个完整结果。

    流的不是模型吐的字，是「系统正在做什么」——原因写在 schemas/conversation.py
    的 StageCode 上面那段注释里。
    """
    # 必须在返回 StreamingResponse 之前把会话确定下来：
    # 会话不存在或不属于当前用户时这一步会抛 ConversationError -> 404。
    # 一旦开始流，HTTP 状态码就改不了了。
    cid = await service.open_conversation(data.conversation_id, user_id)

    async def wrap() -> AsyncIterator[str]:
        async for event in service.chat_stream(data.user_input, cid, user_id):
            yield _sse(event)

    return StreamingResponse(
        wrap(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # nginx 默认缓冲上游响应。不关掉的话事件会被攒到最后一次性吐出来，
            # 流式就白做了。这个响应头让 nginx 对这一条响应单独关缓冲。
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{conversation_id}/history", response_model=HistoryOut)
async def get_history(
        conversation_id: int,
        user_id: int = Depends(authhandler.auth_access_dependency),
        service: ChatService = Depends(get_chat_service),
):
    return await service.get_history(conversation_id=conversation_id, user_id=user_id)
