import discord
import botconfig
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

  @commands.command(name='invite')
  @commands.has_any_role(*botconfig.config['invite_roles'])
  async def invite(self, ctx, member: discord.Member = None):
    """Send the invitation's link in a DM"""
    member = member or ctx.author
    error = False
    try:
      url = await self.get_link()
      await member.send (url)
    except Exception as e:
      await ctx.message.channel.send (f'Oups je ne peux pas envoyer le DM ! {type(e).__name__} - {e}')
      error = True
    await self.logger.log('invite_log', member, ctx.message, error)

  @commands.command(name='setinvitechannel', aliases=['sic'])
  @commands.has_any_role(*botconfig.config['invite_roles'])
  async def invite(self, ctx):
    """Set the invitation channel"""
    error = False
    try:
      url = await self.get_link()
      await member.send (url)
    except Exception as e:
      await ctx.message.channel.send (f'Oups je ne peux pas envoyer le DM ! {type(e).__name__} - {e}')
      error = True
    await self.logger.log('invite_log', member, ctx.message, error)

  @commands.Cog.listener('on_message')
  @commands.guild_only()
  async def invitation(self, message):
    """ Send the invitation's link in a DM
        if the word 'invitation' is found
        and the message was sent on a guild_channel
    """
    invite_channel = self.db.fetch_one("select * from invite_channel where guild_id='{message.channel.guild.id}'")
    galerie_channel = self.db.fetch_one("select * from galerie_channel where guild_id='{message.channel.guild.id}'")
    if (    (message.guild == None)
         or (     (not message.channel.id == invite_channel)
              and (not message.channel.id == galerie_channel)
            )
         or (     (not "invitation" in message.content.lower())
              and (not "compte" in message.content.lower())
            )
       ):
      return
    member = message.author
    error = False
    try:
      if "invitation" in message.content.lower():
        url = await self.get_invitation_link()
      else:
        url = await self.get_galerie_link(member)

      await member.send (url)
    except Exception as e:
      await message.channel.send (f'Oups je ne peux pas envoyer le DM ! {type(e).__name__} - {e}')
      error = True
    if "invitation" in message.content.lower():
      await self.logger.log('invite_log', member, message, error)
    else:
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