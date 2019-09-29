from discord.ext import commands
from ..logs import Logs
from database import Database
from Utils import Utils
from discord.ext import commands

from Utils import Utils
from database import Database
from ..logs import Logs


class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.Cog.listener('on_message')
  async def all_caps_emoji(self, message):
    if (message.guild == None):
      return
    if (message.author.id == self.bot.user.id):
      return
    if len (message.content) > 5 and message.content.isupper():
      await message.add_reaction ("<:CapsLock:621629196359303168>")
    return

  @commands.Cog.listener('on_message_edit')
  async def all_caps_emoji_edit(self, before, after):
    if (before.guild == None) or (after.guild == None):
      return
    if (before.author.id == self.bot.user.id):
      return
    if len (after.content) > 5 and after.content.isupper():
      await after.add_reaction ("<:CapsLock:621629196359303168>")
    if (     (len (before.content) > 5 and before.content.isupper())
         and (not after.content.isupper())
       ):
      await after.remove_reaction ("<:CapsLock:621629196359303168>", self.bot.user)
    return
