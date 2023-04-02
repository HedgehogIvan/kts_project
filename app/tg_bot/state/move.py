import logging

from . import *
from .round import Round
from ..api import MessageUpdateObj


class MoveState(State):
    def __init__(
        self,
        chat_id: int,
        session_id: int,
        store: Store,
        message: Optional[MessageUpdateObj] = None,
    ):
        super().__init__(chat_id, store)

        self.session_id = session_id
        self.message = message

    async def handler(self) -> list[MessageToSend | AnswerForCallbackQuery]:
        return_messages = []

        if self.message:
            session = await self.store.game_sessions.get_session(self.chat_id)
            round_ = await self.store.round.get_round(self.session_id)
            cur_player = await self.store.players.get_player(
                self.session_id, self.message.message.from_.id
            )

            if self.message.message.text == "/stop":
                return_messages.append(
                    MessageToSend(self.chat_id, "Всем спасибо, все свободны")
                )
                await self.stop()

            elif cur_player and round_.player_id == cur_player.id:
                if (
                    self.message.message.text.lower()
                    not in session.used_answers
                ):
                    answers = await self.store.answers.get_answers(
                        session.question_id
                    )
                    text_answers = [answer.text for answer in answers]

                    if self.message.message.text.lower() not in text_answers:
                        await self.store.players.kick_out_player(
                            self.session_id, self.message.message.from_.id
                        )
                        message_text = "Неправильный ответ"
                    else:
                        reward = 0
                        for answer in answers:
                            if answer.text == self.message.message.text.lower():
                                reward = answer.reward
                                break

                        await self.store.scores.add_value(
                            round_.player_id, reward
                        )

                        used_answers = session.used_answers
                        used_answers.append(self.message.message.text.lower())
                        await self.store.game_sessions.update_used_answers(
                            self.chat_id, used_answers
                        )
                        message_text = f"Правильный ответ\nНаграда {reward}"
                else:
                    await self.store.players.kick_out_player(
                        self.session_id, self.message.message.from_.id
                    )
                    message_text = "Неправильный ответ"

                return_messages.append(
                    MessageToSend(self.chat_id, message_text)
                )
                try:
                    await self.store.game_sessions.change_state(
                        self.chat_id, "round"
                    )
                    state = Round(self.chat_id, self.store, self.session_id)
                    final_message = await state.check_final()
                    if final_message:
                        return_messages.append(final_message)
                    else:
                        return_messages += await state.start()
                except Exception:
                    logging.exception(Exception, exc_info=True)

        return return_messages

    async def start(
        self,
    ) -> list[MessageToSend | AnswerForCallbackQuery | UpdateMessage]:
        return [MessageToSend(self.chat_id, "Ну чтож игрок, введите ваш ответ")]

    async def stop(self):
        await self.store.game_sessions.drop_session(self.chat_id)
