"""
_Cron.py
Manage functions for automatic process
"""
import asyncio
# IMPORT
import math
import random
import time
from datetime import datetime

import discord
from crontab import CronTab

import Utils
import database
from .Logger import logger

async def vote_task (bot):
  try:
    guilds = bot.guilds
    # logger ("_Cron::vote_task", f"guilds: {guilds}")
    # CLOSE PHASES"
    for guild in guilds:
      guild_id = guild.id
      if not Utils.is_loaded("vote", guild_id):
        continue
      select = ("select   message_id" +
                "       , channel_id" +
                "       , month" +
                "       , year" +
                "       , author_id" +
                "       , closed " +
                "from vote_message" +
                " where " +
                f" guild_id='{guild_id}' and (closed <> 3) ;"
                )
      fetched_all = database.fetch_all_line(select)
      if fetched_all:
        # logger ("_Cron::vote_task", f"fetched_all: {fetched_all}")
        for line in fetched_all:
          # XX_ended_at > today => close
          # logger ("_Cron::vote_task", f"line: {line}")
          message_id = int(line[0])
          channel_id = int(line[1])
          author_id = int(line[4])
          proposition_phase = (line[5] == 0)
          edit_phase = (line[5] == 1)
          vote_phase = (line[5] == 2)
          # do i have to close it ?
          sql = ("select proposition_ended_at,edit_ended_at," +
                 "vote_ended_at from vote_time where " +
                 f"message_id='{message_id}' ;"
                 )
          fetch_ended_at = database.fetch_one_line(sql)
          # logger ("_Cron::vote_task", (f"fetch_ended_at: {fetch_ended_at}")
          if fetch_ended_at:
            proposition_ended_at = fetch_ended_at[0]
            edit_ended_at = fetch_ended_at[1]
            vote_ended_at = fetch_ended_at[2]
            """
            logger ("_Cron::vote_task", f"vote_ended_at: {vote_ended_at}")
            logger ("_Cron::vote_task", f"time: {math.floor (time.time())}")
            if vote_ended_at:
              logger ("_Cron::vote_task", f"res: {vote_ended_at <= math.floor (time.time())}")
            """
            if ((proposition_ended_at)
                    and (proposition_ended_at <= math.floor(time.time()))
                    and (proposition_phase)
            ):
              logger ("_Cron::vote_task", "close proposition")
              try:
                # plogger ("_Cron::vote_task", f"guild: {guild.channels}")
                vote_channel = guild.get_channel(channel_id)
              except Exception as e:
                logger ("_Cron::vote_task", f"Error on guild.get_channel: {type(e).__name__} - {e}")
              if vote_channel:
                vote_message = None
                try:
                  vote_message = await vote_channel.fetch_message(message_id)
                except Exception as e:
                  logger ("_Cron::vote_task", f"Error on vote_channel.fetch_message: {type(e).__name__} - {e}")
                if vote_message:
                  logger ("_Cron::vote_task", "vote_channel and vote_message OK")
                  embed = vote_message.embeds[0]
                  colour = discord.Colour(0)
                  colour = colour.from_rgb(56, 255, 56)
                  embed.colour = colour
                  embed.set_footer(text=f"{line[2]}/{line[3]} Phase de " +
                                        "proposition terminée"
                                   )
                  await vote_message.edit(embed=embed)
                  update = ("update vote_message set closed = 1 where " +
                            f"message_id='{message_id}' ;"
                            )
                  database.execute_order(update)
                  # send feedback
                  select = ("select a.role_id, b.channel_id" +
                            " from vote_role as a, vote_channel as b" +
                            " where" +
                            " a.guild_id=b.guild_id" +
                            " and" +
                            f" a.guild_id='{guild_id}' ;"
                            )
                  # logger ("_Cron::vote_task", f"select: {select}")
                  fetched = database.fetch_one_line(select)
                  # logger ("_Cron::vote_task", f"fetched: {fetched}")
                  if fetched:
                    feedback_role_id = int(fetched[0])
                    feedback_channel_id = int(fetched[1])
                    feedback_channel = guild.get_channel(feedback_channel_id)
                    await feedback_channel.send(
                      Utils.get_text(guild_id, "vote_proposition_phase_end_2").format(f'<@&{feedback_role_id}>'))
                  else:
                    # nothing => send DM to author
                    await guild.get_member(author_id).send(Utils.get_text('fr', 'vote_proposition_phase_end_3'))
                else:
                  logger ("_Cron::vote_task", "ERROR: NO MESSAGE FOUND")
              else:
                logger ("_Cron::vote_task", "ERROR: NO CHANNEL FOUND")
            if ((vote_ended_at)
                    and (vote_ended_at <= math.floor(time.time()))
            ):
              logger ("_Cron::vote_task", "close vote")
              try:
                # logger ("_Cron::vote_task", f"guild: {guild.channels}")
                vote_channel = guild.get_channel(channel_id)
              except Exception as e:
                logger ("_Cron::vote_task", f"Error on guild.get_channel: {type(e).__name__} - {e}")
              if vote_channel:
                vote_message = None
                try:
                  vote_message = await vote_channel.fetch_message(message_id)
                except Exception as e:
                  logger ("_Cron::vote_task", f"Error on vote_channel.fetch_message: {type(e).__name__} - {e}")
                if vote_message:
                  embed = vote_message.embeds[0]
                  colour = discord.Colour(0)
                  colour = colour.from_rgb(255, 71, 71)
                  embed.colour = colour
                  embed.set_footer(text=f"{line[2]}/{line[3]} " +
                                        "Phase de vote terminée"
                                   )
                  embed = embed_get_result(message_id, guild_id, embed)
                  await vote_message.edit(embed=embed)
                  update = (f"update vote_message set closed = 3 " +
                            f"where message_id='{message_id}' ;"
                            )
                  database.execute_order(update)
                  # send feedback
                  select = ("select a.role_id, b.channel_id" +
                            " from vote_role as a, vote_channel as b" +
                            f" where a.guild_id=b.guild_id and a.guild_id='{guild_id}' ;"
                            )
                  # logger ("_Cron::vote_task", f"select: {select}")
                  fetched = database.fetch_one_line(select)
                  # logger ("_Cron::vote_task", f"fetched: {fetched}")
                  if fetched:
                    feedback_role_id = int(fetched[0])
                    feedback_channel_id = int(fetched[1])
                    feedback_channel = guild.get_channel(feedback_channel_id)
                    await feedback_channel.send(
                      Utils.get_text(guild_id, "vote_proposition_phase_end_2").format(f'<@&{feedback_role_id}>'))
                  else:
                    # nothing => send DM to author
                    await guild.get_member(author_id).send(Utils.get_text('fr', 'vote_phase_end_2'))
                else:
                  logger ("_Cron::vote_task", "ERROR: NO MESSAGE FOUND")
              else:
                logger ("_Cron::vote_task", "ERROR: NO CHANNEL FOUND")
  except Exception as e:
    logger ("_Cron::vote_task", f"auto task {type(e).__name__} - {e}")

async def utip_task (bot):
  try:
    guilds = bot.guilds
    # logger ("_Cron::utip_task", f"guilds: {guilds}")
    # CLOSE PHASES"
    for guild in guilds:
      guild_id = guild.id
      if not Utils.is_loaded("utip", guild_id):
        continue
      select = ("select   user_id" +
                "       , until" +
                " from utip_timer " +
                " where " +
                f" guild_id='{guild_id}'" +
                " and " +
                " (until is not null and until <>0) " +
                " ;"
                )
      logger ("_Cron::utip_task", f"select: {select}")
      fetched_all = database.fetch_all_line(select)
      if fetched_all:
        select_role = f"select role_id from utip_role where guild_id='{guild_id}' ;"
        logger ("_Cron::utip_task", f"select_role: {select_role}")
        fetched_role = database.fetch_one_line(select_role)
        role_utip = guild.get_role(int(fetched_role[0]))
        for utiper in fetched_all:
          user_id = int(utiper[0])
          until = utiper[1]
          if math.floor(time.time()) > until:
            delete = ("delete from utip_timer " +
                      f" where user_id='{user_id}'" +
                      " and " +
                      f" guild_id='{guild_id}' ;" +
                      ""
                      )
            database.execute_order(delete)
            logger ("_Cron::utip_task", f"delete: {delete}")
            member = guild.get_member(user_id)
            logger ("_Cron::utip_task", f"member: {str(member)}")
            logger ("_Cron::utip_task", f"role_utip: {role_utip.name} [{role_utip.id}]")
            if member:
              await member.remove_roles(role_utip)
              await member.send(Utils.get_text(int(guild_id), 'utip_user_lost_role'))
  except Exception as e:
    logger ("_Cron::utip_task", f"{type(e).__name__} - {e}")


def embed_get_result (message_id, guild_id, embed):
  field = embed.fields[0]
  select = ("select proposition_id,emoji,proposition,ballot" +
            " from vote_propositions" +
            f" where message_id='{message_id}' order by proposition_id asc ;"
            )
  fetched = database.fetch_all_line(select)
  if not fetched:
    new_value = "\uFEFF"
  else:
    logger ("_Cron::embed_get_result", f"fetched: {fetched}")
    for line in fetched:
      proposition_id = line[0]
      emoji = line[1]
      proposition = line[2]
      ballot = line[3]
      if proposition_id == 1:
        new_value = "- " + emoji + " " + proposition + " (" + str(ballot) + ")"
      else:
        new_value = new_value + "\n - " + emoji + " " + proposition + " (" + str(ballot) + ")"
  field = embed.fields[0]
  embed.clear_fields()
  embed.add_field(name=field.name, value=new_value, inline=False)
  return embed


async def birthday_task(bot):
  try:
    for guild in bot.guilds:
      guild_id = guild.id
      if not Utils.is_loaded("birthday", guild_id):
        continue
      sql = "SELECT time FROM birthday_time WHERE guild_id=? ;"
      response = database.fetch_one_line(sql, [guild_id])
      if not (response is None or response[0] is None):
        birthday_hour = int(response[0])
        current_hour = int(datetime.now().strftime('%-H'))
        if current_hour < birthday_hour:
          logger("_Cron::birthday_task", f"It is {current_hour}; birthdays are wished at {birthday_hour} and after")
          continue
      sql = "SELECT channel_id FROM birthday_channel WHERE guild_id=? ;"
      channel_id = database.fetch_one_line(sql, [guild_id])
      if not channel_id:
        logger("_Cron::birthday_task", f"birthday_channel not set for guild {guild.name}")
        continue
      birthday_channel = guild.get_channel(int(channel_id[0]))
      date = datetime.now().strftime('%d/%m')
      sql = "SELECT user_id, guild_id, last_year_wished FROM birthday_user WHERE user_birthday=? AND guild_id=? ;"
      data = database.fetch_all_line(sql, [date, guild_id])
      current_year = datetime.now().strftime('%Y')
      logger ("_Cron::birthday_task", f"birthday_channel: {birthday_channel} in guild {guild.name}")
      if not birthday_channel:
        logger ("_Cron::birthday_task", f"birthday_channel not found in guild {guild.name} !")
        continue
      for line in data:
        member_id, guild_id, last_year_wished = line[0], line[1], line[2]
        member = guild.get_member(int(member_id))
        if not member or current_year == last_year_wished:
          logger("_Cron::birthday_task", f"Birthday already wished this year for member {member}")
          continue
        birthday_message = get_birthday_message(guild, member)
        await birthday_channel.send(birthday_message)
        logger("_Cron::birthday_task", f"Wishing birthday to member {member.name}")
        sql = f"UPDATE birthday_user SET last_year_wished=? WHERE user_id=? AND guild_id=? ;"
        try:
          database.execute_order(sql, [current_year, member_id, guild_id])
        except Exception as e:
          await birthday_channel.send(Utils.get_text(guild_id, 'error_database_writing'))
          logger ("_Cron::birthday_task", f"execute_order {type(e).__name__} - {e}")
      logger ("_Cron::birthday_task", f"End of birthday loop for guild {guild.name}\n---")
  except Exception as e:
    logger ("_Cron::birthday_task", f"birthday_task {type(e).__name__} - {e}")


def get_birthday_message (guild: discord.Guild, member: discord.Member) -> str:
  select = f"SELECT message FROM birthday_message WHERE guild_id='{guild.id}' ;"
  fetched = database.fetch_one_line(select)
  if not fetched:
    logger("_Cron::birthday_task::get_birthday_message", f"Birthday message not set for guild {guild.name}")
    return f"Happy birthday {member.mention} !"
  text = ""
  # split around '{'
  text_rand = (fetched[0]).split('{')
  logger ("_Cron::get_birthday_message", "text_rand: {text_rand}")
  for current in text_rand:
    parts = current.split('}')
    logger ("_Cron::get_birthday_message", f"parts: {parts}")
    for part in parts:
      all_rand = part.split("|")
      logger ("_Cron::get_birthday_message", f"all_rand: {all_rand}")
      current_part = random.choice(all_rand)
      logger ("_Cron::get_birthday_message", f"current_part: {current_part}")
      text = text + current_part
  return text.replace("$member", f"{member.mention}")


def get_random_nickname(guild_id: int):
  sql = "SELECT nicknames FROM nickname_next_troll_nickname WHERE guild_id=? ;"
  response = database.fetch_one_line(sql, [guild_id])
  return random.choice(response[0].split('|')) if response else None

async def rename_warn_task(bot):
  try:
    for guild in bot.guilds:
      guild_id = guild.id
      if not Utils.is_loaded("nickname", guild_id):
        continue
      sql = "SELECT member_id, timer_limit FROM nickname_next_limit WHERE guild_id=? ;"
      response = database.fetch_all_line(sql, [guild_id])
      for data in response:
        limit = time.mktime(datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S').timetuple())
        duration = math.floor((limit - time.time()))
        if duration > 0:
          continue
        member = guild.get_member(int(data[0]))

        # Warn user and punish if already warned
        sql = "SELECT * FROM nickname_next_warn WHERE member_id=? AND guild_id=? ;"
        response = database.fetch_one_line(sql, [member.id, guild_id])

        # If user has already been warned, hard rename
        if response:
          nickname = get_random_nickname(guild_id) or Utils.get_text(guild_id, "nickname_troll_nickname")
          await member.edit(nick=nickname)
          # write in db last_time
          select = f"SELECT * FROM last_nickname WHERE guild_id='{guild_id}' AND member_id='{member.id}'"
          fetched = database.fetch_one_line(select)
          if not fetched:
            sql = f"INSERT INTO last_nickname VALUES ('{member.id}', '{guild_id}', datetime('{datetime.now()}'))"
          else:
            sql = f"UPDATE last_nickname SET last_change=datetime('{datetime.now()}') WHERE member_id='{member.id}' AND guild_id='{guild_id}'"
          database.execute_order(sql, [])

          # write in db current nickanme
          select = f"SELECT * FROM nickname_current WHERE guild_id='{guild_id}' AND member_id='{member.id}' ;"
          fetched = database.fetch_one_line(select)
          if not fetched:
            sql = f"INSERT INTO nickname_current VALUES ('{member.id}', '{guild_id}', ?) ;"
          else:
            sql = f"UPDATE nickname_current SET nickname=? WHERE member_id='{member.id}' AND guild_id='{guild_id}' ;"
          database.execute_order(sql, [nickname])

        # Soft rename and add a warn
        else:
          nickname = Utils.get_text(guild_id, "nickname_troll_nickname")
          await member.edit(nick=nickname)
          sql = "INSERT INTO nickname_next_warn VALUES (?, ?) ;"
          database.execute_order(sql, [member.id, guild_id])

        # Delete limit record
        sql = "DELETE FROM nickname_next_limit WHERE member_id=? AND guild_id=? ;"
        database.execute_order(sql, [member.id, guild_id])

  except Exception as e:
    logger ("_Cron::rename_warn_task", f"rename_warn_task {type(e).__name__} - {e}")


async def run_task (bot, task, interval):
  await bot.wait_until_ready()
  cron = CronTab(interval)
  while True:
    try:
      await asyncio.sleep(cron.next(default_utc=True))
    except Exception as e:
      logger ("_Cron::run_task", f"task {task} => {type(e).__name__} - {e}")
    try:
      if task == "vote":
        await vote_task (bot)
      elif task == "utip":
        await utip_task (bot)
      elif task == "birthday":
        await birthday_task (bot)
      elif task == "rename":
        await rename_warn_task (bot)
    except:
      logger ("_Cron::run_task", f'I could not perform task `{task}` :(')
