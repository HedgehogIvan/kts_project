from aiohttp.web_response import json_response

from app.web.aiohttp_extansion import View


class SQLTestView(View):
    async def get(self):
        # await self.store.chats.add_chat(-1001859433322)
        # logging.info("Создан чат")
        # await self.store.users.add_user(1, -1001859433322)
        # logging.info("Создан пользователь")
        # await self.store.games.create_game(-1001859433322)
        # logging.info("Создана игра")
        # await self.store.games.add_user_in_game(1, -1001859433322, 1)
        # logging.info("Пользователь добавлен в игру")
        # a = await self.store.games.get_last_game(-1001859433322)
        # logging.info(a)
        # a = await self.store.users.get_chat_users(-1001965161469)

        return json_response(data={})
