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
    sql = "INSERT INTO invite_log VALUES ('{0}', '{1}') ON CONFLICT(channel_id) DO UPDATE SET channel_id='{0}'".format(log_channel.id, guild_id)
    print (sql)
    self.db.execute_order(sql)
    await log_channel.send ("Logs for invite will be put here")