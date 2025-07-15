import asyncio
from typing import Union, Coroutine, Any

import pyvolt
from pyvolt.ext import commands
from pyvolt.ext.chunking import MemberChunker, MemberChunkerFlags

from constants import REVOLT_TOKEN
from features.auto_react import AutoReact
from features.auto_response import AutoResponse
from features.birthdays import Birthdays
from features.chat_streaks import ChatStreaks
from features.chat_summary import ChatSummary

bot = commands.Bot(command_prefix=commands.when_mentioned_or("/"), user_bot=True)

MemberChunker(bot)

@bot.on(pyvolt.ReadyEvent)
async def on_ready(event: pyvolt.ReadyEvent):
    await bot.add_gear(AutoReact())
    await bot.add_gear(AutoResponse())
    await bot.add_gear(Birthdays(bot))
    await bot.add_gear(ChatStreaks(bot))
    await bot.add_gear(ChatSummary(bot))

    print(f"{len(event.servers)} servers")
    print(f"{len(event.users)} users")
    print("ready")
    print(f"logged on as {event.me.tag}")

bot.run(REVOLT_TOKEN)
