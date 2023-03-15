from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey, Text

from ....store.database.sqlalchemy_base import db


@dataclass
class Score:
    id: int
    user_id: str
    session_id: int
    points: int


class ScoreModel(db):
    __tablename__ = "score"

    id = Column(Integer, primary_key=True)
    user_id = Column(Text, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True)
    points = Column(Integer, nullable=False)
