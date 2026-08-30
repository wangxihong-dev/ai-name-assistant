from core.mail import create_mail_instance
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession
from models import AsyncSessionFactory
from service.name_service import NameService
from fastapi import Depends
from service.favorite_service import FavoritesService


async def get_mail() -> FastMail:
    return create_mail_instance()


async def get_session() -> AsyncSession:
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()

async def get_name_service(session:AsyncSession=Depends(get_session)) -> NameService:
    return NameService(session=session)


async def get_favorite_service(session:AsyncSession=Depends(get_session)) -> FavoritesService:
    return FavoritesService(session=session)