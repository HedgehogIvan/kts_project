from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey, BigInteger

from ....store.database.sqlalchemy_base import db


@dataclass
class Round:
    id: int
    prev_round: int
    next_round: int
    session: int
    active_player: int


class RoundModel(db):
    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True)
    prev_round = Column(Integer, ForeignKey("rounds.id", ondelete='SET NULL'), nullable=True)
    next_round = Column(Integer, ForeignKey("rounds.id", ondelete='SET NULL'), nullable=True)
    session = Column(Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    active_player = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
