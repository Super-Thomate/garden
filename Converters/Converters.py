from discord.ext import commands
import discord
from core import logger


class GetMessage(commands.Converter):
  async def convert(self, ctx: commands.Context, message_id: str) -> discord.Message:
    """
    Search a message in the current channel using its ID and returns it

    :param ctx: The current context
    :param message_id: The ID of the message to be found
    :return: The message if found else None
    """
    try:
      message_id = int(message_id)
      message = await ctx.channel.fetch_message(message_id)
      return message
    except Exception as e:
      logger("Converters::GetMessage", f"{type(e).__name__} - {e}")
      return None


class GetInt(commands.Converter):
  async def convert(self, ctx: commands.Context, string: str) -> int:
    """
    Convert a string to an int, send an error message if an error occurs

    :param ctx: The current context
    :param string: The string to be converted
    :return: The integer value of the string or None if an error occured
    """
    try:
      integer = int(string)
      return integer
    except Exception as e:
      logger("Converters::GetInt", f"{type(e).__name__} - {e}")
      return None


class GetChannel(commands.Converter):
  async def convert(self, ctx: commands.Context, channel_id: str) -> discord.TextChannel:
    """
    Search a channel in the current guild using its ID and returns it

    :param ctx: The current context
    :param channel_id: The Id of the channel to be found
    :return: The channel if found else None
    """
    try:
      channel_id = "".join([x for x in channel_id if x.isdigit()])
      channel_id = int(channel_id)
      channel = ctx.guild.get_channel(channel_id)
      return channel
    except Exception as e:
      logger("Converters::GetChannel", f"{type(e).__name__} - {e}")
      return None