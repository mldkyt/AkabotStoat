import datetime
import math

import pyvolt
from pyvolt.ext import commands

from database import client


class ChatStreaks(commands.Gear):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="streak")
    async def streak_cmd(self, ctx: commands.Context):
        """Get your current streak"""

        user = client['chatstreaks'].find_one({
            'server': ctx.server.id,
            'user': ctx.author.id
        })

        diff = (user['lastmessagedate'] - user['startdate']).total_seconds() // 86400 + 1

        await ctx.send(f"your streak is {math.floor(diff)} days :3")

    @commands.Gear.listener()
    async def on_message(self, event: pyvolt.MessageCreateEvent):

        data = client['chatstreaks'].find_one({
            'server': event.message.server.id,
            'user': event.message.author.id
        })

        if data is None:
            client['chatstreaks'].insert_one({
                'server': event.message.server.id,
                'user': event.message.author.id,
                'lastmessagedate': datetime.datetime.now(),
                'startdate': datetime.datetime.now()
            })

            return

        if (datetime.datetime.now() - data['lastmessagedate']).total_seconds() >= 129600:
            client['chatstreaks'].update_one({
                'server': event.message.server.id,
                'user': event.message.author.id
            }, {
                '$set': {
                    'lastmessagedate': datetime.datetime.now(),
                    'startdate': datetime.datetime.now()
                }
            })

            days = (datetime.datetime.now() - data['startdate']).total_seconds() // 86400 + 1
            await event.message.channel.send(f"{event.message.author.mention} your {math.floor(days)} day chat streak has expired :(")

        else:
            before = (datetime.datetime.now() - data['startdate']).total_seconds() // 86400 + 1

            client['chatstreaks'].update_one({
                'server': event.message.server.id,
                'user': event.message.author.id
            }, {
                '$set': {
                    'lastmessagedate': datetime.datetime.now()
                }
            })

            data_a = client['chatstreaks'].find_one({
                'server': event.message.server.id,
                'user': event.message.author.id
            })

            after = (datetime.datetime.now() - data_a['startdate']).total_seconds() // 86400 + 1

            if before != after:
                await event.message.channel.send(f"{event.message.author.mention} {math.floor(after)} day chat streak :3")
