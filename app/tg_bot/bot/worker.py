import asyncio
import logging
from typing import List, Optional

from ..api import (
    TgClient,
    MessageUpdateObj,
    MessageToSend,
    CallbackQueryObj,
    AnswerForCallbackQuery,
    UpdateMessage,
)
from ..game.game_session.models import Session
from ..state.idle import Idle
from ..state.move import MoveState
from ..state.preparation import Preparation
from ..state.round import Round
from ...web.aiohttp_extansion import Application


class StateType:
    preparation = "preparation"
    round = "round"
    movestate = "movestate"


class UpdateAttrs:
    message = "message"
    callback_query = "callback_query"


class Worker:
    def __init__(
        self,
        app: Application,
        to_worker_queue: asyncio.Queue,
        to_sender_queue: asyncio.Queue,
        tg_client: TgClient,
        concurrent_workers: int,
    ):
        self.app = app
        self.tg_client = tg_client
        self.to_worker_queue = to_worker_queue
        self.to_sender_queue = to_sender_queue
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

        self.__logger = logging.getLogger(__name__)
        self.__setup_logger()

    async def handle_update(
        self, upd
    ) -> list[MessageToSend | AnswerForCallbackQuery]:
        messages_for_sender = []

        if hasattr(upd, UpdateAttrs.message):
            self.__logger.debug(f"Получен апдейт типа 'message'")
            messages_for_sender += await self.__handle_message(upd)

        elif hasattr(upd, UpdateAttrs.callback_query):
            self.__logger.debug(f"Получен апдейт типа 'callback'")
            messages_for_sender += await self.__handle_callback(upd)

        else:
            self.__logger.warning(f"Получен неизвестный апдейт, {dir(upd)}")
        return messages_for_sender

    async def _worker(self):
        while True:
            try:
                upd = await self.to_worker_queue.get()
                self.__logger.debug(f"Получен апдейт, {type(upd)}")

                messages_to_send: list[MessageToSend | AnswerForCallbackQuery] = await self.handle_update(upd)
                self.__logger.debug(f"Апдейт обработан")

                for message in messages_to_send:
                    self.to_sender_queue.put_nowait(message)
            except:
                if not asyncio.CancelledError:
                    self.__logger.error("Ошибка", exc_info=True)
            finally:
                self.to_worker_queue.task_done()

    async def start(self):
        self._tasks = [
            asyncio.create_task(self._worker())
            for _ in range(self.concurrent_workers)
        ]
        self.__logger.info("Обработчики запущены")

    async def stop(self):
        await self.to_worker_queue.join()
        for t in self._tasks:
            t.cancel()
        self.__logger.info("Обработчики остановлены")

    def __setup_logger(self):
        self.__logger.setLevel(10)
        handler = logging.FileHandler(f"etc/logs/{__name__}.log", mode="w")
        formatter_ = logging.Formatter(
            "%(name)s %(asctime)s %(levelname)s %(message)s"
        )

        handler.setFormatter(formatter_)

        self.__logger.addHandler(handler)

    async def __handle_message(
        self, message_upd: MessageUpdateObj
    ) -> list[MessageToSend | UpdateMessage]:
        messages_for_send = []
        chat = message_upd.message.chat

        if chat.type == "supergroup" or chat.type == "group":
            messages_for_send += await self.__get_state_reaction(message_upd)

        elif chat.type == "private":
            return_message = MessageToSend(
                chat.id,
                "Извините, но бот не работает с пользователем на прямую\n"
                "Для работы чат-бота советую использовать группы",
            )
            messages_for_send.append(return_message)

        return messages_for_send

    async def __handle_callback(
        self, callback_upd: CallbackQueryObj
    ) -> list[AnswerForCallbackQuery | UpdateMessage]:
        messages_for_send = []
        messages_for_send += await self.__get_state_reaction(callback_upd)
        return messages_for_send

    async def __get_state_reaction(
        self, update: MessageUpdateObj | CallbackQueryObj
    ) -> list[MessageToSend | AnswerForCallbackQuery | UpdateMessage]:
        messages_for_send = []

        if type(update) is MessageUpdateObj:
            chat = update.message.chat
        elif type(update) is CallbackQueryObj:
            chat = update.callback_query.message.chat
        else:
            self.__logger.exception("Неизвестное обновление")
            raise Exception

        session: Optional[Session] = await self.app.store.game_sessions.get_session(chat.id)

        # Это ответвление доступно как для MessageUpdateObj, так и для CallbackQueryObj
        if session:
            messages_for_send += await self.__call_state(chat.id, session, update)

        elif type(update) is MessageUpdateObj:
            state = Idle(chat.id, self.app.store, update)
            messages_for_send += await state.handler()

        return messages_for_send

    async def __call_state(
            self,
            chat_id: int,
            session: Session,
            update_obj: MessageUpdateObj | CallbackQueryObj
    ) -> list[MessageToSend | AnswerForCallbackQuery | UpdateMessage]:
        state_type = session.current_state
        state_response = []

        if state_type.lower() == StateType.preparation:
            state = Preparation(chat_id, session.id, self.app.store, update_obj)
            state_response += await state.handler()
        elif state_type.lower() == StateType.round:
            state = Round(chat_id, self.app.store, session.id, update_obj)
            state_response += await state.handler()
        elif state_type.lower() == StateType.movestate:
            state = MoveState(chat_id, session.id, self.app.store, update_obj)
            state_response += await state.handler()

        return state_response
