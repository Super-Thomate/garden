import discord
from discord.ext import commands

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='help')
  async def help(self, ctx, *, cog: str = None):
    """Says hello"""
    if cog:
      await ctx.channel.send (f"You asked for help for cog {cog}")
    else:
      await ctx.channel.send ("You asked for global help")