from discord.ext import commands
import discord
import Utils
from ..logs import Logs


class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  @commands.Cog.listener('on_message')
  async def all_caps_emoji(self, message):
    if (message.guild is None):
      return
    if (message.author.id == self.bot.user.id):
      return
    if not Utils.is_loaded("moderation", message.guild.id):
      return
    if len(message.content) > 5 and message.content.isupper():
      await message.add_reaction("<:CapsLock:621629196359303168>")
    return

  @commands.Cog.listener('on_message_edit')
  async def all_caps_emoji_edit(self, before, after):
    if (before.guild is None) or (after.guild is None):
      return
    if (before.author.id == self.bot.user.id):
      return
    if not Utils.is_loaded("moderation", before.guild.id):
      return
    if len(after.content) > 5 and after.content.isupper():
      await after.add_reaction("<:CapsLock:621629196359303168>")
    if ((len(before.content) > 5 and before.content.isupper())
            and (not after.content.isupper())
    ):
      await after.remove_reaction("<:CapsLock:621629196359303168>", self.bot.user)
    return

  @commands.command(name="faqlore", aliases=['faq'])
  @Utils.require(['authorized', 'not_banned', 'cog_loaded'])
  async def react_faq_lore(self, ctx: commands.Context, message: discord.Message):
    reactions = ["🇫", "🇦", "🇶", "🇱", "🇴", "🇷", "🇪", "🇸", "🇹", "🇵"]
    await ctx.message.delete()
    try:
      for reaction in reactions:
        await message.add_reaction(reaction)
    except Exception:
      pass