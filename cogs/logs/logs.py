import discord
import botconfig
from discord.ext import commands
from datetime import datetime
from ..database import Database

class Logs(commands.Cog):
  def __init__ (self, bot):
    self.bot = bot
    self.db = Database()

  @commands.command(name='setinvitelog', aliases=['setinvite', 'sil', 'invitelog'])
  @commands.has_any_role(*botconfig.config['invite_roles'])
  async def set_invitation_log(self, ctx, channel: discord.TextChannel = None):
    log_channel = channel or ctx.message.channel
    guild_id = ctx.message.guild.id
    log_channel = self.db.fetch_one (f"select * from invite_log where guild_id='{guild_id}'")
    if not log_channel:
      sql = "INSERT INTO invite_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
    else:
      sql = "update invite_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
    self.db.execute_order(sql)
    await log_channel.send ("Logs for invite will be put here")

  @commands.command(name='setgalerielog', aliases=['setgalerie', 'sgl', 'galerielog'])
  @commands.has_any_role(*botconfig.config['invite_roles'])
  async def set_galerie_log(self, ctx, channel: discord.TextChannel = None):
    log_channel = channel or ctx.message.channel
    guild_id = ctx.message.guild.id
    log_channel = self.db.fetch_one (f"select * from galerie_log where guild_id='{guild_id}'")
    if not log_channel:
      sql = "INSERT INTO galerie_log VALUES ('{0}', '{1}')".format(log_channel.id, guild_id)
    else:
      sql = "update galerie_log set channel_id='{log_channel.id}' where guild_id='{guild_id}'"
    self.db.execute_order(sql)
    await log_channel.send ("Logs for galerie will be put here")

  async def log(self, db, member, message, error):
    guild_id = message.guild.id
    log_channel = self.db.fetch_one (f"select * from {db} where guild_id='{guild_id}'")
    if not log_channel:
      log_channel = message.channel
    embed = discord.Embed(colour=colour)
    embed.set_author(icon_url=member.avatar_url, name=str(member))
    embed.description = message.content
    embed.timestamp = datetime.today()
    embed.set_footer(text=f"ID: {message.id}")
    await log_channel.send(content=None, embed=embed)