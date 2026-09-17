from models import AsyncSession
from models.law_version import LawVersion
from models.law_clause import LawClause
from sqlalchemy import select,exists,or_
from datetime import date
from errors import TrademarkDataError


class LawRepo:
    def __init__(self,session:AsyncSession):
        self.session = session


    async def insert_law_version(self,law_version:LawVersion):
        self.session.add(law_version)
        await self.session.flush()
        return law_version

    async def insert_law_clause(self,law_clause:LawClause):
        self.session.add(law_clause)

    async def law_is_exist(self,law_name:str,version_name:str)->bool:
        stmt= select(exists().where(LawVersion.law_name==law_name ,LawVersion.version_name==version_name))
        return await self.session.scalar(stmt)

    async def get_law_clause(self,version_id:int,clause_number:str)->LawClause|None:
        stmt = select(LawClause).where(LawClause.version_id==version_id,
                                       LawClause.clause_number==clause_number)
        return await self.session.scalar(stmt)

    async def get_law_version(self,version_name:str,law_name:str)->LawVersion|None:
        stmt = select(LawVersion).where(LawVersion.version_name==version_name,
                                        LawVersion.law_name==law_name)
        return await self.session.scalar(stmt)

    async def get_law_version_by_date(self,today:date)->LawVersion:
        stmt = select(LawVersion).where(
            LawVersion.enforcement_date <= today,
            or_(LawVersion.expiry_date.is_(None), LawVersion.expiry_date > today),
            )
        rows = (await self.session.scalars(stmt)).all()
        if len(rows) != 1:
            raise TrademarkDataError(f"当前生效版本应恰好 1 个，实际 {len(rows)} 个")
        return rows[0]

    async def get_law_clause_by_id(self,id:int)->LawClause|None:
        stmt = select(LawClause).where(LawClause.id == id)
        return await self.session.scalar(stmt)

    async def get_clauses_by_version(self, version_id: int) -> list[LawClause]:
        stmt = select(LawClause).where(LawClause.version_id == version_id).order_by(LawClause.id)
        return list((await self.session.scalars(stmt)).all())
