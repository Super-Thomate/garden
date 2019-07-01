from discord.ext import commands


class Loader(commands.Cog):

  def __init__(self, bot):
      self.bot = bot
  
  # Hidden means it won't show up on the default help.
  @commands.command(name='load', hidden=True)
  @commands.is_owner()
  async def do_load(self, ctx, *, cog: str):
    """Command which Loads a Module.
    Remember to use dot path. e.g: cogs.greetings"""

    try:
      self.bot.load_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')

  @commands.command(name='unload', hidden=True)
  @commands.is_owner()
  async def do_unload(self, ctx, *, cog: str):
    """Command which Unloads a Module.
    Remember to use dot path. e.g: cogs.greetings"""

    try:
      self.bot.unload_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')

  @commands.command(name='reload', hidden=True)
  @commands.is_owner()
  async def do_reload(self, ctx, *, cog: str):
    """Command which Reloads a Module.
    Remember to use dot path. e.g: cogs.greetings"""

    try:
      self.bot.unload_extension(f'cogs.{cog}')
      self.bot.load_extension(f'cogs.{cog}')
    except Exception as e:
      await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
      await ctx.send('**`SUCCESS`**')