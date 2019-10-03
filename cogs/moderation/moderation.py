from discord.ext import commands
from ..logs import Logs
import Utils


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
    if len (message.content) > 5 and message.content.isupper():
      await message.add_reaction ("<:CapsLock:621629196359303168>")
    return

  @commands.Cog.listener('on_message_edit')
  async def all_caps_emoji_edit(self, before, after):
    if (before.guild is None) or (after.guild is None):
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

  @commands.command(name='rule')
  @Utils.require(required=['authorized', 'not_banned'])
  async def display_rule(self, ctx, rule_number: str = None):
    if not rule_number:
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<rule_index>'))
      return
    if not (1 <= int(rule_number) <= 10):
      await ctx.send(Utils.get_text(ctx.guild.id, "bad_rule_index"))
      return
    await ctx.send(Utils.get_text(ctx.guild.id, f"rule{rule_number}"))