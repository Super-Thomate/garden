import discord
from discord.ext import commands

import Utils
import botconfig
import database
from ..logs import Logs
from core import logger


class Configuration(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  @commands.command(name='addrolemoderateur', aliases=['addrolemodo', 'arm'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def add_role_modo(self, ctx, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not role:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<rôle>'))
      return
    error = False
    try:
      insert = ("insert into config_role" +
                " (`role_id`, `permission`, `guild_id`) " +
                "values " +
                f" ('{role.id}', 1, '{guild_id}') ;"
                )
      database.execute_order(insert)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::add_role_modo", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removerolemoderateur', aliases=['removerolemodo', 'rrm'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def remove_role_modo(self, ctx, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not role:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<role>**'))
      return
    error = False
    try:
      delete = ("delete from config_role" +
                " where " +
                f" `role_id`='{role.id}' and `permission`=1 and" +
                f" `guild_id` = '{guild_id}' ;" +
                ""
                )
      database.execute_order(delete)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::remove_role_modo", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='addprefix')
  @Utils.require(required=['authorized', 'not_banned'])
  async def add_prefix(self, ctx, prefix: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not prefix:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<prefix>**'))
      return
    error = False
    try:
      insert = ("insert into config_prefix" +
                " (`prefix`, `guild_id`) " +
                "values " +
                f" (?, '{guild_id}') ;"
                )
      database.execute_order(insert, [prefix])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::add_prefix", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removeprefix')
  @Utils.require(required=['authorized', 'not_banned'])
  async def remove_prefix(self, ctx, prefix: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not prefix:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<role>**'))
      return
    error = False
    try:
      delete = ("delete from config_prefix" +
                " where " +
                f" `role_id`=?" +
                " and " +
                f" `guild_id` = '{guild_id}' ;" +
                ""
                )
      database.execute_order(delete, [prefix])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::remove_prefix", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='seturl')
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_url(self, ctx, type_url: str = None, url: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not type_url:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<type_url>**'))
      return
    if not url:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<url>**'))
      return
    error = False
    try:
      select = ("select url from config_url" +
                " where " +
                f" `type_url`=? and `guild_id`='{guild_id}'" +
                ""
                )
      fetched = database.fetch_one_line(select, [type_url])
      if fetched:
        order = ("update config_url" +
                 " set `url`=? " +
                 " where " +
                 f" `type_url`=? and `guild_id`='{guild_id}'" +
                 ""
                 )
      else:
        order = ("insert into config_url" +
                 " (`url`, `type_url`, `guild_id`) " +
                 " values " +
                 f" (?, ?, '{guild_id}')" +
                 ""
                 )
      database.execute_order(order, [url, type_url])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::set_url", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removeurl')
  @Utils.require(required=['authorized', 'not_banned'])
  async def remove_url(self, ctx, type_url: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not type_url:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<type_url>**'))
      return
    error = False
    try:
      delete = ("delete from config_url" +
                " where " +
                f" `type_url`=? and `guild_id`='{guild_id}'" +
                ""
                )
      database.execute_order(delete, [type_url])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::remove_url", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='setdelay')
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_delay(self, ctx, type_delay: str = None, delay: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not type_delay:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<type_delay>**'))
      return
    if not delay:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<delay>**'))
      return
    error = False
    try:
      if not delay.isnumeric():
        delay = Utils.parse_time(delay)
      select = ("select delay from config_delay" +
                " where " +
                f" `type_delay`=? and `guild_id`='{guild_id}'" +
                ""
                )
      fetched = database.fetch_one_line(select, [type_delay])
      if fetched:
        order = ("update config_delay" +
                 " set `delay`=? " +
                 " where " +
                 f" `type_delay`=? and `guild_id`='{guild_id}'" +
                 ""
                 )
      else:
        order = ("insert into config_delay" +
                 " (`delay`, `type_delay`, `guild_id`) " +
                 " values " +
                 f" (?, ?, '{guild_id}')" +
                 ""
                 )
      database.execute_order(order, [delay, type_delay])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::set_delay", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removedelay')
  @Utils.require(required=['authorized', 'not_banned'])
  async def remove_delay(self, ctx, type_delay: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not type_delay:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<type_delay>**'))
      return
    error = False
    try:
      delete = ("delete from config_delay" +
                " where " +
                f" `type_delay`=? and `guild_id`='{guild_id}'" +
                ""
                )
      database.execute_order(delete, [type_delay])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::remove_delay", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='setdo')
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_do(self, ctx, type_do: str = None, do: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not type_do:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<type_do>**'))
      return
    if not do:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<do>**'))
      return
    error = False
    try:
      select = ("select do from config_do" +
                " where " +
                f" `type_do`=? and `guild_id`='{guild_id}'" +
                ""
                )
      fetched = database.fetch_one_line(select, [type_do])
      if fetched:
        order = ("update config_do" +
                 " set `do`=? " +
                 " where " +
                 f" `type_do`=? and `guild_id`='{guild_id}'" +
                 ""
                 )
      else:
        order = ("insert into config_do" +
                 " (`do`, `type_do`, `guild_id`) " +
                 " values " +
                 f" (?, ?, '{guild_id}')" +
                 ""
                 )
      database.execute_order(order, [do, type_do])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::set_do", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removedo')
  @Utils.require(required=['authorized', 'not_banned'])
  async def remove_do(self, ctx, type_do: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not type_do:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('**<type_do>**'))
      return
    error = False
    try:
      delete = ("delete from config_do" +
                " where " +
                f" `type_do`=? and `guild_id`='{guild_id}'" +
                ""
                )
      database.execute_order(delete, [type_do])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("configuration::remove_do", f" {type(e).__name__} - {e}")
      error = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='setlanguage')
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_language(self, ctx, lang_code: str):
    guild_id = ctx.guild.id
    lang_code = lang_code.lower()
    if lang_code not in botconfig.config["languages"]:
      await ctx.message.add_reaction('❌')
      await ctx.send(Utils.get_text(ctx.guild.id, "error_unknown_language").format(lang_code))
      return

    sql = f"SELECT language_code FROM config_lang WHERE guild_id='{guild_id}' ;"
    already_set = database.fetch_one_line(sql)
    if already_set:
      sql = f"UPDATE config_lang set language_code='{lang_code}' WHERE guild_id='{guild_id}' ;"
    else:
      sql = f"INSERT INTO config_lang VALUES ('{lang_code}', '{guild_id}') ;"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger ("configuration::set_language", f"{type(e).__name__} - {e}")
    botconfig.__language__[str(guild_id)] = lang_code
    await ctx.send(Utils.get_text(ctx.guild.id, 'language_updated'))
