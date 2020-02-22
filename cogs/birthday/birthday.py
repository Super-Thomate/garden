import datetime

import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs
from core import logger

class Birthday(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  def validate_date(self, date):
    if date in ('29/02', '29/2'):
      return '29/02'
    try:
      date_object = datetime.datetime.strptime(date, "%d/%m")
      return '{:02d}'.format(date_object.day) + '/' + '{:02d}'.format(date_object.month) # Format days into double digits
    except ValueError:
      return None

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
    if data and data [0]:
      already_registered = await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_already_registered'))
      await Utils.delete_messages(already_registered, ctx.message)
      return
    if not date:  # user did not write date after !bd
      one_line = False
      ask = await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_ask_user'))
      response = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author.id == member_id)
      date = response.content
      await Utils.delete_messages(ask, response)
    old_date = date
    date = self.validate_date(date)
    if not date:
      invalid = await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_format_invalid'))
      await Utils.delete_messages(invalid, ctx.message)
      # Log command
      ctx.message.content += f"\n{old_date}" if one_line is False else ""
      await self.logger.log('birthday_log', ctx.author, ctx.message, True)
    else:
      sql = f"INSERT INTO birthday_user VALUES ('{member_id}', '{guild_id}', '{date}', '') ;"
      try:
        database.execute_order(sql, [])
      except Exception as e:
        error = True
        await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
        logger ("birthday::set_birthday", f"{type(e).__name__} - {e}")
      accepted = await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_registered').format(ctx.author.display_name))
      await Utils.delete_messages(accepted, ctx.message)
      # Log command
      ctx.message.content += f"\n{date}" if one_line is False else ""
      await self.logger.log('birthday_log', ctx.author, ctx.message, error)

  @commands.command(name="setbirthdaytime", aliases=['sbt'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_birthday_time(self, ctx: commands.Context, time: str = None):
    if not time:
      sql = "SELECT time FROM birthday_time WHERE guild_id=? ;"
      response = database.fetch_one_line(sql, [ctx.guild.id])
      if response:
        await ctx.send(Utils.get_text(ctx.guild.id, "birthday_current_time").format(response[0]))
      else:
        await ctx.send(Utils.get_text(ctx.guild.id, "birthday_time_not_set"))
      return
    try:
      time = int(time)
      if not (0 <= time < 24):
        raise ValueError
    except ValueError as e:
      await ctx.send(Utils.get_text(ctx.guild.id, "birthday_time_invalid"))
      return
    # Check if time is already set in this guild
    sql = "SELECT time FROM birthday_time WHERE guild_id=? ;"
    response = database.fetch_one_line(sql, [ctx.guild.id])
    if response:
      sql = "UPDATE birthday_time SET time=? WHERE guild_id=? ;"
    else:
      sql = "INSERT INTO birthday_time VALUES (?, ?) ;"
    try:
      database.execute_order (sql, [time, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id, "birthday_time_registered").format(time))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger ("birthday::set_birthday_channel", f"{type(e).__name__} - {e}")



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
      sql = f"INSERT INTO birthday_channel VALUES ('{channel_id}', '{guild_id}') ;"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger ("birthday::set_birthday_channel", f"{type(e).__name__} - {e}")

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
    sql = f"DELETE FROM birthday_user WHERE user_id='{member.id}' and guild_id={ctx.guild.id} ;"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      error = True
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger ("birthday::reset_birthday", f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_reset').format(member.mention))
    await self.logger.log('birthday_log', ctx.author, ctx.message, error)

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
      sql = f"UPDATE birthday_message SET message=? WHERE guild_id='{guild_id}';"
    try:
      database.execute_order(sql, [message])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("birthday::set_birthday_message", f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.channel.send(Utils.get_text(ctx.guild.id, 'display_new_message').format(message))