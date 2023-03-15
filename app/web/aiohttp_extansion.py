from typing import Optional

from aiohttp.web import (Application as AiohttpApplication,
                         View as AiohttpView,
                         Request as AiohttpRequest)

from ..store import Store
from ..store.database.database import Database
from ..web.config import Config


class Application(AiohttpApplication):
    database: Optional[Database] = None
    config: Optional[Config] = None
    store: Optional[Store] = None


class Request(AiohttpRequest):
    @property
    def app(self) -> "Application":
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})
