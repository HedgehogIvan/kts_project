from typing import Optional

from sqlalchemy import insert, CursorResult, select, ChunkedIteratorResult, delete, func, update
from sqlalchemy.orm import selectinload

from ...base.base_accessor import BaseAccessor
from ...tg_bot.game.player.models import Player, PlayerModel


class PlayerAccessor(BaseAccessor):
    async def create_player(
        self, session_id: int, user_id: int, alive: bool = True
    ) -> Player:
        query = insert(PlayerModel).values(
            session_id=session_id, user_id=user_id, alive=alive
        )

        async with self.app.database.session() as session:
            res: CursorResult = await session.execute(query)
            player_id = res.inserted_primary_key[0]
            await session.commit()

        return Player(player_id, user_id, session_id, alive, None)

    async def get_player(
        self, session_id: int, user_id: int
    ) -> Optional[Player]:
        query = (
            select(PlayerModel)
            .where(
                (PlayerModel.session_id == session_id)
                & (PlayerModel.user_id == user_id)
            )
            .options(selectinload(PlayerModel.score))
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            player_m: PlayerModel = res.scalars().first()

        if player_m:
            player = player_m.to_player()
            return player
        return None

    async def delete_player(self, session_id: int, user_id: int):
        query = delete(PlayerModel).where(
            (PlayerModel.session_id == session_id)
            & (PlayerModel.user_id == user_id)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def count_players_in_session(self, session_id: int) -> int:
        query = (
            select(func.count())
            .select_from(PlayerModel)
            .where(PlayerModel.session_id == session_id)
        )

        async with self.app.database.session() as session:
            res = await session.execute(query)

        return res.scalar()

    async def get_players_in_session(self, session_id: int) -> list[Player]:
        query = (
            select(PlayerModel)
            .where(PlayerModel.session_id == session_id)
            .options(selectinload(PlayerModel.score))
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        players_m: list[PlayerModel] = res.scalars().all()
        players = [player_m.to_player() for player_m in players_m]

        return players

    async def kick_out_player(self, session_id: int, user_id: int):
        query = (
            update(PlayerModel)
            .where(
                (PlayerModel.session_id == session_id)
                & (PlayerModel.user_id == user_id)
            )
            .values(alive=False)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
