import asyncio
from typing import List

from ..api import TgClient
from ..api import UpdateObj


class Worker:
    def __init__(self, queue: asyncio.Queue, tg_client: TgClient, concurrent_workers: int):
        self.tg_client = tg_client
        self.queue = queue
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

    async def handle_update(self, upd: UpdateObj):
        await self.tg_client.send_message(upd.message.chat.id, upd.message.text)

    async def _worker(self):
        while True:
            try:
                upd = await self.queue.get()
                await self.handle_update(upd)
            finally:
                self.queue.task_done()

    async def start(self):
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.concurrent_workers)]

    async def stop(self):
        await self.queue.join()
        for t in self._tasks:
            t.cancel()
