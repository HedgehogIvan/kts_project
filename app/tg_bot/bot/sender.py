import asyncio
import logging

from asyncio import Task, Queue
from queue import Queue
from typing import Optional

from ..api.client import TgClient


class Sender:
    def __init__(self, tg_client: TgClient, to_sender_queue: Queue):
        self.to_sender_queue: Queue = to_sender_queue
        self.tg_client: TgClient = tg_client
        self.send_task: Optional[Task] = None

        self.__logger: logging.Logger = logging.getLogger(__name__)
        self.setup_logger()

    async def send_echo_message(self, parameters: dict):
        if parameters["type"] == "message":
            await self.tg_client.send_message(
                parameters["chat_id"], parameters["text"]
            )
        else:
            self.__logger.warning(
                f"Получены неизвестные параметры, ключи {[key for key in parameters]}"
            )

    async def _sender(self):
        while True:
            try:
                params: dict = await self.to_sender_queue.get()
                self.__logger.debug("Параметры для сообщения получены")
                await self.send_echo_message(params)
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

    def setup_logger(self):
        self.__logger.setLevel(10)
        handler = logging.FileHandler(f"etc/logs/{__name__}.log", mode="w")
        formatter_ = logging.Formatter(
            "%(name)s %(asctime)s %(levelname)s %(message)s"
        )

        handler.setFormatter(formatter_)

        self.__logger.addHandler(handler)
