from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, DateTime

from ....store.database.sqlalchemy_base import db


@dataclass
class GameTime:
    session_id: int
    start_game: Optional[datetime]
    end_game: Optional[datetime]


class GameTimeModel(db):
    __tablename__ = "game_times"

    id = Column(Integer, primary_key=True)
    session_id = Column(
        Integer,
        ForeignKey("game_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    start_game = Column(DateTime, nullable=True)
    end_game = Column(DateTime, nullable=True)

    def to_game_time(self):
        return GameTime(
            session_id=self.session_id,
            start_game=self.start_game,
            end_game=self.end_game,
        )
