"""对话版的两个接口。

跟 name_router 一个形状：收 -> 调 -> return，零业务逻辑。
编排全在 ChatService 里，异常到状态码的映射在 main.py 的 exception handler 里
（那也是业务逻辑，所以不放这里）。
"""
from fastapi import APIRouter, Depends

from core.auth import AuthHandler
from dependencies import get_chat_service
from schemas.conversation import ChatIn, ChatResponse, HistoryOut
from service.chat_service import ChatService

authhandler = AuthHandler()

router = APIRouter(prefix="/chat")


@router.post("/", response_model=ChatResponse)
async def chat(
        data: ChatIn,
        user_id: int = Depends(authhandler.auth_access_dependency),
        service: ChatService = Depends(get_chat_service),
):
    return await service.chat(user_input=data.user_input,
                              conversation_id=data.conversation_id,
                              user_id=user_id)


@router.get("/{conversation_id}/history", response_model=HistoryOut)
async def get_history(
        conversation_id: int,
        user_id: int = Depends(authhandler.auth_access_dependency),
        service: ChatService = Depends(get_chat_service),
):
    return await service.get_history(conversation_id=conversation_id, user_id=user_id)
