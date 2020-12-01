import discord
from discord.ext import commands

import Utils
from ..logs import Logs
from core import logger

import json
from datetime import datetime

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
    self.logger = Logs(self.bot)
    self.auto_reply = False

  @commands.command(name='answer', aliases=['reply'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def answer_spy_log(self, ctx, user: discord.User = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not user:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<User>'))
      return
    error = False
    try:
      ask = await ctx.send(Utils.get_text(ctx.guild.id, "turing_ask_message"))
      check = lambda m: m.channel == ctx.channel and m.author == ctx.author
      msg = await self.bot.wait_for('message', check=check)
      message = msg.content
      await user.send(message)
      await ctx.message.delete(delay=2)
      await ask.delete(delay=2)
      await msg.delete(delay=2)
    except Exception as e:
      logger ("turing::answer_spy_log", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error)
    if message:
      await self.logger.log('spy_log', author, msg, error)

  @commands.command(name='say', aliases=['talk', 'speak'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def say_spy_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not channel:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<Channel>'))
      return
    error = False
    try:
      ask = await ctx.send(Utils.get_text(ctx.guild.id, "turing_ask_message"))
      check = lambda m: m.channel == ctx.channel and m.author == ctx.author
      msg = await self.bot.wait_for('message', check=check)
      message = msg.content
      await channel.send(message)
      await ctx.message.delete(delay=2)
      await ask.delete(delay=2)
      await msg.delete(delay=2)
    except Exception as e:
      logger ("turing::say_spy_log", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error)
    if message:
      await self.logger.log('spy_log', author, msg, error)

  @commands.command(name='lmute', aliases=['lionmute', 'lotusmute'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def fake_mute_lion(self, ctx):
    guild_id = ctx.message.guild.id
    author = ctx.author
    error = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send(Utils.get_text(ctx.guild.id, "turing_autoanswer_disable"))
    except Exception as e:
      logger ("turing::fake_mute_lion", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='lstart', aliases=['lionstart', 'lotusstart'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def fake_start_lion(self, ctx):
    guild_id = ctx.message.guild.id
    author = ctx.author
    error = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send(Utils.get_text(ctx.guild.id, "turing_autoanswer_enable"))
    except Exception as e:
      logger ("turing::fake_start_lion", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='sethumor')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def fake_set_humor_lion(self, ctx, percent: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    error = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send(Utils.get_text(ctx.guild.id, "turing_set_humor").format(percent))
    except Exception as e:
      logger ("turing::fake_set_humor_lion", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='react')
  async def react_turing(self, ctx, message_id: int = None, emoji: str = None):
    await self.react_to_message(ctx, message_id, emoji, "add")

  @commands.command(name='unreact')
  async def unreact_turing(self, ctx, message_id: int = None, emoji: str = None):
    await self.react_to_message(ctx, message_id, emoji, "remove")

  @commands.command(name='editmessage')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def edit_message_turing(self, ctx, message_id: int = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not message_id:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<messageID>'))
      return
    error = False
    try:
      message = await self.get_message_general(ctx, message_id)
      if message:
        old_content_title = await ctx.send(Utils.get_text(ctx.guild.id, "turing_old_message"))
        old_content = await ctx.send(message.content)
        ask = await ctx.send(Utils.get_text(ctx.guild.id, "ask_message"))
        check = lambda m: m.channel == ctx.channel and m.author == ctx.author
        msg = await self.bot.wait_for('message', check=check)
        new_content = msg.content
        await message.edit(content=new_content)
        await ctx.message.delete(delay=2)
        await old_content_title.delete(delay=2)
        await old_content.delete(delay=2)
        await ask.delete(delay=2)
        await msg.delete(delay=2)
      else:
        await ctx.send(Utils.get_text(ctx.guild.id, "error_message_not_found"))
        error = True
      # await ctx.message.delete (delay=2)
    except Exception as e:
      logger ("turing::edit_message_turing", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='deletemessage')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def delete_message_turing(self, ctx, message_id: int = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not message_id:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<messageID>'))
      return
    error = False
    try:
      message = await self.get_message_general(ctx, message_id)
      if message:
        await message.delete()
      else:
        await ctx.send(Utils.get_text(ctx.guild.id, "error_message_not_found"))
        error = True
      # await ctx.message.delete (delay=2)
    except Exception as e:
      logger ("turing::delete_message_turing", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.command(name='autoreply')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_auto_reply(self, ctx, status: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not status:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<status>'))
      return
    error = False
    try:
      if status.lower() == "on":
        self.auto_reply = True
      else:
        self.auto_reply = False
      # await ctx.message.delete (delay=2)
    except Exception as e:
      logger ("turing::set_auto_reply", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error)

  @commands.Cog.listener('on_message')
  async def auto_reply_dm(self, message):
    if message.guild:
      return
    if self.auto_reply:
      await message.author.send(Utils.get_text(
        '283243816448819200', "turing_DM_unavailable")  # DM are in the default language 'french' until better solution
                                .format(self.bot.user.name))

  # UTILS
  async def get_message_general(self, ctx, message_id):
    message = None
    for channel in ctx.guild.channels:
      if channel.category and channel.type != discord.ChannelType.voice:
        try:
          message = await channel.fetch_message(message_id)
        except Exception as e:
          logger ("turing::get_message_general", f" {type(e).__name__} - {e}")
        else:
          break
    return message

  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def react_to_message(self, ctx, message_id, emoji, react_type):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not message_id:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<messageID>'))
      return
    if not emoji:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<emoji>'))
      return
    error = False
    try:
      message = await self.get_message_general(ctx, message_id)
      if message:
        if react_type == "add":
          await message.add_reaction(emoji)
        else:
          await message.remove_reaction(emoji, self.bot.user)
      else:
        await ctx.send(Utils.get_text(ctx.guild.id, "error_message_not_found"))
        error = True
      # await ctx.message.delete (delay=2)
    except Exception as e:
      logger ("turing::react_to_message", f" {type(e).__name__} - {e}")
      error = True
    await self.logger.log('spy_log', author, ctx.message, error, {"url_to_go": message.jump_url})



  

  @commands.command(name="embed")
  @commands.guild_only()
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_embed (self, ctx: commands.Context, channel: discord.TextChannel = None):
    """
    
    """
    try:
      channel = channel or ctx.channel
      ask = await ctx.send ("uploader le json: ")
      check = lambda m: m.channel == ctx.channel and m.author == ctx.author
      msg = await self.bot.wait_for('message', check=check)
      await ask.delete(delay=2)
      message = msg.content
    except Exception as e:
      logger ("turing::set embed", f" {type(e).__name__} - {e}")
    data = json.loads(message)
    logger ("turing::embed json", data)
    
    try:
      embed = discord.Embed.from_dict(data)
      await channel.send (content=None, embed=embed)
    except Exception as e:
      logger ("turing::set embed", f" {type(e).__name__} - {e}")
      await ctx.send ("**ERROR** {} - {}".format (type(e).__name__, e))
    