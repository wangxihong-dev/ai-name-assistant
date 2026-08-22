from fastapi import APIRouter,Query,Depends,HTTPException
from pydantic import EmailStr
from typing import Annotated
from dependencies import get_mail,get_session
from models import AsyncSession
from fastapi_mail import FastMail,MessageSchema,MessageType
import string,secrets
from repository.user_repo import EmailCodeRepository,UserRepository
from schemas import ResponseOut
from schemas.user import RegisterIn,UserCreateSchema,LoginIn,LoginOut
from models.user import User
from core.auth import AuthHandler

router = APIRouter(
    prefix="/auth",
    tags=["user"],
)

auth_handler=AuthHandler()
@router.get("/code",response_model=ResponseOut)
async def get_user_code(
        email:Annotated[EmailStr,Query(...)],
        mail:FastMail=Depends(get_mail),
        session:AsyncSession=Depends(get_session),
):
    #1.生成4位数字的验证码
    code = "".join(secrets.choice(string.digits)
                   for _ in range(4))
    #创建消息对象
    message = MessageSchema(
        subject = "【习鸿AI】注册验证码",
        recipients=[email],
        body = f"您的验证码：{code}，五分钟内有效",
        subtype=MessageType.plain
    )
    try:
        await mail.send_message(message)
    except Exception as e:
        print(f"有bug",e)
        raise HTTPException(500,detail="邮件发送失败！")
    else:
        #将邮箱和验证码存到数据库当中
        email_code_repo = EmailCodeRepository(session=session)
        await email_code_repo.create(str(email),code)
    return ResponseOut()



@router.post("/register",response_model=ResponseOut)
async def register(
        data:RegisterIn,
        session:AsyncSession=Depends(get_session),
):
    user_repo = UserRepository(session=session)
    #1.判断邮箱是否存在
    email_exist=await user_repo.email_is_exist(email=data.email)
    if email_exist:
        raise HTTPException(400,detail="该邮箱已经存在")

    #2.校验验证码是否正确
    email_code_repo = EmailCodeRepository(session=session)
    email_code_match=await email_code_repo.check(email=data.email,code=data.code)

    if not email_code_match:
        raise HTTPException(400,detail="邮箱或者验证码错误")
    try:
        await user_repo.create(UserCreateSchema(email = data.email,username=data.username,
        password=data.password))

    except Exception as e:
        raise HTTPException(500,detail=str(e))

    return ResponseOut()

@router.post("/login",response_model=LoginOut)
async def login(
        data:LoginIn,
        session:AsyncSession=Depends(get_session),
):
    #1.创建user_repo对象
    user_repo = UserRepository(session=session)
    #2.通过邮箱检查对象是否存在着
    user: User|None = await user_repo.get_by_email(str(data.email))
    if not user:
        raise HTTPException(400,detail="该用户不存在!")

    if not user.check_password(raw_password=data.password):
        raise HTTPException(400,detail="邮箱或密码错误!")

    #3.生成JWToken
    tokens=auth_handler.encode_login_token(user.id)
    return {
        "user":user,
        "tokens":tokens["access_token"]
    }





