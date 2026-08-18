from pydantic import BaseModel,Field
from typing import List,Annotated,Literal
from schemas.agent import NameSchema


class NameIn(BaseModel):
    surname:Annotated[str,Field(...,description="姓氏")]
    gender:Annotated[Literal["不限","男","女"],Field(...,description="性别")]
    length:Annotated[Literal["不限","三字","两字","四字"],Field(...,description="字数")]
    other:Annotated[str|None,Field("",description="其他要求")]
    exclude:list[str]=[]


class NameOut(BaseModel):
    names:List[NameSchema]