import revolt
from revolt.ext import commands
import emoji as emoji_parse

from database import client


class AutoReact(commands.Cog):
    def __init__(self):
        super().__init__()
        self.qualified_name = 'Auto React'

    @commands.command(name="auto_react_add", usage="/autoreact add [keyword] [emoji]")
    async def auto_react_add(self, ctx: commands.Context, keyword: str, emoji: str):
        # Permission check
        if not ctx.author.has_permissions(manage_server=True):
            await ctx.send("❌ Insufficient permissions")
            return

        # Validation: Keyword
        if len(keyword) < 1 or len(keyword) > 100:
            await ctx.send("❌ Keyword is too long or too short")
            return

        if client['AutoReact'].count_documents({
            'Keyword': keyword.strip()
        }) > 0:
            await ctx.send("❌ Can't have multiple keywords on Auto React")
            return

        # Validation: Emoji
        if not emoji_parse.is_emoji(emoji):
            await ctx.send("❌ Not an emoji (if your keyword contains spaces, use quotes)")
            return

        client['AutoReact'].insert_one({
            'ServerID': ctx.server.id,
            'Keyword': keyword,
            'Emoji': emoji
        })

        await ctx.send("✅ Auto react rule created")

    @commands.command(name="auto_react_remove", usage="/autoreact remove [keyword]")
    async def auto_react_remove(self, ctx: commands.Context, keyword: str):
        # Permission check
        if not ctx.author.has_permissions(manage_server=True):
            await ctx.send("❌ Insufficient permissions")
            return

        if len(keyword) < 1 or len(keyword) > 100:
            await ctx.send("❌ Keyword is too long or too short")
            return

        res = client['AutoReact'].delete_one({
            'ServerID': ctx.server.id,
            'Keyword': keyword
        })

        if res.deleted_count == 1:
            await ctx.send("✅ Deleted auto react rule")
        else:
            await ctx.send("❌ Auto react rule not found")

    @commands.command(name="auto_react_change_keyword", usage="/autoreact change_keyword [oldkeyword] [newkeyword]")
    async def auto_react_change_keyword(self, ctx: commands.Context, old_keyword: str, new_keyword: str):
        # Permission check
        if not ctx.author.has_permissions(manage_server=True):
            await ctx.send("❌ Insufficient permissions")
            return

        if len(new_keyword) < 1 or len(new_keyword) > 100:
            await ctx.send("❌ Keyword is too long or too short")
            return

        if client['AutoReact'].count_documents({
            'ServerID': ctx.server.id,
            'Keyword': new_keyword
        }) > 0:
            await ctx.send("❌ New keyword already in use")
            return

        res = client['AutoReact'].update_one({
            'ServerID': ctx.server.id,
            'Keyword': old_keyword
        }, {
            '$set': {
                'Keyword': new_keyword
            }
        })

        if res.matched_count > 0:
            await ctx.send("✅ Updated")
        else:
            await ctx.send("❌ Not found")

    @commands.command(name="auto_react_change_reaction", usage="/autoreact change_reaction [keyword] [emoji]")
    async def auto_react_change_reaction(self, ctx: commands.Context, keyword: str, emoji: str):
        # Permission check
        if not ctx.author.has_permissions(manage_server=True):
            await ctx.send("❌ Insufficient permissions")
            return

        if not emoji_parse.is_emoji(emoji):
            await ctx.send("❌ Not an emoji (if your keyword contains spaces, use quotes)")
            return

        res = client['AutoReact'].update_one({
            'ServerID': ctx.server.id,
            'Keyword': keyword
        }, {
            '$set': {
                'Emoji': emoji
            }
        })

        if res.matched_count > 0:
            await ctx.send("✅ Updated")
        else:
            await ctx.send("❌ Not found")

    @commands.Cog.listen()
    async def on_message(self, message: revolt.Message):
        if message.author.bot:
            return

        auto_react_rules = client['AutoReact'].find({
            'ServerID': message.server.id
        })

        for i in auto_react_rules:
            if i['Keyword'] in message.content:
                await message.add_reaction(i['Emoji'])
