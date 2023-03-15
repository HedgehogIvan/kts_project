from typing import Optional

from aiohttp import ClientSession

from ..api.models import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token: str, session: ClientSession):
        self.token = token
        self.session = session

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    async def get_me(self) -> dict:
        url = self.get_url("getMe")
        async with self.session.get(url) as resp:
            return await resp.json()

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 0) -> dict:
        url = self.get_url("getUpdates")
        params = {}
        if offset:
            params['offset'] = offset
        if timeout:
            params['timeout'] = timeout
        async with self.session.get(url, params=params) as resp:
            return await resp.json()

    async def get_updates_in_objects(self, offset: Optional[int] = None, timeout: int = 0) -> GetUpdatesResponse:
        res_dict = await self.get_updates(offset=offset, timeout=timeout)
        return GetUpdatesResponse.Schema().load(res_dict)

    async def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url("sendMessage")
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        async with self.session.post(url, json=payload) as resp:
            res_dict = await resp.json()
            return SendMessageResponse.Schema().load(res_dict)
