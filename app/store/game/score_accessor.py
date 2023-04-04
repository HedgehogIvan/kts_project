from typing import Optional

from sqlalchemy import insert, update, select, ChunkedIteratorResult

from ...base.base_accessor import BaseAccessor
from ...tg_bot.game.score.models import ScoreModel, Score


class ScoreAccessor(BaseAccessor):
    async def create_score(self, player_id: int, value: int = 0) -> Score:
        query = insert(ScoreModel).values(player_id=player_id, value=value)

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return Score(player_id, value)

    async def update_value(self, player_id: int, value: int):
        query = (
            update(ScoreModel)
            .where(ScoreModel.player_id == player_id)
            .values(value=value)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def add_value(self, player_id: int, value: int):
        score = await self.get_player_score(player_id)
        new_value = score.value + value

        query = (
            update(ScoreModel)
            .where(ScoreModel.player_id == player_id)
            .values(value=new_value)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def get_player_score(self, player_id: int) -> Optional[Score]:
        query = select(ScoreModel).where(ScoreModel.player_id == player_id)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        score_m: ScoreModel = res.scalars().first()

        if score_m:
            return score_m.to_score()
        return None
