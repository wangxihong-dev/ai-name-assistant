from fastapi import FastAPI, Depends
from fastapi_mail import FastMail,MessageSchema,MessageType
from dependencies import get_mail
from routers.auth_router import router as auth_router
from routers.name_router import router as name_router


app = FastAPI()

app.include_router(auth_router)

app.include_router(name_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/mail/test")
async def mail_test(
        email:str,
        mail:FastMail = Depends(get_mail),
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