import discord
import botconfig
from discord.ext import commands
from datetime import datetime
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import aiohttp

class Invitation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.log_channel = None
  
  @commands.command(name='invite')
  @commands.has_any_role('ModoBot', 'Bénévoles', 'Modos du discord', 'Fondateur-admin', 'Pèse dans le game', 'Modos stagiaires', 'Touristes bienveillant.e.s', 'Equipe de la plateforme')
  async def invite(self, ctx, member: discord.Member = None):
    """Send the invitation's link in a DM"""
    member = member or ctx.author
    error = False
    try:
      url = await self.get_link()
      await member.send (url)
    except Exception as e:
      await ctx.message.channel.send (f'Oups je ne peux pas envoyer le DM !{type(e).__name__} - {e}')
      error = True
    await self.log(member, ctx.message, error)
  
  @commands.Cog.listener('on_message')
  @commands.guild_only()
  async def invitation(self, message):
    """ Send the invitation's link in a DM
        if the word 'invitation' is found
        and the message was sent on a guild_channel
    """
    if (    (message.guild == None)
         or (not message.channel.id == botconfig.config['invitation_channel'])
         or (not "invitation" in message.content.lower())
       ):
      return
    member = message.author
    error = False
    try:
      url = await self.get_link()
      await member.send (url)
    except Exception as e:
      await message.channel.send (f'Oups je ne peux pas envoyer le DM !{type(e).__name__} - {e}')
      error = True
    await self.log(member, message, error)

  async def get_link (self):
    url = botconfig.config['create_url'] #build the web adress
    async with aiohttp.ClientSession() as session:
      response = await session.get(url)
      soupObject = BeautifulSoup(await response.text(), "html.parser")
      return soupObject.p.get_text()
  
  async def log(self, member, message, error):
    if not self.log_channel:
      log_channel = await self.bot.fetch_channel(botconfig.config['invitation_logs'])
      self.log_channel = log_channel
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    if error:
      colour = colour.from_rgb(255, 125, 125)
    embed = discord.Embed(colour=colour)
    embed.set_author(icon_url=member.avatar_url, name=str(member))
    embed.description = message.content
    embed.timestamp = datetime.today()
    embed.set_footer(text=f"ID: {message.id}")
    await self.log_channel.send(content=None, embed=embed)