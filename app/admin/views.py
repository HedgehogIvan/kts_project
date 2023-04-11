from hashlib import sha256
from typing import Optional

from aiohttp.web_exceptions import HTTPForbidden, HTTPConflict, HTTPException, HTTPNotFound
from aiohttp.web_response import json_response
from aiohttp_apispec import request_schema, response_schema, querystring_schema
from aiohttp_session import new_session, get_session

from ..web.aiohttp_extansion import View
from .models import Admin
from .schemes import AdminScheme, AdminChangePasswordSchema, AdminDeleteSchema
from ..web.utils import available_for_admin

__all__ = [
    "AdminCreateView",
    "AdminLoginView",
    "AdminCurrentView",
    "AdminDeleteView",
    "AdminChangePassView",
]


class AdminCreateView(View):
    @request_schema(AdminScheme)
    @response_schema(AdminScheme)
    @available_for_admin
    async def post(self):
        data = await self.request.json()

        login = data["login"]
        password = await hash_password(data["password"])

        admin: Admin = await self.store.admins.get_by_login(login)

        if not admin:
            new_admin = await self.store.admins.create_admin(login, password)
            return json_response(data={"id": new_admin.id, "login": login})
        else:
            raise HTTPConflict


class AdminLoginView(View):
    @request_schema(AdminScheme)
    @response_schema(AdminScheme)
    async def post(self):
        data = self.request["data"]

        login = data["login"]
        password = await hash_password(data["password"])

        admin: Admin = await self.store.admins.get_by_login(login)

        if admin and admin.password == password:
            session = await new_session(request=self.request)
            session["admin"] = {"login": login, "id": admin.id}

            return json_response(data={"id": admin.id, "login": login})

        raise HTTPForbidden


class AdminCurrentView(View):
    @response_schema(AdminScheme)
    @available_for_admin
    async def get(self):
        session = await get_session(self.request)

        try:
            admin = session["admin"]
        except:
            raise HTTPException

        return json_response(data={"id": admin["id"], "login": admin["login"]})


class AdminDeleteView(View):
    @request_schema(AdminDeleteSchema)
    @response_schema(AdminScheme)
    @available_for_admin
    async def post(self):
        session = await get_session(self.request)

        cur_admin = session["admin"]
        full_admin_data: Optional[Admin] = await self.store.admins.get_by_login(
            cur_admin["login"]
        )

        if full_admin_data is None:
            raise HTTPNotFound

        request_data = self.request["data"]

        if (
            await hash_password(request_data["password"])
            != full_admin_data.password
        ):
            raise HTTPForbidden

        await self.store.admins.delete_admin(request_data["admin_for_delete"])

        return json_response(
            data={"id": cur_admin["id"], "login": cur_admin["login"]}
        )


class AdminChangePassView(View):
    @request_schema(AdminChangePasswordSchema)
    @response_schema(AdminScheme)
    @available_for_admin
    async def post(self):
        new_pass = await hash_password(self.request["data"]["new_pass"])
        old_pass = await hash_password(self.request["data"]["old_pass"])

        session = await get_session(self.request)
        cur_admin = session["admin"]

        full_admin_data: Admin = await self.store.admins.get_by_login(
            cur_admin["login"]
        )

        if full_admin_data.password != old_pass:
            raise HTTPForbidden

        await self.store.admins.update_pass_admin(
            full_admin_data.login, new_pass
        )

        return json_response(
            data={"id": cur_admin["id"], "login": cur_admin["login"]}
        )


async def hash_password(password: str) -> str:
    """
    Хэширует пароль
    :return: Хэшированный пароль или None
    """
    return sha256(password.encode("utf-8")).hexdigest()
