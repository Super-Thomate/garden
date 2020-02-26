from discord.ext import commands
from datetime import datetime
from core import logger
import Converters
import database
import discord
import Utils

class Megapin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  async def __add_megapin(self, msg_id, channel_id, span, preview, guild_id):
    try:
      sql = "INSERT INTO megapin_table (message_id, channel_id, span, preview, guild_id, last_pin) VALUES (?, ?, ?, ?, ?, ?) ;"
      now = int(datetime.now().timestamp())
      database.execute_order(sql, [msg_id, channel_id, span, preview, guild_id, now])
      return Utils.get_text(guild_id,  "megapin_add_success")
    except Exception as e:
      logger("megapin::__add_megapin", f"{type(e).__name__} - {e}")
      return Utils.get_text(guild_id, 'error_database_writing')


  class GetSpan(commands.Converter):
    async def convert(self, ctx: commands.Context, span: str) -> int:
      span = await Converters.GetInt.convert(self, ctx, span)
      if span < 1:
        await ctx.send(Utils.get_text(ctx.guild.id, "megapin_span_invalid"))
        return None
      return span


  @commands.group(invoke_without_command=True)
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded', 'authorized'])
  async def megapin(self, ctx: commands.Context, span: Converters.GetInt):
    """
    !megapin

    Send a user-defined message in the current channel regularly
    :param span: The span in minutes between every sending
    """
    if not span:
      return

    ask_message = await ctx.send(Utils.get_text(ctx.guild.id, "megapin_ask_message"))
    response = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    await Utils.delete_messages(ask_message, response)
    msg = await ctx.channel.send(response.content)

    preview = msg.content[:30] if len(msg.content) < 30 else msg.content
    to_send = await self.__add_megapin(msg.id, ctx.channel.id, span, preview, ctx.guild.id)
    await ctx.send(to_send)


  @megapin.command(name='copy')
  async def copy(self, ctx: commands.Context, msg: Converters.GetMessage, span: GetSpan):
    """
    !megapin copy

    Copy and send a message in the current channel regularly
    :param msg: The message to copy content from
    :param span: The span in minutes between every sending
    """
    if not span or not msg:
      return

    new_msg = await ctx.send(msg.content)
    preview = new_msg.content[:30] if len(new_msg.content) < 30 else new_msg.content
    to_send = await self.__add_megapin(new_msg.id, ctx.channel.id, span, preview, ctx.guild.id)
    await ctx.send(to_send)


  @megapin.command()
  async def list(self, ctx: commands.Context):
    """
    !megapin list

    List the existing megapins
    """
    sql = "SELECT message_id, channel_id, span, preview FROM megapin_table WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])

    embed = discord.Embed(colour=discord.Colour(0).from_rgb(176, 255, 176), title=Utils.get_text(ctx.guild.id, 'megapin_list'))
    for megapin in response:
      channel = ctx.guild.get_channel(int(megapin[1]))
      text = f"{megapin[0]} | {channel.mention} | {megapin[2]} minute(s) | {megapin[3]}"
      embed.add_field(name=Utils.get_text(ctx.guild.id, 'megapin_field'), value=text, inline=False)

    await ctx.send(content=None, embed=embed)


  @megapin.command()
  async def delete(self, ctx: commands.Context, id: Converters.GetInt):
    """
    !megapin delete

    Stop the megapin, the message won't be re-sent regurlarly
    :param id_str: The ID of the megapin's last message
    """
    if not id:
      return

    sql = "DELETE FROM megapin_table WHERE message_id=? AND guild_id=? ;"
    try:
      database.execute_order(sql, [id, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_delete_success"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::megapin_delete", f"{type(e).__name__} - {e}")


  @megapin.group(invoke_without_command=True)
  async def edit(self, ctx: commands.Context):
    await ctx.send(Utils.get_text(ctx.guild.id, "megapin_edit_subcommand"))


  @edit.command(name='channel')
  async def edit_channel(self, ctx: commands.Context, msg_id: Converters.GetInt, new_channel: Converters.GetChannel):
    """
    !megapin edit channel

    Edit a megapin's channel
    :param msg_id: The ID of the megapin's last message
    :param new_channel: The new channel where the megapin has to occurs
    """
    if not new_channel or not msg_id:
      return

    try:
      sql = "SELECT channel_id FROM megapin_table WHERE message_id=? AND guild_id=? ;"
      response = database.fetch_one_line(sql, [msg_id, ctx.guild.id])
      old_channel = ctx.guild.get_channel(int(response[0]))
      old_msg = await old_channel.fetch_message(msg_id)
    except Exception:
      ctx.send(Utils.get_text(ctx.guild.id, "megapin_error_old_message"))
      return

    msg = await new_channel.send(old_msg.content)
    sql = "UPDATE megapin_table SET message_id=?, channel_id=? WHERE message_id=? AND guild_id=? ;"
    try:
      database.execute_order(sql, [msg.id, new_channel.id, msg_id, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_edit_success"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::megapin_edit_channel", f"{type(e).__name__} - {e}")


  @edit.command(name='span')
  async def edit_span(self, ctx: commands.Context, msg_id: Converters.GetInt, span: GetSpan):
    """
    !megapin edit span

    Edit a megapin's span
    :param msg_id: The ID of the megapin's last message
    :param span: The new span
    """
    if not span:
      return

    sql = "UPDATE megapin_table SET span=? WHERE message_id=? AND guild_id=? ;"
    try:
      database.execute_order(sql, [span, msg_id, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_edit_success"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::megapin_edit_span", f"{type(e).__name__} - {e}")


  @megapin.group(invoke_without_command=True)
  async def remote(self, ctx: commands.Context, channel: Converters.GetChannel, span: GetSpan):
    """
    !megapin remote

    Send a user-defined message in the given channel regularly
    :param channel: The channel to send the message
    :param span: The span in minutes between every sending
    """
    if not channel or not span:
      return

    ask_message = await ctx.send(Utils.get_text(ctx.guild.id, "megapin_ask_message"))
    response = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    await Utils.delete_messages(ask_message, response)
    msg = await channel.send(response.content)

    preview = msg.content[:30] if len(msg.content) < 30 else msg.content
    to_send = await self.__add_megapin(msg.id, channel.id, span, preview, ctx.guild.id)
    await ctx.send(to_send)


  @remote.command(name='copy')
  async def remote_copy(self, ctx: commands.Context, channel: Converters.GetChannel, msg_id: Converters.GetInt, span: GetSpan):
    """
    !megapin remote copy

    Copy and send a message in the given channel regularly
    :param channel: The channel to send the message
    :param msg_id: The ID of the message to copy content from
    :param span: The span in minutes between every sending
    """
    if not channel or not msg_id or not span:
      return
    try:
      msg = await ctx.channel.fetch_message(msg_id)
    except discord.NotFound:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_remote_copy_message_invalid"))
      return

    new_msg = await channel.send(msg.content)
    preview = new_msg.content[:30] if len(new_msg.content) < 30 else new_msg.content
    to_send = await self.__add_megapin(new_msg.id, channel.id, span, preview, ctx.guild.id)
    await ctx.send(to_send)