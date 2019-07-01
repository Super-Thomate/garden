import discord
from discord.ext import commands


class Trivia(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.running = False
  
  @commands.command(name='trivia'
  @commands.guild_only()
  async def launch_trivia(self, ctx, *args):
    """
    Launch a trivia game
    """