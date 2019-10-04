import datetime
from discord.ext import commands
import discord
import Utils
import database
from ..logs import Logs


class Birthday(commands.Cog):
  """
  set_birthday():
  set_birthday_channel():
  wish_birthday:
  """
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  def validate_date(self, date):
    if date in ('29/02', '29/2', '29.02', '29.2', '29-02', '29-2'):
      return True
    for frmt in ("%d/%m", "%d.%m", "%d-%m"):
      try:
        return datetime.datetime.strptime(date, frmt)
      except ValueError:
        continue
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
    sql = f"SELECT user_id FROM birthday_user WHERE user_id='{member_id}' and guild_id='{guild_id}' ;"
    data = database.fetch_one_line(sql)
    if data is not None:
      already_registered = await ctx.send(Utils.get_text(ctx.guild.id, 'user_already_registered_birthday'))
      await Utils.delete_messages(already_registered, ctx.message)
      return
    if not date: # user did not write date after !bd
      one_line = False
      ask = await ctx.send(Utils.get_text(ctx.guild.id, 'ask_user_register_birthday'))
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
      sql = f"INSERT INTO birthday_user VALUES ('{member_id}', '{guild_id}', '{date}', '') ;"
      try:
        database.execute_order(sql, [])
      except Exception as e:
        error = True
        await ctx.send(Utils.get_text(ctx.guild.id, 'database_writing_error'))
        print(f"{type(e).__name__} - {e}")
      accepted = await ctx.send(Utils.get_text(ctx.guild.id, 'user_birthday_registered').format(ctx.author.display_name))
      await Utils.delete_messages(accepted, ctx.message)
      # Log command
      ctx.message.content += f"\n{date}" if one_line is False else ""
      await self.logger.log('birthday_log', ctx.author, ctx.message, error)

  @commands.command(name="setbirthdaychannel", aliases=['sbc'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_birthday_channel(self, ctx, channel: discord.TextChannel = None):
    """Save channel where birthday will be wished. Param: channel ID"""
    guild_id = ctx.guild.id
    channel                  = channel or ctx.channel
    channel_id               = channel.id

    sql = f"SELECT channel_id FROM birthday_channel WHERE guild_id='{guild_id}'"
    is_already_set = database.fetch_one_line(sql)

    if is_already_set:
      sql = f"UPDATE birthday_channel SET channel_id='{channel_id}' WHERE guild_id='{guild_id}'"
    else:
      sql = f"INSERT INTO birthday_channel VALUES ('{channel_id}', '{guild_id}') ;"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'database_writing_error'))
      print(f"{type(e).__name__} - {e}")

    await ctx.send(Utils.get_text(ctx.guild.id, 'birthday_channel_set').format(f'<#{channel_id}>'))

  @commands.command(name='resetbirthday', aliases=['rb'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def reset_birthday(self, ctx, member: discord.Member = None):
    guild_id = ctx.guild.id
    error = False
    member = member or ctx.author
    if member is None:
      await ctx.send("Le paramètre <member> est obligatoire.")
      await ctx.message.add_reaction('❌')
      await self.logger.log('birthday_log', ctx.author, ctx.message, True)
      return
    sql = f"SELECT user_id FROM birthday_user WHERE user_id={member.id} and guild_id={ctx.guild.id}"
    member_in_db = database.fetch_one_line(sql)
    if not member_in_db:
      await ctx.send(Utils.get_text(ctx.guild.id, "user_not_in_database").format(member.mention, 'birthday_user'))
      return
    sql = f"DELETE FROM birthday_user WHERE user_id='{member.id}' and guild_id={ctx.guild.id} ;"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      error = True
      await ctx.send(Utils.get_text(ctx.guild.id, 'database_writing_error'))
      print(f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, 'user_birthday_reset').format(member.mention))
    await self.logger.log('birthday_log', ctx.author, ctx.message, error)

  @commands.command(name='setbirthdaymessage', aliases=['birthdaymessage', 'sbm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_birthday_message(self, ctx):
    guild_id = ctx.message.guild.id
    member = ctx.author
    await ctx.send(Utils.get_text(ctx.guild.id, "ask_new_birthday_message"))
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    message = msg.content
    sql = f"select message from birthday_message where guild_id='{guild_id}';"
    prev_birthday_message = database.fetch_one_line(sql)
    if not prev_birthday_message:
      sql = f"INSERT INTO birthday_message VALUES (?, '{guild_id}') ;"
    else:
      sql = f"UPDATE birthday_message SET message=? WHERE guild_id='{guild_id}';"
    print(sql)
    try:
      database.execute_order(sql, [message])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.channel.send(Utils.get_text(ctx.guild.id, 'display_new_message').format(message))

  @commands.Cog.listener()
  async def on_command_error(self, ctx, exception):
    if not ctx.command:
      return
    if ctx.command.name in ['resetbirthday', 'setbirthdaychannel']:
      await ctx.channel.send(exception)