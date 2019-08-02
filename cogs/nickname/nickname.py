import discord
import botconfig
import math
from discord.ext import commands
from datetime import datetime
from ..logs import Logs
from database import Database
from Utils import Utils

class Nickname(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.command(name='nickname', aliases=['pseudo'])
  async def set_nickname(self, ctx, *, nickname: str = None):
    message = ctx.message
    member = ctx.author
    guild_id = ctx.guild.id
    # Check if there is a nickname
    if not nickname:
      await self.logger.log('nickname_log', member, message, True)
      await ctx.message.add_reaction('❌')
      await ctx.channel.send (f"Vous n'avez pas donné de pseudo.")
      return
    # Check if I can change my nickname
    nickname_delay = botconfig.config[str(guild_id)]['nickname_delay']
    sql = f'select  datetime(last_change, \'{nickname_delay}\') from last_nickname where guild_id=\'{guild_id}\' and member_id=\'{member.id}\''
    fetched = self.db.fetch_one_line (sql)
    print (f"for {sql}\nget {fetched}")
    if fetched:
      last_change = fetched [0]
      last_change_datetime = datetime.strptime (last_change, '%Y-%m-%d %H:%M:%S')
      duree = last_change_datetime - datetime.now()
      if duree.seconds > 1 and duree.days >= 0::
        # I can't
        total_seconds = duree.days*86400+duree.seconds
        await self.logger.log('nickname_log', member, message, True)
        await ctx.message.add_reaction('❌')
        await ctx.channel.send (f"Vous avez changé de pseudo récemment.\nIl vous faut attendre encore {self.utils.format_time(total_seconds)}")
        return
    # Change my Nickname
    error = False
    try:
      await member.edit(nick = nickname)
    except Exception as e:
      error = True
      print (f"{type(e).__name__} - {e}")
    if not error:
      # write in db
      select = f"select * from last_nickname where guild_id='{guild_id}' and member_id='{member.id}'"
      fetched = self.db.fetch_one_line (select)
      if not fetched:
        sql = f"insert into last_nickname values ('{member.id}', '{guild_id}', datetime('{datetime.now()}'))"
      else:
        sql = f"update last_nickname set last_change=datetime('{datetime.now()}') where member_id='{member.id}' and guild_id='{guild_id}'"
      try:
        self.db.execute_order (sql, [])
      except Exception as e:
        await message.channel.send (f'Inscription en db fail !')
        print (f'{type(e).__name__} - {e}')
        error = True
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
    await self.logger.log('nickname_log', member, message, error)


  @commands.command(name='resetnickname', aliases=['rn'])
  async def reset_nickname(self, ctx, member: discord.Member = None):
    member = member or ctx.author
    guild_id = ctx.guild.id
    if not self.utils.has_role (ctx.author, guild_id):
      print ("Missing permissions")
      return
    sql = f"delete from last_nickname where guild_id='{guild_id}' and member_id='{member.id}'"
    error = False
    try:
      self.db.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      error = True
    await self.logger.log('nickname_log', member, ctx.message, error)


  @commands.command(name='next', aliases=['nextnickname'])
  async def next_nickname(self, ctx):
    member = ctx.author
    guild_id = ctx.guild.id
    nickname_delay = botconfig.config[str(guild_id)]['nickname_delay']
    sql = f'select  datetime(last_change, \'{nickname_delay}\') from last_nickname where guild_id=\'{guild_id}\' and member_id=\'{member.id}\''
    fetched = self.db.fetch_one_line (sql)
    print (f"for {sql}\nget {fetched}")
    await self.logger.log('nickname_log', member, ctx.message, False)
    if fetched:
      last_change = fetched [0]
      last_change_datetime = datetime.strptime (last_change, '%Y-%m-%d %H:%M:%S')
      duree = last_change_datetime - datetime.now()
      if duree.seconds > 1 and duree.days >= 0:
        total_seconds = duree.days*86400+duree.seconds
        print (f"duree.days: {duree.days}")
        print (f"total_seconds: {total_seconds}")
        await ctx.send (f"Il vous faut attendre encore {self.utils.format_time(total_seconds)}")
        return
    await ctx.send (f"Vous pouvez changer de pseudo dès maintenant")