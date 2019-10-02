from datetime import datetime

import discord
from discord.ext import commands

import Utils
import database


class Logs(commands.Cog):
  def __init__ (self, bot):
    self.bot = bot



  @commands.command(name='setinvitelog', aliases=['setinvite', 'sil', 'invitelog'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_invitation_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    try:
      log_channel = channel or ctx.message.channel
      sql = f"select * from invite_log where guild_id='{guild_id}'"
      prev_log_channel = database.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO invite_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update invite_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      database.execute_order(sql)
      await log_channel.send(Utils.get_text(ctx.guild.id, "invitation_log_channel_set"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setgallerylog', aliases=['setgallery', 'sgl', 'gallerylog'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_galerie_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from galerie_log where guild_id='{guild_id}'"
      prev_log_channel = database.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO galerie_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update galerie_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      database.execute_order(sql, [])
      await log_channel.send(Utils.get_text(ctx.guild.id, "gallery_log_channel_set"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setnicknamelog', aliases=['setnickname', 'snl', 'nicknamelog'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_nickname_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from nickname_log where guild_id='{guild_id}'"
      prev_log_channel = database.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO nickname_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update nickname_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      database.execute_order(sql, [])
      await log_channel.send(Utils.get_text(ctx.guild.id, "nickname_log_channel_set"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setvotelog', aliases=['setvote', 'svl', 'votelog'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_vote_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from vote_log where guild_id='{guild_id}'"
      prev_log_channel = database.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO vote_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update vote_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      database.execute_order(sql, [])
      await log_channel.send(Utils.get_text(ctx.guild.id, "vote_log_channel_set"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setwelcomelog', aliases=['swl', 'welcomelog'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_welcome_log(self, ctx, channel: discord.TextChannel = None):
    # useless
    return
    guild_id = ctx.message.guild.id
    member = ctx.author
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from welcome_log where guild_id='{guild_id}'"
      prev_log_channel = database.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO welcome_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update welcome_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      database.execute_order(sql, [])
      await log_channel.send(Utils.get_text(ctx.guild.id, "welcome_log_channel_set"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")


  @commands.command(name='setbirthdaylog', aliases=['sbl'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_birthday_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.guild.id
    member = ctx.author
    try:
      log_channel = channel or ctx.message.channel
      sql = f"SELECT channel_id FROM birthday_log WHERE guild_id={guild_id}"
      channel_already_set = database.fetch_one_line(sql)
      if channel_already_set:
        sql = f"UPDATE birthday_log set channel_id='{log_channel.id}' WHERE guild_id='{guild_id}'"
      else:
        sql = f"INSERT INTO birthday_log VALUES ('{log_channel.id}', '{guild_id}')"
      database.execute_order(sql, [])
      await log_channel.send(Utils.get_text(ctx.guild.id, "birthday_log_channel_set"))
    except Exception as e:
      print(f" {type(e).__name__} - {e}")


  async def log(self, db, member, message, error, params = None):
    guild_id = message.channel.guild.id
    sql = f"select channel_id from {db} where guild_id='{guild_id}'"
    db_log_channel = database.fetch_one_line (sql)
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
    embed.timestamp = datetime.utcnow()
    embed.set_footer(text=f"ID: {message.id}")
    print (f"params: {params}")
    if params and "url_to_go" in params:
      print ("url_to_go")
      embed.description      = embed.description+"\njumpto: "+ params ["url_to_go"]
    try:
      await log_channel.send(content=None, embed=embed)
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='cleanchannel', aliases=['cc'])
  @commands.guild_only()
  @Utils.require(required=['authorized', 'not_banned'])
  async def cleanchannel(self, ctx, length_or_id: str = None, message_id: int = None):
    """Clean the current channel"""
    channel = ctx.channel
    member = ctx.author
    guild_id = ctx.guild.id
    await ctx.message.delete ()
    until_message            = None
    if message_id and length_or_id == 'id':
      try:
        until_message          = await channel.fetch_message (message_id)
      except Exception as e:
        print (f" {type(e).__name__} - {e}")
        if length_or_id == 'id':
          feedback = await ctx.send(Utils.get_text(ctx.guild.id, "not_valid_id").format(message_id))
          await feedback.delete (delay=2)
          return
    print ("Let's go !")
    if until_message:
      # redo length
      counter                = 0
      async for message in channel.history(limit=200):
        if message.id >= message_id:
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
    feedback = await channel.send(Utils.get_text(ctx.guild.id, "deleted_messages").format(len(deleted)))
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
    fetched_log_channel      = database.fetch_all_line (sql)
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
        embed.timestamp        = datetime.utcnow()
        embed.set_footer(text=f"ID: {message.id}")
        try:
          await log_channel.send(content=None, embed=embed)
        except Exception as e:
          print (f" {type(e).__name__} - {e}")
    return

  @commands.command(name='setspylog', aliases=['ssl', 'spylog'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_spy_log(self, ctx, channel: discord.TextChannel = None):
    guild_id                 = ctx.message.guild.id
    member                  = ctx.author
    try:
      log_channel            = channel or ctx.message.channel
      guild_id               = ctx.message.guild.id
      sql                    = f"select * from spy_log where guild_id='{guild_id}'"
      prev_log_channel       = database.fetch_one_line (sql)
      if not prev_log_channel:
        sql                  = f"insert into spy_log values ('{log_channel.id}', '{guild_id}') ;"
      else:
        sql                  = (f"update spy_log set channel_id='{log_channel.id}'"+
                                 " where guild_id='{guild_id}' ;"
                               )
      database.execute_order(sql)
      await log_channel.send(Utils.get_text(ctx.guild.id, "spy_log_channel_set"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")


  @commands.command(name='setconfiglog', aliases=['setconfig', 'scl', 'configlog'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_config_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from config_log where guild_id='{guild_id}'"
      prev_log_channel = database.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO config_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update config_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      database.execute_order(sql, [])
      await log_channel.send(Utils.get_text(ctx.guild.id, "config_log_channel_set"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")


  @commands.command(name='setutiplog', aliases=['setutip', 'sul', 'utiplog'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_utip_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from utip_log where guild_id='{guild_id}'"
      prev_log_channel = database.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO utip_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = f"update utip_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      database.execute_order(sql, [])
      await log_channel.send(Utils.get_text(ctx.guild.id, "utip_log_channel_set"))
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')



  async def log_dm (self, db, member, message, guild, error, params = None):
    if guild.get_member(member.id):
      sql                    = f"select channel_id from {db} where guild_id='{guild.id}'"
      db_log_channel         = database.fetch_one_line (sql)
      if not db_log_channel:
        return
      log_channel            = guild.get_channel (int (db_log_channel[0]))
      colour                 = discord.Colour(0)
      colour                 = colour.from_rgb(76, 110, 76)
      if error:
        colour               = colour.from_rgb(150, 72, 72)
      embed                  = discord.Embed(colour=colour)
      embed.set_author(icon_url=member.avatar_url, name=str(member)+" in DM")
      embed.description      = message.content
      embed.timestamp        = datetime.utcnow()
      embed.set_footer(text=f"ID: {message.id}")
      print (f"params: {params}")
      if params and "url_to_go" in params:
        print ("url_to_go")
        embed.description    = embed.description+"\njumpto: "+ params ["url_to_go"]
      try:
        await log_channel.send(content=None, embed=embed)
      except Exception as e:
        print (f" {type(e).__name__} - {e}")

  @commands.Cog.listener()
  async def on_command_error(self, ctx, exception):
    if not ctx.command:
      return
    if ctx.command.name in ['setbirthdaylog']:
      await ctx.channel.send(exception)