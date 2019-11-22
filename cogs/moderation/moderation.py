import discord
from discord.ext import commands
import Utils
import os
import subprocess
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
  async def set_patch(self, ctx, patch: str = None):
    author                   = ctx.author
    guild_id                 = ctx.guild.id
    """
    if not patch:
      await ctx.send (Utils.get_text (guild_id, "parameter_is_mandatory").format ("<patch>"))
      return
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))+'/'
    try:
        output = subprocess.check_output(
            "cd {0}; git pull; git checkout {1};".format (dir_path, patch),
            shell=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
      print (f'{type(e).__name__} - {e}')
      await ctx.message.add_reaction('❌')
      await ctx.send (f'{type(e).__name__} - {e}')
    else:
      await ctx.send (output.decode('utf-8'))
      await ctx.message.add_reaction('✅')
    

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
