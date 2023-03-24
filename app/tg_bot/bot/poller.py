import asyncio
import logging
from asyncio import Task
from typing import Optional

from ..api import TgClient


class Poller:
    def __init__(self, queue: asyncio.Queue, tg_client: TgClient):
        self.tg_client = tg_client
        self.queue = queue
        self._task: Optional[Task] = None

        self.__logger: logging.Logger = logging.getLogger(__name__)
        self.setup_logger()

    async def _worker(self):
        offset = 0
        while True:
            res = await self.tg_client.get_updates_in_objects(
                offset=offset, timeout=60
            )
            for u in res["result"]:
                offset = u.update_id + 1
                print(u)
                self.queue.put_nowait(u)
            self.__logger.debug("Аптейды отправлены в очередь")

    async def start(self):
        self._task = asyncio.create_task(self._worker())
        self.__logger.info("Поллер запущен")

    async def stop(self):
        self._task.cancel()
        self.__logger.info("Поллер остановлен")

    def setup_logger(self):
        self.__logger.setLevel(10)
        handler = logging.FileHandler(f"etc/logs/{__name__}.log", mode="w")
        formatter_ = logging.Formatter(
            "%(name)s %(asctime)s %(levelname)s %(message)s"
        )

        handler.setFormatter(formatter_)

        self.__logger.addHandler(handler)
