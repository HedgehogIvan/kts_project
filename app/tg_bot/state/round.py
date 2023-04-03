import datetime
import logging

from . import *
from app.tg_bot.game.player.models import Player
from app.tg_bot.game.round.models import Round as GameRound
from app.tg_bot.api import (
    UpdateMessage,
    ReplyKeyboard,
    KeyboardButton,
    MessageUpdateObj, ReplyKeyboardRemove,
)
from ..game.game_session.models import Session
from ..game.game_time.models import GameTime


class Round(State):
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
        from .move import MoveState

        return_messages = []

        if self.message:
            if self.message.message.text == "/stop":
                return_messages.append(
                    MessageToSend(self.chat_id, "Всем спасибо все свободны")
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
                        if player.alive:
                            # Выдать сообщение об успехе
                            return_messages.append(
                                MessageToSend(
                                    self.chat_id,
                                    "Поздравляю первым успел этот участник",
                                    ReplyKeyboardRemove()
                                )
                            )
                            # Проверить есть ли раунд
                            round_ = await self.store.round.get_round(
                                self.session_id
                            )

                            # Создать раунд или сменить активного игрока
                            if round_:
                                await self.store.round.change_active_player(
                                    self.session_id, player.id
                                )
                            else:
                                await self.store.round.create_round(
                                    player.id, self.session_id
                                )

                            # Сменить состояние
                            await self.store.game_sessions.change_state(
                                self.chat_id, "movestate"
                            )
                            # TODO: Вызвать состояние
                            state = MoveState(
                                self.chat_id, self.session_id, self.store
                            )
                            return_messages += await state.start()
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

        if not round_:
            await self.store.game_time.create_game_time(
                self.session_id, datetime.datetime.now()
            )

            for player in players:
                await self.store.scores.create_score(player.id)

            try:
                await self.store.game_sessions.set_question(self.session_id)
            except Exception:
                logging.exception(Exception, exc_info=True)
        else:
            await self.store.round.update_round_number(
                self.session_id, round_.round_number + 1
            )

        # TODO: Запинить сообщение с условиями игры
        ...
        # TODO: Подключить хранение ссылки на пользователя, чтобы можно было показывать им клаву
        return_messages.append(
            MessageToSend(
                self.chat_id,
                "Кто первый нажмет, то и выиграет",
                await self.__get_reply_keyboard(),
            )
        )

        return return_messages

    # TODO Дописать конец истории
    # TODO Придумать, как не выкидывать сообщение о прерывании игры при финализации
    async def stop(self):
        await self.store.game_sessions.drop_session(self.chat_id)

    async def check_final(self) -> Optional[MessageToSend]:
        session: Session = await self.store.game_sessions.get_session(
            self.chat_id
        )

        if len(
            session.used_answers
        ) == 5 or await self.__is_all_players_kick_out(session.players):
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

            # Сбор данных об участниках
            players = session.players

            # Сортировка участников по очкам
            flag = True
            while flag:
                flag = False
                for i in range(len(players) - 1):
                    if players[i].score.value < players[i + 1].score.value:
                        temp = players[i]
                        players[i] = players[i + 1]
                        players[i + 1] = temp
                        flag = True

            # Вывод сообщения
            message_text = (
                f"Игра окончена всем спасибо\n"
                f"Игра началась в: {start_game_time}\n"
                f"Игра закончилась в: {end_game_time}\n"
                f"Кол-во раундов: {round_number}\n"
                f"\n"
                f"Итоги:\n"
                f"Игрок 1: {players[0].score.value}\n"
            )
            # TODO: Разпинить сообщение
            # ...
            await self.stop()
            return MessageToSend(self.chat_id, message_text)

    @staticmethod
    async def __get_reply_keyboard() -> ReplyKeyboard:
        keyboard = ReplyKeyboard([])

        keyboard.keyboard.append([KeyboardButton("Выбери меня")])
        keyboard.one_time_keyboard = True

        return keyboard

    @staticmethod
    async def __is_all_players_kick_out(players: list[Player]) -> bool:
        for player in players:
            if player.alive:
                return False

        return True
