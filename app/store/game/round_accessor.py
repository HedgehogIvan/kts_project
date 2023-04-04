from typing import Optional

from sqlalchemy import insert, select, ChunkedIteratorResult, update

from ...base.base_accessor import BaseAccessor
from ...tg_bot.game.round.models import RoundModel, Round


class RoundAccessor(BaseAccessor):
    async def create_round(self, player_id: int, session_id: int) -> Round:
        query = insert(RoundModel).values(
            player_id=player_id, session_id=session_id, round_number=1
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return Round(player_id, session_id)

    async def get_round(self, session_id: int) -> Optional[Round]:
        query = select(RoundModel).where(RoundModel.session_id == session_id)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        round_m: RoundModel = res.scalars().first()

        if round_m:
            return round_m.to_round()
        return None

    async def update_round_number(self, session_id: int, round_number: int):
        query = (
            update(RoundModel)
            .where(RoundModel.session_id == session_id)
            .values(round_number=round_number)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def change_active_player(self, session_id: int, player_id: int):
        query = (
            update(RoundModel)
            .where(RoundModel.session_id == session_id)
            .values(player_id=player_id)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
