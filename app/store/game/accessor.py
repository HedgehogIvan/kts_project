import logging
import random
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    insert,
    select,
    ChunkedIteratorResult,
    update,
    CursorResult,
    delete,
    func,
)
from sqlalchemy.orm import selectinload

from ...base.base_accessor import BaseAccessor
from ...tg_bot.game.game_session.models import (
    Session,
    SessionModel,
)
from ...tg_bot.game.game_time.models import GameTime, GameTimeModel
from ...tg_bot.game.player.models import Player, PlayerModel
from ...tg_bot.game.round.models import RoundModel, Round
from ...tg_bot.game.score.models import ScoreModel, Score
from ...tg_bot.question.models import (
    QuestionModel,
    Answer,
    AnswerModel,
    Question,
)


class PlayerAccessor(BaseAccessor):
    async def create_player(
        self, session_id: int, user_id: int, alive: bool = True
    ) -> Player:
        query = insert(PlayerModel).values(
            session_id=session_id, user_id=user_id, alive=alive
        )

        async with self.app.database.session() as session:
            res: CursorResult = await session.execute(query)
            player_id = res.inserted_primary_key[0]
            await session.commit()

        return Player(player_id, user_id, session_id, alive, None)

    async def get_player(
        self, session_id: int, user_id: int
    ) -> Optional[Player]:
        query = (
            select(PlayerModel)
            .where(
                (PlayerModel.session_id == session_id)
                & (PlayerModel.user_id == user_id)
            )
            .options(selectinload(PlayerModel.score))
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            player_m: PlayerModel = res.scalars().first()

        if player_m:
            player = player_m.to_player()
            return player
        return None

    async def delete_player(self, session_id: int, user_id: int):
        query = delete(PlayerModel).where(
            (PlayerModel.session_id == session_id)
            & (PlayerModel.user_id == user_id)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def count_players_in_session(self, session_id: int) -> int:
        query = (
            select(func.count())
            .select_from(PlayerModel)
            .where(PlayerModel.session_id == session_id)
        )

        async with self.app.database.session() as session:
            res = await session.execute(query)

        return res.scalar()

    async def get_players_in_session(self, session_id: int) -> list[Player]:
        query = (
            select(PlayerModel)
            .where(PlayerModel.session_id == session_id)
            .options(selectinload(PlayerModel.score))
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        players_m: list[PlayerModel] = res.scalars().all()
        players = [player_m.to_player() for player_m in players_m]

        return players

    async def kick_out_player(self, session_id: int, user_id: int):
        query = (
            update(PlayerModel)
            .where(
                (PlayerModel.session_id == session_id)
                & (PlayerModel.user_id == user_id)
            )
            .values(alive=False)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()


class ScoreAccessor(BaseAccessor):
    async def create_score(self, player_id: int, value: int = 0) -> Score:
        query = insert(ScoreModel).values(player_id=player_id, value=value)

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return Score(player_id, value)

    async def update_value(self, player_id: int, value: int):
        query = (
            update(ScoreModel)
            .where(ScoreModel.player_id == player_id)
            .values(value=value)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def add_value(self, player_id: int, value: int):
        score = await self.get_player_score(player_id)
        new_value = score.value + value

        query = (
            update(ScoreModel)
            .where(ScoreModel.player_id == player_id)
            .values(value=new_value)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def get_player_score(self, player_id: int) -> Optional[Score]:
        query = select(ScoreModel).where(ScoreModel.player_id == player_id)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        score_m: ScoreModel = res.scalars().first()

        if score_m:
            return score_m.to_score()
        return None


class GameSessionAccessor(BaseAccessor):
    async def create_session(
        self,
        chat_id: int,
        cur_state: str = "preparation",
        question_id: int = None,
        players: list[Player] = None,
    ) -> Session:
        query_c_s = insert(SessionModel).values(
            chat_id=chat_id,
            current_state=cur_state,
            question_id=question_id,
            used_answers=[],
        )
        async with self.app.database.session() as session:
            res: CursorResult = await session.execute(query_c_s)
            game_session_id = res.inserted_primary_key[0]

            if players:
                query_add_players: list[dict] = []
                if len(players) > 4:
                    players = players[:4]
                for player in players:
                    query_add_players.append(
                        {
                            "user_id": player.user_id,
                            "session_id": game_session_id,
                            "alive": player.alive,
                        }
                    )

                await session.execute(
                    insert(PlayerModel).values(query_add_players)
                )

            await session.commit()

        return Session(
            game_session_id, chat_id, cur_state, question_id, players, []
        )

    async def get_session(self, chat_id) -> Optional[Session]:
        query = (
            select(SessionModel)
            .where(SessionModel.chat_id == chat_id)
            .options(
                selectinload(SessionModel.players).options(
                    selectinload(PlayerModel.score)
                )
            )
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

            game_m: SessionModel = res.scalars().first()

        if game_m:
            game = game_m.to_session()
            return game
        return None

    async def drop_session(self, chat_id: int):
        query = delete(SessionModel).where(SessionModel.chat_id == chat_id)

        async with self.app.database.session() as session:
            await session.execute(query)

            await session.commit()

    async def change_state(self, chat_id: int, new_state: str):
        query = (
            update(SessionModel)
            .where(SessionModel.chat_id == chat_id)
            .values(current_state=new_state)
        )

        async with self.app.database.session() as session:
            try:
                await session.execute(query)
                await session.commit()
            except Exception:
                logging.warning("UPDATE не удалось произвести")

    async def set_question(self, session_id, title: Optional[str] = None):
        if title:
            question = await self.app.store.questions.get_question_by_title(title)

            query = (
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(question_id=question.id)
            )
        else:
            questions = await self.app.store.questions.get_all_questions()

            index = random.randint(0, len(questions) - 1)
            question = questions[index]

            query = (
                update(SessionModel)
                .where(SessionModel.id == session_id)
                .values(question_id=question.id)
            )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def update_used_answers(
        self, chat_id: int, update_answers: list[str]
    ):
        query = (
            update(SessionModel)
            .where(SessionModel.chat_id == chat_id)
            .values(used_answers=update_answers)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()


class QuestionAccessor(BaseAccessor):
    async def create_question(
        self, title: str, answers: list[Answer]
    ) -> Question:
        query = insert(QuestionModel).values(title=title, answers=answers)

        async with self.app.database.session() as session:
            res: CursorResult = await session.execute(query)
            question_id = res.inserted_primary_key[0]
            await session.commit()

        self.app.store.answers.create_answers(question_id, answers)

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


class GameTimeAccessor(BaseAccessor):
    async def create_game_time(
        self,
        session_id: int,
        start_game: Optional[datetime] = None,
        end_game: Optional[datetime] = None,
    ) -> GameTime:
        query = insert(GameTimeModel).values(
            session_id=session_id, start_game=start_game, end_game=end_game
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return GameTime(session_id, start_game, end_game)

    async def get_game_time(self, session_id: int) -> Optional[GameTime]:
        query = select(GameTimeModel).where(
            GameTimeModel.session_id == session_id
        )

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        game_time_m: GameTimeModel = res.scalars().first()

        if game_time_m:
            game_time = game_time_m.to_game_time()
            return game_time

        return None

    async def set_end_game(self, session_id: int, end_time: datetime):
        query = (
            update(GameTimeModel)
            .where(GameTimeModel.session_id == session_id)
            .values(end_game=end_time)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()


class RoundAccessor(BaseAccessor):
    async def create_round(self, player_id: int, session_id: int) -> Round:
        query = insert(RoundModel).values(
            player_id=player_id, session_id=session_id, round_number=1
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

        return Round(player_id, session_id)

    async def get_round(self, session_id: int) -> Optional[Round]:
        query = select(RoundModel).where(RoundModel.session_id == session_id)

        async with self.app.database.session() as session:
            res: ChunkedIteratorResult = await session.execute(query)

        round_m: RoundModel = res.scalars().first()

        if round_m:
            return round_m.to_round()
        return None

    async def update_round_number(self, session_id: int, round_number: int):
        query = (
            update(RoundModel)
            .where(RoundModel.session_id == session_id)
            .values(round_number=round_number)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()

    async def change_active_player(self, session_id: int, player_id: int):
        query = (
            update(RoundModel)
            .where(RoundModel.session_id == session_id)
            .values(player_id=player_id)
        )

        async with self.app.database.session() as session:
            await session.execute(query)
            await session.commit()
