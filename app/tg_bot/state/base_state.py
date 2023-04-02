import logging
from typing import Optional

from app.store import Store
from app.tg_bot.api import MessageToSend, AnswerForCallbackQuery, UpdateMessage


class State:
    def __init__(self, chat_id: int, store: Store):
        self.chat_id = chat_id
        self.store = store

        self._logger = logging.getLogger(__name__)
        self._setup_logger()

    async def handler(self) -> list[MessageToSend | AnswerForCallbackQuery]:
        pass

    async def stop(self):
        pass

    async def start(self):
        pass

    def _setup_logger(self):
        self._logger.setLevel(10)
        handler = logging.FileHandler(f"etc/logs/{__name__}.log", mode="w")
        formatter_ = logging.Formatter(
            "%(name)s %(asctime)s %(levelname)s %(message)s"
        )

        handler.setFormatter(formatter_)

        self._logger.addHandler(handler)
