import discord
from discord.ext import commands
from Utils import Utils
from ..logs import Logs
from database import Database

class Turing(commands.Cog):

  """
  Turing:
  * answer <user>
  * say <channel>
  * lmute
  * lstart
  * sethumor <str>
  * react <messageid> <emoji>
  * unreact <messageid> <emoji>
  * editmessage <messageid>
  * deletemessage <messageid>
  """
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()
    self.auto_reply = False

  @commands.command(name='answer', aliases=['reply'])
  async def answer_spy_log(self, ctx, user: discord.User = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not user:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<User>'))
      return
    print (f"user obj: {user.id}")
    error                    = False
    try:
      ask                    = await ctx.send(self.utils.get_text(ctx.guild.id, "ask_message_to_send"))
      check                  = lambda m: m.channel == ctx.channel and m.author == ctx.author
      msg                    = await self.bot.wait_for('message', check=check)
      message                = msg.content
      await user.send (message)
      await ctx.message.delete (delay=2)
      await ask.delete (delay=2)
      await msg.delete (delay=2)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error)
    if message:
      await self.logger.log('spy_log', author, msg, error)

  @commands.command(name='say', aliases=['talk', 'speak'])
  async def say_spy_log(self, ctx, channel: discord.TextChannel = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not channel:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<Channel>'))
      return
    error                    = False
    try:
      ask                    = await ctx.send(self.utils.get_text(ctx.guild.id, "ask_message_to_send"))
      check                  = lambda m: m.channel == ctx.channel and m.author == ctx.author
      msg                    = await self.bot.wait_for('message', check=check)
      message                = msg.content
      await channel.send (message)
      await ctx.message.delete (delay=2)
      await ask.delete (delay=2)
      await msg.delete (delay=2)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error)
    if message:
      await self.logger.log('spy_log', author, msg, error)

  @commands.command(name='lmute', aliases=['lionmute', 'lotusmute'])
  async def fake_mute_lion(self, ctx):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    error                    = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send(self.utils.get_text(ctx.guild.id, "auto_answer_mode_disabled"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='lstart', aliases=['lionstart', 'lotusstart'])
  async def fake_start_lion(self, ctx):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    error                    = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send(self.utils.get_text(ctx.guild.id, "auto_answer_mode_enabled"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='sethumor')
  async def fake_set_humor_lion(self, ctx, percent: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    error                    = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send(self.utils.get_text(ctx.guild.id, "set_humor_to").format(percent))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='react')
  async def react_turing(self, ctx, message_id: int = None, emoji: str = None):
    await self.react_to_message (ctx, message_id, emoji, "add")

  @commands.command(name='unreact')
  async def unreact_turing(self, ctx, message_id: int = None, emoji: str = None):
    await self.react_to_message (ctx, message_id, emoji, "remove")

  @commands.command(name='editmessage')
  async def edit_message_turing(self, ctx, message_id: int = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not message_id:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<messageID>'))
      return
    error                    = False
    try:
      message                = await self.get_message_general (ctx, message_id)
      if message:
        old_content_title    = await ctx.send(self.utils.get_text(ctx.guild.id, "old_message"))
        old_content          = await ctx.send (message.content)
        ask                  = await ctx.send(self.utils.get_text(ctx.guild.id, "ask_new_message"))
        check                = lambda m: m.channel == ctx.channel and m.author == ctx.author
        msg                  = await self.bot.wait_for('message', check=check)
        new_content          = msg.content
        await message.edit (content=new_content)
        await ctx.message.delete (delay=2)
        await old_content_title.delete (delay=2)
        await old_content.delete (delay=2)
        await ask.delete (delay=2)
        await msg.delete (delay=2)
      else:
        await ctx.send(self.utils.get_text(ctx.guild.id, "message_not_found"))
        error                = True
      # await ctx.message.delete (delay=2)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='deletemessage')
  async def delete_message_turing(self, ctx, message_id: int = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not message_id:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<messageID>'))
      return
    error                    = False
    try:
      message                = await self.get_message_general (ctx, message_id)
      if message:
        await message.delete ()
      else:
        await ctx.send(self.utils.get_text(ctx.guild.id, "message_not_found"))
        error                = True
      # await ctx.message.delete (delay=2)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='autoreply')
  async def set_auto_reply(self, ctx, status: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not status:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<status>'))
      return
    error                    = False
    try:
      if status.lower() == "on":
        self.auto_reply      = True
      else:
        self.auto_reply      = False
      # await ctx.message.delete (delay=2)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.Cog.listener('on_message')
  async def auto_reply_dm (self, message):
    if message.guild:
      return
    if self.auto_reply:
      await message.author.send(self.utils.get_text(
                                '283243816448819200', "bot_DM_is_unavailable") # DM are in the default language 'french' until better solution
                                .format(self.bot.user.name))

  # UTILS
  async def get_message_general (self, ctx, message_id):
    message                  = None
    for channel in ctx.guild.channels:
      if channel.category and channel.type != discord.ChannelType.voice:
        try:
          message            = await channel.fetch_message (message_id)
        except Exception as e:
          print (f" {type(e).__name__} - {e}")
        else:
          break
    return message

  async def react_to_message (self, ctx, message_id, emoji, react_type):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    if not message_id:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<messageID>'))
      return
    if not emoji:
      await ctx.send(self.utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<emoji>'))
      return
    error                    = False
    print (f"emoji: {emoji}")
    try:
      message                = await self.get_message_general (ctx, message_id)
      if message:
        if react_type == "add":
          await message.add_reaction(emoji)
        else:
          await message.remove_reaction(emoji, self.bot.user)
      else:
        await ctx.send(self.utils.get_text(ctx.guild.id, "message_not_found"))
        error                = True
      # await ctx.message.delete (delay=2)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('spy_log', author, ctx.message, error, {"url_to_go": message.jump_url})