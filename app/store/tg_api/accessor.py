import asyncio
import typing
from typing import Optional
from aiohttp import ClientSession

from ...base.base_accessor import BaseAccessor
from ...tg_bot.api import TgClient
from ...tg_bot.bot import Poller, Worker

from ...web.aiohttp_extansion import Application


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.token = app.config.token
        self.queue = asyncio.Queue()
        self.poller: Optional[Poller] = None
        self.worker: Optional[Worker] = None
        self.api_client: Optional[TgClient] = None
        self.session: Optional[ClientSession] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession()
        self.api_client = TgClient(self.token, self.session)
        self.poller = Poller(self.queue, self.api_client)
        self.worker = Worker(self.app, self.queue, self.api_client, app.config.workers_count)

        await self._start()

    async def disconnect(self, app: "Application"):

        """К сессии обращаются Worker и Poller,
        Поэтому стоит остановить их раньше"""
        await self._stop()

        # Сессия закрывается не сразу для этого нужно немного подождать
        await self.session.close()
        await asyncio.sleep(0.250)

    async def _start(self):
        await self.poller.start()
        await self.worker.start()

    async def _stop(self):
        await self.poller.stop()
        await self.worker.stop()