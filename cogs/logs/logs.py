import discord
import botconfig
from discord.ext import commands
from datetime import datetime
from database import Database
from Utils import Utils

class Logs(commands.Cog):
  def __init__ (self, bot):
    self.bot = bot
    self.db = Database()
    self.utils = Utils()

  @commands.command(name='setinvitelog', aliases=['setinvite', 'sil', 'invitelog'])
  async def set_invitation_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_invite"]:
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    try:
      log_channel = channel or ctx.message.channel
      sql = f"select * from invite_log where guild_id='{guild_id}'"
      prev_log_channel = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO invite_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update invite_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      self.db.execute_order(sql, [])
      await log_channel.send ("Logs for invite will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setgallerylog', aliases=['setgallery', 'sgl', 'gallerylog'])
  async def set_galerie_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_token"]:
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from galerie_log where guild_id='{guild_id}'"
      prev_log_channel = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO galerie_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update galerie_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      self.db.execute_order(sql, [])
      await log_channel.send ("Logs for galerie will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setnicknamelog', aliases=['setnickname', 'snl', 'nicknamelog'])
  async def set_nickname_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from nickname_log where guild_id='{guild_id}'"
      prev_log_channel = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO nickname_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update nickname_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      self.db.execute_order(sql, [])
      await log_channel.send ("Logs for nickname will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setvotelog', aliases=['setvote', 'svl', 'votelog'])
  async def set_vote_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from vote_log where guild_id='{guild_id}'"
      prev_log_channel = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO vote_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update vote_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      self.db.execute_order(sql, [])
      await log_channel.send ("Logs for vote will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setwelcomelog', aliases=['swl', 'welcomelog'])
  async def set_welcome_log(self, ctx, channel: discord.TextChannel = None):
    # useless
    return 
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from welcome_log where guild_id='{guild_id}'"
      prev_log_channel = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO welcome_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update welcome_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      self.db.execute_order(sql, [])
      await log_channel.send ("Logs for welcome will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")


  async def log(self, db, member, message, error):
    guild_id = message.channel.guild.id
    sql = f"select channel_id from {db} where guild_id='{guild_id}'"
    db_log_channel = self.db.fetch_one_line (sql)
    print (db_log_channel)
    if not db_log_channel:
      log_channel = message.channel
    else:
      log_channel = await self.bot.fetch_channel (int (db_log_channel[0]))
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    if error:
      colour = colour.from_rgb(255, 125, 125)
    embed = discord.Embed(colour=colour)
    embed.set_author(icon_url=member.avatar_url, name=str(member))
    embed.description = message.content
    embed.timestamp = datetime.today()
    embed.set_footer(text=f"ID: {message.id}")
    try:
      await log_channel.send(content=None, embed=embed)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='cleanchannel', aliases=['cc'])
  @commands.guild_only()
  async def cleanchannel(self, ctx, length_or_id: str = None, message_id: int = None):
    """Clean the current channel"""
    channel = ctx.channel
    member = ctx.author
    guild_id = ctx.guild.id
    await ctx.message.delete (delay=1)
    until_message            = None
    if message_id and length_or_id == 'id':
      try:
        until_message          = await channel.fetch_message (message_id)
      except Exception as e:
        print (f" {type(e).__name__} - {e}")
        if length_or_id == 'id':
          feedback           = await ctx.send (f"{message_id} n'est pas un id valide.")
          await feedback.delete (delay=2)
          return
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    print ("Let's go !")
    if until_message:
      # redo length
      counter                = 0
      async for message in channel.history(limit=200):
        if message.id >= length_or_id:
          counter           += 1
      length                 = counter
    else:
      if not length_or_id:
        length               = 10
      else:
        try:
          length_or_id       = int (length_or_id)
        except Exception as e:
          print (f" {type(e).__name__} - {e}")
          return
        else:
          length             = length_or_id if (length_or_id <= 200) else 10
      
    not_is_pin = lambda message : not message.pinned
    # delete all messages except ping
    deleted = await channel.purge(limit=length, check=not_is_pin)
    feedback = await channel.send (f"Deleted {len (deleted)} messages")
    await feedback.delete (delay=2)
    
  # Get all the DM and log them
  @commands.Cog.listener('on_message')
  async def garden_dm (self, message):
    # message = dm ?
    if message.channel.type != discord.ChannelType.private:
      return
    # don't read a bot yourself included
    if message.author.bot:
      return
    # log for dm
    sql                      = f"select channel_id,guild_id from spy_log ;"
    fetched_log_channel      = self.db.fetch_all_line (sql)
    # print (f"fetched_log_channel: {fetched_log_channel}")
    if fetched_log_channel:
      for db_log_channel in fetched_log_channel:
        log_channel            = await self.bot.fetch_channel (int (db_log_channel[0]))
        # guild_id               = await self.bot.fetch_channel (int (db_log_channel[1]))
        member                 = message.author
        colour                 = discord.Colour(0)
        colour                 = colour.from_rgb(225, 199, 255)
        embed                  = discord.Embed(colour=colour)
        embed.set_author(icon_url=member.avatar_url, name="DM by "+str(member)+" ["+str(member.id)+"]")
        embed.description      = message.content
        embed.timestamp        = datetime.today()
        embed.set_footer(text=f"ID: {message.id}")
        try:
          await log_channel.send(content=None, embed=embed)
        except Exception as e:
          print (f" {type(e).__name__} - {e}")
    return

  @commands.command(name='setspylog', aliases=['ssl', 'spylog'])
  async def set_spy_log(self, ctx, channel: discord.TextChannel = None):
    guild_id                 = ctx.message.guild.id
    member                  = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    try:
      log_channel            = channel or ctx.message.channel
      guild_id               = ctx.message.guild.id
      sql                    = f"select * from spy_log where guild_id='{guild_id}'"
      prev_log_channel       = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql                  = f"insert into spy_log values ('{log_channel.id}', '{guild_id}') ;"
      else:
        sql                  = (f"update spy_log set channel_id='{log_channel.id}'"+
                                 " where guild_id='{guild_id}' ;"
                               )
      self.db.execute_order(sql)
      await log_channel.send ("Logs for spy will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
  
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