from fastapi import APIRouter,Depends
from schemas.name import NameIn,NameOut,NameResponseOut
from service.name_service import NameService
from core.auth import AuthHandler
from dependencies import get_name_service,get_favorite_service
from schemas.favorite import FavoritesResponseOut,FavoriteIn,FavoriteOut
from service.favorite_service import FavoritesService


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


@router.post("/favorite",response_model=FavoriteOut)
async def take_favorite(
        data:FavoriteIn,
        user_id:int =Depends(authhandler.auth_access_dependency),
        service:FavoritesService=Depends(get_favorite_service)
):
    favorite_result=await service.create_favorite(favoritein=data,user_id=user_id)
    return favorite_result

@router.delete("/delete/{favorite_id}",response_model=bool)
async def delete_favorite(
        favorite_id:int ,
        user_id:int =Depends(authhandler.auth_access_dependency),
        service:FavoritesService=Depends(get_favorite_service),

):
    return await service.delete_favorite(favorite_id=favorite_id,user_id=user_id)


@router.get("/favorites",response_model=FavoritesResponseOut)
async def get_favorites(
        user_id:int =Depends(authhandler.auth_access_dependency),
        service:FavoritesService=Depends(get_favorite_service)
):
    favorites=await service.get_favorites(user_id=user_id)
    return favorites



