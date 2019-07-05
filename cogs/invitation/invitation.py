import discord
import botconfig
import math
import urllib
from discord.ext import commands
from datetime import datetime
from ..logs import Logs
from ..database import Database
try: # check if BeautifulSoup4 is installed
	 from bs4 import BeautifulSoup
	 soupAvailable = True
except:
	 soupAvailable = False
import aiohttp

class Invitation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)
    self.db = Database()
    self.db.test ("un test")

  @commands.command(name='invite')
  @commands.has_any_role(*botconfig.config['invite_roles'])
  async def invite(self, ctx, member: discord.Member = None):
    """Send the invitation's link in a DM"""
    member = member or ctx.author
    error = False
    try:
      url = await self.get_invitation_link()
      await member.send (url)
    except Exception as e:
      await ctx.message.channel.send (f'Oups je ne peux pas envoyer le DM ! {type(e).__name__} - {e}')
      error = True
    await self.logger.log('invite_log', member, ctx.message, error)

  @commands.command(name='setinvitechannel', aliases=['sic'])
  @commands.has_any_role(*botconfig.config['invite_roles'])
  async def set_invite_channel(self, ctx, channel: discord.TextChannel = None):
    invite_channel = channel or ctx.channel
    guild_id = ctx.message.guild.id
    sql = f"select * from invite_channel where guild_id='{guild_id}'"
    prev_invite_channel = self.db.fetch_one_line (sql)
    if not prev_invite_channel:
      sql = f"INSERT INTO galerie_channel VALUES ('{invite_channel.id}', '{guild_id}')"
    else:
      sql = f"update invite_channel set channel_id='{invite_channel.id}' where guild_id='{guild_id}'"
    self.db.execute_order(sql)
    await invite_channel.send ("Request for invite will be put here")

  @commands.command(name='setgaleriechannel', aliases=['sgc'])
  @commands.has_any_role(*botconfig.config['galerie_roles'])
  async def set_galerie_channel(self, ctx, channel: discord.TextChannel = None):
    galerie_channel = channel or ctx.channel
    guild_id = ctx.message.guild.id
    sql = f"select * from galerie_channel where guild_id='{guild_id}'"
    prev_galerie_channel = self.db.fetch_one_line (sql)
    if not prev_galerie_channel:
      sql = f"INSERT INTO galerie_channel VALUES ('{galerie_channel.id}', '{guild_id}')"
    else:
      sql = f"update galerie_channel set channel_id='{galerie_channel.id}' where guild_id='{guild_id}'"
    self.db.execute_order(sql)
    await galerie_channel.send ("Request for galerie will be put here")


  @commands.Cog.listener('on_message')
  @commands.guild_only()
  async def invitation(self, message):
    """ Send the invitation's link in a DM
        if the word 'invitation' is found
        and the message was sent on a guild_channel
    """
    if (message.guild == None):
      return
    if message.author == self.bot.user:
      return
    sql = f"select * from invite_channel where guild_id='{message.channel.guild.id}'"
    invite_channel = self.db.fetch_one_line (sql)
    if invite_channel:
      invite_channel = int (invite_channel [0])
    sql = f"select * from galerie_channel where guild_id='{message.channel.guild.id}'"
    galerie_channel = self.db.fetch_one_line (sql)
    if galerie_channel:
      galerie_channel = int (galerie_channel [0])
    if not (    (     (    ("invitation" in message.content.lower())
                        or ("compte" in message.content.lower())
                      )
                  and (message.channel.id == invite_channel)
                )
             or (     (    ("galerie" in message.content.lower())
                        or ("jeton" in message.content.lower())
                      )
                  and (message.channel.id == galerie_channel)
                )
           ):
      print ("FALSE !")
      return
    member = message.author
    error = False
    # If I ask for invite, we check for the last time i asked for it
    if (     (    ("invitation" in message.content.lower())
               or ("compte" in message.content.lower())
             )
         and (message.channel.id == invite_channel)
       ):
      sql = f"select last from last_invite where guild_id='{message.guild.id}' and member_id='{member.id}'"
      sql = f"select datetime(last, '6 months') from last_invite where guild_id='{message.guild.id}' and member_id='{member.id}'"
      last_invite = self.db.fetch_one_line (sql)
      if last_invite:
        last = last_invite[0]
        last_datetime = datetime.strptime (last, '%Y-%m-%d %H:%M:%S')
        duree = last_datetime - datetime.now()
        print (duree)
        print (duree.seconds)
        if duree.seconds > 1:
          await message.channel.send(f"Vous avez déjà demandé une invitation récemment.\nIl vous faut attendre encore {self.format_time(duree.seconds)}")
          return
    try:
      if (     (    ("invitation" in message.content.lower())
                 or ("compte" in message.content.lower())
               )
           and (message.channel.id == invite_channel)
         ):
        url = await self.get_invitation_link()
      elif (     (    ("galerie" in message.content.lower())
                   or ("jeton" in message.content.lower())
                 )
             and (message.channel.id == galerie_channel)
           ):
        url = await self.get_galerie_link(member)

      await member.send (url)
    except Exception as e:
      await message.channel.send (f'Oups je ne peux pas envoyer le DM ! {type(e).__name__} - {e}')
      error = True
    if (     (    ("invitation" in message.content.lower())
               or ("compte" in message.content.lower())
             )
         and (message.channel.id == invite_channel)
       ):
      # LOG LAST INVITE
      sql = f"select * from last_invite where guild_id='{message.guild.id}' and member_id='{member.id}'"
      last_invite = self.db.fetch_one_line (sql)
      if not last_invite:
        sql = f"insert into last_invite values ('{member.id}', '{message.guild.id}', datetime('now'))"
      else:
        sql = f"update last_invite set last=datetime('now') where member_id='{member.id}' and guild_id='{message.guild.id}'"
      try:
        self.db.execute_order (sql)
      except Exception as e:
        await message.channel.send (f'Inscription en db fail ! {type(e).__name__} - {e}')
        error = True
      await self.logger.log('invite_log', member, message, error)
    elif (     (    ("galerie" in message.content.lower())
                 or ("jeton" in message.content.lower())
               )
           and (message.channel.id == galerie_channel)
         ):
      await self.logger.log('galerie_log', member, message, error)


  async def get_invitation_link (self):
    url = botconfig.config['create_url']['invitation'] #build the web adress
    return await self.get_text(url)

  async def get_galerie_link (self, author):
    url = botconfig.config['create_url']['galerie'] + urllib.parse.urlencode({ 'user' : author.display_name}) #build the web adress
    return await self.get_text(url)

  async def get_text(self, url):
    async with aiohttp.ClientSession() as session:
      response = await session.get(url)
      soupObject = BeautifulSoup(await response.text(), "html.parser")
      return soupObject.p.get_text()
      
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