from ..admin.routes import setup_routes as admin_setup_routes
from ..test_requests.routes import setup_routes as test_requests_setup_routes
from .aiohttp_extansion import Application


def setup_routes(app: Application):
    admin_setup_routes(app)
    test_requests_setup_routes(app)
