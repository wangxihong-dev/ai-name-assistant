from schemas.favorite import FavoriteIn,FavoritesResponseOut,FavoriteOut
from repository.name_favorite_repository import NameFavoriteRepository
from models import AsyncSession
from models.name_favorite import NameFavorite


class FavoritesService:
    def __init__(self,session: AsyncSession):
        self.session = session
        self.repo=NameFavoriteRepository(session)

    async def create_favorite(self,favoritein: FavoriteIn,user_id: int)->FavoriteOut :
        favorite=NameFavorite(
            user_id=user_id,
            name=favoritein.name,
            reference=favoritein.reference,
            moral=favoritein.moral
        )
        await self.repo.save_favorite(favorite)
        return FavoriteOut.model_validate(favorite)


    async def delete_favorite(self,favorite_id:int,user_id: int)->bool :
        return await self.repo.delete_favorite(favorite_id,user_id)

    async def get_favorites(self,user_id: int) -> FavoritesResponseOut:
        favorites=await self.repo.get_favorites_by_user_id(user_id)
        return FavoritesResponseOut(favorites=favorites)


