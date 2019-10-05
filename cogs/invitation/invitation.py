import math
import time
from datetime import datetime

import discord
from discord.ext import commands

import Utils
import botconfig
import database
from ..logs import Logs

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

  @commands.command(name='inviteuser', aliases=['iu'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def invite(self, ctx, member: discord.Member = None):
    """Send the invitation's link in a DM"""
    member                   = member or ctx.author
    guild_id                 = ctx.guild.id
    error                    = False
    colour                   = discord.Colour(0)
    try:
      url                    = "Votre lien d'invitation:\n"+await self.get_invitation_link(guild_id)
      sql                    = f"select message from invite_message where guild_id='{guild_id}'"
      invite_message         = database.fetch_one_line (sql)
      if invite_message:
        url                  = url+"\n"+invite_message [0]
      colour                 = colour.from_rgb(255, 51, 124)
      icon_url               = "https://cdn.discordapp.com/attachments/597091535242395649/597091654847037514/Plan_de_travail_18x.png"
      name                   = "Steven Universe Fantasy"
      embed                  = discord.Embed(colour=colour)
      embed.set_author(icon_url=icon_url, name=name)
      embed.description      = url
      embed.timestamp        = datetime.utcnow()
      await member.send (content=None, embed=embed)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      await ctx.message.channel.send (Utils.get_text(ctx.guild.id, "user_disabled_PM").format(member.display_name))

      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      error = True
    await self.logger.log('invite_log', ctx.author, ctx.message, error)

  @commands.command(name='resetinvite', aliases=['ri'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def reset_invite(self, ctx, member: discord.Member = None):
    member                   = member or ctx.author
    guild_id                 = ctx.guild.id
    sql                      = f"delete from last_invite where guild_id='{guild_id}' and member_id='{member.id}'"
    error                    = False
    try:
      database.execute_order(sql)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      error                  = True
    await self.logger.log('invite_log', ctx.author, ctx.message, error)

  @commands.command(name='setinvitechannel', aliases=['sic'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_invite_channel(self, ctx, channel: discord.TextChannel = None):
    invite_channel           = channel or ctx.channel
    member                   = ctx.author
    guild_id                 = ctx.message.guild.id
    if not Utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if Utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(Utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    sql                      = f"select * from invite_channel where guild_id='{guild_id}'"
    prev_invite_channel      = database.fetch_one_line (sql)
    if not prev_invite_channel:
      sql                    = f"INSERT INTO invite_channel VALUES ('{invite_channel.id}', '{guild_id}')"
    else:
      sql                    = f"update invite_channel set channel_id='{invite_channel.id}' where guild_id='{guild_id}'"
    database.execute_order(sql)
    await invite_channel.send(Utils.get_text(ctx.guild.id, "invite_channel_set"))

  @commands.command(name='invitemessage', aliases=['im'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_invite_message(self, ctx):
    guild_id                 = ctx.message.guild.id
    member                   = ctx.author
    await ctx.send ("Entrez le message d'invitation : ")
    check                    = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg                      = await self.bot.wait_for('message', check=check)
    message                  = msg.content
    # message = re.escape(message)
    sql                      = f"select message from invite_message where guild_id='{guild_id}'"
    prev_invite_message      = database.fetch_one_line (sql)
    if not prev_invite_message:
      sql                    = f"INSERT INTO invite_message VALUES (?, '{guild_id}')"
    else:
      sql                    = f"update invite_message set message=? where guild_id='{guild_id}'"
    try:
      database.execute_order(sql, [message])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
    await ctx.channel.send(Utils.get_text(ctx.guild.id, "display_new_message"))

  @commands.command(name='setinvitedelay', aliases=['sid'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_invite_delay(self, ctx, delay: str = None):
    author                   = ctx.author
    guild_id                 = ctx.message.guild.id
    try:
      if not delay.isnumeric():
        delay                = Utils.parse_time(delay)
      type_delay             = "invite"
      select                 = (  "select delay from config_delay"+
                                  " where "+
                                 f" `type_delay`=? and `guild_id`='{guild_id}'"+
                                  ""
                               )
      fetched                = database.fetch_one_line (select, [type_delay])
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
      database.execute_order (order, [delay, type_delay])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
      error                  = True
      await ctx.message.add_reaction('❌')
    await self.logger.log('config_log', author, ctx.message, error)

  @commands.Cog.listener('on_message')
  async def invitation(self, message):
    """
    Send the invitation's link in a DM
    if the word 'invitation' is found
    """
    if not (     ("invitation" in message.content.lower())
              or ("compte" in message.content.lower())
           ):
      return
    if message.author == self.bot.user: # don't read yourself
      return
    if (message.guild == None):
      # DM => debile-proof
      for guild in self.bot.guilds:
        if Utils.is_loaded ("invitation", guild.id) and guild.get_member(message.author.id):
          print (f"HERE ! on guild {guild.id}")
          guild_id           = guild.id
          member             = message.author
          error              = False
          await member.trigger_typing() # add some tension !!
          invite_delay       = Utils.invite_delay (guild_id) or botconfig.config[str(guild_id)]["invite_delay"]
          sql                = f"select last from last_invite where guild_id='{guild_id}' and member_id='{member.id}'"
          last_invite        = database.fetch_one_line (sql)
          if last_invite and last_invite[0]:
            last_timestamp   = time.mktime(datetime.strptime(last_invite [0], "%Y-%m-%d %H:%M:%S").timetuple())
            if str(invite_delay).isnumeric():
              invite_delay   = int(invite_delay)
            else:
              invite_delay   = Utils.convert_str_to_time(invite_delay)
            print (f"last_timestamp: {last_timestamp}")
            print (f"invite_delay: {invite_delay}")
            duree            = math.floor ((last_timestamp + invite_delay) - time.time())
            print (f"duree: {duree}")
            if duree > 0:
              await message.add_reaction('❌')
              error          = True
              feedback       = await message.channel.send(Utils.get_text(guild_id, "user_already_ask_invitation").format(Utils.format_time(duree)))
              await self.logger.log_dm('invite_log', self.bot.user, feedback, guild, error)
          if not error:
            try:
              colour         = discord.Colour(0)
              url            = "Votre lien d'invitation:\n"+await self.get_invitation_link(guild_id)
              sql            = f"select message from invite_message where guild_id='{guild_id}'"
              invite_message =  database.fetch_one_line (sql)
              if invite_message:
                url          = url+"\n\n"+invite_message [0]
              colour         = colour.from_rgb(255, 51, 124)
              icon_url       = "https://cdn.discordapp.com/attachments/597091535242395649/597091654847037514/Plan_de_travail_18x.png"
              name           = "Steven Universe Fantasy"
              #embed.set_footer(text=f"ID: {message.id}")
              embed          = discord.Embed(colour=colour)
              embed.set_author(icon_url=icon_url, name=name)
              embed.description        = url
              embed.timestamp          = datetime.utcnow()
              await member.send (content=None, embed=embed)
            except Exception as e:
              await message.channel.send(Utils.get_text(guild_id, "user_disabled_PM_2"))
              print (f" {type(e).__name__} - {e}")
              error          = True
          if not error:
            # LOG LAST INVITE
            sql              = f"select * from last_invite where guild_id='{guild_id}' and member_id='{member.id}'"
            last_invite      = database.fetch_one_line (sql)
            if not last_invite:
              sql            = f"insert into last_invite values ('{member.id}', '{guild_id}', datetime('{datetime.now()}'))"
            else:
              sql            = f"update last_invite set last=datetime('{datetime.now()}') where member_id='{member.id}' and guild_id='{guild_id}'"
            try:
              database.execute_order (sql)
            except Exception as e:
              print (f'{type(e).__name__} - {e}')
              error          = True
          await self.logger.log_dm ('invite_log', member, message, guild, error)
          try:
            if error:
              await message.add_reaction('❌')
            else:
              await message.delete (delay=2)
              await message.add_reaction('✅')
          except Exception as e:
              print (f'{type(e).__name__} - {e}')
    else:
      if not Utils.is_loaded ("invitation", message.guild.id):
        return
      guild_id               = message.channel.guild.id
      sql                    = f"select * from invite_channel where guild_id='{message.channel.guild.id}'"
      invite_channel         = database.fetch_one_line (sql)
      if invite_channel:
        invite_channel       = int (invite_channel [0])
      member                 = message.author
      error                  = False
      # If I ask for invite, we check for the last time i asked for it
      if (message.channel.id == invite_channel):
        invite_delay         = Utils.invite_delay (guild_id) or botconfig.config[str(guild_id)]["invite_delay"]
        sql                  = f"select last from last_invite where guild_id='{message.guild.id}' and member_id='{member.id}'"
        last_invite          = database.fetch_one_line (sql)
        if last_invite and last_invite[0]:
          last_timestamp     = time.mktime(datetime.strptime(last_invite [0], "%Y-%m-%d %H:%M:%S").timetuple())
          if str(invite_delay).isnumeric():
            invite_delay     = int(invite_delay)
          else:
            invite_delay     = Utils.convert_str_to_time(invite_delay)
          print (f"last_timestamp: {last_timestamp}")
          print (f"invite_delay: {invite_delay}")
          duree              = math.floor ((last_timestamp + invite_delay) - time.time())
          print (f"duree: {duree}")
          if duree > 0:
            await self.logger.log('invite_log', member, message, True)
            await message.add_reaction('❌')
            await message.channel.send(Utils.get_text(guild_id, "user_already_ask_invitation").format(Utils.format_time(duree)))
            return
        try:
          colour             = discord.Colour(0)
          url                = "Votre lien d'invitation:\n"+await self.get_invitation_link(guild_id)
          sql                = f"select message from invite_message where guild_id='{guild_id}'"
          invite_message     =  database.fetch_one_line (sql)
          if invite_message:
            url              = url+"\n\n"+invite_message [0]
          colour             = colour.from_rgb(255, 51, 124)
          icon_url           = "https://cdn.discordapp.com/attachments/597091535242395649/597091654847037514/Plan_de_travail_18x.png"
          name               = "Steven Universe Fantasy"
          #embed.set_footer(text=f"ID: {message.id}")
          embed              = discord.Embed(colour=colour)
          embed.set_author(icon_url=icon_url, name=name)
          embed.description  = url
          embed.timestamp    = datetime.utcnow()
          await member.send (content=None, embed=embed)
        except Exception as e:
          await message.channel.send(Utils.get_text(guild_id, "user_disabled_PM_2"))
          print (f" {type(e).__name__} - {e}")
          error              = True
        if not error:
          # LOG LAST INVITE
          sql                = f"select * from last_invite where guild_id='{message.guild.id}' and member_id='{member.id}'"
          last_invite        = database.fetch_one_line (sql)
          if not last_invite:
            sql              = f"insert into last_invite values ('{member.id}', '{message.guild.id}', datetime('{datetime.now()}'))"
          else:
            sql              = f"update last_invite set last=datetime('{datetime.now()}') where member_id='{member.id}' and guild_id='{message.guild.id}'"
          try:
            database.execute_order (sql)
          except Exception as e:
            await message.channel.send(Utils.get_text(guild_id, "database_writing_error"))
            print (f'{type(e).__name__} - {e}')
            error            = True
        await self.logger.log('invite_log', member, message, error)
        try:
          if error:
            await message.add_reaction('❌')
          else:
            await message.delete (delay=2)
            await message.add_reaction('✅')
        except Exception as e:
            print (f'{type(e).__name__} - {e}')

  async def get_invitation_link (self, guild_id):
    url                      = Utils.invite_url(guild_id) or botconfig.config[str(guild_id)]['create_url']['invitation'] #build the web adress
    return await self.get_text(url)

  async def get_text(self, url):
    async with aiohttp.ClientSession() as session:
      response               = await session.get(url)
      soupObject             = BeautifulSoup(await response.text(), "html.parser")
      return soupObject.p.get_text().replace(";","")