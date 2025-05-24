import asyncio
from typing import Union, Coroutine, Any

import aiohttp
import revolt
from revolt.ext import commands

from constants import REVOLT_TOKEN
from features.auto_react import AutoReact
from features.auto_response import AutoResponse


class Client(commands.CommandsClient):
    def __init__(self, session, token):
        super().__init__(session, token)
        self.add_cog(AutoReact())
        self.add_cog(AutoResponse())

    async def get_prefix(self, message: revolt.Message) -> Union[str, list[str]]:
        return "/"

    async def on_ready(self) -> None:
        await self.edit_status(text="/help | 1.0")


async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, REVOLT_TOKEN)
        await client.start()

asyncio.run(main())