import math
import random
import time

import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs
from core import logger


class Welcome(commands.Cog):
  """
  PublicWelcome:
  setwelcomechannel [channel_id]
  setwelcomemessage role_id message
  setwelcomerole role_id
  """

  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    # guild id
    guild_id = before.guild.id
    if not Utils.is_loaded("welcome", guild_id):
      return
    unique_welcome = True  # to put on config later
    # all roles to listen
    select = f"select role_id from welcome_role where guild_id='{guild_id}'"
    fetched = database.fetch_all_line(select)
    for line in fetched:
      role_id = int(line[0])
      if (not Utils.has_role(before, role_id)
              and Utils.has_role(after, role_id)
      ):
        # The member obtained the role
        logger ("welcome::on_member_update", 'The member obtained the role')
        # already welcomed ?
        if unique_welcome:
          select = f"select * from welcome_user where user_id='{before.id}' and guild_id='{guild_id}' and role_id={role_id} ;"
          fetched = database.fetch_one_line(select)
          if fetched:
            # already welcomed !
            logger ("welcome::on_member_update", 'already welcomed')
            return
        # get the channel
        channel = None
        select = f"select channel_id from welcome_channel where guild_id='{guild_id}' ;"
        fetched = database.fetch_one_line(select)
        if fetched:
          channel_id = fetched[0]
          channel = before.guild.get_channel(int(channel_id))
        if not channel:
          logger ("welcome::on_member_update", 'Not channel')
          channel = before.guild.system_channel
        # get the message
        select = f"select message from welcome_message where guild_id='{guild_id}' and role_id={role_id} ; "
        fetched = database.fetch_one_line(select)
        if fetched:
          text = ""
          # split around '{'
          text_rand = (fetched[0]).split('{')
          logger ("welcome::on_member_update", f"text_rand: {text_rand}")
          for current in text_rand:
            parts = current.split('}')
            logger ("welcome::on_member_update", f"parts: {parts}")
            for part in parts:
              all_rand = part.split("|")
              logger ("welcome::on_member_update", f"all_rand: {all_rand}")
              current_part = all_rand[random.randint(0, len(all_rand) - 1)]
              logger ("welcome::on_member_update", f"current_part: {current_part}")
              text = text + current_part
          """
          if text.startswith('{') and text.endswith('}'):
            # random
            text = text [1:len(text)-1]
            all_rand = text.split ("|")
            index = random.randint(0,len(all_rand)-1)
            text = all_rand [index]
          """
          message = text.replace("$member", before.mention).replace("$role", f"<@&{role_id}>")
        else:
          message = Utils.get_text(guild_id, 'welcome_user_1').format(before.mention)
        # send
        await channel.send(message)
        # save welcome
        if unique_welcome:
          sql = ("insert into welcome_user " +
                 " (`user_id`, `role_id`, `welcomed_at` ,`guild_id`) " +
                 " values " +
                 f"('{before.id}', {role_id}, {math.floor(time.time())}, '{guild_id}') ;"
                 )
          database.execute_order(sql)

  @commands.command(name='setwelcomerole', aliases=['swr', 'welcomerole'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_welcome_role(self, ctx, *, role: discord.Role = None):
    """
    Set welcome role
    """
    guild_id = ctx.guild.id
    if not role:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<role>'))
      await self.logger.log('nickname_log', ctx.author, ctx.message, True)
      return
    role_id = role.id
    select = f"select role_id from welcome_role where guild_id='{guild_id}' and role_id='{role_id}' ;"
    fetched = database.fetch_one_line(select)
    if fetched:
      sql = f"update welcome_role set role_id='{role_id}' where guild_id='{guild_id}' and role_id='{role_id}' ;"
    else:
      sql = f"insert into welcome_role values ('{role_id}', '{guild_id}') ;"
    error = False
    logger ("welcome::set_welcome_role", sql)
    try:
      database.execute_order(sql, [])
    except Exception as e:
      error = True
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
    # await self.logger.log('welcome_log', ctx.author, ctx.message, error) # no logs

  @commands.command(name='setwelcomechannel', aliases=['swc', 'welcomechannel', 'wc'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_welcome(self, ctx, *, channel: discord.TextChannel = None):
    """
    Set the welcome channel
    """
    channel = channel or ctx.channel
    guild_id = ctx.guild.id
    error = False
    select = f"select * from welcome_channel where guild_id='{guild_id}' ;"
    fetched = database.fetch_one_line(select)
    if not fetched:
      sql = f"insert into welcome_channel values ('{channel.id}', '{guild_id}') ;"
    else:
      sql = f"update welcome_channel set channel_id='{channel.id}' where guild_id='{guild_id}' ;"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      await ctx.channel.send(Utils.get_text(ctx.guild.id, "error_database_writing"))
      logger ("welcome::set_welcome", f'{type(e).__name__} - {e}')
      error = True
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
    # await self.logger.log('welcome_log', ctx.author, ctx.message, error) # no logs

  @commands.command(name='setwelcomemessage', aliases=['welcomemessage', 'swm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_welcome_message(self, ctx, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not role:
      await ctx.message.add_reaction('❌')
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<role>'))
      return
    await ctx.send(Utils.get_text(ctx.guild.id, "ask_welcome_message"))
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    message = msg.content
    sql = f"select message from welcome_message where guild_id='{guild_id}' and role_id={role.id}; "
    prev_galerie_message = database.fetch_one_line(sql)
    if not prev_galerie_message:
      sql = f"INSERT INTO welcome_message (`message`,`role_id`,`guild_id`) VALUES (?, {role.id},'{guild_id}') ;"
    else:
      sql = f"update welcome_message set message=? where guild_id='{guild_id}' and role_id={role.id} ;"
    logger ("welcome::set_welcome_message", sql)
    try:
      database.execute_order(sql, [message])
    except Exception as e:
      logger ("welcome::set_welcome_message", f"{type(e).__name__} - {e}")
    await ctx.channel.send(Utils.get_text(ctx.guild.id, "display_new_message").format(message))
    # await self.logger.log('welcome_log', ctx.author, ctx.message, error) # no logs

  @commands.command(name='updatewelcome', aliases=['uw'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def update_welcomeuser(self, ctx):
    guild_id = ctx.message.guild.id
    member = ctx.author
    select = f"select role_id from welcome_role where guild_id='{guild_id}'"
    fetched_all = database.fetch_all_line(select)
    if not fetched_all:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_role_defined"))
      return
    for fetched in fetched_all:
      role_id = int(fetched[0])
      # get the role
      role = ctx.guild.get_role(role_id)
      # write every member
      for member in role.members:
        # sql
        insert = ("insert into welcome_user (`user_id`, `role_id`, `welcomed_at`, `guild_id`)" +
                  f"values ('{member.id}', {role_id},{math.floor(time.time())}, '{guild_id}') ;")
        try:
          database.execute_order(insert)
        except Exception as e:
          logger ("welcome::update_welcomeuser", f'{type(e).__name__} - {e}')
    await ctx.message.add_reaction('✅')

  @commands.command(name='clearwelcome', aliases=['cw'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def reset_welcomeuser(self, ctx, member: discord.Member = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    member = member or author
    delete = ("delete from welcome_user " +
              " where " +
              f"user_id='{member.id}' ;" +
              ""
              )
    try:
      database.execute_order(delete)
    except Exception as e:
      await ctx.message.add_reaction('❌')
      logger ("welcome::reset_welcomeuser", f'{type(e).__name__} - {e}')
    else:
      await ctx.message.add_reaction('✅')
