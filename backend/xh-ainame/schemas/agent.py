from typing import Annotated, List
from pydantic import BaseModel,Field

class NameSchema(BaseModel):
    name: Annotated[str,Field(...,description="姓名")]
    reference:Annotated[str,Field(...,description="出处")]
    #author:Annotated[str,Field(...,description="作者")]
    #dynasty:Annotated[str,Field(...,description="朝代")]
    moral:Annotated[str,Field(...,description="寓意")]


class NameResultSchema(BaseModel):
    names:List[NameSchema]