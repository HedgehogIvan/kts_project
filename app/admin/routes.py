from ..web.aiohttp_extansion import Application

from .views import *


def setup_routes(app: Application):
    app.router.add_view("/create.admin", AdminCreateView)
    app.router.add_view("/admin.login", AdminLoginView)
    app.router.add_view("/admin.cur", AdminCurrentView)
    app.router.add_view("/delete.admin", AdminDeleteView)
    app.router.add_view("/admin.change.pass", AdminChangePassView)
