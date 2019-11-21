
import os

from discord.ext import commands

import Utils
import database


class Loader(commands.Cog):
  def __init__(self, bot):
      self.bot = bot

  # Hidden means it won't show up on the default help.
  @commands.command(name='cogload', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_load_cog(self, ctx, *, cog: str):
    """
    Load a cog for Garden
    """
    cog                      = cog.lower()
    try:
      self.bot.load_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, "exception_error").format(type(e).__name__, e))
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, 'success'))

  @commands.command(name='cogunload', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_unload_cog(self, ctx, *, cog: str):
    """
    Unload a cog for Garden
    """
    cog                      = cog.lower()
    try:
      self.bot.unload_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, "exception_error").format(type(e).__name__, e))
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, 'success'))

  @commands.command(name='cogreload', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_reload_cog(self, ctx, *, cog: str):
    """
    Reload a cog for Garden
    """
    cog                      = cog.lower()
    try:
      self.bot.unload_extension(f'cogs.{cog}')
      self.bot.load_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, "exception_error").format(type(e).__name__, e))
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, 'success'))

  @commands.command(name='cogs', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def list_load(self, ctx):
    """
    Command which lists all loaded cogs
    """
    all_loaded = ""
    for name in self.bot.cogs.keys():
      all_loaded += f"- **{name}**\n"
    if not len (all_loaded):
      all_loaded = "**NONE**"
    try:
      await ctx.send (all_loaded)
    except Exception as e:
      print(f'{type(e).__name__} - {e}')
  

  @commands.command(name='load', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_load(self, ctx, *, cog: str):
    """
    Load cogs for this guild
    """
    author                   = ctx.author
    guild_id                 = ctx.guild.id
    if not cog:
      await ctx.message.add_reaction('❌')
      await ctx.send ("Paramètre <cog> obligatoire.")
      return
    cog                      = cog.lower()
    try:
      select                 = (   "select   status "
                                   "from     config_cog "+
                                   "where "+
                                   "cog=? "+
                                   " and "+
                                   "guild_id=? ;"+
                                   ""
                               )
      fetched                = database.fetch_one_line (select, [cog, guild_id])
      sql                    = ""
      if fetched:
        status               = fetched [0]
        if status == 0:
          sql                = "update config_cog set status=1 where cog=? and guild_id=? ;"
      else:
        sql                  = "insert into config_cog (`cog`, `guild_id`, `status`) values (?,?,1) ;"
      print (sql)
      if len(sql):
        database.execute_order (sql, [cog, guild_id])
    except Exception as e:
      await ctx.message.add_reaction('❌')
      print (f"{type(e).__name__} - {e}")
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='unload', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_unload(self, ctx, *, cog: str):
    """
    Unload cogs for this guild
    """
    author                   = ctx.author
    guild_id                 = ctx.guild.id
    if not cog:
      await ctx.message.add_reaction('❌')
      await ctx.send ("Paramètre <cog> obligatoire.")
      return
    cog                      = cog.lower()
    if cog in ["configuration", "help", "loader", "logs"]:
      await ctx.message.add_reaction('❌')
      await ctx.send ("Vous ne pouvez pas désactiver le cog `{0}`.".format(cog))
      return
    try:
      select                 = (   "select   status "
                                   "from     config_cog "+
                                   "where "+
                                   "cog=? "+
                                   " and "+
                                   "guild_id=? ;"+
                                   ""
                               )
      fetched                = database.fetch_one_line (select, [cog, guild_id])
      sql                    = ""
      if fetched:
        status               = fetched [0]
        if status == 1:
          sql                = "update config_cog set status=0 where cog=? and guild_id=? ;"
      else:
        sql                  = "insert into config_cog (`cog`, `guild_id`, `status`) values (?,?,0) ;"
      if len(sql):
        database.execute_order (sql, [cog, guild_id])
    except Exception as e:
      await ctx.message.add_reaction('❌')
      print (f"{type(e).__name__} - {e}")
    else:
      await ctx.message.add_reaction('✅')


  @commands.command(name='unloadall', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_unload_all(self, ctx):
    """
    Unload cogs for this guild
    """
    author                   = ctx.author
    guild_id                 = ctx.guild.id
    try:
      select                 = (   "select   status "
                                   "from     config_cog "+
                                   "where "+
                                   "guild_id=? ;"+
                                   ""
                               )
      fetched                = database.fetch_all_line (select, [guild_id])
      if fetched:
        for line in fetched:
          if line [0] == 1:
            update           = "update config_cog set status=0 where guild_id=? ;"
            database.execute_order (update, [guild_id])
    except Exception as e:
      await ctx.message.add_reaction('❌')
      print (f"{type(e).__name__} - {e}")
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='listcogs', hidden=True, aliases=['lc'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def list_cogs_guild(self, ctx):
    """
    Command which lists all loaded cogs for this guild
    """
    author                   = ctx.author
    guild_id                 = ctx.guild.id
    all_loaded = ""
    for name in self.bot.cogs.keys():
      cog                    = name.lower()
      try:
        select               = (   "select   status "
                                   "from     config_cog "+
                                   "where "+
                                   "cog=? "+
                                   " and "+
                                   "guild_id=? ;"+
                                   ""
                               )
        fetched              = database.fetch_one_line (select, [cog, guild_id])
        if (fetched and fetched[0]==1) or (cog in ["configuration", "help", "loader", "logs"]):
          all_loaded += f"- **{name}**\n"
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
    if not len (all_loaded):
      all_loaded = "**NONE**"
    try:
      await ctx.send (all_loaded)
    except Exception as e:
      print(f'{type(e).__name__} - {e}')