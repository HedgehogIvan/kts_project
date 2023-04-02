import typing

from .database.database import Database

if typing.TYPE_CHECKING:
    from ..web.aiohttp_extansion import Application


class Store:
    def __init__(self, app: "Application"):
        from .admin.accessor import AdminAccessor
        from .tg_api.accessor import TgApiAccessor
        from .game.accessor import (
            AnswerAccessor,
            GameSessionAccessor,
            GameTimeAccessor,
            QuestionAccessor,
            PlayerAccessor,
            RoundAccessor,
            ScoreAccessor,
        )

        self.admins = AdminAccessor(app)
        self.answers = AnswerAccessor(app)
        self.game_sessions = GameSessionAccessor(app)
        self.game_time = GameTimeAccessor(app)
        self.questions = QuestionAccessor(app)
        self.players = PlayerAccessor(app)
        self.round = RoundAccessor(app)
        self.scores = ScoreAccessor(app)
        self.tg_api = TgApiAccessor(app)


def setup_store(app: "Application"):
    app.database = Database(app)
    app.on_startup.append(app.database.connect)
    app.on_cleanup.append(app.database.disconnect)
    app.store = Store(app)
