import discord
from discord.ext import commands
from datetime import datetime
from datetime import timezone
from ..logs import Logs
from database import Database
from Utils import Utils
import random
import time
import math


class Config(commands.Cog):

  """
  Config:
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
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    if not role:
      await ctx.send ("Le paramètre `<role>` est obligatoire.")
      return
    error                    = False
    try:
      insert                 = (  "insert into config_role"+
                                  " (`role_id`, `permission`, `guild_id`) "+
                                  "values "+
                                 f" ('{role.id}', 2, '{guild_id}') ;"
                               )
      self.db.execute_order (insert)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
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
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    if not role:
      await ctx.send ("Le paramètre `<role>` est obligatoire.")
      return
    error                    = False
    try:
      delete                 = (  "delete from config_role"+
                                  " where "+
                                 f" `role_id`='{role.id}' and `permission`=2 and"+
                                 f" `guild_id` = '{guild_id}' ;"+
                                  ""
                               )
      self.db.execute_order (delete)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
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
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    if not prefix:
      await ctx.send ("Le paramètre `<prefix>` est obligatoire.")
      return
    error                    = False
    try:
      insert                 = (  "insert into config_prefix"+
                                  " (`prefix`, `guild_id`) "+
                                  "values "+
                                 f" (?, '{guild_id}') ;"
                               )
      self.db.execute_order (insert, [prefix])
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
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
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    if not prefix:
      await ctx.send ("Le paramètre `<prefix>` est obligatoire.")
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
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('config_log', author, ctx.message, error)
