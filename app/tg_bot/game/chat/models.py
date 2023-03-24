from dataclasses import dataclass

from sqlalchemy import Column, BigInteger

from ....store.database.sqlalchemy_base import db


@dataclass
class Chat:
    tg_id: int


class ChatModel(db):
    __tablename__ = "chats"

    tg_id = Column(BigInteger, primary_key=True, autoincrement=False)
