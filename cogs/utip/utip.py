import discord
from discord.ext import commands
from Utils import Utils
from ..logs import Logs
from database import Database
import math
import time

class Utip(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()
    self.language_code = 'fr'

  @commands.command(name='utip')
  async def utip_send(self, ctx):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if self.utils.is_banned (ctx.command, author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    # First get channel, if no channel => big error
    select_channel           = f"select channel_id from utip_channel where guild_id='{guild_id}' ;"
    fetched_channel          = self.db.fetch_one_line (select_channel)
    if not fetched_channel:
      await ctx.send (self.utils.get_text('fr', 'moderation_channel_not_set'))
      await ctx.message.add_reaction('❌')
      return
    try:
      channel_id             = int (fetched_channel[0])
      channel                = await self.bot.fetch_channel (channel_id)
    except Exception as e:
      await ctx.send (self.utils.get_text('fr', 'moderation_channel_error').format(type(e).__name__))
      await ctx.message.add_reaction('❌')
      print (f"{type(e).__name__} - {e}")
      return
    error = False
    try:
      ask                    = await ctx.send(self.utils.get_text(self.language_code, "ask_utip_URL"))
      check                  = lambda m: m.channel == ctx.channel and m.author == ctx.author
      msg                    = await self.bot.wait_for('message', check=check)
      content                = msg.content
      is_attachment          = len(msg.attachments) > 0
      is_url                 = self.utils.is_url_image(content)
      if is_attachment:
        attachment           = msg.attachments[0].proxy_url
      # FEEDBACK
      if (    (not is_url and not is_attachment)
           #or (is_url and not self.utils.is_url_image(content) and not is_attachment)
         ):
        await ctx.message.add_reaction('❌')
        await ask.delete (delay=2)
        await msg.delete (delay=2)
        await self.logger.log('utip_log', author, ctx.message, True)
        await self.logger.log('utip_log', author, msg, True)
        return
      select                 = f"select message from utip_message where guild_id='{guild_id}' ;"
      fetch_utip_message     = self.db.fetch_one_line (select)
      if fetch_utip_message:
        await author.send (fetch_utip_message [0])
      else:
        await author.send (self.utils.get_text('fr', 'utip_demand_transfered'))
      # ASK MODO
      title                  = (  "Demande de rôle pour"+
                                  f"{str(author)} "+
                                  ""
                               )
      description            = (  "La pièce jointe suivante donne-t-elle le droit à "+
                                 f"{author.display_name} "+
                                  "de recevoir le rôle Crystal Clods ?\n"+
                                  "👍 Oui "+
                                  "👎 Non"+
                                  "\n"
                               )
      if is_url:
        description         += ( f"\nURL: {content}"+
                                  ""
                               )
      if is_attachment:
        description         += ( f"\nAttachments: {attachment}"+
                                  ""
                               )
      embed                  = self.create_embed (title, description, author)
      if is_url:
        embed.set_image(url=content)
      elif is_attachment:
        embed.set_image(url=attachment)
      modo_message           = await channel.send (embed=embed)
      await modo_message.add_reaction ("👍")
      await modo_message.add_reaction ("👎")
      # SET WAIT LIST
      insert_wait            = (  "insert into utip_waiting "+
                                  "(`user_id`, `status`, `message_id`, `valid_by`, `valid_at`, `guild_id`) "+
                                  "values "+
                                 f"('{author.id}', 0, '{modo_message.id}', NULL, NULL, '{guild_id}')"+
                                  ";"
                               )
      self.db.execute_order (insert_wait)
      # DELETE
      await ctx.message.delete (delay=2)
      await ask.delete (delay=2)
      await msg.delete (delay=2)
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      error                  = True
    await self.logger.log('utip_log', author, ctx.message, error)
    await self.logger.log('utip_log', author, msg, error)
  
  @commands.command(name='setutipchannel', aliases=['utipchannel', 'suc'])
  async def set_utip_channel(self, ctx, channel: discord.TextChannel = None):
    guild_id                 = ctx.message.guild.id
    author                   = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    channel                 = channel or ctx.channel
    if not channel:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<channelID>'))
      return
    sql                      = f"select channel_id from utip_channel where guild_id='{guild_id}'"
    prev_galerie_channel     = self.db.fetch_one_line (sql)
    if not prev_galerie_channel:
      sql                    = f"insert into utip_channel (`channel_id`, `guild_id`) values (?, '{guild_id}')"
    else:
      sql                    = f"update utip_channel set channel_id=? where guild_id='{guild_id}'"
    # print (sql)
    try:
      self.db.execute_order (sql, [channel.id])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='setutiprole', aliases=['utiprole', 'sur'])
  async def set_utip_role(self, ctx, role: discord.Role = None):
    guild_id                 = ctx.message.guild.id
    author                   = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not role:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<roleID>'))
      return
    sql                      = f"select role_id from utip_role where guild_id='{guild_id}'"
    prev_galerie_role        = self.db.fetch_one_line (sql)
    if not prev_galerie_role:
      sql                    = f"insert into utip_role (`role_id`, `guild_id`) values (?, '{guild_id}')"
    else:
      sql                    = f"update utip_role set role_id=? where guild_id='{guild_id}'"
    # print (sql)
    try:
      self.db.execute_order (sql, [role.id])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
  
  @commands.command(name='setutipmessage', aliases=['utipmessage', 'sum'])
  async def set_utip_message(self, ctx):
    guild_id                 = ctx.message.guild.id
    author                   = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await ctx.send(self.utils.get_text(self.language_code, "ask_utip_feedback_message"))
    check                    = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg                      = await self.bot.wait_for('message', check=check)
    message                  = msg.content
    sql                      = f"select message from utip_message where guild_id='{guild_id}'"
    prev_galerie_message     = self.db.fetch_one_line (sql)
    if not prev_galerie_message:
      sql                    = f"insert into utip_message (`message`, `guild_id`) values (?, '{guild_id}')"
    else:
      sql                    = f"update utip_message set message=? where guild_id='{guild_id}'"
    # print (sql)
    try:
      self.db.execute_order (sql, [message])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
      await ctx.channel.send(self.utils.get_text(self.language_code, "display_new_message").format(message))
  
  @commands.command(name='setutipdelay', aliases=['utipdelay', 'sud'])
  async def set_utip_delay(self, ctx):
    guild_id                 = ctx.message.guild.id
    author                   = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await ctx.send(self.utils.get_text(self.language_code, "ask_utip_delay"))
    check                    = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg                      = await self.bot.wait_for('message', check=check)
    message                  = msg.content
    sql                      = f"select delay from config_delay where guild_id='{guild_id}' and type_delay='utip_role' ;"
    try:
      delay                  = self.utils.parse_time (message)
    except Exception as e:
      await ctx.message.add_reaction('❌')
      await ctx.channel.send(self.utils.get_text(self.language_code, "utip_delay_error").format(message))
      return
    prev_galerie_delay       = self.db.fetch_one_line (sql)
    if not prev_galerie_delay:
      sql                    = f"insert into config_delay (`delay`, `type_delay`, `guild_id`) values (?, 'utip_role', '{guild_id}')"
    else:
      sql                    = f"update config_delay set delay=? where guild_id='{guild_id}' and type_delay='utip_role' ;"
    # print (sql)
    try:
      self.db.execute_order (sql, [delay])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
  
  async def give_role (self, member, role_utip, delay):
    # until = today+3
    try:
      error                  = False
      until                  = math.floor(time.time())+delay
      select                 = (  "select   user_id "+
                                  " from    utip_timer "+
                                  "where "+
                                 f"user_id = '{member.id}'"+
                                  " and "+
                                 f"guild_id = '{member.guild.id}'"+
                                  ""
                               )
      fetched                = self.db.fetch_one_line (select)
      if self.utils.has_role (member, role_utip.id) or fetched:
        sql                  = (  "update utip_timer "+
                                 f"set until={until} "+
                                  " where "+
                                 f"user_id = '{member.id}'"+
                                  " and "+
                                 f"guild_id = '{member.guild.id}'"+
                                  ""
                               )
      else:
        sql                  = (  "insert into utip_timer "+
                                  "(`until`, `user_id`, `guild_id`)"+
                                  "values "+
                                 f"({until}, '{member.id}', '{member.guild.id}')"+
                                  ""
                               )
      await member.add_roles(role_utip)
      self.db.execute_order (sql)
    except Exception as e:
       print (f"give_role: {type(e).__name__} - {e}")
       error                 = True
    return error

  def create_embed(self, title, description, author):
    colour                   = discord.Colour(0)
    colour                   = colour.from_rgb(150, 178, 255)
    embed                    = discord.Embed(colour=colour)
    embed.set_author(icon_url=author.avatar_url, name=str(author))
    embed.title              = title
    embed.description        = description
    return embed

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    message_id               = payload.message_id
    guild_id                 = payload.guild_id
    channel_id               = payload.channel_id
    emoji                    = payload.emoji
    author_id                = payload.user_id
    if author_id == self.bot.user.id:
      return
    if not str(emoji) in ["👍", "👎"]:
      return
    select_waiting           = f"select user_id from utip_waiting where message_id='{message_id}' and status=0;"
    fetched_waiting          = self.db.fetch_one_line (select_waiting)
    if not fetched_waiting:
      # print ("Utip reaction listener: Not a utip message !")
      return
    user_id                  = int (fetched_waiting[0])
    channel_selected         = await self.bot.fetch_channel (channel_id)
    message_selected         = await channel_selected.fetch_message (message_id)
    guild_select             = message_selected.guild
    member_selected          = guild_select.get_member (user_id)
    author_selected          = guild_select.get_member (author_id)
    select_role              = f"select role_id from utip_role where guild_id='{guild_id}' ;"
    fetched_role             = self.db.fetch_one_line (select_role)
    if not fetched_role:
      await channel_selected.send(self.utils.get_text(self.language_code, "utip_role_undefined"))
      return
    role_utip                = guild_select.get_role (int (fetched_role [0]))
    select_delay             = (  "select delay from config_delay "+
                                 f"where guild_id='{guild_id}' and type_delay='utip_role' ;"
                               )
    fetched_delay            = self.db.fetch_one_line (select_delay)
    if not fetched_delay:
      await channel_selected.send(self.utils.get_text(self.language_code, "utip_role_undefined"))
      return
    delay                    = int (fetched_delay [0])
    embed                    = message_selected.embeds [0]
    colour                   = discord.Colour(0)
    if str(emoji) == "👍":
      update_waiting         = (   "update utip_waiting "+
                                   "set status=1 "+
                                  f"where message_id='{message_id}' ;"
                               )
      await self.give_role (member_selected, role_utip, delay)
      colour                 = colour.from_rgb(56, 255, 56)
      embed.set_footer(text=f"Accepté par {str(author_selected)}")
      feedback_message       = ( ":white_check_mark: Demande validée ! "+
                                f"Tu dispose du role de backers pendant **{self.utils.format_time(delay)}**."+
                                # ":arrow_right: Ton role prendra fin le **XX/XX/XXX** à **XX:XX**"+
                                 ""
                               )
    else:
      update_waiting         = (   "update utip_waiting "+
                                   "set status=2 "+
                                  f"where message_id='{message_id}' ;"
                               )
      colour                 = colour.from_rgb(255, 71, 71)
      embed.set_footer(text=f"Refusé par {str(author_selected)}")
      feedback_message       = ( "Votre demande a été refusée."+
                                 ""
                               )
    self.db.execute_order (update_waiting)
    embed.colour             = colour
    await message_selected.edit (embed=embed)
    await member_selected.send (feedback_message)
  """
  @commands.command(name='testgiveutip', aliases=['tgu'])
  async def test_give_utip(self, ctx, member: discord.Member = None):
    guild_id                 = ctx.message.guild.id
    author                   = ctx.author
    if not self.utils.is_authorized (author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "STRING_TO_CHANGE"))
      return
    member                   = member or author
    select                   = f"select role_id from utip_role where guild_id='{guild_id}'"
    fetched                  = self.db.fetch_one_line (select)
    print (f"select: {select}")
    print (f"fetched: {fetched}")
    if not fetched:
      await ctx.send(self.utils.get_text(self.language_code, "STRING_TO_CHANGE"))
      return
    role                     = ctx.guild.get_role (int (fetched [0]))
    error                    = await self.give_role(member, role, 3600)
    if error:
      await ctx.send(self.utils.get_text(self.language_code, "STRING_TO_CHANGE"))
      await ctx.message.add_reaction('❌')
    else:
      await ctx.send(self.utils.get_text(self.language_code, "STRING_TO_CHANGE"))
      await ctx.message.add_reaction('✅')
  """