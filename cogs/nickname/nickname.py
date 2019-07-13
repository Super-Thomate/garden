import discord
import botconfig
from discord.ext import commands
from datetime import datetime
from ..logs import Logs
from ..database import Database

class Nickname(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.command(name='nickname', aliases=['pseudo'])
  async def nickname(self, ctx, *, nickname: str = None):
    # Check if I can change my nickname
    # Change my Nickname
    # Log my change