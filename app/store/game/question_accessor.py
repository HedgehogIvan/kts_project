from typing import Optional

from sqlalchemy import insert, CursorResult, select, ChunkedIteratorResult
from sqlalchemy.orm import selectinload

from ...base.base_accessor import BaseAccessor
from ...tg_bot.question.models import Answer, QuestionModel, Question


class QuestionAccessor(BaseAccessor):
    async def create_question(
        self, title: str, answers: list[Answer]
    ) -> Question:
        query = insert(QuestionModel).values(title=title)

        async with self.app.database.session() as session:
            res: CursorResult = await session.execute(query)
            question_id = res.inserted_primary_key[0]
            await session.commit()

        await self.app.store.answers.create_answers(question_id, answers)

        return Question(question_id, title, answers)

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        query = select(QuestionModel)\
                .where(QuestionModel.title == title)\
                .options(selectinload(QuestionModel.answers))

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        question_m: QuestionModel = res.scalars().first()

        if question_m:
            return question_m.to_question()
        return None

    async def get_question_by_id(self, question_id: int):
        query = select(QuestionModel)\
                .where(QuestionModel.id == question_id)\
                .options(selectinload(QuestionModel.answers))

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        question_m: QuestionModel = res.scalars().first()

        if question_m:
            return question_m.to_question()
        return None

    async def get_all_questions(self) -> list[Question]:
        query = select(QuestionModel).options(
            selectinload(QuestionModel.answers)
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        questions_m: list[QuestionModel] = res.scalars().all()
        questions = [question_m.to_question() for question_m in questions_m]

        return questions
