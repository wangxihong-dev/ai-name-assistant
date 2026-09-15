from sqlalchemy import select,exists
from models import AsyncSession
from models.forbidden_word import ForbiddenWord,WordKindClause

class ForbiddenWordRepo:
    def __init__(self,session: AsyncSession):
        self.session = session


    async def insert_forbidden_word(self,forbidden_word:ForbiddenWord):
        self.session.add(forbidden_word)
        await self.session.flush()
        return forbidden_word

    async def forbidden_is_exists(self,word:str,word_kind:str)->bool:
        stmt = select(exists().where(ForbiddenWord.word == word,
                                     ForbiddenWord.word_kind ==word_kind))

        return await self.session.scalar(stmt)


    async def insert_word_kind_clause(self,wordkindclause:WordKindClause):
        self.session.add(wordkindclause)
        await self.session.flush()
        return wordkindclause


    async def word_kind_is_exists(self,word_kind:str,version_id:int)->bool:
        stmt = select(exists().where(WordKindClause.word_kind == word_kind,
                      WordKindClause.version_id==version_id))

        return await self.session.scalar(stmt)
