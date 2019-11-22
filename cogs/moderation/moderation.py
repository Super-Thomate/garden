import discord
from discord.ext import commands
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
    if not Utils.is_loaded ("moderation", message.guild.id):
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
    if not Utils.is_loaded ("moderation", before.guild.id):
      return
    if len (after.content) > 5 and after.content.isupper():
      await after.add_reaction ("<:CapsLock:621629196359303168>")
    if (     (len (before.content) > 5 and before.content.isupper())
         and (not after.content.isupper())
       ):
      await after.remove_reaction ("<:CapsLock:621629196359303168>", self.bot.user)
    return


  @commands.command(name='setpatch')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded', 'dev_only'])
  async def set_patch(self, ctx, member: discord.Member = None):
    member                   = member or ctx.author
    guild_id                 = ctx.guild.id
    await ctx.send ("Dev only")

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
