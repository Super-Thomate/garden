import discord
from discord.ext import commands
import botconfig
from datetime import datetime
from datetime import timezone
from ..logs import Logs
from database import Database
from Utils import Utils
import random
import time
import math


class Configuration(commands.Cog):

  """
  Configuration:
  "283243816448819200":
  {          "roles": [   580062847900450867
                        , 283247966490460160
                        , 283245747694993410
                        , 507978584342659082
                      ]
  ,       "prefixes": [   "!"
                        , "?"
                        , "-"
                      ]
  ,     "create_url": {   "invitation":"https://admin.realms-of-fantasy.net/bot.php"
                        , "gallery":"https://admin.realms-of-fantasy.net/bot-AR.php?"
                      }
  ,   "invite_delay": "6 months"
  ,      "do_invite": 1
  ,       "do_token": 0
  , "nickname_delay": "1 week"
  }
  """
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.command(name='addrolemoderateur', aliases=['addrolemodo', 'arm'])
  async def add_role_modo (self, ctx, role: discord.Role = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not role:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<rôle>'))
      return
    error                    = False
    try:
      insert                 = (  "insert into config_role"+
                                  " (`role_id`, `permission`, `guild_id`) "+
                                  "values "+
                                 f" ('{role.id}', 1, '{guild_id}') ;"
                               )
      self.db.execute_order (insert)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removerolemoderateur', aliases=['removerolemodo', 'rrm'])
  async def remove_role_modo (self, ctx, role: discord.Role = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not role:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<role>**'))
      return
    error                    = False
    try:
      delete                 = (  "delete from config_role"+
                                  " where "+
                                 f" `role_id`='{role.id}' and `permission`=1 and"+
                                 f" `guild_id` = '{guild_id}' ;"+
                                  ""
                               )
      self.db.execute_order (delete)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='addprefix')
  async def add_prefix (self, ctx, prefix: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not prefix:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<prefix>**'))
      return
    error                    = False
    try:
      insert                 = (  "insert into config_prefix"+
                                  " (`prefix`, `guild_id`) "+
                                  "values "+
                                 f" (?, '{guild_id}') ;"
                               )
      self.db.execute_order (insert, [prefix])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removeprefix')
  async def remove_prefix (self, ctx, prefix: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not prefix:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<role>**'))
      return
    error                    = False
    try:
      delete                 = (  "delete from config_prefix"+
                                  " where "+
                                 f" `role_id`=?"+
                                  " and "+
                                 f" `guild_id` = '{guild_id}' ;"+
                                  ""
                               )
      self.db.execute_order (delete, [prefix])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='seturl')
  async def set_url (self, ctx, type_url: str = None, url: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not type_url:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<type_url>**'))
      return
    if not url:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<url>**'))
      return
    error                    = False
    try:
      select                 = (  "select url from config_url"+
                                  " where "+
                                 f" `type_url`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      fetched                = self.db.fetch_one_line (select, [type_url])
      if fetched:
        order                = (  "update config_url"+
                                  " set `url`=? "+
                                  " where "+
                                 f" `type_url`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      else:
        order                = (  "insert into config_url"+
                                  " (`url`, `type_url`, `guild_id`) "+
                                  " values "+
                                 f" (?, ?, '{guild_id}')"+
                                  ""
                               )
      self.db.execute_order (order, [url, type_url])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removeurl')
  async def remove_url (self, ctx, type_url: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not type_url:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<type_url>**'))
      return
    error                    = False
    try:
      delete                 = (  "delete from config_url"+
                                  " where "+
                                 f" `type_url`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      self.db.execute_order (delete, [type_url])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='setdelay')
  async def set_delay (self, ctx, type_delay: str = None, delay: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not type_delay:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<type_delay>**'))
      return
    if not delay:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<delay>**'))
      return
    error                    = False
    try:
      if not delay.isnumeric():
        delay                = self.utils.parse_time(delay)
      select                 = (  "select delay from config_delay"+
                                  " where "+
                                 f" `type_delay`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      fetched                = self.db.fetch_one_line (select, [type_delay])
      if fetched:
        order                = (  "update config_delay"+
                                  " set `delay`=? "+
                                  " where "+
                                 f" `type_delay`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      else:
        order                = (  "insert into config_delay"+
                                  " (`delay`, `type_delay`, `guild_id`) "+
                                  " values "+
                                 f" (?, ?, '{guild_id}')"+
                                  ""
                               )
      self.db.execute_order (order, [delay, type_delay])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removedelay')
  async def remove_delay (self, ctx, type_delay: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not type_delay:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<type_delay>**'))
      return
    error                    = False
    try:
      delete                 = (  "delete from config_delay"+
                                  " where "+
                                 f" `type_delay`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      self.db.execute_order (delete, [type_delay])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='setdo')
  async def set_do (self, ctx, type_do: str = None, do: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not type_do:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<type_do>**'))
      return
    if not do:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<do>**'))
      return
    error                    = False
    try:
      select                 = (  "select do from config_do"+
                                  " where "+
                                 f" `type_do`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      fetched                = self.db.fetch_one_line (select, [type_do])
      if fetched:
        order                = (  "update config_do"+
                                  " set `do`=? "+
                                  " where "+
                                 f" `type_do`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      else:
        order                = (  "insert into config_do"+
                                  " (`do`, `type_do`, `guild_id`) "+
                                  " values "+
                                 f" (?, ?, '{guild_id}')"+
                                  ""
                               )
      self.db.execute_order (order, [do, type_do])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='removedo')
  async def remove_do (self, ctx, type_do: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not type_do:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('**<type_do>**'))
      return
    error                    = False
    try:
      delete                 = (  "delete from config_do"+
                                  " where "+
                                 f" `type_do`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      self.db.execute_order (delete, [type_do])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.command(name='setlanguage')
  async def set_language(self, ctx, lang_code: str):
    guild_id = ctx.guild.id
    lang_code = lang_code.lower()
    if not self.utils.is_authorized (ctx.author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if lang_code not in botconfig.config["languages"]:
      await ctx.message.add_reaction('❌')
      await ctx.send(self.utils.get_text(ctx.guild.id, "unknown_language_code").format(lang_code))
      return

    sql = f"SELECT language_code FROM config_lang WHERE guild_id='{guild_id}' ;"
    already_set = self.db.fetch_one_line(sql)
    if already_set:
      sql = f"UPDATE config_lang set language_code='{lang_code}' WHERE guild_id='{guild_id}' ;"
    else:
      sql = f"INSERT INTO config_lang VALUES ('{lang_code}', '{guild_id}') ;"
    try:
      self.db.execute_order(sql, [])
    except Exception as e:
      await ctx.send(self.utils.get_text(ctx.guild.id, 'database_writing_error'))
      print(f"{type(e).__name__} - {e}")

    await ctx.send(self.utils.get_text(ctx.guild.id, 'language_updated'))



