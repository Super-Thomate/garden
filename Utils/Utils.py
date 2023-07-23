import inspect
import json
import math
import os
import re
import sys
import time
from threading import Timer as _Timer
from functools import wraps
from urllib.request import urlopen
from core.Logger import logger

import botconfig
import database
import emoji

from discord.ext.commands import BadArgument, EmojiConverter
from discord.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
strings = {}
for language in botconfig.config["languages"]:
  with open(f'{dir_path}../language_files/{language}.json', 'r') as file:
    strings[language] = json.load(file)


def require(required: list):
  def decorator(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
      ctx = args[1]
      if 'authorized' in required:
        if not is_authorized(ctx.author, ctx.guild.id):
          logger ("Utils::require::is_authorized", "Missing permissions")
          return
      if 'not_banned' in required:
        if is_banned(ctx.command, ctx.author, ctx.guild.id):
          await ctx.send("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
          await ctx.message.add_reaction('❌')
          return
      if 'cog_loaded' in required:
        if not is_loaded(ctx.cog.qualified_name.lower(), ctx.guild.id):
          if is_authorized(ctx.author, ctx.guild.id):
            await ctx.send(get_text(ctx.guild.id, "not_loaded").format(ctx.command, ctx.cog.qualified_name.lower()))
            await ctx.message.add_reaction('❌')
          return False
      return await f(*args, **kwargs)

    return decorated

  return decorator


def is_authorized(member, guild_id):
  # Test server bypasses
  if guild_id == 494812563016777729:
    return True
  # admin can't be blocked
  try:
    if is_admin(member):
      return True
  except Exception as e:
      logger ("Utils::is_authorized", f"{type(e).__name__} - {e}")
      return False
  # if perm
  try:
    if is_allowed(member, guild_id):
      return True
  except Exception as e:
      logger ("Utils::is_authorized", f"{type(e).__name__} - {e}")
      return False



def is_banned(command, member, guild_id):
  # admin can't be blocked
  if is_admin(member):
    return False
  # ban user
  select = f"select until from ban_command_user where guild_id='{guild_id}' and user_id='{member.id}' and command='{command}' ;"
  fetched = database.fetch_one_line(select)
  if fetched:
    try:
      until = int(fetched[0])
    except Exception as e:
      logger ("Utils::is_banned", f"{type(e).__name__} - {e}")
      return True
    if until > math.floor(time.time()):  # still ban
      return True
  # ban role
  select = f"select until,role_id from ban_command_role where guild_id='{guild_id}' and command='{command}' ;"
  fetched = database.fetch_all_line(select)
  if fetched:
    for line in fetched:
      try:
        role_id = int(line[1])
      except Exception as e:
        logger ("Utils::is_banned", f"{type(e).__name__} - {e}")
        return True
      if has_role(role_id, member):
        try:
          until = int(line[0])
        except Exception as e:
          logger ("Utils::is_banned", f"{type(e).__name__} - {e}")
          return True
        if until > math.floor(time.time()):  # still ban
          return True
  # neither
  return False


def is_banned_user(command, member, guild_id):
  select = f"select until from ban_command_user where guild_id='{guild_id}' and user_id='{member.id}' and command='{command}' ;"
  fetched = database.fetch_one_line(select)
  if fetched:
    try:
      until = int(fetched[0])
    except Exception as e:
      logger ("Utils::is_banned_user", f"{type(e).__name__} - {e}")
      return True
    return until > math.floor(time.time())  # still ban
  return False


def is_banned_role(command, member, guild_id):
  select = f"select until,role_id from ban_command_role where guild_id='{guild_id}' and command='{command}' ;"
  fetched = database.fetch_one_line(select)
  if fetched:
    try:
      role_id = int(fetched[1])
    except Exception as e:
      logger ("Utils::is_banned_role", f"{type(e).__name__} - {e}")
      return True
    if has_role(role_id, member):
      try:
        until = int(fetched[0])
      except Exception as e:
        logger ("Utils::is_banned_role", f"{type(e).__name__} - {e}")
        return True
      return until > math.floor(time.time())  # still ban
  return False


def is_admin(member):
  # if perm administrator => True
  for perm, value in member.guild_permissions:
    if perm == "administrator" and value:
      return True
  return False


def is_allowed(member, guild_id):
  for obj_role in member.roles:
    if ((obj_role.id in get_roles_modo(guild_id))
    ):
      return True
  return False


def format_time(timestamp):
  timer = [["j", 86400]
    , ["h", 3600]
    , ["m", 60]
    , ["s", 1]
           ]
  current = timestamp
  logger ("Utils::format_time", f"current: {current}")
  to_ret = ""
  for obj_time in timer:
    if math.floor(current / obj_time[1]) > 0:
      to_ret += str(math.floor(current / obj_time[1])) + obj_time[0] + " "
      current = current % obj_time[1]
  if not len(to_ret):
    logger ("Utils::format_time", "to ret is empty")
  return to_ret.strip()


def has_role(member, role_id):
  try:
    for obj_role in member.roles:
      if obj_role.id == int(role_id):
        return True
  except Exception as e:
    logger ("Utils::has_role", f"{type(e).__name__} - {e}")
  return False


def parse_time(timestr):
  units = {   "j": 86400
            , "h": 3600
            , "m": 60
            , "s": 1
          }
  to_ret = 0
  number = 0
  for elem in timestr:
    try:
      cast = int(elem)
    except Exception:
      # is it a letter in units ?
      if elem not in units:
        raise Exception(f"Unknown element: {elem}")
      to_ret = to_ret + number * units[elem]
      number = 0
    else:
      number = number * 10 + cast
  return to_ret


def get_roles_modo(guild_id):
  all_roles = []
  select = ("select   role_id " +
            "from     config_role " +
            "where " +
            "          permission=1 " +
            "      and " +
            f"          guild_id='{guild_id}' " +
            ";" +
            ""
            )
  try:
    fetched = database.fetch_all_line(select)
  except Exception as e:
    logger ("Utils::get_roles_modo", f"{type(e).__name__} - {e}")
  if fetched:
    for role_fetched in fetched:
      all_roles.append(int(role_fetched[0]))
  return all_roles


def debug(message):
  """
  Debug function, to use rather than print (message)
  https://stackoverflow.com/questions/6810999/how-to-determine-file-function-and-line-number
  """
  info = inspect.getframeinfo((inspect.stack()[1])[0])
  print(sys._getframe().f_lineno)
  print(info.filename, 'func=%s' % info.function, 'line=%s:' % info.lineno, message)


def do_invite(guild_id):
  select = ("select   do " +
            "       , type_do " +
            "from     config_do " +
            "where " +
            "          type_do='invite' " +
            "      and " +
            f"          guild_id='{guild_id}' " +
            ";" +
            ""
            )
  try:
    fetched = database.fetch_one_line(select)
  except Exception as e:
    logger ("Utils::do_invite", f"{type(e).__name__} - {e}")
  if fetched:
    return (fetched[0] == 1)
  return False


def do_token(guild_id):
  select = ("select   do " +
            "       , type_do " +
            "from     config_do " +
            "where " +
            "          type_do='token' " +
            "      and " +
            f"          guild_id='{guild_id}' " +
            ";" +
            ""
            )
  try:
    fetched = database.fetch_one_line(select)
  except Exception as e:
    logger ("Utils::do_token", f"{type(e).__name__} - {e}")
  if fetched:
    return (fetched[0] == 1)
  return False


def invite_delay (guild_id):
  select = ("select   delay " +
            "       , type_delay " +
            "from     config_delay " +
            "where " +
            "          type_delay='invite' " +
            "      and " +
            f"          guild_id='{guild_id}' " +
            ";" +
            ""
            )
  try:
    fetched = database.fetch_one_line(select)
  except Exception as e:
    logger ("Utils::invite_delay", f"{type(e).__name__} - {e}")
  if fetched:
    return fetched[0]
  return None


def nickname_delay (guild_id):
  select = ("select   delay " +
            "       , type_delay " +
            "from     config_delay " +
            "where " +
            "          type_delay='nickname' " +
            "      and " +
            f"          guild_id='{guild_id}' " +
            ";" +
            ""
            )
  try:
    fetched = database.fetch_one_line(select)
  except Exception as e:
    logger ("Utils::nickname_delay", f"{type(e).__name__} - {e}")
  if fetched:
    return fetched[0]
  return None


def invite_url (guild_id):
  select = ("select   url " +
            "       , type_url " +
            "from     config_url " +
            "where " +
            "          type_url='invite' " +
            "      and " +
            f"          guild_id='{guild_id}' " +
            ";" +
            ""
            )
  try:
    fetched = database.fetch_one_line(select)
  except Exception as e:
    logger ("Utils::invite_url", f"{type(e).__name__} - {e}")
  if fetched:
    return fetched[0]
  return ""


def token_url (guild_id):
  select = ("select   url " +
            "       , type_url " +
            "from     config_url " +
            "where " +
            "          type_url='token' " +
            "      and " +
            f"          guild_id='{guild_id}' " +
            ";" +
            ""
            )
  try:
    fetched = database.fetch_one_line(select)
  except Exception as e:
    logger ("Utils::token_url", f"{type(e).__name__} - {e}")
  if fetched:
    return fetched[0]
  return ""


def is_valid_url(url):
  regex = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
  return url is not None and regex.search(url)


def is_url_image(image_url):
  if not is_valid_url(image_url):
    return False
  image_formats = ("image/png", "image/jpeg", "image/jpg", "image/gif")
  try:
    site = urlopen(image_url)
    meta = site.info()  # get header of the http request
  except Exception as e:
    logger ("Utils::is_url_image", f"{type(e).__name__} - {e}")
    return False
  return meta["content-type"] in image_formats


def convert_str_to_time(time_string):
  time_array = time_string.split(" ")
  logger ("Utils::convert_str_to_time", f"time_array: {time_array}")
  timestamp = 0
  current = 0
  for element in time_array:
    logger ("Utils::convert_str_to_time", f"element: {element}")
    if element.isnumeric():
      current = int(element)
      logger ("Utils::convert_str_to_time", f"isnumeric = current: {current}")
    else:
      if element == "months":
        current = current * 28 * 24 * 3600
      elif element == "weeks":
        current = current * 7 * 24 * 3600
      logger ("Utils::convert_str_to_time", f"else current: {current}")
      timestamp = timestamp + current
      current = 0
  logger ("Utils::convert_str_to_time", f"timestamp: {timestamp}")
  return timestamp


def get_text(guild_id: int, text_key: str) -> str:
  language_code = botconfig.__language__[str(guild_id)]
  try:
    return strings[language_code][text_key]
  except KeyError:
    return f"**keyError** for `{text_key}` in language `{language_code}`. Show this message to a moderator."


async def delete_messages(*args):
  for msg in args:
    await msg.delete(delay=2)


def is_loaded(cog, guild_id):
  if (cog in ["configuration", "help", "loader", "logs"]):
    return True
  if (guild_id is None):
    logger ("Utils::is_loaded", "is_loaded({0}, {1})".format(cog, guild_id))
    return False
  try:
    guild_id = int(guild_id)
    select = ("select   status "
              "from     config_cog " +
              "where " +
              "cog=? " +
              " and " +
              "guild_id=? ;" +
              ""
              )
    try:
      fetched = database.fetch_one_line(select, [str(cog), guild_id])
      if (fetched):
        logger ("Utils::is_loaded", f"fetched: {fetched[0]}")
      else:
        logger ("Utils::is_loaded", f"fetched: null")
    except Exception as e:
      logger ("Utils::is_loaded", f"{type(e).__name__} - {e}")
    # logger ("Utils::is_loaded", f"In fetched for {str(cog)}: {fetched}")
    return (fetched and fetched[0] == 1)
  except Exception as e:
    logger ("Utils::is_loaded", f"{type(e).__name__} - {e}")
    return False


def set_log_channel(table: str, channel_id: int, guild_id: int):
  sql = f"SELECT channel_id FROM {table} WHERE guild_id='{guild_id}'"
  is_already_set = database.fetch_one_line(sql)
  if is_already_set:
    sql = f"UPDATE {table} SET channel_id='{channel_id}' WHERE guild_id='{guild_id}'"
  else:
    sql = f"INSERT INTO {table} VALUES ('{channel_id}', '{guild_id}') ;"
  try:
    database.execute_order(sql, [])
  except Exception as e:
    logger ("Utils::set_log_channel", f"{type(e).__name__} - {e}")
    return False
  return True


def is_custom_emoji(emoji_text: str):
  split = emoji_text.split(':')
  if len(split) == 3:
    return split[2][:-1]  # remove '>' at the end
  return None

def is_emoji (character: str):
  return character in emoji.UNICODE_EMOJI

async def get_emoji (ctx: commands.Context, emoji: str):
  try:
    converter              = EmojiConverter ()
    return await converter.convert (ctx, emoji)
  except BadArgument:
    if is_emoji (emoji):
      return emoji
    raise

def emojize (character: str):
  return emoji.emojize (character, use_aliases=True)

def demojize (character: str):
  return emoji.demojize (character)

def setInterval(timer, task, *args):
  isStop                     = task()
  if not isStop:
    _Timer(timer, setInterval, [timer, task, args]).start()

def str_bool (boolean: bool):
  return "True" if boolean else "False"