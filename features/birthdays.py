import asyncio
import datetime
import re

import revolt
from revolt.ext import commands

from database import client


class Birthdays(commands.Cog):
    def __init__(self, bot: commands.CommandsClient):
        super().__init__()
        self.qualified_name = "Birthdays"
        self.bot = bot

    @commands.Cog.listen()
    async def on_ready(self):
        asyncio.create_task(self.handle_birthday())

    @commands.command(name="set_birthday", usage="/set_birthday YYYY-MM-DD")
    async def set_birthday(self, ctx: commands.Context, date: str):
        """Set the birthday for birthday announcements to work"""
        if not re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date):
            await ctx.send("❌ invalid date, please use format yyyy-mm-dd")
            return

        split_date = date.split("-")

        now = datetime.datetime.now()

        year = int(split_date[0])
        month = int(split_date[1])
        day = int(split_date[2])

        if 1900 < year > now.year:
            await ctx.send("❌ year is out of range, please specify a valid year")
            return

        if 1 < month >= 12:
            await ctx.send("❌ month is out of range, please specify a valid month")
            return

        if 1 < day >= 31:
            await ctx.send("❌ day is out of range, please specify a valid day")
            return

        if now < datetime.datetime(year, month, day):
            await ctx.send("❌ date is out of range, please specify a valid date")
            return

        client['birthdays'].update_one({
            'user': ctx.author.id
        }, {
            'year': int(split_date[0]),
            'month': int(split_date[1]),
            'day': int(split_date[2])
        }, upsert=True)

        await ctx.send("✅ birthday saved ❤️")

    @commands.command(name="announce_birthday")
    async def announce_birthday(self, ctx: commands.Context, announce: str):
        """Whether announce birthday in the current server you're in or not"""
        if announce in ["on", "yes", "yesh", "yesh~", "1", "ye", "y", "Y"]:
            val = True
        elif announce in ["off", "no", "nyo", "nyoo", "nyo~", "0", "na", "n", "N"]:
            val = False
        else:
            await ctx.send("❌ invalid value for the announce parameter, pwease specify yes or no uwu")
            return

        if val:
            client['birthdays'].update_one({
                'user': ctx.author.id
            }, {
                '$push': {
                    'announce': ctx.server.id
                }
            })
        else:
            client['birthdays'].update_one({
                'user': ctx.author.id
            }, {
                '$pull': {
                    'announce': ctx.server.id
                }
            })

        await ctx.send("✅ set")

    @commands.command(name="birthday_announcement_channel")
    async def birthday_announcement_channel(self, ctx: commands.Context, announcement: str):
        announcement_channel = commands.channel_converter(announcement, ctx)

        client['ServerSettings'].update_one({
            'server': ctx.server.id
        }, {
            '$set': {
                'birthdayChannel': announcement_channel.id
            }
        }, upsert=True)

        await ctx.send("✅ set")

    async def handle_birthday(self):
        while True:
            now = datetime.datetime.now()

            if now.hour == 12 and now.minute == 0:
                try:
                    # handle birthdays
                    birthdays = client['birthdays'].find({
                        'month': now.month,
                        'day': now.day
                    }).to_list()

                    for birthday in birthdays:
                        user = self.bot.get_user(birthday['user'])

                        now = datetime.datetime.now()
                        birthday_date = datetime.datetime(birthday['year'], birthday['month'], birthday['day'])

                        if user is not None:
                            try:  # try send dm, otherwise continue to channels
                                await user.send(
                                    f"# 🎊 happy {(now - birthday_date).days // 365}th birthday {user.display_name} ❤️🎊")
                            except Exception as e:
                                pass

                        if 'announce' in birthday:
                            for server_id in birthday['announce']:
                                server = self.bot.get_server(server_id)
                                if server is None:
                                    continue

                                birthday_channel = client['ServerSettings'].find_one({
                                    'server': server_id
                                })
                                if birthday_channel is None:
                                    continue
                                if 'birthdayChannel' not in birthday_channel:
                                    continue

                                try:  # try and get channel, and skip if not found
                                    channel: revolt.TextChannel = self.bot.get_channel(birthday_channel['birthdayChannel'])
                                except Exception as e:
                                    continue
                                if channel.channel_type != revolt.ChannelType.text_channel:
                                    continue

                                await channel.send(
                                    f"# 🎊 <@{birthday['user']}> is celebrating their {(now - birthday_date).days // 365}th birthday! 🎊")
                except Exception as e:
                    print(e)

            await asyncio.sleep(60)
