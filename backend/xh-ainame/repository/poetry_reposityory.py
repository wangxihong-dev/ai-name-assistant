
from sqlalchemy import select,exists
from models.poetry import Poetry
from models import AsyncSession
from typing import List



class PoetryRepo:
    def __init__(self,session: AsyncSession):
        self.session = session

    async def poetry_is_exist(self,source:str,source_id:str) ->bool:
        stmt = select(exists().where(Poetry.source == source ,Poetry.source_id == source_id))
        return await self.session.scalar(stmt)



    async def batch_insert(self,poetry:List[Poetry]) -> None :

        self.session.add_all(poetry)
