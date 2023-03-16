import asyncio
import logging
from typing import List

from marshmallow_dataclass import dataclass

from ..api import TgClient
from ..api import UpdateObj, ChannelPostUpdateObj


class Worker:
    def __init__(self, queue: asyncio.Queue, tg_client: TgClient, concurrent_workers: int):
        self.tg_client = tg_client
        self.queue = queue
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

    async def handle_update(self, upd: dataclass):
        if hasattr(upd, "message"):
            await self.tg_client.send_message(upd.message.chat.id, upd.message.text)
        if hasattr(upd, "channel_post"):
            channel_upd: ChannelPostUpdateObj = upd
            await self.tg_client.send_message(channel_upd.channel_post.chat.id, channel_upd.channel_post.text)
        pass

    async def _worker(self):
        while True:
            try:
                upd = await self.queue.get()
                logging.info("Я взять апдейт из очереди")
                await self.handle_update(upd)
                logging.info("Я запросить сообщение")
            finally:
                self.queue.task_done()

    async def start(self):
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.concurrent_workers)]

    async def stop(self):
        await self.queue.join()
        for t in self._tasks:
            t.cancel()
