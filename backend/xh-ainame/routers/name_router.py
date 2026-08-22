from fastapi import APIRouter,Depends
from schemas.name import NameIn,NameOut,NameResponseOut
from service.name_service import NameService
from core.auth import AuthHandler
from dependencies import get_name_service


authhandler = AuthHandler()

router = APIRouter(prefix="/name")


@router.post('/',response_model=NameOut)
async def take_name(
        data:NameIn,
        user_id:int =Depends(authhandler.auth_access_dependency),
        service:NameService=Depends(get_name_service)
):
    name_result=await service.generate_and_save_name(name_in=data,user_id=user_id)
    return name_result


@router.get('/history',response_model=NameResponseOut)
async def get_history(
        user_id:int =Depends(authhandler.auth_access_dependency),
        service:NameService=Depends(get_name_service)
):
    history=await service.get_name_history(user_id=user_id)
    return history



