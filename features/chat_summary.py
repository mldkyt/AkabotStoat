import asyncio
import datetime

import stoat
from stoat.ext import commands

from database import client


class ChatSummary(commands.Cog):
    def __init__(self, bot: commands.CommandsClient):
        self.bot = bot
        self.qualified_name = "Chat Summary"

    @commands.Cog.listen()
    async def on_ready(self):
        asyncio.create_task(self.handle_chat_summary())

    @commands.Cog.listen()
    async def on_message(self, message: stoat.Message):
        if message.author.bot:
            return

        client['chatsummary'].update_one({
            'server': message.server.id,
            'channel': message.channel.id
        }, {
            '$inc': {
                'messages': 1,
                f'members.{message.author.id}': 1
            }
        })

    @commands.command(name="chat_summary_set", usage="/chat_summary_set <enabled>")
    async def chat_summary_set(self, ctx: commands.Context, enabled: str):
        """Enable or disable chat summary in the current channel"""
        if enabled in ["on", "yes", "yesh", "yesh~", "1", "ye", "y", "Y"]:
            val = True
        elif enabled in ["off", "no", "nyo", "nyoo", "nyo~", "0", "na", "n", "N"]:
            val = False
        else:
            await ctx.send("❌ invalid value for the enabled parameter, pwease specify yes or no uwu")
            return

        existing = client['chatsummary'].find_one({
            'server': ctx.server.id,
            'channel': ctx.channel.id
        })

        if existing is not None and val:
            await ctx.send("✅ already enabled")
            return

        if existing is None and not val:
            await ctx.send("✅ already disabled")
            return

        if val:
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
                    server = self.bot.get_server(i['server'])
                except Exception:
                    continue

                # try and get the channel
                try:
                    channel: stoat.TextChannel = server.get_channel(i['channel'])
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
