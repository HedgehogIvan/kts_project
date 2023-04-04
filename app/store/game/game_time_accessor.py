from datetime import datetime
from typing import Optional

from sqlalchemy import insert, select, ChunkedIteratorResult, update

from ...base.base_accessor import BaseAccessor
from ...tg_bot.game.game_time.models import GameTime, GameTimeModel


class GameTimeAccessor(BaseAccessor):
    async def create_game_time(
        self,
        session_id: int,
        start_game: Optional[datetime] = None,
        end_game: Optional[datetime] = None,
    ) -> GameTime:
        query = insert(GameTimeModel).values(
            session_id=session_id, start_game=start_game, end_game=end_game
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return GameTime(session_id, start_game, end_game)

    async def get_game_time(self, session_id: int) -> Optional[GameTime]:
        query = select(GameTimeModel).where(
            GameTimeModel.session_id == session_id
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        game_time_m: GameTimeModel = res.scalars().first()

        if game_time_m:
            game_time = game_time_m.to_game_time()
            return game_time

        return None

    async def set_end_game(self, session_id: int, end_time: datetime):
        query = (
            update(GameTimeModel)
            .where(GameTimeModel.session_id == session_id)
            .values(end_game=end_time)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
