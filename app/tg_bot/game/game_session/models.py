from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, Integer, ForeignKey, Text, ARRAY, BigInteger
from sqlalchemy.orm import relationship

from ..player.models import Player
from ....store.database.sqlalchemy_base import db


@dataclass
class Session:
    id: int
    chat_id: int
    current_state: str
    question_id: Optional[int]
    players: list[Player]
    used_answers: list[str]


class SessionModel(db):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    current_state = Column(Text, nullable=False)
    question_id = Column(
        Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True
    )
    players = relationship("PlayerModel")
    used_answers = Column(ARRAY(Text), nullable=False)

    def to_session(self):
        return Session(
            id=self.id,
            chat_id=self.chat_id,
            current_state=self.current_state,
            question_id=self.question_id,
            players=[player.to_player() for player in self.players],
            used_answers=self.used_answers,
        )
