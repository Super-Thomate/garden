import discord
from discord.ext import commands
from Utils import Utils
from ..logs import Logs
from database import Database


class Turing(commands.Cog):

  """
  Turing:
  * setroledm role
  * unsetroledm role
  * setroledmmessage role
  * displayroledmmessage role
  """
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.command(name='answer', aliases=['reply'])
  async def answer_spy_log(self, ctx, user: discord.User = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    if not user:
      await ctx.send ("Le paramètre `<user>` est obligatoire.")
    print (f"user obj: {user.id}")
    error                    = False
    try:
      ask                    = await ctx.send ("Entrez le message à envoyer:")
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
    await self.log('spy_log', author, ctx.message, error)
    if message:
      await self.log('spy_log', author, msg, error)

  @commands.command(name='say', aliases=['talk', 'speak'])
  async def say_spy_log(self, ctx, channel: discord.TextChannel = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    if not channel:
      await ctx.send ("Le paramètre `<channel>` est obligatoire.")
    error                    = False
    try:
      ask                    = await ctx.send ("Entrez le message à envoyer:")
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
    await self.log('spy_log', author, ctx.message, error)
    if message:
      await self.log('spy_log', author, msg, error)

  @commands.command(name='lmute', aliases=['lionmute', 'lotusmute'])
  async def fake_mute_lion(self, ctx):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    error                    = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send ("`FONCTION AUTOREPONSE DESACTIVEE`")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.log('spy_log', author, ctx.message, error)

  @commands.command(name='lstart', aliases=['lionstart', 'lotusstart'])
  async def fake_start_lion(self, ctx):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    error                    = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send ("`FONCTION AUTOREPONSE ACTIVEE`")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.log('spy_log', author, ctx.message, error)

  @commands.command(name='sethumor')
  async def fake_set_humor_lion(self, ctx, percent: str = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    error                    = False
    try:
      await ctx.message.add_reaction('✅')
      await ctx.send (f"**`HUMOUR REGLE A {percent}`**")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.log('spy_log', author, ctx.message, error)

  @commands.command(name='react')
  async def react_turing(self, ctx, message: discord.Message = None, emoji: discord.Emoji = None):
    guild_id                 = ctx.message.guild.id
    author                  = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    if not message:
      await ctx.send ("Le paramètre `<message>` est obligatoire.")
    if not emoji:
      await ctx.send ("Le paramètre `<emoji>` est obligatoire.")
    error                    = False
    try:
      await message.add_reaction(emoji)
      # await ctx.message.delete (delay=2)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
    await self.log('spy_log', author, ctx.message, error)

 