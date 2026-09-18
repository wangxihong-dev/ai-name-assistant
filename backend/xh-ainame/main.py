import logging

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, MessageType

from dependencies import get_mail
from errors import ConversationError, TrademarkDataError
from routers.auth_router import router as auth_router
from routers.chat_router import router as chat_router
from routers.name_router import router as name_router

logger = logging.getLogger(__name__)

app = FastAPI()

# H5 前端与后端跨端口调用所需：开发期放开跨域，部署时再按需收紧
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

app.include_router(name_router)

app.include_router(chat_router)


# ══════════════════════════════════════════════════════════════
# 异常 -> HTTP 状态码
#
# 为什么放这里、不放 router 里 try/except：
#   「哪种异常配哪个状态码」是业务逻辑，而 router 只做「收 -> 调 -> return」。
# 为什么返回给前端的是一句固定的话：
#   把内部错误详情原样吐给客户端，等于把库结构和数据现状告诉外人。
#   真实原因写进服务端日志就够了。
# ══════════════════════════════════════════════════════════════

@app.exception_handler(ConversationError)
async def conversation_error_handler(request: Request, exc: ConversationError):
    logger.warning("会话错误 %s -> %s", request.url.path, exc)
    # 故意不区分「不存在」和「不属于当前用户」：区分了就能被拿来枚举别人的会话 id
    return JSONResponse(status_code=404, content={"detail": "会话不存在"})


@app.exception_handler(TrademarkDataError)
async def trademark_data_error_handler(request: Request, exc: TrademarkDataError):
    logger.exception("法条／名录数据故障 %s", request.url.path)
    return JSONResponse(status_code=500,
                        content={"detail": "系统的法条数据出了点问题，请稍后再试"})


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/mail/test")
async def mail_test(
        email: str,
        mail: FastMail = Depends(get_mail),
):
    message = MessageSchema(
        subject="hello",
        recipients=[email],
        body="Hello " + email,
        subtype=MessageType.plain
    )
    await mail.send_message(message)
    return {"message": "Mail sent"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
