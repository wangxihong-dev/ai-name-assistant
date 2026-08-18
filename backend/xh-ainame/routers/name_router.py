from fastapi import APIRouter,Depends
from schemas.name import NameIn,NameOut
from core.agent import generate_name
from core.auth import AuthHandler

authhandler = AuthHandler()

router = APIRouter(prefix="/name")


@router.post('/',response_model=NameOut)
async def take_name(
        data:NameIn,
        user_id:int =Depends(authhandler.auth_access_dependency)
):
    name_result =await generate_name(data)
    return NameOut(names=name_result.names)


