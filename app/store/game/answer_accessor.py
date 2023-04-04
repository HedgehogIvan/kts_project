from sqlalchemy import insert, select, ChunkedIteratorResult

from ...base.base_accessor import BaseAccessor
from ...tg_bot.question.models import Answer, AnswerModel


class AnswerAccessor(BaseAccessor):
    async def create_answer(
        self, text: str, question_id: int, reward: int
    ) -> Answer:
        query = insert(AnswerModel).values(
            text=text, question_id=question_id, reward=reward
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return Answer(text, reward)

    async def create_answers(
        self, question_id: int, answers: list[Answer]
    ) -> list[Answer]:
        query_list = []

        for answer in answers:
            query = insert(AnswerModel).values(
                text=answer.text, question_id=question_id, reward=answer.reward
            )
            query_list.append(query)

        async with self.app.database.session() as session:
            for answer in answers:
                query = insert(AnswerModel).values(
                    text=answer.text,
                    question_id=question_id,
                    reward=answer.reward,
                )

                await session.execute(query)
            await session.commit()
        return answers

    async def get_answers(self, question_id: int) -> list[Answer]:
        query = select(AnswerModel).where(
            AnswerModel.question_id == question_id
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        answers_m: list[AnswerModel] = res.scalars().all()
        answers = [answer_m.to_answer() for answer_m in answers_m]

        return answers
