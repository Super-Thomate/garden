import discord
import botconfig
import math
from discord.ext import commands
from datetime import datetime
from ..logs import Logs
from database import Database
from Utils import Utils

class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.Cog.listener('on_message')
  @commands.guild_only()
  async def all_caps_emoji(self, message):
    if (message.guild == None):
      return
    if (message.author.id == self.bot.user.id):
      return
    if len (message.content) > 5 and message.content.isupper():
      await message.add_reaction ("<:CapsLock:621629196359303168>")
    return