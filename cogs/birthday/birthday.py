import discord
from discord.ext import commands
from database import Database
from Utils import Utils
from ..logs import Logs
import datetime


class Birthday(commands.Cog):
  """
  set_birthday():
  set_birthday_channel():
  wish_birthday:
  """
  def __init__(self, bot):
    self.bot = bot
    self.db = Database()
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.language_code = 'fr'

  @commands.command(name="setbirthday", aliases=['sb', 'bd', 'anniversaire', 'birthday'])
  async def set_birthday(self, ctx):
    """Save user's birthday in database. Format DD/MM"""
    guild_id = ctx.message.guild.id
    member_id = ctx.author.id
    error = False

    if self.utils.is_banned(ctx.command, ctx.author, guild_id):
      await ctx.send(self.utils.get_text(self.language_code, 'user_unauthorized_use_command'))
      await ctx.message.add_reaction('❌')
      return

    sql = f"SELECT user_id FROM birthday_user WHERE user_id='{member_id}'"
    data = self.db.fetch_one_line(sql)
    if data is not None:
      await ctx.send(self.utils.get_text(self.language_code, 'user_already_registered_birthday'))
      await ctx.message.add_reaction('❌')
      return

    await ctx.send(self.utils.get_text(self.language_code, 'ask_user_register_birthday'))
    response = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author.id == member_id)
    birthday = response.content

    try:
      valid = True if birthday == "29/02" else datetime.datetime.strptime(birthday, '%d/%m')
    except ValueError:
      await ctx.send(self.utils.get_text(self.language_code, 'birthday_format_invalid'))
      await response.add_reaction('❌')
      ctx.message.content += '\n' + birthday
      await self.logger.log('birthday_log', ctx.author, ctx.message, True)
      return

    sql = f"SELECT user_birthday FROM birthday_user WHERE user_id='{member_id}'"
    user_already_registered = self.db.fetch_one_line(sql)
    if user_already_registered:
      sql = f"UPDATE birthday_user set user_birthday='{birthday}' where user_id='{member_id}'"
    else:
      sql = f"INSERT INTO birthday_user VALUES ('{member_id}', '{guild_id}', '{birthday}', '') ;"
    try:
      self.db.execute_order(sql, [])
    except Exception as e:
      error = True
      await ctx.send(self.utils.get_text(self.language_code, 'database_writing_error'))
      print(f"{type(e).__name__} - {e}")

    await ctx.send(self.utils.get_text(self.language_code, 'user_birthday_registered').format(ctx.author.display_name))
    await response.add_reaction('✅')
    # Log command
    ctx.message.content += '\n' + birthday
    await self.logger.log('birthday_log', ctx.author, ctx.message, error)

  @commands.command(name="setbirthdaychannel", aliases=['sbc'])
  async def set_birthday_channel(self, ctx, channel_id: str = None):
    """Save channel where birthday will be wished. Param: channel ID"""
    guild_id = ctx.guild.id
    channel_id = channel_id or ctx.channel.id

    if not self.utils.is_authorized(ctx.author, guild_id):
      print("Missing permissions")
      return
    if self.utils.is_banned(ctx.command, ctx.author, guild_id):
      await ctx.send(self.utils.get_text(self.language_code, 'user_unauthorized_use_command'))
      await ctx.message.add_reaction('❌')
      return

    sql = f"SELECT channel_id FROM birthday_channel WHERE guild_id='{guild_id}'"
    is_already_set = self.db.fetch_one_line(sql)

    if is_already_set:
      sql = f"UPDATE birthday_channel SET channel_id='{channel_id}' WHERE guild_id='{guild_id}'"
    else:
      sql = f"INSERT INTO birthday_channel VALUES ('{channel_id}', '{guild_id}') ;"
    try:
      self.db.execute_order(sql, [])
    except Exception as e:
      await ctx.send(self.utils.get_text(self.language_code, 'database_writing_error'))
      print(f"{type(e).__name__} - {e}")

    await ctx.send(self.utils.get_text(self.language_code, 'birthday_channel_set').format(channel_id))

  @commands.command(name='resetbirthday', aliases=['rb'])
  async def reset_birthday(self, ctx, member_id: str = None):
    guild_id = ctx.guild.id
    error = False
    if not self.utils.is_authorized(ctx.author, guild_id):
      print("Missing permissions")
      return
    if self.utils.is_banned(ctx.command, ctx.author, guild_id):
      await ctx.send(self.utils.get_text(self.language_code, 'user_unauthorized_use_command'))
      await ctx.message.add_reaction('❌')
      return
    if member_id is None:
      await ctx.send(self.utils.get_text(self.language_code, 'parameter_is_mandatory').format("memberID"))
      await ctx.message.add_reaction('❌')
      await self.logger.log('birthday_log', ctx.author, ctx.message, True)
      return

    sql = f"DELETE FROM birthday_user WHERE user_id='{member_id}'"
    try:
      self.db.execute_order(sql, [])
    except Exception as e:
      error = True
      await ctx.send(self.utils.get_text(self.language_code, 'database_writing_error'))
      print(f"{type(e).__name__} - {e}")

    await ctx.send(self.utils.get_text(self.language_code, 'user_birthday_reset').format(member_id))
    await self.logger.log('birthday_log', ctx.author, ctx.message, error)

  @commands.command(name='setbirthdaymessage', aliases=['birthdaymessage', 'sbm'])
  async def set_birthday_message(self, ctx):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized(member, guild_id):
      print("Missing permissions")
      return
    if self.utils.is_banned(ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await ctx.send(self.utils.get_text(self.language_code, "ask_new_birthday_message"))
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    message = msg.content
    sql = f"select message from birthday_message where guild_id='{guild_id}';"
    prev_birthday_message = self.db.fetch_one_line(sql)
    if not prev_birthday_message:
      sql = f"INSERT INTO birthday_message VALUES (?, '{guild_id}') ;"
    else:
      sql = f"UPDATE birthday_message SET message=? WHERE guild_id='{guild_id}';"
    print(sql)
    try:
      self.db.execute_order(sql, [message])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.channel.send(self.utils.get_text(self.language_code, 'display_new_message').format(message))