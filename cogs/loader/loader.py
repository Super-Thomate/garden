from discord.ext import commands
from Utils import Utils
from databse import Database
import os

class Loader(commands.Cog):

  def __init__(self, bot):
      self.bot               = bot
      self.utils             = Utils ()
      self.db                = Database()

  @commands.command(name='cogload', hidden=True)
  async def cog_do_load(self, ctx, *, cog: str):
    """Command which Loads a Module.
    Remember to use dot path. e.g: cogs.greetings"""
    if not self.utils.is_authorized (ctx.author, ctx.guild.id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
      return
    try:
      self.bot.load_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')

  @commands.command(name='cogunload', hidden=True)
  async def cog_do_unload(self, ctx, *, cog: str):
    """Command which Unloads a Module.
    Remember to use dot path. e.g: cogs.greetings"""
    if not self.utils.is_authorized (ctx.author, ctx.guild.id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
      return
    try:
      self.bot.unload_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')

  @commands.command(name='cogreload', hidden=True)
  async def cog_do_reload(self, ctx, *, cog: str):
    """Command which Reloads a Module.
    Remember to use dot path. e.g: cogs.greetings"""
    if not self.utils.is_authorized (ctx.author, ctx.guild.id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
      return
    try:
      self.bot.unload_extension(f'cogs.{cog}')
      self.bot.load_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')

  @commands.command(name='listcogs', hidden=True, aliases=['lc'])
  async def list_load(self, ctx):
    """Command which lists all loaded cogs
    """
    if not self.utils.is_authorized (ctx.author, ctx.guild.id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
      return
    all_loaded = ""
    for name in self.bot.cogs.keys():
      all_loaded += f"- **{name}**\n"
    if not len (all_loaded):
      all_loaded = "**NONE**"
    try:
      await ctx.send (all_loaded)
    except Exception as e:
      print(f'{type(e).__name__} - {e}')

  @commands.command(name='patch', hidden=True)
  async def get_patch(self, ctx):
    """
    Command which give the current patch
    """
    if not self.utils.is_authorized (ctx.author, ctx.guild.id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
      return
    # `cd ${__dirname}; git branch | grep \\* | awk '{ print $2 }';`
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
    cmd = "cd "+dir_path+"; git branch | grep \\* | awk '{ print $2 }';"
    current_patch = os.popen(cmd).read()
    try:
      await ctx.send (current_patch)
    except Exception as e:
      print(f'{type(e).__name__} - {e}')
  

  @commands.command(name='load', hidden=True)
  async def do_load(self, ctx, *, cog: str):
    """
    Load cogs for this guild
    """
    author                   = ctx.author
    guild_id                 = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, author, guild_id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
      return
    if not cog:
      await ctx.message.add_reaction('❌')
      await ctx.send ("Paramètre <cog> obligatoire.")
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
      fetched                = self.db.fetch_one_line (select, [cog, guild_id])
      sql                    = ""
      if fetched:
        status               = fetched [0]
        if status == 0:
          sql                = "update config_cog set status=1 where cog=? and guild_id=? ;"
      else:
        sql                  = "insert_into config_cog (`cog`, `guild_id`, `status`) values (?,?,1) ;"
      if len(sql):
        self.db.execute_order (sql, [cog, guild_id])
    except Exception as e:
      await ctx.message.add_reaction('❌')
      print (f"{type(e).__name__} - {e}")
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='unload', hidden=True)
  async def do_unload(self, ctx, *, cog: str):
    """
    Unload cogs for this guild
    """
    author                   = ctx.author
    guild_id                 = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, author, guild_id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
      return
    if not cog:
      await ctx.message.add_reaction('❌')
      await ctx.send ("Paramètre <cog> obligatoire.")
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
      fetched                = self.db.fetch_one_line (select, [cog, guild_id])
      sql                    = ""
      if fetched:
        status               = fetched [0]
        if status == 1:
          sql                = "update config_cog set status=0 where cog=? and guild_id=? ;"
      else:
        sql                  = "insert_into config_cog (`cog`, `guild_id`, `status`) values (?,?,0) ;"
      if len(sql):
        self.db.execute_order (sql, [cog, guild_id])
    except Exception as e:
      await ctx.message.add_reaction('❌')
      print (f"{type(e).__name__} - {e}")
    else:
      await ctx.message.add_reaction('✅')
