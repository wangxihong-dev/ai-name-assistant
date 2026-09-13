from sqlalchemy.orm import relationship,mapped_column,Mapped
from sqlalchemy import Integer, String, ForeignKey,Text
from . import Base
from .law_version import LawVersion
from typing import Literal

class LawClause(Base):
    __tablename__ = 'law_clause'
    id :Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    version_id:Mapped[int]= mapped_column(Integer,ForeignKey('law_version.id'))
    clause_number:Mapped[str]= mapped_column(String(100),nullable=False)
    clause_original:Mapped[str]= mapped_column(Text,nullable=False)
    risk_grade:Mapped[Literal["禁止使用","不予注册","例外规定"]] = mapped_column(String(20),nullable=False)
    law_version:Mapped["LawVersion"] =relationship("LawVersion",back_populates="law_clauses")