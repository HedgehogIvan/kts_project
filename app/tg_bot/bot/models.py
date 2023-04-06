from dataclasses import dataclass

from sqlalchemy import Column, BigInteger, Text, Integer, ForeignKey

from ...store.database.sqlalchemy_base import db


@dataclass
class TraceableMessage:
    chat_id: int
    session_id: int
    type: str
    message_id: int


class TraceableMessageModel(db):
    __tablename__ = "traceable_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    session_id = Column(Integer, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False)
    type = Column(Text, nullable=False)
    message_id = Column(BigInteger, unique=True, nullable=False)

    def to_traceable_message(self):
        return TraceableMessage(
            chat_id=self.chat_id,
            session_id=self.session_id,
            type=self.type,
            message_id=self.message_id
        )
