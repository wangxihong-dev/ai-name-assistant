from models.name_history import NameHistory
from repository.name_history_repo import NameHistoryRepo
from schemas.name import NameIn,NameOut,NameResponseOut
from core.agent import generate_name
from models import AsyncSession



class NameService:
    def __init__(self,session:AsyncSession):
        self.session = session
        self.repo = NameHistoryRepo(self.session)

    async def generate_and_save_name(self,name_in:NameIn,user_id:int) ->NameOut:
        try:
            name_result=await generate_name(name_in)
        except Exception as e:
            print(e)
            raise
        history=NameHistory(
            user_id=user_id,
            surname=name_in.surname,
            gender=name_in.gender,
            length=name_in.length,
            other=name_in.other,
            result=(name_result.model_dump())
        )
        try:
            await self.repo.save_history(history)
        except Exception:
            return NameOut(
                names=name_result.names,
                message="历史记录保存失败"
            )
        return NameOut(
            names=name_result.names,
            message=None
        )

    async def get_name_history(self,user_id:int) ->NameResponseOut:
        histories=await self.repo.get_history_by_user_id(user_id)
        return NameResponseOut(
            histories=histories
        )





