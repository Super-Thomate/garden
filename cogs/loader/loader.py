import os

from discord.ext import commands

import Utils


class Loader(commands.Cog):

  def __init__(self, bot):
      self.bot = bot

  # Hidden means it won't show up on the default help.
  @commands.command(name='load', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_load(self, ctx, *, cog: str):
    """Command which Loads a Module.
    Remember to use dot path. e.g: cogs.greetings"""
    try:
      self.bot.load_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, "exception_error").format(type(e).__name__, e))
    else:
      await ctx.send(Utils.get_text((ctx.guild.id, 'success'))

  @commands.command(name='unload', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_unload(self, ctx, *, cog: str):
    """Command which Unloads a Module.
    Remember to use dot path. e.g: cogs.greetings"""
    try:
      self.bot.unload_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, "exception_error").format(type(e).__name__, e))
    else:
      await ctx.send(Utils.get_text((ctx.guild.id, 'success'))

  @commands.command(name='reload', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_reload(self, ctx, *, cog: str):
    """Command which Reloads a Module.
    Remember to use dot path. e.g: cogs.greetings"""
    try:
      self.bot.unload_extension(f'cogs.{cog}')
      self.bot.load_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, "exception_error").format(type(e).__name__, e))
    else:
      await ctx.send(Utils.get_text((ctx.guild.id, 'success'))

  @commands.command(name='listcogs', hidden=True, aliases=['lc'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def list_load(self, ctx):
    """Command which lists all loaded cogs
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

  @commands.command(name='patch', hidden=True)
  @Utils.require(required=['authorized', 'not_banned'])
  async def get_patch(self, ctx):
    """
    Command which give the current patch
    """
    # `cd ${__dirname}; git branch | grep \\* | awk '{ print $2 }';`
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
    cmd = "cd "+dir_path+"; git branch | grep \\* | awk '{ print $2 }';"
    current_patch = os.popen(cmd).read()
    try:
      await ctx.send (current_patch)
    except Exception as e:
      print(f'{type(e).__name__} - {e}')