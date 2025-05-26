import datetime
import math

import revolt
from revolt.ext import commands

from database import client


class ChatStreaks(commands.Cog):
    def __init__(self, bot: commands.CommandsClient):
        super().__init__()
        self.bot = bot
        self.qualified_name = "Chat Streaks"

    @commands.command(name="streak")
    async def streak_cmd(self, ctx: commands.Context):
        """Get your current streak"""

        user = client['chatstreaks'].find_one({
            'server': ctx.server.id,
            'user': ctx.author.id
        })

        diff = (user['lastmessagedate'] - user['startdate']).total_seconds() // 86400 + 1

        await ctx.send(f"your streak is {math.floor(diff)} days :3")

    @commands.Cog.listen()
    async def on_message(self, message: revolt.Message):

        data = client['chatstreaks'].find_one({
            'server': message.server.id,
            'user': message.author.id
        })

        if data is None:
            client['chatstreaks'].insert_one({
                'server': message.server.id,
                'user': message.author.id,
                'lastmessagedate': datetime.datetime.now(),
                'startdate': datetime.datetime.now()
            })

            return

        if (datetime.datetime.now() - data['lastmessagedate']).total_seconds() >= 129600:
            client['chatstreaks'].update_one({
                'server': message.server.id,
                'user': message.author.id
            }, {
                '$set': {
                    'lastmessagedate': datetime.datetime.now(),
                    'startdate': datetime.datetime.now()
                }
            })

            days = (datetime.datetime.now() - data['startdate']).total_seconds() // 86400 + 1
            await message.channel.send(f"{message.author.mention} your {math.floor(days)} day chat streak has expired :(")

        else:
            before = (datetime.datetime.now() - data['startdate']).total_seconds() // 86400 + 1

            client['chatstreaks'].update_one({
                'server': message.server.id,
                'user': message.author.id
            }, {
                '$set': {
                    'lastmessagedate': datetime.datetime.now()
                }
            })

            data_a = client['chatstreaks'].find_one({
                'server': message.server.id,
                'user': message.author.id
            })

            after = (datetime.datetime.now() - data_a['startdate']).total_seconds() // 86400 + 1

            if before != after:
                await message.channel.send(f"{message.author.mention} {math.floor(after)} day chat streak :3")
