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


  async def __add_megapin(self, msg_id: int, channel_id: int, span: int, preview: str, guild_id: int) -> str:
    """
    Intern method to add a megapin in the database.
    Return the text to send (success or error).
    """
    try:
      sql = "INSERT INTO megapin_table (message_id, channel_id, span, preview, guild_id, last_pin) VALUES (?, ?, ?, ?, ?, ?) ;"
      now = int(datetime.now().timestamp())
      database.execute_order(sql, [msg_id, channel_id, span, preview, guild_id, now])
      return Utils.get_text(guild_id,  "megapin_add_success")
    except Exception as e:
      logger("megapin::__add_megapin", f"{type(e).__name__} - {e}")
      return Utils.get_text(guild_id, 'error_database_writing')



  @commands.group(invoke_without_command=True)
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded', 'authorized'])
  async def megapin(self, ctx: commands.Context, span: int):
    """
    megapin <span>
    Create a megapin in the current channel with span <span>.
    """
    if span < 1:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_span_invalid"))
      return

    ask_message = await ctx.send(Utils.get_text(ctx.guild.id, "megapin_ask_message"))
    response = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    await Utils.delete_messages(ask_message, response)
    msg = await ctx.channel.send(response.content)

    preview = msg.content[:30] if len(msg.content) < 30 else msg.content
    to_send = await self.__add_megapin(msg.id, ctx.channel.id, span, preview, ctx.guild.id)
    await ctx.send(to_send)



  @megapin.command(name='copy')
  async def copy(self, ctx: commands.Context, msg: discord.Message, span: int):
    """
    megapin copy <ID> <span>
    Create a megapin in the current channel.
    Copy megapin content from message <ID>.
    Message <ID> must be in the current channel.
    """
    if span < 1:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_span_invalid"))
      return

    new_msg = await ctx.send(msg.content)
    preview = new_msg.content[:30] if len(new_msg.content) < 30 else new_msg.content
    to_send = await self.__add_megapin(new_msg.id, ctx.channel.id, span, preview, ctx.guild.id)
    await ctx.send(to_send)



  @megapin.command()
  async def list(self, ctx: commands.Context):
    """
    megapin list
    List the existing megapins.
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
  async def delete(self, ctx: commands.Context, id: int):
    """
    megapin delete <ID>
    Delete a megapin.
    <ID> is the megapin last message's ID (use `megapin list`)
    """
    sql = "DELETE FROM megapin_table WHERE message_id=? AND guild_id=? ;"
    try:
      database.execute_order(sql, [id, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_delete_success"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::megapin_delete", f"{type(e).__name__} - {e}")



  @megapin.group(invoke_without_command=True)
  async def edit(self, ctx: commands.Context):
    """
    !megapin edit
    Does nothing except printing the valid subcommands.
    """
    await ctx.send(Utils.get_text(ctx.guild.id, "megapin_edit_subcommand").format(ctx.prefix))



  @edit.command(name='channel')
  async def edit_channel(self, ctx: commands.Context, msg_id: int, new_channel: discord.TextChannel):
    """
    megapin edit channel <ID> <new_channel>
    Edit a megapin's channel.
    <ID> is the megapin last message's ID (use `megapin list`).
    <new_channel> is the new channel for the megapin.
    """
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
  async def edit_span(self, ctx: commands.Context, msg_id: int, new_span: int):
    """
    megapin edit span <ID> <new_span>
    Edit a megapin's span
    <ID> is the megapin last message's ID (use `megapin list`).
    <new_span> is the new span for the megapin.
    """
    if new_span < 1:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_span_invalid"))
      return

    sql = "UPDATE megapin_table SET span=? WHERE message_id=? AND guild_id=? ;"
    try:
      database.execute_order(sql, [new_span, msg_id, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_edit_success"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::megapin_edit_span", f"{type(e).__name__} - {e}")



  @megapin.group(invoke_without_command=True)
  async def remote(self, ctx: commands.Context, channel: discord.TextChannel, span: int):
    """
    megapin remote <channel> <span>
    Create a megapin in the channel <channel> with span <span>.
    """
    if span < 1:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_span_invalid"))
      return

    ask_message = await ctx.send(Utils.get_text(ctx.guild.id, "megapin_ask_message"))
    response = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    await Utils.delete_messages(ask_message, response)
    msg = await channel.send(response.content)

    preview = msg.content[:30] if len(msg.content) < 30 else msg.content
    to_send = await self.__add_megapin(msg.id, channel.id, span, preview, ctx.guild.id)
    await ctx.send(to_send)



  @remote.command(name='copy')
  async def remote_copy(self, ctx: commands.Context, channel: discord.TextChannel, msg_id: int, span: int):
    """
    megapin remote copy <channel> <ID> <span>
    Create a megapin in the channel <channel> with span <span>.
    Copy megapin content from message <ID>.
    Message <ID> must be in the current channel OR channel <channel>.
    """
    if span < 1:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_span_invalid"))
      return

    try:
      msg = await channel.fetch_message(msg_id)
    except discord.NotFound:
      try:
        msg = await ctx.channel.fetch_message(msg_id)
      except discord.NotFound:
        await ctx.send(Utils.get_text(ctx.guild.id, "megapin_remote_copy_message_invalid"))
        return

    new_msg = await channel.send(msg.content)
    preview = new_msg.content[:30] if len(new_msg.content) < 30 else new_msg.content
    to_send = await self.__add_megapin(new_msg.id, channel.id, span, preview, ctx.guild.id)
    await ctx.send(to_send)