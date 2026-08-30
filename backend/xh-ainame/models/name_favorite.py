from datetime import datetime

from sqlalchemy.orm import relationship,Mapped,mapped_column
from sqlalchemy import Integer, String, DATETIME, ForeignKey,Text
from . import Base
from .user import User


class NameFavorite(Base):
    __tablename__ = 'name_favorite'
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    user_id:Mapped[int]=mapped_column(Integer,ForeignKey('user.id'))
    name:Mapped[str]=mapped_column(String(10),nullable=False)
    reference :Mapped[str]=mapped_column(Text,nullable=False)
    moral:Mapped[str]=mapped_column(Text,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DATETIME,default=datetime.now)
    user:Mapped["User"]=relationship("User",back_populates="name_favorites")