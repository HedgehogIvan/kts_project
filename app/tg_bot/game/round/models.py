from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Boolean

from ....store.database.sqlalchemy_base import db


@dataclass
class Round:
    player_id: int
    session_id: int
    round_number: int = 1


class RoundModel(db):
    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True)
    player_id = Column(
        BigInteger, ForeignKey("players.id", ondelete="SET NULL")
    )
    session_id = Column(
        Integer,
        ForeignKey("game_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    round_number = Column(Integer, nullable=False, default=0)

    def to_round(self):
        return Round(
            player_id=self.player_id,
            session_id=self.session_id,
            round_number=self.round_number,
        )
