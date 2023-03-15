from dataclasses import dataclass

from sqlalchemy import Column, Text

from ....store.database.sqlalchemy_base import db


@dataclass
class Chat:
    tg_id: str


class ChatModel(db):
    __tablename__ = "chats"

    tg_id = Column(Text, primary_key=True)
