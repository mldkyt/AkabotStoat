import asyncio
from typing import Union, Coroutine, Any

import pyvolt
from pyvolt import ReadyEvent, utils
from pyvolt.ext import commands
from pyvolt.ext.chunking import MemberChunker

from constants import REVOLT_TOKEN
from features.auto_react import AutoReact
from features.auto_response import AutoResponse
from features.birthdays import Birthdays
from features.chat_streaks import ChatStreaks
from features.chat_summary import ChatSummary

class Akabot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("/"), user_bot=True)

        MemberChunker(self)

    async def setup_hook(self) -> None:
        await bot.add_gear(AutoReact())
        await bot.add_gear(AutoResponse())
        await bot.add_gear(Birthdays(bot))
        await bot.add_gear(ChatStreaks(bot))
        await bot.add_gear(ChatSummary(bot))

    async def on_ready(self, event: ReadyEvent, /):
        print(f"{len(event.servers)} servers")
        print(f"{len(event.users)} users")
        print(f"{len(event.channels)} channels")
        for i in event.channels:
            if not isinstance(i, pyvolt.TextChannel):
                continue

            print([j for j in event.servers if j.id == i.server_id][0].name, i.name)

        print("ready")
        print(f"logged on as {event.me.tag}")

bot = Akabot()
bot.run(REVOLT_TOKEN)
