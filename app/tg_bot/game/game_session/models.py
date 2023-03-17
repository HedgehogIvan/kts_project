from datetime import datetime
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, BigInteger
from sqlalchemy.orm import relationship

from ..user.models import User, UserModel
from ....store.database.sqlalchemy_base import db


@dataclass
class Session:
    id: int
    chat_id: int
    start_game: datetime
    players: [list[User]]
    end_game: Optional[datetime] = None


class SessionModel(db):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey("chats.tg_id", ondelete="CASCADE"), nullable=False)
    start_game = Column(DateTime, nullable=False)
    end_game = Column(DateTime, nullable=True)
    players = relationship("UserModel")

    def to_session(self):
        return Session(
            self.id,
            self.chat_id,
            self.start_game,
            [player_m.to_user() for player_m in self.players],
            self.end_game
        )
