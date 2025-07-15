import pyvolt
from pyvolt.ext import commands

from database import client


class AutoResponse(commands.Gear):
    def __init__(self):
        super().__init__()

    @commands.command(name="auto_response_add")
    @commands.has_permissions(manage_server=True)
    async def auto_response_add(self, ctx: commands.Context, keyword: str, reply: str):
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

    @commands.command(name="auto_response_remove")
    @commands.has_permissions(manage_server=True)
    async def auto_response_remove(self, ctx: commands.Context, keyword: str):
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

    @commands.command(name="auto_response_change_keyword")
    @commands.has_permissions(manage_server=True)
    async def auto_response_change_keyword(self, ctx: commands.Context, old_keyword: str, new_keyword: str):
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

    @commands.command(name="auto_response_change_reply")
    @commands.has_permissions(manage_server=True)
    async def auto_response_change_reply(self, ctx: commands.Context, keyword: str, reply: str):
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

    @commands.Gear.listener()
    async def on_message(self, event: pyvolt.MessageCreateEvent):
        if event.message.author.bot:
            return

        auto_response_rules = client['AutoResponse'].find({
            'ServerID': event.message.server.id
        })

        for i in auto_response_rules:
            if i['Keyword'] in event.message.content:
                await event.message.channel.send(i['Reply'], replies=[event.message])
