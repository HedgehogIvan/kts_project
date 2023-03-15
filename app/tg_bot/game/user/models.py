from dataclasses import dataclass

from sqlalchemy import Column, Integer, ForeignKey, Text

from ....store.database.sqlalchemy_base import db


@dataclass
class User:
    tg_id: str
    current_chat: str
    current_session: int


class UserModel(db):
    __tablename__ = "users"

    tg_id = Column(Text, primary_key=True)
    current_chat = Column(Text, ForeignKey("chats.tg_id"), nullable=True)
    current_session = Column(Integer, ForeignKey("sessions.id"), nullable=True)
