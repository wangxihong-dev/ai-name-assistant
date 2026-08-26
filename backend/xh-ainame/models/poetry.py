
from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import mapped_column,Mapped
from . import Base

class Poetry(Base):
    __tablename__ = 'poetry'
    id: Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    source:Mapped[str]=mapped_column(String(100),nullable=False)
    source_id:Mapped[str]=mapped_column(String(50),nullable=False)
    title:Mapped[str]=mapped_column(String(100),nullable=False)
    author:Mapped[str]=mapped_column(String(50),nullable=False)
    dynasty:Mapped[str]=mapped_column(String(50),nullable=False)
    content:Mapped[str]=mapped_column(Text,nullable=False)

    __table_args__ = (
        UniqueConstraint('source_id','source'),
    )