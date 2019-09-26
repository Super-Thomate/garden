import discord
from discord.ext import commands
from Utils import Utils

class Greetings(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self._last_member = None
    self.utils = Utils()

  @commands.Cog.listener()
  async def on_member_join(self, member):
    channel = member.guild.system_channel
    if channel is not None:
      await channel.send(self.utils.get_text('fr', 'welcome_user_1').format(member.mention))

  @commands.command(name='hi')
  async def hello(self, ctx, *, member: discord.Member = None):
    """Says hello"""
    member = member or ctx.author
    if self._last_member is None or self._last_member.id != member.id:
      await ctx.send(self.utils.get_text('fr', 'welcome_user_2').format(member))
    else:
      await ctx.send(self.utils.get_text('fr', 'welcome_user_2_familiar').format(member))
    self._last_member = member