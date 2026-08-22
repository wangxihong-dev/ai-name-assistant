from sqlalchemy import select
from models import AsyncSession
from models.name_history import NameHistory
from typing import List


class NameHistoryRepo:
    def __init__(self,session: AsyncSession):
        self.session = session


    async def  save_history(self,name_history: NameHistory) -> NameHistory:
        async with self.session.begin():
            self.session.add(name_history)
            return name_history

    async def get_history_by_user_id(self,user_id:int) -> List[NameHistory]:

        stmt = select(NameHistory).where(NameHistory.user_id == user_id)
        results=await self.session.scalars(stmt)
        return results.all()