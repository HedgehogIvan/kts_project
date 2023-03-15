import os

from aiohttp_session import setup as session_setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from app.store import setup_store
from .aiohttp_extansion import Application
from .config import setup_config
from .logger import setup_logging
from .middlewares import setup_middlewares
from .routes import setup_routes

from aiohttp_apispec import setup_aiohttp_apispec


app = Application()


def setup_app() -> Application:
    setup_logging()
    setup_routes(app)
    setup_aiohttp_apispec(app,
                          title="TGBot MiniGame",
                          url="/docs/json",
                          swagger_path="/docs")
    setup_middlewares(app)
    # TODO: Вынести передачу путя до конфиг файла в другое место
    setup_config(app, "config.yaml")
    session_setup(app, EncryptedCookieStorage(os.urandom(32)))
    setup_store(app)
    return app
