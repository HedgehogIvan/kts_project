import datetime

from . import *
from ..api import (
    UpdateMessage,
    ReplyKeyboard,
    KeyboardButton,
    MessageUpdateObj,
    ReplyKeyboardRemove,
    TraceableMessage as TMsgForSender,
    UnpinChatMessage
)
from ..bot.models import TraceableMessage
from ..game.game_session.models import Session
from ..game.game_time.models import GameTime
from ..game.player.models import Player
from ..game.round.models import Round as GameRound
from ..question.models import Question


class Round(State):
    max_players = 1

    def __init__(
        self,
        chat_id: int,
        store: Store,
        session_id: int,
        update: Optional[MessageUpdateObj] = None,
    ):
        super().__init__(chat_id, store)

        self.session_id = session_id
        self.message = update

    async def handler(self) -> list[MessageToSend | AnswerForCallbackQuery]:
        return_messages = []

        if self.message:
            if self.message.message.text == "/stop":
                return_messages.append(
                    MessageToSend(self.chat_id, "Игра завершена досрочно. Всем спасибо все свободны")
                )
                await self.stop()
            else:
                players: list[
                    Player
                ] = await self.store.players.get_players_in_session(
                    self.session_id
                )

                for player in players:
                    if self.message.message.from_.id == player.user_id:
                        if player.alive and self.message.message.text.lower() == "ответить":
                            return_messages += await self.__start_move(player)
                        else:
                            break

        return return_messages

    async def start(
        self,
    ) -> list[MessageToSend | AnswerForCallbackQuery | UpdateMessage]:
        return_messages = []

        round_: Optional[GameRound] = await self.store.round.get_round(
            self.session_id
        )
        players: list[Player] = await self.store.players.get_players_in_session(
            self.session_id
        )
        session: Session = await self.store.game_sessions.get_session(self.chat_id)
        question: Question = await self.store.game_sessions.set_question(self.session_id)

        if not round_:
            return_messages += await self.__create_round(session, question, players)
        else:
            await self.store.round.update_round_number(
                self.session_id, round_.round_number + 1
            )

            if len(session.used_answers) != 0 and session.bot_status == "administrator":
                return_messages += await self.__update_pin_msg(session, question)

        return_messages += await self.__invite_for_answer(players)

        return return_messages

    async def stop(self):
        await self.store.game_sessions.drop_session(self.chat_id)

    async def check_final(self) -> list[MessageToSend | UnpinChatMessage]:
        return_messages = []

        session: Session = await self.store.game_sessions.get_session(
            self.chat_id
        )

        if len(session.used_answers) == 5 \
           or await self.__is_all_players_kick_out(session.players):

            # Остановка времени
            end_game_time = datetime.datetime.now()
            await self.store.game_time.set_end_game(
                self.session_id, end_game_time
            )

            # Сбор данных об игре
            game_time: GameTime = await self.store.game_time.get_game_time(
                self.session_id
            )
            start_game_time = game_time.start_game

            round_: GameRound = await self.store.round.get_round(
                self.session_id
            )
            round_number = round_.round_number

            question: Question = await self.store.questions.get_question_by_id(session.question_id)

            # Сбор данных об участниках
            players = session.players

            # Сортировка участников по очкам
            await self.__sort_players_by_score(players)

            # Сбор очков игроков
            players_result = ""
            for player in players:
                players_result += f"{player.user_name}: {player.score.value}\n"
            players_result = players_result[:-1]

            winner: Optional[str] = None
            if len(players):
                winner = players[0].user_name

            # Вывод сообщения
            message_text = (
                f"Игра окончена всем спасибо\n"
                f"Вопрос: {question.title}?\n"
                f"Кол-во раундов: {round_number}\n"
                f"Игра началась в: {start_game_time}\n"
                f"Игра закончилась в: {end_game_time}\n"
                f"\n"
                f"Поздравляем победителя: @{winner}\n"
                f"\n"
                f"Итоги:\n"
                f"{players_result}"
            )

            return_messages.append(MessageToSend(self.chat_id, message_text))

            if session.bot_status == "administrator":
                unpin_msgs: list[TraceableMessage] = await self.store.t_msg.get_messages(self.chat_id, "pin")
                for msg in unpin_msgs:
                    return_messages.append(UnpinChatMessage(
                        msg.chat_id,
                        msg.message_id
                    ))
                    await self.store.t_msg.delete_messages(self.chat_id, msg.type, msg.message_id)

            await self.stop()

        return return_messages

    @staticmethod
    async def __get_reply_keyboard() -> ReplyKeyboard:
        keyboard = ReplyKeyboard([])

        keyboard.keyboard.append([KeyboardButton("Ответить")])
        keyboard.one_time_keyboard = False
        keyboard.selective = True

        return keyboard

    @staticmethod
    async def __is_all_players_kick_out(players: list[Player]) -> bool:
        for player in players:
            if player.alive:
                return False

        return True

    @staticmethod
    async def __sort_players_by_score(players: list[Player]):
        flag = True
        while flag:
            flag = False
            for i in range(len(players) - 1):
                if players[i].score.value < players[i + 1].score.value:
                    temp = players[i]
                    players[i] = players[i + 1]
                    players[i + 1] = temp
                    flag = True

    async def __start_move(self, player: Player) -> list[MessageToSend]:
        from .move import MoveState

        return_messages = []

        session = await self.store.game_sessions.get_session(self.chat_id)
        question = await self.store.questions.get_question_by_id(session.question_id)
        round_ = await self.store.round.get_round(self.session_id)

        # Выдать сообщение об успехе
        return_messages.append(
            MessageToSend(
                self.chat_id,
                f"Поздравляю первым успел {player.user_name}",
                ReplyKeyboardRemove()
            )
        )

        # Если бот не админ, повторить вопрос
        if session.bot_status != "administrator":
            answers_str = ""

            for answer in session.used_answers:
                answers_str += f"{answer}\n"

            answers_str = answers_str[:-1]

            if len(answers_str):
                return_messages.append(MessageToSend(
                    self.chat_id,
                    f"Внимание, вопрос:\n{question.title}?\n"
                    f"Угаданные ответы:\n"
                    f"{answers_str}"
                ))
            else:
                return_messages.append(MessageToSend(
                    self.chat_id,
                    f"Внимание, вопрос:\n{question.title}?\n"
                ))

        # Проверить есть ли раунд
        # Создать раунд или сменить активного игрока
        if round_:
            await self.store.round.change_active_player(
                self.session_id, player.id
            )
        else:
            await self.store.round.create_round(
                player.id, self.session_id
            )

        await self.store.game_sessions.change_state(
            self.chat_id, StateType.movestate
        )
        state = MoveState(
            self.chat_id, self.session_id, self.store
        )
        return_messages += await state.start()

        return return_messages

    async def __create_round(self, session: Session, question: Question, players: list[Player]) -> list[MessageToSend | TMsgForSender]:
        return_messages = []

        await self.__prepare_round_data(players)

        return_messages.append(MessageToSend(
            self.chat_id,
            "Все в сборе, начинаем нашу игру"
        ))

        if session.bot_status == "administrator":
            return_messages.append(TMsgForSender(
                self.chat_id,
                self.session_id,
                "pin",
                MessageToSend(
                    self.chat_id,
                    f"Внимание, вопрос:\n{question.title}?"
                )
            ))
        else:
            return_messages.append(MessageToSend(
                self.chat_id,
                f"Внимание, вопрос:\n{question.title}?"
            ))

        return return_messages

    async def __prepare_round_data(self, players: list[Player]):
        """
        Является сугубо вспомогательной функцией\n
        :param players: Список игроков
        :return: None
        """
        await self.store.game_time.create_game_time(
            self.session_id, datetime.datetime.now()
        )

        for player in players:
            await self.store.scores.create_score(player.id)

    async def __invite_for_answer(self, players: list[Player]) -> list[MessageToSend]:
        return_messages = []

        user_labels = ""

        for player in players:
            user_labels += f"@{player.user_name} "
        user_labels += "\n\n"

        return_messages.append(
            MessageToSend(
                self.chat_id,
                f"{user_labels}Кто хочет ответить на вопрос?\n",
                await self.__get_reply_keyboard(),
            )
        )

        return return_messages

    async def __update_pin_msg(self, session: Session, question: Question) -> list[UpdateMessage]:
        return_messages = []

        pin_msgs: list[TraceableMessage] = await self.store.t_msg.get_messages(self.chat_id, "pin")

        answers_str = ""

        for answer in session.used_answers:
            answers_str += f"{answer}\n"

        answers_str = answers_str[:-1]

        for pin_msg in pin_msgs:
            return_messages.append(UpdateMessage(
                self.chat_id,
                pin_msg.message_id,
                f"Внимание, вопрос:\n{question.title}?\n"
                f"Угаданные ответы:\n"
                f"{answers_str}"
            ))
            break

        return return_messages
