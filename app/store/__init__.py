import typing

from .database.database import Database

if typing.TYPE_CHECKING:
    from ..web.aiohttp_extansion import Application


class Store:
    def __init__(self, app: "Application"):
        from .admin.accessor import AdminAccessor
        from .tg_api.accessor import TgApiAccessor
        from .game.accessor import ChatAccessor, UserAccessor, GameSessionAccessor, ScoreAccessor

        self.admins = AdminAccessor(app)
        self.tg_api = TgApiAccessor(app)
        self.chats = ChatAccessor(app)
        self.users = UserAccessor(app)
        self.games = GameSessionAccessor(app)
        self.scores = ScoreAccessor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
