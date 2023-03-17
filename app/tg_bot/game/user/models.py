from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from ..score.models import Score
from ....store.database.sqlalchemy_base import db


@dataclass
class User:
    tg_id: int
    chat: int
    current_session: Optional[int]
    scores: Optional[list[Score]]


class UserModel(db):
    __tablename__ = "users"

    tg_id = Column(BigInteger, primary_key=True, autoincrement=False)
    chat = Column(BigInteger, ForeignKey("chats.tg_id", ondelete="SET NULL"), nullable=True)
    current_session = Column(Integer, ForeignKey("game_sessions.id", ondelete="SET NULL"), nullable=True)
    scores = relationship("ScoreModel", cascade="all, delete")

    def to_user(self):
        return User(self.tg_id, self.chat, self.current_session, [score.to_score() for score in self.scores])
