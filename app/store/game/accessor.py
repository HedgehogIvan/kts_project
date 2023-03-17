from datetime import datetime
from typing import Optional

from sqlalchemy import insert, select, ChunkedIteratorResult, update
from sqlalchemy.orm import selectinload

from ...base.base_accessor import BaseAccessor
from ...tg_bot.game.chat.models import ChatModel, Chat
from ...tg_bot.game.game_session.models import Session as Game, SessionModel as GameModel
from ...tg_bot.game.score.models import ScoreModel, Score
from ...tg_bot.game.user.models import UserModel, User


class ChatAccessor(BaseAccessor):
    async def add_chat(self, tg_id: int) -> Chat:
        query = insert(ChatModel).values(tg_id=tg_id)

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return Chat(tg_id)

    async def get_all_chats(self) -> list[Chat]:
        query = select(ChatModel)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            chats_m: list[ChatModel] = res.scalars().all()

        chats = [Chat(chat_m.tg_id) for chat_m in chats_m]
        return chats

    async def get_all_chats_id(self) -> list[int]:
        query = select(ChatModel)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            chats_m: list[ChatModel] = res.scalars().all()

        chats_id = [chat_m.tg_id for chat_m in chats_m]
        return chats_id


class UserAccessor(BaseAccessor):
    async def add_user(self, tg_id: int, chat_id: int, current_session: Optional[int] = None) -> User:
        query = insert(UserModel).values(tg_id=tg_id, chat=chat_id, current_session=current_session)

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return User(tg_id, chat_id, current_session, [])

    async def get_chat_users(self, chat_tg_id: int) -> list[User]:
        query = select(UserModel).where(UserModel.chat == chat_tg_id).options(selectinload(UserModel.scores))

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            users: list[UserModel] = res.scalars().all()

        return_users = [user.to_user() for user in users]
        return return_users

    async def update_user_game_session(self, user_id: int, chat_id: int, session_id: int):
        query = update(UserModel)\
            .where(UserModel.tg_id == user_id and UserModel.chat == chat_id)\
            .values(current_session=session_id)

        async with self.app.database.session() as session:
            await session.execute(query)

            await session.commit()


class ScoreAccessor(BaseAccessor):
    async def create_score(self, user_id: int, session_id: int, points: int = 0) -> Score:
        query = insert(ScoreModel).values(user_id=user_id, session_id=session_id, points=points)

        async with self.app.database.session() as session:
            res = await session.execute(query)
            score_id = res.inserted_primary_key[0]

            await session.commit()

        return Score(score_id, user_id, session_id, points)

    async def update_points(self, session_id: int, user_id: int, points: int):
        query = update(ScoreModel)\
            .where(ScoreModel.session_id == session_id and ScoreModel.user_id == user_id)\
            .values(points=points)

        async with self.app.database.session() as session:
            await session.execute(query)

            await session.commit()

    async def get_user_scores(self, user_id: int) -> list[Score]:
        query = select(ScoreModel).where(ScoreModel.user_id == user_id)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            scores_m: list[ScoreModel] = res.scalars().all()

        scores = [score_m.to_score() for score_m in scores_m]
        return scores

    async def get_user_score_in_game(self, user_id: int, session_id: int) -> Optional[Score]:
        query = select(ScoreModel).where(ScoreModel.user_id == user_id and ScoreModel.session_id == session_id)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            score_m: ScoreModel = res.scalars().one_or_none()

        if score_m:
            return score_m.to_score()
        return score_m


class GameSessionAccessor(BaseAccessor):
    async def create_game(self, chat_id: int) -> Game:
        create_time = datetime.now()
        query = insert(GameModel).values(chat_id=chat_id, start_game=create_time)

        async with self.app.database.session() as session:
            res = await session.execute(query)
            await session.commit()
        game_id = res.inserted_primary_key[0]

        return Game(id=game_id, chat_id=chat_id, start_game=create_time, players=[])

    async def get_last_game(self, chat: int) -> Optional[Game]:
        query = select(GameModel)\
            .where(GameModel.chat_id == chat)\
            .order_by(GameModel.start_game.desc())\
            .options(selectinload(GameModel.players).selectinload(UserModel.scores))

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            game_m: GameModel = res.scalars().first()

        game = game_m.to_session()
        return game

    async def add_user_in_game(self, user_id: str, chat_id: str, session_id: int):
        await self.app.store.users.update_user_game_session(user_id, chat_id, session_id)
