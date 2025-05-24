import revolt
from revolt.ext import commands

from database import client


class AutoResponse(commands.Cog):
    def __init__(self):
        super().__init__()
        self.qualified_name = 'Auto Response'

    @commands.command(name="auto_response_add", usage="/auto_response_add [keyword] [reply]")
    async def auto_response_add(self, ctx: commands.Context, keyword: str, reply: str):
        # Permission check
        if not ctx.author.has_permissions(manage_server=True):
            await ctx.send("❌ Insufficient permissions")
            return

        # Validation: Keyword
        if len(keyword) < 1 or len(keyword) > 100:
            await ctx.send("❌ Keyword is too long or too short")
            return

        if client['AutoResponse'].count_documents({
            'Keyword': keyword.strip()
        }) > 0:
            await ctx.send("❌ Can't have multiple keywords on Auto Response")
            return

        # Validation: Reply
        if len(reply) < 1 or len(reply) > 1000:
            await ctx.send("❌ Reply is too short or too long")
            return

        client['AutoResponse'].insert_one({
            'ServerID': ctx.server.id,
            'Keyword': keyword,
            'Reply': reply
        })

        await ctx.send("✅ Auto response rule created")

    @commands.command(name="auto_response_remove", usage="/auto_response_remove [keyword]")
    async def auto_response_remove(self, ctx: commands.Context, keyword: str):
        # Permission check
        if not ctx.author.has_permissions(manage_server=True):
            await ctx.send("❌ Insufficient permissions")
            return

        if len(keyword) < 1 or len(keyword) > 100:
            await ctx.send("❌ Keyword is too long or too short")
            return

        res = client['AutoResponse'].delete_one({
            'ServerID': ctx.server.id,
            'Keyword': keyword
        })

        if res.deleted_count == 1:
            await ctx.send("✅ Deleted auto response rule")
        else:
            await ctx.send("❌ Auto response rule not found")

    @commands.command(name="auto_response_change_keyword", usage="/auto_resonse_change_keyword [oldkeyword] [newkeyword]")
    async def auto_response_change_keyword(self, ctx: commands.Context, old_keyword: str, new_keyword: str):
        # Permission check
        if not ctx.author.has_permissions(manage_server=True):
            await ctx.send("❌ Insufficient permissions")
            return

        if len(new_keyword) < 1 or len(new_keyword) > 100:
            await ctx.send("❌ Keyword is too long or too short")
            return

        if client['AutoResponse'].count_documents({
            'ServerID': ctx.server.id,
            'Keyword': new_keyword
        }) > 0:
            await ctx.send("❌ New keyword already in use")
            return

        res = client['AutoResponse'].update_one({
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

    @commands.command(name="auto_response_change_reply", usage="/auto_response_change_reply [keyword] [reply]")
    async def auto_response_change_reply(self, ctx: commands.Context, keyword: str, reply: str):
        # Permission check
        if not ctx.author.has_permissions(manage_server=True):
            await ctx.send("❌ Insufficient permissions")
            return

        if len(reply) < 1 or len(reply) > 1000:
            await ctx.send("❌ Reply is too short or too long")
            return

        res = client['AutoResponse'].update_one({
            'ServerID': ctx.server.id,
            'Keyword': keyword
        }, {
            '$set': {
                'Reply': reply
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

        auto_response_rules = client['AutoResponse'].find({
            'ServerID': message.server.id
        })

        for i in auto_response_rules:
            if i['Keyword'] in message.content:
                await message.channel.send(i['Reply'])
