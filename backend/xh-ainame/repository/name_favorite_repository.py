
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.name_favorite import NameFavorite
from typing import List


class NameFavoriteRepository:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def save_favorite(self,name_favorite: NameFavorite) -> NameFavorite:
        async with self.session.begin():
            self.session.add(name_favorite)
            return name_favorite


    async def delete_favorite(self,id:int,user_id:int) -> bool:
        async with self.session.begin():
            stmt = delete(NameFavorite).where(NameFavorite.id == id,NameFavorite.user_id == user_id)
            result=await self.session.execute(stmt)
            return result.rowcount >0

    async def get_favorites_by_user_id(self,user_id: int) -> List[NameFavorite]:
        stmt = select(NameFavorite).where(NameFavorite.user_id == user_id)
        result=await self.session.scalars(stmt)
        return result.all()
