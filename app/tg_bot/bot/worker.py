import asyncio
import logging
from typing import List

from marshmallow_dataclass import dataclass

from ..api import TgClient, MessageUpdateObj
from ...web.aiohttp_extansion import Application


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
        self.setup_logger()

    async def handle_update(self, upd: dataclass):
        if hasattr(upd, "message"):
            self.__logger.debug(f"Получен апдейт типа 'message'")
            param = await self.get_parameters(upd)
            self.to_sender_queue.put_nowait(param)
        else:
            self.__logger.warning(f"Получен неизвестный апдейт, {dir(upd)}")
        pass

    async def _worker(self):
        while True:
            try:
                upd = await self.to_worker_queue.get()
                self.__logger.debug(f"Получен апдейт, {type(upd)}")
                await self.handle_update(upd)
                self.__logger.debug(f"Апдейт отправлен на обработку")
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

    async def get_parameters(self, update: MessageUpdateObj) -> dict:
        parameters = {
            "type": "message",
            "chat_id": update.message.chat.id,
            "text": update.message.text,
        }
        return parameters

    def setup_logger(self):
        self.__logger.setLevel(10)
        handler = logging.FileHandler(f"etc/logs/{__name__}.log", mode="w")
        formatter_ = logging.Formatter(
            "%(name)s %(asctime)s %(levelname)s %(message)s"
        )

        handler.setFormatter(formatter_)

        self.__logger.addHandler(handler)
