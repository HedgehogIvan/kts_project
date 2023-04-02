from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey

from ....store.database.sqlalchemy_base import db


@dataclass
class Score:
    player_id: int
    value: int


class ScoreModel(db):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True)
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    value = Column(Integer, nullable=False)

    def to_score(self):
        return Score(self.player_id, self.value)
