from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship

from ..score.models import Score
from ....store.database.sqlalchemy_base import db


@dataclass
class Player:
    id: int
    user_id: int
    session_id: int
    alive: bool
    score: Optional[Score]


class PlayerModel(db):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    session_id = Column(
        Integer,
        ForeignKey("game_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    alive = Column(Boolean, unique=False, default=True)
    score = relationship("ScoreModel", uselist=False)

    def to_player(self):
        return Player(
            id=self.id,
            user_id=self.user_id,
            session_id=self.session_id,
            alive=self.alive,
            score=self.score,
        )
