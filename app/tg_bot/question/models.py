from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from ...store.database.sqlalchemy_base import db


@dataclass
class Answer:
    text: str
    reward: int


class AnswerModel(db):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    question_id = Column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )
    reward = Column(Integer, nullable=False)

    def to_answer(self):
        return Answer(text=self.text, reward=self.reward)


@dataclass
class Question:
    id: int
    title: str
    answers: list[Answer]


class QuestionModel(db):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    title = Column(Text, unique=True, nullable=False)
    answers = relationship("AnswerModel")

    def to_question(self):
        return Question(
            id=self.id,
            title=self.title,
            answers=[answer.to_answer() for answer in self.answers],
        )
