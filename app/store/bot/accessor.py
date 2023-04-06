from typing import Optional

from sqlalchemy import select, ChunkedIteratorResult, insert, delete, update, Select, Delete

from ...base.base_accessor import BaseAccessor
from ...tg_bot.bot.models import TraceableMessageModel as TMsgModel, TraceableMessage


class TraceableMessageAccessor(BaseAccessor):
    async def create_message(self, chat_id: int, session_id: int, type_: str, message_id: int) -> TraceableMessage:
        query = insert(TMsgModel).values(
            chat_id=chat_id,
            session_id=session_id,
            type=type_,
            message_id=message_id
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return TraceableMessage(chat_id, session_id, type_, message_id)

    async def get_messages(
            self,
            chat_id: int,
            type_: Optional[str] = None,
            message_id: int = None
    ) -> list[TraceableMessage]:
        # Здесь не указана переменная session_id, так как в чате может быть только одна сессия,
        # а значит запросы по этим параметрам будут возвращать одинаковые результаты
        query = await self.__get_select(chat_id, type_, message_id)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        msgs_m: list[TMsgModel] = res.scalars().all()
        msgs = [msg.to_traceable_message() for msg in msgs_m]

        return msgs

    async def delete_messages(
            self,
            chat_id: int,
            type_: Optional[str] = None,
            message_id: int = None
    ):
        query = await self.__get_delete(chat_id, type_, message_id)

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    @staticmethod
    async def __get_select(chat_id: int, type_: Optional[str], message_id: Optional[int]) -> Select:
        if type_ and message_id:
            query = select(TMsgModel).where(
                TMsgModel.chat_id == chat_id,
                TMsgModel.type == type_,
                TMsgModel.message_id == message_id
            )
        elif type_:
            query = select(TMsgModel).where(
                TMsgModel.chat_id == chat_id,
                TMsgModel.type == type_
            )
        elif message_id:
            query = select(TMsgModel).where(
                TMsgModel.chat_id == chat_id,
                TMsgModel.message_id == message_id
            )
        else:
            query = select(TMsgModel).where(
                TMsgModel.chat_id == chat_id
            )

        return query

    @staticmethod
    async def __get_delete(chat_id: int, type_: Optional[str], message_id: Optional[int]) -> Delete:
        if type_ and message_id:
            query = delete(TMsgModel).where(
                TMsgModel.chat_id == chat_id,
                TMsgModel.type == type_,
                TMsgModel.message_id == message_id
            )
        elif type_:
            query = delete(TMsgModel).where(
                TMsgModel.chat_id == chat_id,
                TMsgModel.type == type_
            )
        elif message_id:
            query = delete(TMsgModel).where(
                TMsgModel.chat_id == chat_id,
                TMsgModel.message_id == message_id
            )
        else:
            query = delete(TMsgModel).where(
                TMsgModel.chat_id == chat_id
            )

        return query
