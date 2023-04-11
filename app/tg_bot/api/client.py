import logging
from typing import Optional

from aiohttp import ClientSession

from ..api.models import (
    SendMessageResponse,
    MessageUpdateObj,
    ChatMemberUpdateObj,
    ChannelPostUpdateObj,
    CallbackQueryObj,
    UpdateObj,
    ChatMemberResponse
)


class TgClient:
    def __init__(self, token: str, session: ClientSession):
        self.token = token
        self.session = session

        self.__logger: logging.Logger = logging.getLogger(__name__)
        self.__setup_logger()

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    async def get_me(self) -> dict:
        url = self.get_url("getMe")
        async with self.session.get(url) as resp:
            return await resp.json()

    async def get_updates(
        self, offset: Optional[int] = None, timeout: int = 0
    ) -> dict:
        url = self.get_url("getUpdates")
        params = {}

        if offset:
            params["offset"] = offset
        if timeout:
            params["timeout"] = timeout

        async with self.session.get(url, params=params) as resp:
            return await resp.json()

    async def get_updates_in_objects(
        self, offset: Optional[int] = None, timeout: int = 0
    ) -> dict:
        res_dict = await self.get_updates(offset=offset, timeout=timeout)
        return_upds = []

        for update in res_dict["result"]:
            if "message" in update:
                return_upds.append(MessageUpdateObj.Schema().load(update))
                continue
            if "callback_query" in update:
                return_upds.append(CallbackQueryObj.Schema().load(update))
                continue
            if "channel_post" in update:
                return_upds.append(ChannelPostUpdateObj.Schema().load(update))
                continue
            if "chat_member" in update:
                return_upds.append(ChatMemberUpdateObj.Schema().load(update))
                continue
            return_upds.append(UpdateObj.Schema().load(update))

        return {"ok": res_dict["ok"], "result": return_upds}

    async def send_message(
        self, chat_id: int, text: str, reply_markup: Optional[dict] = None
    ) -> SendMessageResponse:
        url = self.get_url("sendMessage")
        if reply_markup:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "reply_markup": reply_markup,
            }
        else:
            payload = {"chat_id": chat_id, "text": text}

        try:
            async with self.session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return SendMessageResponse.Schema().load(res_dict)
        except Exception:
            logging.exception(Exception)
            return None

    async def send_callback_answer(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
    ):
        url = self.get_url("answerCallbackQuery")
        payload = {"callback_query_id": callback_query_id}

        if text:
            payload["text"] = text
        if show_alert:
            payload["show_alert"] = show_alert

        try:
            async with self.session.post(url, json=payload) as resp:
                res_dict = await resp.json()
        except Exception:
            logging.exception(Exception)

    async def update_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: Optional[dict] = None,
    ):
        url = self.get_url("editMessageText")
        payload = {"chat_id": chat_id, "message_id": message_id, "text": text}

        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            async with self.session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                print()
        except Exception:
            logging.exception(Exception)

    async def pin_message(self, chat_id: int, message_id: int, disable_notification: Optional[bool] = None):
        url = self.get_url("pinChatMessage")
        if not disable_notification:
            payload = {"chat_id": chat_id, "message_id": message_id}
        else:
            payload = {"chat_id": chat_id, "message_id": message_id, "disable_notification": disable_notification}

        async with self.session.post(url, json=payload) as resp:
            res_dict = await resp.json()

    async def unpin_message(self, chat_id: int, message_id: Optional[int] = None):
        url = self.get_url("unpinChatMessage")
        payload = {"chat_id": chat_id, "message_id": message_id}

        async with self.session.post(url, json=payload) as resp:
            res_dict = await resp.json()

    async def get_chat_member(self, chat_id: int, user_id: int = 6122536778):
        url = self.get_url("getChatMember")
        payload = {"chat_id": chat_id, "user_id": user_id}

        async with self.session.post(url, json=payload) as resp:
            res_dict = await resp.json()
            return ChatMemberResponse.Schema().load(res_dict)

    def __setup_logger(self):
        self.__logger.setLevel(10)
        handler = logging.FileHandler(f"etc/logs/{__name__}.log", mode="w")
        formatter_ = logging.Formatter(
            "%(name)s %(asctime)s %(levelname)s %(message)s"
        )

        handler.setFormatter(formatter_)

        self.__logger.addHandler(handler)
