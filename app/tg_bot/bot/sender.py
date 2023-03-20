import asyncio
from asyncio import Task, Queue
from queue import Queue
from typing import Optional

from ..api.client import TgClient


class Sender:
    def __init__(self, tg_client: TgClient, to_sender_queue: Queue):
        self.to_sender_queue: Queue = to_sender_queue
        self.tg_client: TgClient = tg_client
        self.send_task: Optional[Task] = None

    async def send_echo_message(self, parameters: dict):
        if parameters["type"] == "message":
            await self.tg_client.send_message(
                parameters["chat_id"], parameters["text"]
            )

    async def _sender(self):
        while True:
            try:
                params: dict = await self.to_sender_queue.get()
                await self.send_echo_message(params)
            finally:
                self.to_sender_queue.task_done()

    async def start(self):
        self.send_task = asyncio.create_task(self._sender())

    async def stop(self):
        self.send_task.cancel()
