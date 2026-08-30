from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List

class FavoriteIn(BaseModel):
    name:str
    reference:str
    moral:str


class FavoriteOut(BaseModel):
    id:int
    name:str
    reference:str
    moral:str
    created_at:datetime


    model_config = ConfigDict(
        from_attributes=True,
    )

class FavoritesResponseOut(BaseModel):
    favorites:List[FavoriteOut]