from dataclasses import field, dataclass
from typing import Optional

from sqlalchemy import Column, BigInteger, Text

from ..store.database.sqlalchemy_base import db


@dataclass
class Admin:
    id: int
    login: str
    password: Optional[str] = None


class AdminModel(db):
    __tablename__ = "admins"

    id = Column(BigInteger, primary_key=True)
    login = Column(Text, nullable=False)
    password = Column(Text, nullable=True)

    def to_admin(self) -> Admin:
        return Admin(id=self.id, login=self.login, password=self.password)
