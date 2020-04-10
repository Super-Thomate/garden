import math
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import Utils
import botconfig
import database
from ..logs import Logs
from core import logger

class Nickname(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  @commands.command(name='nickname', aliases=['pseudo'])
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def set_nickname(self, ctx, *, nickname: str = None):
    message = ctx.message
    member = ctx.author
    guild_id = ctx.guild.id
    # Check if there is a nickname
    if not nickname:
      await self.logger.log('nickname_log', member, message, True)
      await ctx.message.add_reaction('❌')
      await ctx.channel.send(Utils.get_text(ctx.guild.id, "nickname_none_given"))
      return
    # Check if I can change my nickname
    nickname_delay = Utils.nickname_delay(guild_id)
    sql = f'select last_change from last_nickname where guild_id=\'{guild_id}\' and member_id=\'{member.id}\''
    fetched = database.fetch_one_line(sql)
    if nickname_delay and fetched and fetched[0]:
      last_change = time.mktime(datetime.strptime(fetched[0], '%Y-%m-%d %H:%M:%S').timetuple())
      if str(nickname_delay).isnumeric():
        nickname_delay = int(nickname_delay)
      else:
        nickname_delay = Utils.convert_str_to_time(nickname_delay)
      duree = math.floor((last_change + nickname_delay) - time.time())
      if duree > 0:
        # I can't
        total_seconds = duree
        await self.logger.log('nickname_log', member, message, True)
        await ctx.message.add_reaction('❌')
        await ctx.channel.send(Utils.get_text(ctx.guild.id, "nickname_changed_recently").format(Utils.format_time(total_seconds)))
        return

    # Remove warn and next limit (spam of command `next` without rename)
    sql1 = "DELETE FROM nickname_next_limit WHERE member_id=? AND guild_id=? ;"
    sql2 = "DELETE FROM nickname_next_warn WHERE member_id=? AND guild_id=? ;"
    database.execute_order(sql1, [member.id, guild_id])
    database.execute_order(sql2, [member.id, guild_id])

    # Change my Nickname
    error = False
    try:
      if member.name == nickname:
        # nickname = nickname+"\uFEFF_"
        nickname = nickname[0] + "\u17b5" + nickname[1:]
      await member.edit(nick=nickname)
    except Exception as e:
      error = True
      logger ("nickname::set_nickname", f" change nickname {type(e).__name__} - {e}")
    if not error:
      # write in db last_time
      select = f"select * from last_nickname where guild_id='{guild_id}' and member_id='{member.id}'"
      fetched = database.fetch_one_line(select)
      if not fetched:
        sql = f"insert into last_nickname values ('{member.id}', '{guild_id}', datetime('{datetime.now()}'))"
      else:
        sql = f"update last_nickname set last_change=datetime('{datetime.now()}') where member_id='{member.id}' and guild_id='{guild_id}'"
      try:
        database.execute_order(sql, [])
      except Exception as e:
        await message.channel.send(Utils.get_text(ctx.guild.id, "error_database_writing"))
        logger ("nickname::set_nickname", f'last_time {type(e).__name__} - {e}')
        error = True
    if not error:
      # write in db current nickanme
      select = f"select * from nickname_current where guild_id='{guild_id}' and member_id='{member.id}' ;"
      fetched = database.fetch_one_line(select)
      if not fetched:
        sql = f"insert into nickname_current values ('{member.id}', '{guild_id}', ?) ;"
      else:
        sql = f"update nickname_current set nickname=? where member_id='{member.id}' and guild_id='{guild_id}' ;"
      try:
        database.execute_order(sql, [nickname])
      except Exception as e:
        await message.channel.send(Utils.get_text(ctx.guild.id, "error_database_writing"))
        logger ("nickname::set_nickname", f'current_nickname {type(e).__name__} - {e}')
        error = True
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
    await self.logger.log('nickname_log', member, message, error)

  @commands.command(name='resetnickname', aliases=['rn'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def reset_nickname(self, ctx, member: discord.Member = None):
    member = member or ctx.author
    guild_id = ctx.guild.id
    sql = f"delete from last_nickname where guild_id='{guild_id}' and member_id='{member.id}'"
    error = False
    try:
      database.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("nickname::reset_nickname", f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      error = True
    await self.logger.log('nickname_log', ctx.author, ctx.message, error)

  def _add_next_timer(self, member_id: int, guild_id: int):
    # Auto rename user after X minutes if they havent renamed themselves (see Cron)
    sql = "SELECT timer FROM nickname_next_timer WHERE guild_id=? ;"
    response = database.fetch_one_line(sql, [guild_id])
    timer = response[0] if response else 15

    sql = "INSERT INTO nickname_next_limit VALUES (?, ?, datetime(?)) ;"
    limit = datetime.now() + timedelta(minutes=timer)
    database.execute_order(sql, [member_id, guild_id, limit])


  @commands.command(name='next', aliases=['nextnickname'])
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def next_nickname(self, ctx):
    member = ctx.author
    guild_id = ctx.guild.id
    nickname_delay = Utils.nickname_delay(guild_id) or botconfig.config[str(guild_id)]['nickname_cannot_change']
    sql = f'select last_change from last_nickname where guild_id=\'{guild_id}\' and member_id=\'{member.id}\''
    fetched = database.fetch_one_line(sql)
    error = False
    if fetched:
      last_timestamp = time.mktime(datetime.strptime(fetched[0], "%Y-%m-%d %H:%M:%S").timetuple())
      if str(nickname_delay).isnumeric():
        nickname_delay = int(nickname_delay)
      else:
        nickname_delay = Utils.convert_str_to_time(nickname_delay)
      duree = math.floor((last_timestamp + nickname_delay) - time.time())
      if duree > 0:
        await ctx.channel.send(Utils.get_text(
          ctx.guild.id,
          "nickname_cannot_change")
                               .format(Utils.format_time(duree)))
        error = True
    if not error:
      self._add_next_timer(member.id, guild_id)
      await ctx.send(Utils.get_text(ctx.guild.id, "nickname_can_change"))
    await self.logger.log('nickname_log', member, ctx.message, error)

  @commands.command(name='setnickcd', aliases=['ncd'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_nickname_cd(self, ctx):
    author = ctx.author
    guild_id = ctx.guild.id
    error = False
    ask = await ctx.send(Utils.get_text(guild_id, "nickname_new_delay"))
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    old_delay = Utils.nickname_delay(guild_id)
    try:
      delay = Utils.parse_time(msg.content)
    except Exception as e:
      error = True
      await ctx.send(f"{type(e).__name__} -{e}")
    else:
      if not old_delay:
        sql = "insert into config_delay (`delay`,`type_delay`,`guild_id`) values (?,?,?) ;"
      else:
        sql = "update config_delay set delay=? where type_delay=? and guild_id=? ;"
      try:
        database.execute_order(sql, [delay, 'nickname', guild_id])
      except Exception as e:
        error = True
        await ctx.send(f"{type(e).__name__} -{e}")
    # type delay = nickname
    if not error:
      await ctx.message.add_reaction('✅')
      await msg.add_reaction('✅')
    else:
      await ctx.message.add_reaction('❌')
      await msg.add_reaction('❌')
    await ctx.message.delete(delay=1.5)
    await ask.delete(delay=1.5)
    await msg.delete(delay=1.5)
    await self.logger.log('nickname_log', author, ctx.message, error)
    await self.logger.log('nickname_log', author, msg, error)

  @commands.command(name='getnickcd')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def get_nickname_cd(self, ctx):
    author = ctx.author
    guild_id = ctx.guild.id
    error = False
    nickname_delay = Utils.nickname_delay(guild_id)
    await ctx.send(Utils.get_text(guild_id, "nickname_delay").format(Utils.format_time(nickname_delay)))
    # type delay = nickname
    await self.logger.log('nickname_log', author, ctx.message, error)

  @commands.Cog.listener()
  async def on_member_join(self, member):
    select = f"select nickname from nickname_current where guild_id='{member.guild.id}' and member_id='{member.id}' ;"
    fetched = database.fetch_one_line(select)
    if fetched:
      nickname = fetched[0]
      try:
        await member.edit(nick=nickname)
      except Exception as e:
        logger ("nickname::on_member_join", f'readd nickname{type(e).__name__} - {e}')
    return

  @commands.command(name='updatenickname')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def update_nickname(self, ctx):
    author = ctx.author
    guild_id = ctx.guild.id
    try:
      for member in ctx.guild.members:
        if member.nick:
          select = (f"select nickname from nickname_current" +
                    f" where guild_id='{guild_id}' and member_id='{member.id}' ;"
                    )
          fetched = database.fetch_one_line(select)
          sql = ""
          if not fetched:
            sql = (f"insert into nickname_current values ('{member.id}', " +
                   f" '{guild_id}' , '{member.nick}') ;"
                   )
          elif not member.nick == fetched[0]:
            # Impossibru
            sql = (f"update nickname_current set nickname='{member.nick}'" +
                   f" where guild_id='{guild_id}' and member_id='{member.id}' ;"
                   )
          if len(sql):
            database.execute_order(sql)
      await ctx.send(Utils.get_text(ctx.guild.id, "nickname_updated"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_occured").format(f"{type(e).__name__}", f"{e}"))
      logger ("nickname::update_nickname", f"{type(e).__name__} - {e}")

  @commands.command(name='checknickname')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def check_nickname(self, ctx, member: discord.Member = None):
    member = member or ctx.author
    if member.nick:
      await ctx.send("{0} a.k.a. {1}".format(str(member), member.nick))
    else:
      await ctx.send("{0} with no nickname".format(str(member)))

  @commands.command(name='settrollnicknames', aliases=['stn'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_troll_nicknames(self, ctx: commands.Context, *, nicknames: str):
    nickname_list = [nickname.strip() for nickname in nicknames.split('|')]
    for name in nickname_list:
      if name == '' or len(name) >= 32:
        await ctx.send(Utils.get_text(ctx.guild.id, "nickname_troll_too_long").format(name))
        return

    to_save = "|".join(nickname_list)
    sql = "SELECT * FROM nickname_next_troll_nickname WHERE guild_id=? ;"
    update = database.fetch_one_line(sql, [ctx.guild.id])
    if not update:
      sql = "INSERT INTO nickname_next_troll_nickname VALUES (?, ?)"
    else:
      sql = "UPDATE nickname_next_troll_nickname SET nicknames=? WHERE guild_id=? ;"
    database.execute_order(sql, [to_save, ctx.guild.id])

    await ctx.send(Utils.get_text(ctx.guild.id, "nickname_troll_saved"))

  @commands.command(name='setnexttimer', aliases=['snt'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_troll_nicknames(self, ctx: commands.Context, timer: int):
    if timer <= 0:
      await ctx.send(Utils.get_text(ctx.guild.id, "nickname_timer_invalid"))
      await ctx.message.add_reaction('❌')
      return
    sql = "SELECT timer FROM nickname_next_timer WHERE guild_id=? ;"
    response = database.fetch_one_line(sql, [ctx.guild.id])
    if response:
      sql = "UPDATE nickname_next_timer SET timer=? WHERE guild_id=? ;"
    else:
      sql = "INSERT INTO nickname_next_timer VALUES (?, ?) ;"

    database.execute_order(sql, [timer, ctx.guild.id])
    await ctx.message.add_reaction('✅')
