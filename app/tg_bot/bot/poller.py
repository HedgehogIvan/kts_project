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

    async def _worker(self):
        offset = 0
        while True:
            res = await self.tg_client.get_updates_in_objects(offset=offset, timeout=60)
            for u in res["result"]:
                offset = u.update_id + 1
                print(u)
                self.queue.put_nowait(u)
                logging.info("Я положить аптейды в очередь")

    async def start(self):
        self._task = asyncio.create_task(self._worker())

    async def stop(self):
        self._task.cancel()
