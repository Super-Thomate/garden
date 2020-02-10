import datetime

import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs


class Birthday(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  def validate_date(self, date):
    if date is '29/02':
      return True
    try:
      return datetime.datetime.strptime(date, '%d/%m')
    except ValueError:
     return False

  @commands.command(name="setbirthday", aliases=['bd'])
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def set_birthday(self, ctx, date: str = None):
    """Save user's birthday in database."""
    guild_id = ctx.message.guild.id
    member_id = ctx.author.id
    error = False
    one_line = True
    sql = f"SELECT user_id FROM birthday_user WHERE user_id=? and guild_id=? ;"
    data = database.fetch_one_line(sql, [member_id, guild_id])
    if data is not None:
      already_registered = await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_already_registered'))
      await Utils.delete_messages(already_registered, ctx.message)
      return
    if not date:  # user did not write date after !bd
      one_line = False
      ask = await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_ask_user'))
      response = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author.id == member_id)
      date = response.content
      await Utils.delete_messages(ask, response)
    valid = self.validate_date(date)
    if not valid:
      invalid = await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_format_invalid'))
      await Utils.delete_messages(invalid, ctx.message)
      # Log command
      ctx.message.content += f"\n{date}" if one_line is False else ""
      await self.logger.log('birthday_log', ctx.author, ctx.message, True)
    else:
      sql = f"INSERT INTO birthday_user VALUES (?, ?, ?, ?) ;"
      error = not database.write_data(ctx, sql, [member_id, guild_id, date, '']) # Function returns sucess, so error == not success
      accepted = await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_registered').format(ctx.author.display_name))
      await Utils.delete_messages(accepted, ctx.message)
      # Log command
      ctx.message.content += f"\n{date}" if one_line is False else ""
      await self.logger.log('birthday_log', ctx.author, ctx.message, error)

  @commands.command(name="setbirthdaychannel", aliases=['sbc'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_birthday_channel(self, ctx, channel: discord.TextChannel = None):
    """Save channel where birthday will be wished. Param: channel ID"""
    guild_id = ctx.guild.id
    channel = channel or ctx.channel
    channel_id = channel.id

    sql = f"SELECT channel_id FROM birthday_channel WHERE guild_id=? ;"
    is_already_set = database.fetch_one_line(sql, [guild_id])

    if is_already_set:
      sql = f"UPDATE birthday_channel SET channel_id=? WHERE guild_id=? ;"
    else:
      sql = f"INSERT INTO birthday_channel VALUES (?, ?) ;"
    success = database.write_data(ctx, sql, [channel, guild_id])
    if success:
      await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_channel_set').format(f'<#{channel_id}>'))

  @commands.command(name='resetbirthday', aliases=['rb'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def reset_birthday(self, ctx, member: discord.Member = None):
    guild_id = ctx.guild.id
    error = False
    member = member or ctx.author
    if member is None:
      await ctx.send(Utils.get_text(guild_id, "error_no_parameter").format("<member>"))
      await ctx.message.add_reaction('❌')
      await self.logger.log('birthday_log', ctx.author, ctx.message, True)
      return
    sql = "SELECT user_id FROM birthday_user WHERE user_id=? and guild_id=? ;"
    member_in_db = database.fetch_one_line(sql, [member.id, guild_id])
    if not member_in_db:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_user_not_found").format(member.mention, 'birthday_user'))
      return
    sql = "DELETE FROM birthday_user WHERE user_id=? and guild_id=? ;"
    error = not database.write_data(ctx, sql, [member.id, guild_id])
    if error:
      await self.logger.log('birthday_log', ctx.author, ctx.message, error)
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_reset').format(member.mention))

  @commands.command(name='setbirthdaymessage', aliases=['birthdaymessage', 'sbm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_birthday_message(self, ctx):
    guild_id = ctx.message.guild.id
    member = ctx.author
    await ctx.send(Utils.get_text(ctx.guild.id, "birthday_new_message"))
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    message = msg.content
    sql = "select message from birthday_message where guild_id=? ;"
    prev_birthday_message = database.fetch_one_line(sql, [guild_id])
    if not prev_birthday_message:
      sql = f"INSERT INTO birthday_message VALUES (?, ?) ;"
    else:
      sql = f"UPDATE birthday_message SET message=? WHERE guild_id=? ;"
    success = database.write_data(ctx, sql, [message, guild_id])
    if success:
      await ctx.channel.send(Utils.get_text(ctx.guild.id, 'display_new_message').format(message))
