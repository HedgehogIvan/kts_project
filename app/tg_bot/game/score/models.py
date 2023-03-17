from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey, BigInteger

from ....store.database.sqlalchemy_base import db


@dataclass
class Score:
    id: int
    user_id: int
    session_id: int
    points: int


class ScoreModel(db):
    __tablename__ = "score"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=True)
    points = Column(Integer, nullable=False)

    def to_score(self):
        return Score(self.id, self.user_id, self.session_id, self.points)
