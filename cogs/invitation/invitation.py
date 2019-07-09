import discord
import botconfig
import math
import urllib
import re
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
  
  def has_role (self, member, guild_id):
    for obj_role in member.roles:
      if (    (obj_role.name in botconfig.config[str(guild_id)]['roles'])
           or (obj_role.id in botconfig.config[str(guild_id)]['roles'])
         ):
        return True
    return False

  @commands.command(name='inviteuser', aliases=['iu'])
  async def invite(self, ctx, member: discord.Member = None):
    """Send the invitation's link in a DM"""
    member = member or ctx.author 
    guild_id = ctx.guild.id
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_invite"]:
      return
    error = False
    colour = discord.Colour(0)
    try:
      url = "Votre lien d'invitation:\n"+await self.get_invitation_link(guild_id)
      sql = f"select message from invite_message where guild_id='{guild_id}'"
      invite_message = self.db.fetch_one_line (sql)
      if invite_message:
        url = url+"\n"+invite_message [0]
      colour = colour.from_rgb(255, 51, 124)
      icon_url="https://cdn.discordapp.com/attachments/597091535242395649/597091654847037514/Plan_de_travail_18x.png"
      name="Steven Universe Fantasy"
      embed =  discord.Embed(colour=colour)
      embed.set_author(icon_url=icon_url, name=name)
      embed.description = url
      embed.timestamp = datetime.today()
      await member.send (content=None, embed=embed)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      await ctx.message.channel.send (f"Oups il semblerait que {member.display_name} n'ait pas activé l'envoi de messages privés.")
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      error = True
    await self.logger.log('invite_log', member, ctx.message, error)


  @commands.command(name='resetinvite', aliases=['ri'])
  async def reset_invite(self, ctx, member: discord.Member = None):
    member = member or ctx.author
    guild_id = ctx.guild.id
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_invite"]:
      return
    sql = f"delete from last_invite where guild_id='{guild_id}' and member_id='{member.id}'"
    error = False
    try:
      self.db.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      error = True
    await self.logger.log('invite_log', member, ctx.message, error)

  @commands.command(name='token')
  async def token(self, ctx, member: discord.Member = None):
    """Send the token's link in a DM"""
    member = member or ctx.author
    guild_id = ctx.guild.id
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_token"]:
      return
    error = False
    try:
      colour = discord.Colour(0)
      url = "Votre jeton:\n"+await self.get_galerie_link(guild_id, member)
      sql = f"select message from galerie_message where guild_id='{guild_id}'"
      galerie_message = self.db.fetch_one_line (sql)
      if galerie_message:
        url = url+"\n\n"+galerie_message [0]
      colour = colour.from_rgb(170, 117, 79)
      icon_url="https://cdn.discordapp.com/attachments/494812564086194177/597037745344348172/LotusBlanc.png"
      name="LotusBlanc"
      embed =  discord.Embed(colour=colour)
      embed.set_author(icon_url=icon_url, name=name)
      embed.description = url
      embed.timestamp = datetime.today()
      await member.send (content=None, embed=embed)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      await ctx.message.channel.send (f"Oups il semblerait que {member.display_name} n'ait pas activé l'envoi de messages privés.")
      print (f" {type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      error = True
    await self.logger.log('galerie_log', member, ctx.message, error)

  @commands.command(name='setinvitechannel', aliases=['sic'])
  async def set_invite_channel(self, ctx, channel: discord.TextChannel = None):
    invite_channel = channel or ctx.channel
    member = ctx.author
    guild_id = ctx.message.guild.id
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_invite"]:
      return
    sql = f"select * from invite_channel where guild_id='{guild_id}'"
    print (sql)
    prev_invite_channel = self.db.fetch_one_line (sql)
    print (prev_invite_channel)
    if not prev_invite_channel:
      sql = f"INSERT INTO invite_channel VALUES ('{invite_channel.id}', '{guild_id}')"
    else:
      sql = f"update invite_channel set channel_id='{invite_channel.id}' where guild_id='{guild_id}'"
    print (sql)
    self.db.execute_order(sql, [])
    await invite_channel.send ("Request for invite will be put here")

  @commands.command(name='setgaleriechannel', aliases=['sgc'])
  async def set_galerie_channel(self, ctx, channel: discord.TextChannel = None):
    galerie_channel = channel or ctx.channel
    member = ctx.author
    guild_id = ctx.message.guild.id
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_token"]:
      return
    sql = f"select * from galerie_channel where guild_id='{guild_id}'"
    prev_galerie_channel = self.db.fetch_one_line (sql)
    if not prev_galerie_channel:
      sql = f"INSERT INTO galerie_channel VALUES ('{galerie_channel.id}', '{guild_id}')"
    else:
      sql = f"update galerie_channel set channel_id='{galerie_channel.id}' where guild_id='{guild_id}'"
    self.db.execute_order(sql, [])
    await galerie_channel.send ("Request for galerie will be put here")

  @commands.command(name='invitemessage', aliases=['im'])
  async def set_invite_message(self, ctx, *args):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_invite"]:
      return
    message = ' '.join(arg for arg in args)
    # message = re.escape(message)
    sql = f"select message from invite_message where guild_id='{guild_id}'"
    prev_invite_message = self.db.fetch_one_line (sql)
    if not prev_invite_message:
      sql = f"INSERT INTO invite_message VALUES (?, '{guild_id}')"
    else:
      sql = f"update invite_message set message=? where guild_id='{guild_id}'"
    print (sql)
    try:
      self.db.execute_order(sql, [message])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
    await ctx.channel.send (f"Nouveau message : `{message}`")

  @commands.command(name='galeriemessage', aliases=['gm'])
  async def set_galerie_message(self, ctx, *args):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.has_role (member, guild_id):
      print ("Missing permissions")
      return
    if not botconfig.config[str(guild_id)]["do_token"]:
      return
    message = ' '.join(arg for arg in args)
    # message = re.escape(message)
    sql = f"select message from galerie_message where guild_id='{guild_id}'"
    prev_galerie_message = self.db.fetch_one_line (sql)
    if not prev_galerie_message:
      sql = f"INSERT INTO galerie_message VALUES (?, '{guild_id}')"
    else:
      sql = f"update galerie_message set message=? where guild_id='{guild_id}'"
    print (sql)
    try:
      self.db.execute_order(sql, [message])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
    await ctx.channel.send (f"Nouveau message : `{message}`")


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
    guild_id = message.channel.guild.id
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
                  and (botconfig.config[str(guild_id)]["do_invite"])
                )
             or (     (    ("galerie" in message.content.lower())
                        or ("jeton" in message.content.lower())
                      )
                  and (message.channel.id == galerie_channel)
                  and (botconfig.config[str(guild_id)]["do_token"])
                )
           ):
      print (f"content: {message.content.lower()}")
      print (("invitation" in message.content.lower()) or ("compte" in message.content.lower()) or ("galerie" in message.content.lower()) or ("jeton" in message.content.lower()))
      print (f"message.channel.id: {message.channel.id}")
      print (f"invite_channel: {invite_channel}")
      print ((message.channel.id == invite_channel) or (message.channel.id == galerie_channel))
      print ((((("invitation" in message.content.lower())or ("compte" in message.content.lower()))and (message.channel.id == invite_channel)) or ((("galerie" in message.content.lower())or ("jeton" in message.content.lower())) and (message.channel.id == galerie_channel))))
      return
    member = message.author
    error = False
    # If I ask for invite, we check for the last time i asked for it
    if (     (    ("invitation" in message.content.lower())
               or ("compte" in message.content.lower())
             )
         and (message.channel.id == invite_channel)
         and (botconfig.config[str(guild_id)]["do_invite"])
       ):
      #sql = f"select last from last_invite where guild_id='{message.guild.id}' and member_id='{member.id}'"
      invite_delay = botconfig.config[str(guild_id)]['invite_delay']
      sql = f"select datetime(last, '{invite_delay}') from last_invite where guild_id='{message.guild.id}' and member_id='{member.id}'"
      last_invite = self.db.fetch_one_line (sql)
      print (sql)
      print (last_invite)
      if last_invite:
        last = last_invite[0]
        last_datetime = datetime.strptime (last, '%Y-%m-%d %H:%M:%S')
        duree = last_datetime - datetime.now()
        if duree.seconds > 1:
          total_seconds = duree.days*86400+duree.seconds
          await message.add_reaction('❌')
          await message.channel.send(f"Vous avez déjà demandé une invitation récemment.\nIl vous faut attendre encore {self.format_time(total_seconds)}")
          return
    try:
      colour = discord.Colour(0)
      if (     (    ("invitation" in message.content.lower())
                 or ("compte" in message.content.lower())
               )
           and (message.channel.id == invite_channel)
           and (botconfig.config[str(guild_id)]["do_invite"])
         ):
        url = "Votre lien d'invitation:\n"+await self.get_invitation_link(guild_id)
        sql = f"select message from invite_message where guild_id='{guild_id}'"
        invite_message = self.db.fetch_one_line (sql)
        if invite_message:
          url = url+"\n\n"+invite_message [0]
        colour = colour.from_rgb(255, 51, 124)
        icon_url="https://cdn.discordapp.com/attachments/597091535242395649/597091654847037514/Plan_de_travail_18x.png"
        name="Steven Universe Fantasy"
        #embed.set_footer(text=f"ID: {message.id}")
      elif (     (    ("galerie" in message.content.lower())
                   or ("jeton" in message.content.lower())
                 )
             and (message.channel.id == galerie_channel)
           and (botconfig.config[str(guild_id)]["do_token"])
           ):
        url = "Votre jeton:\n"+await self.get_galerie_link(guild_id, member)
        sql = f"select message from galerie_message where guild_id='{guild_id}'"
        galerie_message = self.db.fetch_one_line (sql)
        if galerie_message:
          url = url+"\n\n"+galerie_message [0]
        colour = colour.from_rgb(170, 117, 79)
        icon_url="https://cdn.discordapp.com/attachments/494812564086194177/597037745344348172/LotusBlanc.png"
        name="LotusBlanc"
      embed =  discord.Embed(colour=colour)
      embed.set_author(icon_url=icon_url, name=name)
      embed.description = url
      embed.timestamp = datetime.today()
      await member.send (content=None, embed=embed)
    except Exception as e:
      await message.channel.send (f"Oups il semblerait que tu n'aies pas activé l'envoi de messages privés.")
      print (f" {type(e).__name__} - {e}")
      error = True
    if (     (    ("invitation" in message.content.lower())
               or ("compte" in message.content.lower())
             )
         and (message.channel.id == invite_channel)
         and (botconfig.config[str(guild_id)]["do_invite"])
         and not error
       ):
      # LOG LAST INVITE
      sql = f"select * from last_invite where guild_id='{message.guild.id}' and member_id='{member.id}'"
      last_invite = self.db.fetch_one_line (sql)
      if not last_invite:
        sql = f"insert into last_invite values ('{member.id}', '{message.guild.id}', datetime('now'))"
      else:
        sql = f"update last_invite set last=datetime('now') where member_id='{member.id}' and guild_id='{message.guild.id}'"
      try:
        self.db.execute_order (sql, [])
      except Exception as e:
        await message.channel.send (f'Inscription en db fail !')
        print (f'{type(e).__name__} - {e}')
        error = True
      await self.logger.log('invite_log', member, message, error)
    elif (     (    ("galerie" in message.content.lower())
                 or ("jeton" in message.content.lower())
               )
           and (message.channel.id == galerie_channel)
           and (botconfig.config[str(guild_id)]["do_token"])
         ):
      await self.logger.log('galerie_log', member, message, error)
    if error:
      await message.add_reaction('❌')
    else:
      await message.add_reaction('✅')


  async def get_invitation_link (self, guild_id):
    url = botconfig.config[str(guild_id)]['create_url']['invitation'] #build the web adress
    return await self.get_text(url)

  async def get_galerie_link (self, guild_id, author):
    url = botconfig.config[str(guild_id)]['create_url']['gallery'] + urllib.parse.urlencode({ 'user' : author.display_name}) #build the web adress
    return await self.get_text(url)

  async def get_text(self, url):
    async with aiohttp.ClientSession() as session:
      response = await session.get(url)
      soupObject = BeautifulSoup(await response.text(), "html.parser")
      return soupObject.p.get_text().replace(";","")

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