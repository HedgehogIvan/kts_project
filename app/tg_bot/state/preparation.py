from . import *
from .round import Round
from ..game.player.models import Player
from ..api import (
    MessageUpdateObj,
    CallbackQueryObj,
    InlineKeyboard,
    InlineButton,
    UpdateMessage,
)


class Preparation(State):
    max_players = 1

    def __init__(
        self,
        chat_id: int,
        session_id: int,
        store: Store,
        update: MessageUpdateObj | CallbackQueryObj | None = None,
    ):
        super().__init__(chat_id, store)
        self.session_id = session_id

        if type(update) is MessageUpdateObj:
            self.message: MessageUpdateObj = update
            self.callback = None
        if type(update) is CallbackQueryObj:
            self.callback: CallbackQueryObj = update
            self.message = None

    async def handler(self) -> list[MessageToSend | AnswerForCallbackQuery]:
        return_messages = []

        if self.message:
            return_messages += await self.__handle_message()

        if self.callback:
            return_messages += await self.__handle_callback()

        return return_messages

    async def start(
        self,
    ) -> list[MessageToSend | AnswerForCallbackQuery | UpdateMessage]:
        return_messages = []

        keyboard = await self.__get_keyboard()
        start_message = MessageToSend(
            self.chat_id,
            "Добро пожаловать в игру 100 к 1\n"
            "Кто хочет присоединиться к игре?",
            keyboard
        )
        return_messages.append(start_message)

        return return_messages

    async def stop(self):
        await self.store.game_sessions.drop_session(self.chat_id)

    @staticmethod
    async def __get_keyboard(
        add: bool = True, exit_: bool = False, start: bool = False
    ):
        keyboard = InlineKeyboard([])

        if add:
            keyboard.inline_keyboard.append(
                [InlineButton("Присоединиться", "add_player")]
            )

        if start:
            keyboard.inline_keyboard.append(
                [InlineButton("Начать игру", "start_session")]
            )

        if exit_:
            keyboard.inline_keyboard.append(
                [InlineButton("Выйти из игры", "delete_player")]
            )

        return keyboard

    async def __get_update_message(self) -> UpdateMessage:
        players = await self.store.players.get_players_in_session(self.session_id)
        players_number = len(players)

        username_str = ""
        for player in players:
            username_str += f"@{player.user_name}, "
        username_str = username_str[:-2]
        username_str += "\n"

        if players_number == self.max_players:
            new_keyboard = await self.__get_keyboard(False, True, True)
        elif players_number > 0:
            new_keyboard = await self.__get_keyboard(True, True)
        else:
            new_keyboard = await self.__get_keyboard()

        return UpdateMessage(
            self.chat_id,
            self.callback.callback_query.message.message_id,
            f"Место сбора игроков\n"
            f"Игроки {players_number}/{self.max_players}:\n"
            f"{username_str}",
            new_keyboard,
        )

    async def __handle_message(self) -> list[MessageToSend]:
        return_messages = []

        if self.message and self.message.message.text in ["/stop", "stop", "стоп"]:
            await self.stop()
            return_messages.append(
                MessageToSend(
                    self.chat_id,
                    "Игра окончена досрочно, приятного времени суток",
                )
            )

        return return_messages

    async def __handle_callback(self) -> list[AnswerForCallbackQuery]:
        return_messages = []

        if self.callback:
            if self.callback.callback_query.data == "add_player":
                return_messages += await self.__add_player()

            elif self.callback.callback_query.data == "delete_player":
                return_messages += await self.__delete_player()

            elif self.callback.callback_query.data == "start_session":
                return_messages += await self.__start_session()

            else:
                return_messages.append(
                    AnswerForCallbackQuery(
                        str(self.callback.callback_query.query_id), None, None
                    )
                )
                self._logger.warning("Получен неизвестный колбек")

        return return_messages

    async def __add_player(self) -> list[AnswerForCallbackQuery]:
        return_messages = []
        cur_player: Optional[Player] = await self.store.players.get_player(
            self.session_id, self.callback.callback_query.from_.id
        )

        if cur_player is None:
            await self.store.players.create_player(
                self.session_id,
                self.callback.callback_query.from_.id,
                self.callback.callback_query.from_.username
            )

            return_messages.append(
                AnswerForCallbackQuery(
                    str(self.callback.callback_query.query_id),
                    None,
                    None,
                )
            )

            return_messages.append(await self.__get_update_message())
        else:
            self._logger.error(
                "Нельзя добавлять игру одного и того же игрока"
            )
            return_messages.append(
                AnswerForCallbackQuery(
                    str(self.callback.callback_query.query_id),
                    None,
                    None,
                )
            )

        return return_messages

    async def __delete_player(self) -> list[AnswerForCallbackQuery]:
        return_messages = []
        cur_player: Optional[Player] = await self.store.players.get_player(
            self.session_id, self.callback.callback_query.from_.id
        )

        if cur_player is None:
            logging.error("Попытка удаления несуществующего игрока")
            return_messages.append(
                AnswerForCallbackQuery(
                    str(self.callback.callback_query.query_id),
                    None,
                    None,
                )
            )
        else:
            await self.store.players.delete_player(
                self.session_id, cur_player.user_id
            )
            return_messages.append(
                AnswerForCallbackQuery(
                    str(self.callback.callback_query.query_id),
                    None,
                    None,
                )
            )

            return_messages.append(await self.__get_update_message())

        return return_messages

    async def __start_session(self) -> list[AnswerForCallbackQuery]:
        return_messages = []

        return_messages.append(
            AnswerForCallbackQuery(
                str(self.callback.callback_query.query_id), None, None
            )
        )

        players_number = await self.store.players.count_players_in_session(self.session_id)

        if players_number == self.max_players:
            await self.store.game_sessions.change_state(
                self.chat_id, StateType.round
            )

            state = Round(self.chat_id, self.store, self.session_id)
            return_messages += await state.start()
        else:
            self._logger.warning("Что-то не так, похоже был получен сторонний колбек или сломана клавиатура")

        return return_messages
