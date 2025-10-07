import asyncio
from typing import Union

import aiohttp
import stoat
from stoat.ext import commands

from constants import STOAT_TOKEN
from features.auto_react import AutoReact
from features.auto_response import AutoResponse
from features.birthdays import Birthdays
from features.chat_streaks import ChatStreaks
from features.chat_summary import ChatSummary


class Client(commands.CommandsClient):
    def __init__(self, session, token):
        super().__init__(session, token)
        self.add_cog(AutoReact())
        self.add_cog(AutoResponse())
        self.add_cog(Birthdays(self))
        self.add_cog(ChatSummary(self))
        self.add_cog(ChatStreaks(self))

    async def get_prefix(self, message: stoat.Message) -> Union[str, list[str]]:
        return "/"

    async def on_ready(self) -> None:
        await self.edit_status(text="/help | 0.1")


async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, STOAT_TOKEN)
        await client.start()

asyncio.run(main())