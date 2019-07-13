import discord
import botconfig
from discord.ext import commands
from datetime import datetime
from ..logs import Logs
from ..database import Database

class Nickname(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.command(name='nickname', aliases=['pseudo'])
  async def set_nickname(self, ctx, *, nickname: str = None):
    # Check if there is a nickname
    if not nickname:
      await self.logger.log('nickname_log', member, message, True)
      await ctx.message.add_reaction('❌')
      await ctx.channel.send (f"Vous n'avez pas donné de pseudo.")
      return
    # Check if I can change my nickname
    member = ctx.author
    guild_id = ctx.guild.id
    sql = f'select  datetime(last_change, '{nickname_delay}') from last_nickname where guild_id=\'{guild_id}\' and member_id=\'{member.id}\''
    fetched = self.db.fetch_one_line (sql)
    if fetched:
      last_change = fetched [0]
      last_change_datetime = datetime.strptime (last_change, '%Y-%m-%d %H:%M:%S')
      duree = last_change_datetime - datetime.now()
      if duree.seconds > 1:
        # I can'ttotal_seconds = duree.days*86400+duree.seconds
        await self.logger.log('nickname_log', member, message, True)
        await ctx.message.add_reaction('❌')
        await ctx.channel.send (f"Vous avez changé de pseudo récemment.\nIl vous faut attendre encore {self.format_time(total_seconds)}")
        return
    # Change my Nickname
    error = False
    try:
      member.nick = str
    except Exception as e:
      error = True
      print (f"{type(e).__name__} - {e}"})
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
    await self.logger.log('nickname_log', member, message, error)

  def format_time(self, timestamp):
    timer = [   ["j", 86400]
              , ["h", 3600]
              , ["m", 60]
              , ["s", 1]
            ]
    current = timestamp
    to_ret = ""
    for obj_time in timer:
      if math.floor (current/obj_time [1]) > 0:
        to_ret += str(math.floor (current/obj_time [1]))+obj_time[0]+" "
        current = current%obj_time [1]
    return to_ret