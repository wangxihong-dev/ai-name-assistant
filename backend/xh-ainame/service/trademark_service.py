from repository.forbidden_word_repo import ForbiddenWordRepo
from repository.law_repository import LawRepo
from models.law_version import LawVersion
from models import AsyncSession
import asyncio
from models import AsyncSessionFactory
from errors import TrademarkDataError

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



    async def scan_name(self, name: str, version: LawVersion) -> list[tuple[int, str]]:
        longest = await self.get_longest(name)
        if not longest:
            return []

        hits: list[tuple[int, str]] = []
        for kind, word in longest.items():
            wordkindclause = await self.forbidden_word_repo.get_wordkindclause_by_id_kind(
                version_id=version.id, word_kind=kind)
            if not wordkindclause:
                raise TrademarkDataError(
                    f"wordkindclause表里面没有版本为：{version.id} 类别为：{kind!r}的对象")

            hits.append((wordkindclause.clause_id, f"名字中包含『{word}』，属于{kind}"))

        return hits







async def main():
    async with AsyncSessionFactory() as session:
        server=TrademarkService(session)
        result=await server.scan_name("云栖茶叶")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())


