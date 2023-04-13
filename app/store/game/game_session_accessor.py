import logging
import random
from typing import Optional

from sqlalchemy import insert, CursorResult, select, ChunkedIteratorResult, delete, update
from sqlalchemy.orm import selectinload

from ...base.base_accessor import BaseAccessor
from ...tg_bot.game.game_session.models import Session, SessionModel
from ...tg_bot.game.player.models import Player, PlayerModel
from ...tg_bot.question.models import Question


class GameSessionAccessor(BaseAccessor):
    async def create_session(
        self,
        chat_id: int,
        bot_status: Optional[str] = None,
        cur_state: str = "preparation",
        question_id: int = None,
        players: list[Player] = None,
    ) -> Session:
        query_c_s = insert(SessionModel).values(
            chat_id=chat_id,
            bot_status=bot_status,
            current_state=cur_state,
            question_id=question_id,
            used_answers=[],
        )
        async with self.app.database.session() as session:
            res: CursorResult = await session.execute(query_c_s)
            game_session_id = res.inserted_primary_key[0]

            if players:
                query_add_players: list[dict] = []
                if len(players) > 4:
                    players = players[:4]
                for player in players:
                    query_add_players.append(
                        {
                            "user_id": player.user_id,
                            "session_id": game_session_id,
                            "alive": player.alive,
                        }
                    )

                await session.execute(
                    insert(PlayerModel).values(query_add_players)
                )

            await session.commit()

        return Session(
            game_session_id, chat_id, bot_status, cur_state, question_id, players, []
        )

    async def get_session(self, chat_id) -> Optional[Session]:
        query = (
            select(SessionModel)
            .where(SessionModel.chat_id == chat_id)
            .options(
                selectinload(SessionModel.players).options(
                    selectinload(PlayerModel.score)
                )
            )
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            game_m: SessionModel = res.scalars().first()

        if game_m:
            game = game_m.to_session()
            return game
        return None

    async def drop_session(self, chat_id: int):
        query = delete(SessionModel).where(SessionModel.chat_id == chat_id)

        async with self.app.database.session() as session:
            await session.execute(query)

            await session.commit()

    async def change_state(self, chat_id: int, new_state: str):
        query = (
            update(SessionModel)
            .where(SessionModel.chat_id == chat_id)
            .values(current_state=new_state)
        )

        async with self.app.database.session() as session:
            try:
                await session.execute(query)
                await session.commit()
            except Exception:
                logging.warning("UPDATE не удалось произвести")

    async def set_question(self, session_id, title: Optional[str] = None) -> Question:
        if title:
            question = await self.app.store.questions.get_question_by_title(title)

            query = (
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(question_id=question.id)
            )
        else:
            questions = await self.app.store.questions.get_all_questions()

            index = random.randint(0, len(questions) - 1)
            question = questions[index]

            query = (
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(question_id=question.id)
            )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return question

    async def update_used_answers(
        self, chat_id: int, update_answers: list[str]
    ):
        query = (
            update(SessionModel)
            .where(SessionModel.chat_id == chat_id)
            .values(used_answers=update_answers)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def update_bot_status(self, chat_id: int, status: Optional[str]):
        # chat_id используется вместо session_id так как в одном чате может быть только одна сессия,
        # а значит при использовании этих полей результат будет один и тот же
        # также данная функция может использовать
        # до создания сессии (но после сообщения, которое инициирует её создание)
        # что означает, что id сессии в таблицы иногда не предоставляется возможным
        query = (
            update(SessionModel).where(SessionModel.chat_id == chat_id).values(bot_status=status)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
