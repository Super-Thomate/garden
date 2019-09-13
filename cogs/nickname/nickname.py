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
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    # Check if there is a nickname
    if not nickname:
      await self.logger.log('nickname_log', member, message, True)
      await ctx.message.add_reaction('❌')
      await ctx.channel.send (f"Vous n'avez pas donné de pseudo.")
      return
    # Check if I can change my nickname
    nickname_delay = self.utils.nickname_delay (guild_id) or botconfig.config[str(guild_id)]['nickname_delay']
    sql = f'select  datetime(last_change, \'{nickname_delay}\') from last_nickname where guild_id=\'{guild_id}\' and member_id=\'{member.id}\''
    fetched = self.db.fetch_one_line (sql)
    print (f"for {sql}\nget {fetched}")
    if fetched:
      last_change = fetched [0]
      last_change_datetime = datetime.strptime (last_change, '%Y-%m-%d %H:%M:%S')
      duree = last_change_datetime - datetime.now()
      if duree.seconds > 1 and duree.days >= 0:
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
      # write in db last_time
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
    if not error:
      # write in db current nickanme
      select = f"select * from nickname_current where guild_id='{guild_id}' and member_id='{member.id}' ;"
      fetched = self.db.fetch_one_line (select)
      print (f"fetched: {fetched}")
      if not fetched:
        sql = f"insert into nickname_current values ('{member.id}', '{guild_id}', ?) ;"
      else:
        sql = f"update nickname_current set nickname=? where member_id='{member.id}' and guild_id='{guild_id}' ;"
      try:
        self.db.execute_order (sql, [nickname])
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
    if not self.utils.is_authorized (ctx.author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
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
    await self.logger.log('nickname_log', ctx.author, ctx.message, error)


  @commands.command(name='next', aliases=['nextnickname'])
  async def next_nickname(self, ctx):
    member = ctx.author
    guild_id = ctx.guild.id
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    nickname_delay = self.utils.nickname_delay (guild_id) or botconfig.config[str(guild_id)]['nickname_delay']
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
    
    
  @commands.Cog.listener()
  async def on_member_join(self, member):
    select = f"select nickname from nickname_current where guild_id='{member.guild.id}' and member_id='{member.id}' ;"
    fetched = self.db.fetch_one_line (select)
    if fetched:
      nickname = fetched [0]
      try:
        await member.edit(nick = nickname)
      except Exception as e:
        print (f'{type(e).__name__} - {e}')
    return

  @commands.command(name='updatenickname')
  async def update_nickname(self, ctx):
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utilisez cette commande pour le moment.")
      return
    try:
      for member in ctx.guild.members:
        if member.nick:
          select = (   f"select nickname from nickname_current"+
                       f" where guild_id='{guild_id}' and member_id='{member.id}' ;"
                   )
          fetched = self.db.fetch_one_line (select)
          sql = ""
          if not fetched:
            sql = (   f"insert into nickname_current values ('{member.id}', "+
                      f" '{guild_id}' , '{member.nick}') ;"
                  )
          elif not member.nick == fetched [0]:
            # Impossibru
            sql = (   f"update nickname_current set nickname='{member.nick}'"+
                      f" where guild_id='{guild_id}' and member_id='{member.id}' ;"
                  )
          if len (sql):
            self.db.execute_order (sql)
      await ctx.send ("Nickname updated")
    except Exception as e:
      await ctx.send ("An error occured")
      print (f"{type(e).__name__} - {e}")