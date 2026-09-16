from repository.forbidden_word_repo import ForbiddenWordRepo
from repository.law_repository import LawRepo
from models.forbidden_word import ForbiddenWord,WordKindClause
from models.law_version import LawVersion
from models.law_clause import LawClause
from models import AsyncSession
from schemas.agent import RiskDetail
import asyncio
from models import AsyncSessionFactory
from datetime import date


class TrademarkDataError(Exception):
    """名录或法条数据对不上：系统故障，不是业务结果"""

class TrademarkService:
    def __init__(self,session:AsyncSession):
        self.session = session
        self.law_repo = LawRepo(self.session)
        self.forbidden_word_repo = ForbiddenWordRepo(self.session)

    async def get_longest(self,name:str):
        all_words=await self.forbidden_word_repo.get_all_forbidden_words()
        upper_name=name.upper()
        hits=[(w.word,w.word_kind) for w in all_words if w.word in upper_name]
        longest = {}
        for word ,kind in hits:
            if kind not in longest or len(word)> len(longest[kind]):
                longest[kind]=word
        return longest



    async def scan_name(self, name: str) -> list[RiskDetail]:
        longest=await self.get_longest(name)
        if not longest:
            return []
        today=date.today()
        version=await self.law_repo.get_law_version_by_date(today)
        risk_detail_list=[]
        for kind,word in longest.items():
            wordkindclause=await (self.forbidden_word_repo.get_wordkindclause_by_id_kind
                                  (version_id=version.id,word_kind=kind))
            if wordkindclause:
                clause_id=wordkindclause.clause_id
                clause=await self.law_repo.get_law_clause_by_id(clause_id)
                if clause:
                    detail=RiskDetail(
                        clause_number=clause.clause_number,
                        clause_original=clause.clause_original,
                        risk_grade=clause.risk_grade,
                        law_name=version.law_name,
                        law_version_name=version.version_name,
                        reason=f"名字中包含『{word}』，属于{kind}"
                    )
                    risk_detail_list.append(detail)
                else:
                    raise TrademarkDataError(f"clause表里没有id为：{clause_id}的对象")
            else:
                raise TrademarkDataError(f"wordkindclause表里面没有版本为：{version.id} 类别为：{kind!r}的对象")

        return risk_detail_list







async def main():
    async with AsyncSessionFactory() as session:
        server=TrademarkService(session)
        result=await server.scan_name("云栖茶")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())


