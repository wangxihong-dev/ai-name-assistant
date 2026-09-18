from repository.law_repository import LawRepo
from models import AsyncSession
from models.law_version import LawVersion
from errors import TrademarkDataError


class LawService:
    def __init__(self,session:AsyncSession):
        self.law_repo = LawRepo(session)


    async def build_clause_block(self, version: LawVersion) -> str:
        clauses=await self.law_repo.get_all_clauses_by_version(version.id)
        if not clauses:
            raise TrademarkDataError(f"law_clause 表里没有 version_id={version.id} 的条款"
                                     f"（{version.law_name} {version.version_name}）")

        lines = [f"【{c.id}】{c.clause_number}：{c.clause_original}" for c in clauses]
        return "\n".join(lines)

