import asyncio
import logging
from typing import Optional
from aiohttp import ClientSession

from ...base.base_accessor import BaseAccessor
from ...tg_bot.api import TgClient
from ...tg_bot.bot import Poller, Worker, Sender

from ...web.aiohttp_extansion import Application


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.token = app.config.token
        self.to_worker_queue = asyncio.Queue()
        self.to_sender_queue = asyncio.Queue()
        self.poller: Optional[Poller] = None
        self.worker: Optional[Worker] = None
        self.sender: Optional[Sender] = None
        self.api_client: Optional[TgClient] = None
        self.session: Optional[ClientSession] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession()
        self.api_client = TgClient(self.token, self.session)
        self.poller = Poller(self.to_worker_queue, self.api_client)
        self.worker = Worker(
            self.app,
            self.to_worker_queue,
            self.to_sender_queue,
            self.api_client,
            app.config.workers_count,
        )
        self.sender = Sender(self.api_client, self.to_sender_queue)
        await self._start()

        logging.info("Бот запущен")

    async def disconnect(self, app: "Application"):

        """К сессии обращаются Worker и Poller,
        Поэтому стоит остановить их раньше"""
        await self._stop()

        # Сессия закрывается не сразу для этого нужно немного подождать
        await self.session.close()
        await asyncio.sleep(0.250)

        logging.info("Бот остановлен")

    async def _start(self):
        await self.poller.start()
        await self.worker.start()
        await self.sender.start()

    async def _stop(self):
        await self.poller.stop()
        await self.worker.stop()
        await self.sender.stop()
