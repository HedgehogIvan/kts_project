import datetime
from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

from ..user.models import User, UserModel
from ....store.database.sqlalchemy_base import db


@dataclass
class Session:
    id: int
    chat_id: str
    start_game: datetime
    end_game: datetime
    players: list[User]


class SessionModel(db):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Text, ForeignKey("chats.tg_id", ondelete="CASCADE"), nullable=False)
    start_game = Column(DateTime, nullable=False)
    end_game = Column(DateTime, nullable=True)
    players = relationship("UserModel")
