import discord
import botconfig
import math
import urllib
import re
from discord.ext import commands
from datetime import datetime
import time
from ..logs import Logs
from database import Database
from Utils import Utils
try: # check if BeautifulSoup4 is installed
  from bs4 import BeautifulSoup
  soupAvailable = True
except:
  soupAvailable = False
import aiohttp

class Gallery(commands.Cog):
  def __init__(self, bot):
    self.bot                 = bot
    self.utils               = Utils()
    self.logger              = Logs(self.bot)
    self.db                  = Database()

  @commands.command(name='token')
  async def send_token(self, ctx, member: discord.Member = None):
    """Send the token's link in a DM"""
    member                   = member or ctx.author
    guild_id                 = ctx.guild.id
    if not self.utils.is_authorized (ctx.author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    error                    = False
    try:
      colour                 = discord.Colour(0)
      url                    = "Votre jeton:\n"+await self.get_galerie_link(guild_id, member)
      sql                    = f"select message from galerie_message where guild_id='{guild_id}'"
      galerie_message        = self.db.fetch_one_line (sql)
      if galerie_message:
        url = url+"\n\n"+galerie_message [0]
      colour                 = colour.from_rgb(170, 117, 79)
      icon_url               = "https://cdn.discordapp.com/attachments/494812564086194177/597037745344348172/LotusBlanc.png"
      name                   = self.bot.user.display_name
      embed                  = discord.Embed(colour=colour)
      embed.set_author(icon_url=icon_url, name=name)
      embed.description      = url
      embed.timestamp        = datetime.utcnow()
      await member.send (content=None, embed=embed)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      await ctx.message.channel.send (f"Oups il semblerait que {member.display_name} n'ait pas activé l'envoi de messages privés.")
      print (f" {type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      error                  = True
    await self.logger.log('galerie_log', ctx.author, ctx.message, error)

  @commands.command(name='setgallerychannel', aliases=['sgc'])
  async def set_gallery_channel(self, ctx, channel: discord.TextChannel = None):
    gallery_channel          = channel or ctx.channel
    member                   = ctx.author
    guild_id                 = ctx.message.guild.id
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if not self.utils.do_token (guild_id) and not botconfig.config[str(guild_id)]["do_token"]:
      return
    if (    self.utils.is_banned_user (ctx.command, ctx.author, ctx.guild.id)
         or self.utils.is_banned_role (ctx.command, ctx.author, ctx.guild.id)
       ):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    sql                      = f"select * from galerie_channel where guild_id='{guild_id}'"
    prev_gallery_channel     = self.db.fetch_one_line (sql)
    if not prev_gallery_channel:
      sql                    = f"INSERT INTO galerie_channel VALUES ('{gallery_channel.id}', '{guild_id}')"
    else:
      sql                    = f"update galerie_channel set channel_id='{gallery_channel.id}' where guild_id='{guild_id}'"
    self.db.execute_order(sql)
    await gallery_channel.send(self.utils.get_text(self.language_code, "gallery_channel_set"))

  @commands.command(name='gallerymessage', aliases=['gm'])
  async def set_gallery_message(self, ctx):
    guild_id                 = ctx.message.guild.id
    member                   = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await ctx.send(self.utils.get_text(self.language_code, "ask_new_gallery_message"))
    check                    = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg                      = await self.bot.wait_for('message', check=check)
    message                  = msg.content
    # message = re.escape(message)
    sql = f"select message from galerie_message where guild_id='{guild_id}'"
    prev_galerie_message     = self.db.fetch_one_line (sql)
    if not prev_galerie_message:
      sql                    = f"INSERT INTO galerie_message VALUES (?, '{guild_id}')"
    else:
      sql                    = f"update galerie_message set message=? where guild_id='{guild_id}'"
    try:
      self.db.execute_order(sql, [message])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
    await ctx.channel.send (f"Nouveau message : `{message}`")


  @commands.command(name='setgallerydelay', aliases=['sgd'])
  async def set_gallery_delay(self, ctx, delay: str = None):
    author                   = ctx.author
    guild_id                 = ctx.message.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    try:
      if not delay.isnumeric():
        delay                = self.utils.parse_time(delay)
      type_delay             = "gallery"
      select                 = (  "select delay from config_delay"+
                                  " where "+
                                 f" `type_delay`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      fetched                = self.db.fetch_one_line (select, [type_delay])
      if fetched:
        order                = (  "update config_delay"+
                                  " set `delay`=? "+
                                  " where "+
                                 f" `type_delay`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      else:
        order                = (  "insert into config_delay"+
                                  " (`delay`, `type_delay`, `guild_id`) "+
                                  " values "+
                                 f" (?, ?, '{guild_id}')"+
                                  ""
                               )
      self.db.execute_order (order, [delay, type_delay])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.Cog.listener('on_message')
  # @commands.guild_only()
  async def token(self, message):
    """
    Send the token's link in a DM
    if the word 'galerie' is found
    """
    if message.author == self.bot.user: # don't read yourself
      return
    if not (    ("galerie" in message.content.lower())
             or ("jeton" in message.content.lower())
           ):
      return
    if (message.guild == None):
      # DM => debile-proof
      author                 = message.author
      await author.trigger_typing() # add some tension !!
      for guild in self.bot.guilds:
        if guild.get_member(author.id):
          error              = False
          guild_id           = guild.id
          try:
            colour           = discord.Colour(0)
            url              = "Votre jeton:\n"+await self.get_galerie_link(guild_id, author)
            sql              = f"select message from galerie_message where guild_id='{guild_id}'"
            galerie_message  = self.db.fetch_one_line (sql)
            if galerie_message:
              url            = url+"\n\n"+galerie_message [0]
            colour           = colour.from_rgb(170, 117, 79)
            icon_url         = "https://cdn.discordapp.com/attachments/494812564086194177/597037745344348172/LotusBlanc.png"
            name             = "LotusBlanc"
            embed            = discord.Embed(colour=colour)
            embed.set_author(icon_url=icon_url, name=name)
            embed.description= url
            embed.timestamp  = datetime.utcnow()
            await author.send (content=None, embed=embed)
          except Exception as e:
            print (f" {type(e).__name__} - {e}")
            error            = True
          await self.logger.log_dm('galerie_log', author, message,guild, error)
          try:
            if error:
              await message.add_reaction('❌')
            else:
              await message.delete (delay=2)
              await message.add_reaction('✅')
          except Exception as e:
              print (f'{type(e).__name__} - {e}')
    else:
      guild_id               = message.channel.guild.id
      sql                    = f"select * from galerie_channel where guild_id='{message.channel.guild.id}'"
      galerie_channel        = self.db.fetch_one_line (sql)
      if galerie_channel:
        galerie_channel      = int (galerie_channel [0])
      if (message.channel.id == galerie_channel):
        member               = message.author
        error                = False
        try:
          colour             = discord.Colour(0)
          url                = "Votre jeton:\n"+await self.get_galerie_link(guild_id, member)
          sql                = f"select message from galerie_message where guild_id='{guild_id}'"
          galerie_message    = self.db.fetch_one_line (sql)
          if galerie_message:
            url              = url+"\n\n"+galerie_message [0]
          colour             = colour.from_rgb(170, 117, 79)
          icon_url           = "https://cdn.discordapp.com/attachments/494812564086194177/597037745344348172/LotusBlanc.png"
          name               = "LotusBlanc"
          embed              = discord.Embed(colour=colour)
          embed.set_author(icon_url=icon_url, name=name)
          embed.description  = url
          embed.timestamp    = datetime.utcnow()
          await member.send (content=None, embed=embed)
        except Exception as e:
          await message.channel.send (f"Oups il semblerait que tu n'aies pas activé l'envoi de messages privés.")
          print (f" {type(e).__name__} - {e}")
          error              = True
        await self.logger.log('galerie_log', member, message, error)
        try:
          if error:
            await message.add_reaction('❌')
          else:
            await message.delete (delay=2)
            await message.add_reaction('✅')
        except Exception as e:
            print (f'{type(e).__name__} - {e}')

  async def get_galerie_link (self, guild_id, author):
    url                      = (self.utils.token_url(guild_id) or botconfig.config[str(guild_id)]['create_url']['gallery']) + urllib.parse.urlencode({ 'user' : author.display_name}) #build the web adress
    return await self.get_text(url)

  async def get_text(self, url):
    async with aiohttp.ClientSession() as session:
      response               = await session.get(url)
      soupObject             = BeautifulSoup(await response.text(), "html.parser")
      return soupObject.p.get_text().replace(";","")