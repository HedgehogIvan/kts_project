from . import *
from .preparation import Preparation
from app.tg_bot.game.game_session.models import Session
from app.tg_bot.api import MessageUpdateObj, InlineKeyboard, InlineButton, GetChatMember


class Idle(State):
    def __init__(self, chat_id: int, store: Store, message: MessageUpdateObj):
        super().__init__(chat_id, store)

        self.message_upd: MessageUpdateObj = message

    async def handler(self):
        if self.message_upd.message.text in ["start", "/start", "начать"]:
            return await self.__prepare_for_next_state("preparation")

    async def __prepare_for_next_state(
        self, next_state: str
    ) -> list[MessageToSend | GetChatMember]:
        return_messages = []
        if next_state == "preparation":
            game_session: Session = (
                await self.store.game_sessions.create_session(self.chat_id)
            )
            return_messages.append(GetChatMember(self.chat_id))

            state = Preparation(self.chat_id, game_session.id, self.store)
            return_messages += await state.start()

        return return_messages

    @staticmethod
    def __create_preparation_keyboard() -> InlineKeyboard:
        keyboard = InlineKeyboard(
            [
                [
                    InlineButton(
                        text="Присоединиться", callback_data="add_player"
                    ),
                ]
            ]
        )
        return keyboard
