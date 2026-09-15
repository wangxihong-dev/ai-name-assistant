from . import Base
from sqlalchemy.orm import mapped_column,Mapped
from sqlalchemy import Integer,String,UniqueConstraint,ForeignKey
from typing import Literal

WordKind=Mapped[Literal[
    "国家名称","国旗国徽勋章","中央国家机关","特定地点或标志性建筑","公众知晓的外国地名",
    "外国国家名称","政府间国际组织","官方标志或检验印记","红十字红新月","行政区划地名"
]]

class ForbiddenWord(Base):
    __tablename__ = 'forbidden_word'
    id :Mapped[int] =mapped_column(Integer,primary_key=True,autoincrement=True)
    word:Mapped[str]=mapped_column(String(50),nullable=False)
    word_kind:WordKind=mapped_column(String(30),nullable=False)

    __table_args__ = (
        UniqueConstraint('word','word_kind'),
    )

class WordKindClause(Base):
    __tablename__ = 'word_kind_clause'
    id :Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    word_kind:WordKind=mapped_column(String(30),nullable=False)
    version_id:Mapped[int]=mapped_column(Integer,ForeignKey("law_version.id"),nullable=False)
    clause_id:Mapped[int]=mapped_column(Integer,ForeignKey("law_clause.id"),nullable=False)

    __table_args__ = (
        UniqueConstraint('version_id',"word_kind"),
    )