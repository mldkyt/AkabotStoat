import asyncio
from typing import Union

import aiohttp
import revolt
from revolt.ext import commands

from constants import REVOLT_TOKEN


class Client(commands.CommandsClient):
    async def get_prefix(self, message: revolt.Message) -> Union[str, list[str]]:
        return "/"

    async def on_ready(self) -> None:
        await self.edit_status(text="/help | 1.0")

async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, REVOLT_TOKEN)
        await client.start()

asyncio.run(main())