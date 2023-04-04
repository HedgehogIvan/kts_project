from ...web.aiohttp_extansion import Application

from .views import *


def setup_routes(app: Application):
    app.router.add_view("/create.question", QuestionCreateView)
