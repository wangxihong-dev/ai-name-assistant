from datetime import datetime

from . import Base
from sqlalchemy import Integer, String,DateTime,ForeignKey,JSON
from sqlalchemy.orm import mapped_column,Mapped,relationship
from .user import User


class NameHistory(Base):
    __tablename__ = 'name_history'
    id: Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    user_id :Mapped[int]=mapped_column(Integer,ForeignKey("user.id"))
    surname:Mapped[str]=mapped_column(String(10),nullable=False)
    gender:Mapped[str]=mapped_column(String(10),nullable=False)
    length:Mapped[str]=mapped_column(String(10),nullable=False)
    other:Mapped[str]=mapped_column(String(500))
    result:Mapped[dict ]=mapped_column(JSON,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.now)
    user:Mapped["User"]=relationship("User",back_populates="name_histories")