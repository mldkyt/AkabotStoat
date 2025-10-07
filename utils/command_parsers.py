import re

import stoat
from stoat.ext import commands
from utils.errors import CommandParseError


def parse_text_channel(ctx: commands.Context, channel: str) -> stoat.TextChannel:
    """
    Parses the channel in the channel parameter and validates it's a real text channel.
    :param ctx: The command context
    :param channel: Channel mention (usually a command parameter)
    :return: TextChannel
    """

    if not re.match(r"<#[A-Z0-9]+>", channel):
        raise CommandParseError(f"Invalid mention: {channel}")

    channel_id = channel[2:-1]
    channel_inst = ctx.server.get_channel(channel_id)

    if not channel_inst:
        raise CommandParseError(f"Invalid channel: {channel}")

    if channel_inst.channel_type != stoat.ChannelType.text_channel:
        raise CommandParseError(f"Not a text channel: {channel}")

    return channel_inst
