import discord
import botconfig
from discord.ext import commands
from datetime import datetime
from ..database import Database

class Logs(commands.Cog):
  def __init__ (self, bot):
    self.bot = bot
    self.db = Database()

  def has_role (self, member, guild_id):
    for obj_role in member.roles:
      if (    (obj_role.name in botconfig.config[str(guild_id)]['roles'])
           or (obj_role.id in botconfig.config[str(guild_id)]['roles'])
         ):
        return True
    return False

  @commands.command(name='setinvitelog', aliases=['setinvite', 'sil', 'invitelog'])
  async def set_invitation_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_invite"]:
      return
    try:
      log_channel = channel or ctx.message.channel
      sql = f"select * from invite_log where guild_id='{guild_id}'"
      prev_log_channel = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO invite_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = "update invite_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      self.db.execute_order(sql, [])
      await log_channel.send ("Logs for invite will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setgallerylog', aliases=['setgallery', 'sgl', 'gallerylog'])
  async def set_galerie_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_token"]:
      return
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from galerie_log where guild_id='{guild_id}'"
      prev_log_channel = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO galerie_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = "update galerie_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      self.db.execute_order(sql, [])
      await log_channel.send ("Logs for galerie will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  @commands.command(name='setnicknamelog', aliases=['setnickname', 'snl', 'nicknamelog'])
  async def set_nickname_log(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    try:
      log_channel = channel or ctx.message.channel
      guild_id = ctx.message.guild.id
      sql = f"select * from nickname_log where guild_id='{guild_id}'"
      prev_log_channel = self.db.fetch_one_line (sql)
      if not prev_log_channel:
        sql = "INSERT INTO nickname_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
      else:
        sql = "update nickname_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
      self.db.execute_order(sql, [])
      await log_channel.send ("Logs for nickname will be put here")
    except Exception as e:
      print (f" {type(e).__name__} - {e}")

  async def log(self, db, member, message, error):
    guild_id = message.channel.guild.id
    sql = f"select * from {db} where guild_id='{guild_id}'"
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