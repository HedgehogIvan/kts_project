import asyncio
import logging

from asyncio import Task, Queue
from dataclasses import asdict
from queue import Queue
from typing import Optional

from ..api import MessageToSend, AnswerForCallbackQuery, UpdateMessage, TraceableMessage, UnpinChatMessage, \
    GetChatMember, ChatMemberResponse
from ..api.client import TgClient
from ...store import Store


class Sender:
    def __init__(self, store: Store, tg_client: TgClient, to_sender_queue: Queue):
        self.to_sender_queue: Queue = to_sender_queue
        self.store: Store = store
        self.tg_client: TgClient = tg_client
        self.send_task: Optional[Task] = None

        self.__logger: logging.Logger = logging.getLogger(__name__)
        self.__setup_logger()

    async def _sender(self):
        while True:
            try:
                object_to_send = await self.to_sender_queue.get()

                if type(object_to_send) is UnpinChatMessage:
                    unpin_msg: UnpinChatMessage = object_to_send
                    self.__logger.debug("Параметры для открепления сообщения получены")
                    await self.unpin_message(unpin_msg)
                    self.__logger.debug("Сообщение отправлено")

                if type(object_to_send) is TraceableMessage:
                    t_msg: TraceableMessage = object_to_send
                    self.__logger.debug("Параметры для отслеживаемого сообщения получены")
                    await self.send_traceable_message(t_msg)
                    self.__logger.debug("Сообщение отправлено")

                if type(object_to_send) is GetChatMember:
                    request: GetChatMember = object_to_send
                    self.__logger.debug("Параметры для получения статуса пользователя получены")
                    await self.get_chat_member(request)
                    self.__logger.debug("Сообщение отправлено")

                if type(object_to_send) is MessageToSend:
                    message: MessageToSend = object_to_send
                    self.__logger.debug("Параметры для сообщения получены")
                    await self.send_message(message)
                    self.__logger.debug("Сообщение отправлено")

                if type(object_to_send) is AnswerForCallbackQuery:
                    answer: AnswerForCallbackQuery = object_to_send
                    self.__logger.debug("Параметры для ответа получены")
                    await self.send_answer(answer)
                    self.__logger.debug("Сообщение отправлено")

                if type(object_to_send) is UpdateMessage:
                    update: UpdateMessage = object_to_send
                    self.__logger.debug("Параметры для обновления получены")
                    await self.update_message(update)
                    self.__logger.debug("Сообщение отправлено")
            finally:
                self.to_sender_queue.task_done()

    async def start(self):
        self.send_task = asyncio.create_task(self._sender())
        self.__logger.info("Доставщик сообщений запущен")

    async def stop(self):
        await self.to_sender_queue.join()
        self.send_task.cancel()
        self.__logger.info("Доставщик сообщений остановлен")

    def __setup_logger(self):
        self.__logger.setLevel(10)
        handler = logging.FileHandler(f"etc/logs/{__name__}.log", mode="w")
        formatter_ = logging.Formatter(
            "%(name)s %(asctime)s %(levelname)s %(message)s"
        )

        handler.setFormatter(formatter_)

        self.__logger.addHandler(handler)

    async def send_message(self, message: MessageToSend):
        if message.reply_markup:
            dict_reply_markup = asdict(message.reply_markup)

            await self.tg_client.send_message(
                message.chat_id, message.text, dict_reply_markup
            )
        else:
            await self.tg_client.send_message(message.chat_id, message.text)

    async def send_answer(self, answer: AnswerForCallbackQuery):
        await self.tg_client.send_callback_answer(
            callback_query_id=answer.callback_query_id,
            text=answer.text,
            show_alert=answer.show_alert,
        )

    async def send_traceable_message(self, traceable_message: TraceableMessage):
        message = traceable_message.message

        res = await self.tg_client.send_message(
            message.chat_id, message.text
        )

        await self.tg_client.pin_message(traceable_message.chat_id, res.result.message_id, True)

        await self.store.t_msg.create_message(
            message.chat_id,
            traceable_message.session_id,
            traceable_message.type,
            res.result.message_id
        )

    async def unpin_message(self, message_data: UnpinChatMessage):
        await self.tg_client.unpin_message(
            message_data.chat_id,
            message_data.message_id
        )

    async def update_message(self, message: UpdateMessage):
        if message.reply_markup:
            dict_reply_markup = asdict(message.reply_markup)
            await self.tg_client.update_message(
                message.chat_id,
                message.message_id,
                message.text,
                dict_reply_markup,
            )
        else:
            await self.tg_client.update_message(
                message.chat_id, message.message_id, message.text
            )

    async def get_chat_member(self, request: GetChatMember):
        res: ChatMemberResponse = await self.tg_client.get_chat_member(request.chat_id, request.user_id)

        await self.store.game_sessions.update_bot_status(request.chat_id, res.result.status)
