"""会话与消息的存取。

这一层只管数据库，不含任何业务判断——业务判断在 service 层。
跟 law_repository.py 一个形状：方法名 get_ 开头就是纯取数，
含规则计算的不许叫 get（这是本项目自己的命名规矩）。
"""
from models import AsyncSession
from models.conversation import Conversation, ConversationMessage
from sqlalchemy import select


class ConversationRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def insert_conversation(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        # flush 之后自增 id 就有了，但还没提交。
        # 事务边界属于业务动作，所以 begin() 在调用方（chat_service），不在这里。
        await self.session.flush()
        return conversation

    async def get_conversation(self, conversation_id: int) -> Conversation | None:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        return await self.session.scalar(stmt)

    async def get_messages(self, conversation_id: int) -> list[ConversationMessage]:
        # 按 id 升序 = 按插入顺序 = 按时间顺序。
        # 这里没有「恰好 N 行」那种守卫，因为 0 行是合法的（新会话）。
        stmt = (select(ConversationMessage)
                .where(ConversationMessage.conversation_id == conversation_id)
                .order_by(ConversationMessage.id))
        return list((await self.session.scalars(stmt)).all())

    async def insert_messages(self, messages: list[ConversationMessage]) -> None:
        # 一次 add_all，自增 id 会按列表顺序连续分配，
        # 所以下次按 id 升序读出来，顺序跟这一轮发生的顺序一致。
        self.session.add_all(messages)
        await self.session.flush()
