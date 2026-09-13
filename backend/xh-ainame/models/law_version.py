from . import Base
from sqlalchemy.orm import Mapped,relationship,mapped_column
from sqlalchemy import Integer,String,DATE
from datetime import date
from typing import List,TYPE_CHECKING

if TYPE_CHECKING:
    from .law_clause import LawClause

class LawVersion(Base):
    __tablename__ = 'law_version'
    id:Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    law_name:Mapped[str] = mapped_column(String(50))
    version_name:Mapped[str] = mapped_column(String(30))
    enforcement_date:Mapped[date] = mapped_column(DATE)
    expiry_date:Mapped[date|None] = mapped_column(DATE,nullable=True)
    law_clauses:Mapped[List["LawClause"]] = relationship("LawClause",back_populates="law_version")