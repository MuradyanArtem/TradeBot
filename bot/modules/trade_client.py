import aiohttp

from . import utils

class TradeClient:
    def __init__(self, base_url: str, timeout: int) -> None:
        self.__base_url = utils.sanitize_url(base_url)
        self.__timeout = aiohttp.ClientTimeout(total=timeout)

    async def transaction(self, data: str, cookie: str):
        # TODO make reusable session
        async with aiohttp.ClientSession(
            timeout=self.__timeout, headers={"Cookie": cookie}
        ) as session:
            async with session.post(
                self.__base_url + "transactions", json=data
            ) as response:
                return {"status": response.status}

    async def login(self, data: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.__timeout) as session:
            async with session.post(
                self.__base_url + "users/session", json=data
            ) as response:
                return {
                    "status": response.status,
                    "cookie": response.headers["Set-Cookie"],
                }

    async def logout(self, cookie: str) -> int:
        async with aiohttp.ClientSession(
            timeout=self.__timeout, headers={"Cookie": cookie}
        ) as session:
            async with session.delete(self.__base_url + "users/session") as response:
                return {"status": response.status}

    async def register(self, data: str) -> dict:
        async with aiohttp.ClientSession(timeout=self.__timeout) as session:
            async with session.post(
                self.__base_url + "users/account", json=data
            ) as response:
                if response.status != 201:
                    return {"status": response.status}
                return {
                    "status": response.status,
                    "cookie": response.headers["Set-Cookie"],
                }

    async def get_wallet(self, cookie: str) -> dict:
        async with aiohttp.ClientSession(
            timeout=self.__timeout, headers={"Cookie": cookie}
        ) as session:
            async with session.get(self.__base_url + "users/wallet") as response:
                return {"status": response.status, "body": await response.json()}
