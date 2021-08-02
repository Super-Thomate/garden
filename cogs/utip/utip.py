import math
import time

import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs
from core import logger

class Utip(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  @commands.command(name='utip')
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def utip_send(self, ctx):
    guild_id = ctx.message.guild.id
    author = ctx.author
    # First get channel, if no channel => big error
    select_channel = f"select channel_id from utip_channel where guild_id='{guild_id}' ;"
    fetched_channel = database.fetch_one_line(select_channel)
    if not fetched_channel:
      await ctx.send(Utils.get_text('fr', 'error_moderation_channel_unset'))
      await ctx.message.add_reaction('❌')
      return
    try:
      channel_id = int(fetched_channel[0])
      channel = await self.bot.fetch_channel(channel_id)
    except Exception as e:
      await ctx.send(Utils.get_text('fr', 'error_moderation_channel').format(type(e).__name__))
      await ctx.message.add_reaction('❌')
      logger ("utip::utip_send", f"{type(e).__name__} - {e}")
      return
    error = False
    try:
      ask = await ctx.send(Utils.get_text(ctx.guild.id, "utip_ask_URL"))
      check = lambda m: m.channel == ctx.channel and m.author == ctx.author
      msg = await self.bot.wait_for('message', check=check)
      content = msg.content
      is_attachment = len(msg.attachments) > 0
      is_url = Utils.is_url_image(content)
      if is_attachment:
        attachment = msg.attachments[0].proxy_url
      # FEEDBACK
      if ((not is_url and not is_attachment)
              # or (is_url and not Utils.is_url_image(content) and not is_attachment)
      ):
        await ctx.message.add_reaction('❌')
        await ask.delete(delay=2)
        await msg.delete(delay=2)
        await self.logger.log('utip_log', author, ctx.message, True)
        await self.logger.log('utip_log', author, msg, True)
        return
      select = f"select message from utip_message where guild_id='{guild_id}' ;"
      fetch_utip_message = database.fetch_one_line(select)
      if fetch_utip_message:
        await author.send(fetch_utip_message[0])
      else:
        await author.send(Utils.get_text('fr', 'utip_demand_transfered'))
      # ASK MODO
      title = ("Demande de rôle pour" +
               f"{str(author)} " +
               ""
               )
      description = ("La pièce jointe suivante donne-t-elle le droit à " +
                     f"{author.display_name} " +
                     "de recevoir le rôle Crystal Clods ?\n" +
                     "👍 Oui " +
                     "👎 Non" +
                     "\n"
                     )
      if is_url:
        description += (f"\nURL: {content}" +
                        ""
                        )
      if is_attachment:
        description += (f"\nAttachments: {attachment}" +
                        ""
                        )
      embed = self.create_embed(title, description, author)
      if is_url:
        embed.set_image(url=content)
      elif is_attachment:
        embed.set_image(url=attachment)
      modo_message = await channel.send(embed=embed)
      await modo_message.add_reaction("👍")
      await modo_message.add_reaction("👎")
      # SET WAIT LIST
      insert_wait = ("insert into utip_waiting " +
                     "(`user_id`, `status`, `message_id`, `valid_by`, `valid_at`, `guild_id`) " +
                     "values " +
                     f"('{author.id}', 0, '{modo_message.id}', NULL, NULL, '{guild_id}')" +
                     ";"
                     )
      database.execute_order(insert_wait)
      # DELETE
      await ctx.message.delete(delay=2)
      await ask.delete(delay=2)
      await msg.delete(delay=2)
    except Exception as e:
      logger ("utip::utip_send", f"{type(e).__name__} - {e}")
      error = True
    await self.logger.log('utip_log', author, ctx.message, error)
    await self.logger.log('utip_log', author, msg, error)

  @commands.command(name='setutipchannel', aliases=['utipchannel', 'suc'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_utip_channel(self, ctx, channel: discord.TextChannel = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    channel = channel or ctx.channel
    if not channel:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<channelID>'))
      return
    sql = f"select channel_id from utip_channel where guild_id='{guild_id}'"
    prev_galerie_channel = database.fetch_one_line(sql)
    if not prev_galerie_channel:
      sql = f"insert into utip_channel (`channel_id`, `guild_id`) values (?, '{guild_id}')"
    else:
      sql = f"update utip_channel set channel_id=? where guild_id='{guild_id}'"
    try:
      database.execute_order(sql, [channel.id])
    except Exception as e:
      logger ("utip::set_utip_channel", f"{type(e).__name__} - {e}")
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='setutiprole', aliases=['utiprole', 'sur'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_utip_role(self, ctx, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    sql = f"select role_id from utip_role where guild_id='{guild_id}'"
    prev_galerie_role = database.fetch_one_line(sql)
    if not prev_galerie_role:
      sql = f"insert into utip_role (`role_id`, `guild_id`) values (?, '{guild_id}')"
    else:
      sql = f"update utip_role set role_id=? where guild_id='{guild_id}'"
    try:
      database.execute_order(sql, [role.id])
    except Exception as e:
      logger ("utip::set_utip_role", f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='setutipmessage', aliases=['utipmessage', 'sum'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_utip_message(self, ctx):
    guild_id = ctx.message.guild.id
    author = ctx.author
    await ctx.send("Entrez le message de feedback pour la commande `!utip` : ")
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    message = msg.content
    sql = f"select message from utip_message where guild_id='{guild_id}'"
    prev_galerie_message = database.fetch_one_line(sql)
    if not prev_galerie_message:
      sql = f"insert into utip_message (`message`, `guild_id`) values (?, '{guild_id}')"
    else:
      sql = f"update utip_message set message=? where guild_id='{guild_id}'"
    try:
      database.execute_order(sql, [message])
    except Exception as e:
      logger ("utip::set_utip_message", f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
      await ctx.channel.send(Utils.get_text(ctx.guild.id, "display_new_message").format(message))

  @commands.command(name='setutipdelay', aliases=['utipdelay', 'sud'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_utip_delay(self, ctx):
    guild_id = ctx.message.guild.id
    author = ctx.author
    await ctx.send("Entrez le délai durant lequel le membre garde le rôle : ")
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    message = msg.content
    sql = f"select delay from config_delay where guild_id='{guild_id}' and type_delay='utip_role' ;"
    try:
      delay = Utils.parse_time(message)
    except Exception as e:
      await ctx.message.add_reaction('❌')
      await ctx.channel.send(Utils.get_text(ctx.guild.id, "utip_delay_error").format(message))
      return
    prev_galerie_delay = database.fetch_one_line(sql)
    if not prev_galerie_delay:
      sql = f"insert into config_delay (`delay`, `type_delay`, `guild_id`) values (?, 'utip_role', '{guild_id}')"
    else:
      sql = f"update config_delay set delay=? where guild_id='{guild_id}' and type_delay='utip_role' ;"
    try:
      database.execute_order(sql, [delay])
    except Exception as e:
      logger ("utip::set_utip_delay", f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='cartoon16', aliases=['acces', 'accescartoon16', 'g18ans'])
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def acces_send(self, ctx):
    guild_id = ctx.message.guild.id
    author = ctx.author
    # First get channel, if no channel => big error
    select_channel = f"select channel_id from utip_channel where guild_id='{guild_id}' ;"
    fetched_channel = database.fetch_one_line(select_channel)
    if not fetched_channel:
      await ctx.send(Utils.get_text('fr', 'error_moderation_channel_unset'))
      await ctx.message.add_reaction('❌')
      return
    try:
      channel_id = int(fetched_channel[0])
      channel = await self.bot.fetch_channel(channel_id)
    except Exception as e:
      await ctx.send(Utils.get_text('fr', 'error_moderation_channel').format(type(e).__name__))
      await ctx.message.add_reaction('❌')
      logger ("utip::acces_send", f"{type(e).__name__} - {e}")
      return
    error = False
    try:
      await author.send(Utils.get_text('fr', 'acces_demand_transfered'))
      # ASK MODO
      title = ("Demande d'accès 16+ pour" +
               f"{str(author)} " +
               ""
               )
      description = ("Souhaitez-vous donner à " +
                     f"{author.display_name} " +
                     "le rôle permettant l'accès au contenu 16+ ?\n" +
                     "👍 Oui " +
                     "👎 Non" +
                     "\n"
                     )
      embed = self.create_embed(title, description, author)
      modo_message = await channel.send(embed=embed)
      await modo_message.add_reaction("👍")
      await modo_message.add_reaction("👎")
      # SET WAIT LIST
      insert_wait = ("insert into utip_waiting " +
                     "(`user_id`, `status`, `message_id`, `valid_by`, `valid_at`, `guild_id`) " +
                     "values " +
                     f"('{author.id}', 0, '{modo_message.id}', NULL, NULL, '{guild_id}')" +
                     ";"
                     )
      database.execute_order(insert_wait)
      # DELETE
      await ctx.message.delete(delay=2)
    except Exception as e:
      logger ("utip::utip_send", f"{type(e).__name__} - {e}")
      error = True
    await self.logger.log('utip_log', author, ctx.message, error)


  async def give_role(self, member, role_utip, delay):
    # until = today+3
    try:
      error = False
      until = 0
      if not delay == "forever":
        until = math.floor(time.time()) + delay
      select = ("select   user_id " +
                " from    utip_timer " +
                "where " +
                f"user_id = '{member.id}'" +
                " and " +
                f"guild_id = '{member.guild.id}'" +
                ""
                )
      fetched = database.fetch_one_line(select)
      if until > 0:
        if Utils.has_role(member, role_utip.id) or fetched:
          sql = ("update utip_timer " +
                f"set until={until} " +
                " where " +
                f"user_id = '{member.id}'" +
                " and " +
                f"guild_id = '{member.guild.id}'" +
                ""
                )
        else:
          sql = ("insert into utip_timer " +
                "(`until`, `user_id`, `guild_id`)" +
                "values " +
                f"({until}, '{member.id}', '{member.guild.id}')" +
                ""
                )
      await member.add_roles(role_utip)
      database.execute_order(sql)
    except Exception as e:
      logger ("utip::give_role", f"give_role: {type(e).__name__} - {e}")
      error = True
    return error

  def create_embed(self, title, description, author):
    colour = discord.Colour(0)
    colour = colour.from_rgb(150, 178, 255)
    embed = discord.Embed(colour=colour)
    embed.set_author(icon_url=author.avatar_url, name=str(author))
    embed.title = title
    embed.description = description
    return embed

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    message_id = payload.message_id
    guild_id = payload.guild_id
    channel_id = payload.channel_id
    emoji = payload.emoji
    author_id = payload.user_id
    if author_id == self.bot.user.id:
      return
    if not str(emoji) in ["👍", "👎"]:
      return
    select_waiting = f"select user_id from utip_waiting where message_id='{message_id}' and status=0;"
    fetched_waiting = database.fetch_one_line(select_waiting)
    if not fetched_waiting:
      return
    user_id = int(fetched_waiting[0])
    channel_selected = await self.bot.fetch_channel(channel_id)
    message_selected = await channel_selected.fetch_message(message_id)
    guild_select = message_selected.guild
    member_selected = guild_select.get_member(user_id)
    author_selected = guild_select.get_member(author_id)
    select_role = f"select role_id from utip_role where guild_id='{guild_id}' ;"
    fetched_role = database.fetch_one_line(select_role)
    if not fetched_role:
      await channel_selected.send(Utils.get_text(guild_id, "utip_role_undefined"))
      return
    role_utip = guild_select.get_role(int(fetched_role[0]))
    select_delay = ("select delay from config_delay " +
                    f"where guild_id='{guild_id}' and type_delay='utip_role' ;"
                    )
    fetched_delay = database.fetch_one_line(select_delay)
    if not fetched_delay:
      await channel_selected.send(Utils.get_text(guild_id, "utip_delay_undefined"))
      return
    delay = int(fetched_delay[0])
    embed = message_selected.embeds[0]
    colour = discord.Colour(0)
    if str(emoji) == "👍":
      update_waiting = ("update utip_waiting " +
                        "set status=1 " +
                        f"where message_id='{message_id}' ;"
                        )
      # await self.give_role(member_selected, role_utip, delay)
      await self.give_role(member_selected, role_utip, "forever")
      colour = colour.from_rgb(56, 255, 56)
      embed.set_footer(text=f"Accepté par {str(author_selected)}")
      """
      feedback_message = (":white_check_mark: Demande validée ! " +
                          f"Tu dispose du role de backers pendant **{Utils.format_time(delay)}**." +
                          # ":arrow_right: Ton role prendra fin le **XX/XX/XXX** à **XX:XX**"+
                          ""
                          )
      """
      feedback_message = (":white_check_mark: Demande validée ! " +
                          f"Tu disposes du rôle te permettant de voir le contenu 16+ ." +
                          ""
                          )
    else:
      update_waiting = ("update utip_waiting " +
                        "set status=2 " +
                        f"where message_id='{message_id}' ;"
                        )
      colour = colour.from_rgb(255, 71, 71)
      embed.set_footer(text=f"Refusé par {str(author_selected)}")
      feedback_message = ("Votre demande a été refusée." +
                          ""
                          )
    database.execute_order(update_waiting)
    embed.colour = colour
    await message_selected.edit(embed=embed)
    await member_selected.send(feedback_message)