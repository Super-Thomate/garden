import discord
import botconfig
from discord.ext import commands
try: # check if BeautifulSoup4 is installed
	from bs4 import BeautifulSoup
	soupAvailable = True
except:
	soupAvailable = False
import aiohttp

class Invitation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='invite')
  async def hello(self, ctx, member: discord.Member = None):
    """Send the invitation's link in a DM"""
    member = member or ctx.author
    try:
      url = await self.get_link()
    except Exception as e:
      await ctx.message.channel.send (f'**`ERROR:`** {type(e).__name__} - {e}')
    try:
      await member.send (url)
    except Exception as e:
      await ctx.message.channel.send (f'Oups je ne peux pas envoyer le DM !{type(e).__name__} - {e}')
  
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
    try:
      url = await self.get_link()
    except Exception as e:
      await message.channel.send (f'**`ERROR:`** {type(e).__name__} - {e}')
    try:
      await member.send (url)
    except Exception as e:
      await message.channel.send (f'Oups je ne peux pas envoyer le DM !{type(e).__name__} - {e}')

  async def get_link (self):
    url = botconfig.config['create_url'] #build the web adress
    async with aiohttp.ClientSession() as session:
      response = await session.get(url)
      soupObject = BeautifulSoup(await response.text(), "html.parser")
      return soupObject.p.get_text()
