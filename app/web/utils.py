from functools import wraps
from typing import Optional
from aiohttp.web_response import json_response as aiohttp_json_response
from aiohttp_session import get_session
from aiohttp.web import HTTPUnauthorized

from app.admin.models import Admin
from app.web.aiohttp_extansion import View


def error_json_response(
    http_status: int,
    status: str = "error",
    message: Optional[str] = None,
    data: Optional[dict] = None,
):
    if data is None:
        data = {}
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "message": str(message),
            "data": data,
        },
    )


def available_for_admin(func):
    @wraps(func)
    async def wrapped(self: View):
        session = await get_session(self.request)

        try:
            session_data = session["admin"]
        except:
            raise HTTPUnauthorized

        if "login" not in session_data and "id" not in session_data:
            raise HTTPUnauthorized

        admin: Admin = await self.store.admins.get_by_login(
            session_data["login"]
        )

        if admin and admin.id == session_data["id"]:
            return await func(self)

        raise HTTPUnauthorized

    return wrapped
