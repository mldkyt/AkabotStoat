import asyncio
import datetime

import pyvolt
from pyvolt.ext import commands

from database import client


class ChatSummary(commands.Gear):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Gear.listener()
    async def on_ready(self, event: pyvolt.ReadyEvent):
        asyncio.create_task(self.handle_chat_summary())

    @commands.Gear.listener()
    async def on_message(self, event: pyvolt.MessageCreateEvent):
        if event.message.author.bot:
            return

        client['chatsummary'].update_one({
            'server': event.message.server.id,
            'channel': event.message.channel.id
        }, {
            '$inc': {
                'messages': 1,
                f'members.{event.message.author.id}': 1
            }
        })

    @commands.command(name="chat_summary_set")
    @commands.has_permissions(manage_server=True)
    async def chat_summary_set(self, ctx: commands.Context, enabled: bool):
        """Enable or disable chat summary in the current channel"""
        existing = client['chatsummary'].find_one({
            'server': ctx.server.id,
            'channel': ctx.channel.id
        })

        if existing is not None and enabled:
            await ctx.send("✅ already enabled")
            return

        if existing is None and not enabled:
            await ctx.send("✅ already disabled")
            return

        if enabled:
            client['chatsummary'].insert_one({
                'server': ctx.server.id,
                'channel': ctx.channel.id,
                'messages': 0,
                'members': {}
            })
        else:
            client['chatsummary'].delete_one({
                'server': ctx.server.id,
                'channel': ctx.channel.id
            })

    async def handle_chat_summary(self):
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)

            if now.hour != 0 or now.minute != 0:
                await asyncio.sleep(60)
                continue

            for i in client['chatsummary'].find():
                # try and get the server
                try:
                    server = await self.bot.fetch_server(i['server'])
                except Exception:
                    continue

                # try and get the channel
                try:
                    channel = await self.bot.fetch_channel(i['channel'])
                except Exception:
                    continue

                yesterday = now - datetime.timedelta(days=1)

                # base message
                message = (f"# Chat Summary for {yesterday.year}-{yesterday.month}-{yesterday.day}\n"
                           f"Total messages: {i['messages']}\n")

                # top 5 members
                for j, (k, v) in enumerate(i['members'].items()):
                    message += f"{j + 1}: <@{k}> with {v} messages\n"
                    if j > 5:
                        break

                # send message
                try:
                    await channel.send(message)
                except Exception:
                    continue

                # reset guild
                client['chatsummary'].update_one({
                    'server': server.id,
                    'channel': channel.id
                }, {
                    '$set': {
                        'messages': 0,
                        'members': {}
                    }
                })

            await asyncio.sleep(60)
