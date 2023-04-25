import sys
import asyncio
import logging

import discord
from discord.ext import commands


import botconfig
import database
# IMPORT FOR AUTOBOT
from core import run_task, logger

DISCORD_CRON_CRONTAB         = {   "vote": "* * * * *"
                                 #, "utip": "* * * * *"
                                 , "birthday": "0 * * * *"
                                 , "rename": "* * * * * *"
                               }

DISCORD_TASKS                = []


def get_prefix(bot, message):
  """A callable Prefix for our bot."""
  prefixes = []
  if message.guild:
    select = ("select   prefix " +
              "from     config_prefix " +
              " where " +
              "guild_id='{0}' ;" +
              ""
              ).format(message.guild.id)
    fetched = database.fetch_all_line(select)
    if fetched:
      for line in fetched:
        prefixes.append(line[0])
  if not len(prefixes):
    prefixes = ['!']
  return commands.when_mentioned_or(*prefixes)(bot, message)


# Define all of our cogs
initial_extensions = ['cogs.loader'
  , 'cogs.logs'
  , 'cogs.invitation'
  , 'cogs.help'
  , 'cogs.nickname'
  , 'cogs.welcome'
  , 'cogs.bancommand'
  , 'cogs.roledm'
  , 'cogs.vote'
  , 'cogs.turing'
  , 'cogs.moderation'
  , 'cogs.configuration'
  , 'cogs.birthday'
  , 'cogs.gallery'
  , 'cogs.utip'
  , 'cogs.rules'
  , 'cogs.source'
  , 'cogs.pwet'
  , 'cogs.pet'
  , 'cogs.timer'
  , 'cogs.highlight'
                      ]

# intents = discord.Intents.default()
# intents.members = True
intents = discord.Intents().all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help")  # we used our own help command

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
  for extension in initial_extensions:
    bot.load_extension(extension)


@bot.event
async def on_guild_join(guild):
  guild_id = guild.id
  # Create default config
  inserts = [
    "insert into config_prefix (`prefix`, `guild_id`) values ('!', ?) ;"
    , "insert into config_delay (`delay`, `type_delay`, `guild_id`) values (0, 'nickname', ?) ;"
    , "insert into config_delay (`delay`, `type_delay`, `guild_id`) values (0, 'invite', ?) ;"
    , "insert into config_delay (`delay`, `type_delay`, `guild_id`) values (0, 'utip_role', ?) ;"
    , "insert into config_lang (`language_code`, `guild_id`) values ('en', ?) ;"
  ]
  for insert in inserts:
    database.execute_order(insert, [guild_id])
  botconfig.__language__[str(guild_id)] = "en"


@bot.event
async def on_ready():
  logged_in_as               = "Logged in as {0} [{1}]".format (bot.user.name, bot.user.id)
  discord_version            = "Discord.py version {0}".format(discord.__version__)
  len_logged_in_as           = len (logged_in_as)
  len_discord_version        = len (discord_version)
  discord_version            = discord_version + (" " * (len_logged_in_as-len_discord_version))
  dash                       = "----"+("-"*len_logged_in_as)
  
  login                      = (   "{0}\n"
                                   "| {1} |\n"
                                   "{0}\n"
                                   "| {2} |\n"
                                   "{0}\n"
                               ).format (dash, logged_in_as,  discord_version)
  print(login)
  try:
    await bot.change_presence(activity=discord.Game(name=botconfig.config['activity']))
    for guild in bot.guilds:
      select = "select language_code from config_lang where guild_id=? ;"
      language_code = database.fetch_one_line(select, [guild.id])
      botconfig.__language__[str(guild.id)] = language_code[0] if language_code else "en"
  except TypeError as type_err:
    logger ("bot::on_ready", "Error TypeError : {}".format(type_err))
    sys.exit(0)
  except Exception as e:
    logger ("bot::on_ready", f"{type(e).__name__} - {e}")
    sys.exit(0)

  # AUTOBOT
  try:
    for task in DISCORD_CRON_CRONTAB:
      interval               = DISCORD_CRON_CRONTAB [task]
      logger ("bot::on_ready::autobot", "Scheduling {0} with intervall [{1}]".format (task, interval))
      DISCORD_TASKS.append  (bot.loop.create_task (run_task (bot, task, interval)))
  except Exception as e:
    logger ("bot::on_ready::autobot", f"{type(e).__name__} - {e}")
    sys.exit(0)

@bot.event
async def on_command_error(ctx: commands.Context, exception):
  logger ("bot::on_command_error", f"ctx.message: {ctx.message.content}")
  logger ("bot::on_command_error", f"ctx.args: {ctx.args}")
  logger ("bot::on_command_error", f"ctx.command_failed: {ctx.command_failed}")
  print(exception)
  if not ctx.command:
    return
  await ctx.channel.send(exception)


@bot.event
async def on_disconnect ():
  logger ("bot::on_disconnect", "Called when the client has disconnected from Discord.")
  logger ("bot::on_disconnect", DISCORD_TASKS)
  for task in DISCORD_TASKS:
    logger ("bot::on_disconnect", "Cancel task.")
    task.cancel ()
    DISCORD_TASKS.remove (task)
  logger ("bot::on_disconnect", DISCORD_TASKS)

#@bot.event
#async def on_connect ():
  #logger ("bot::on_connect", "Called when the client has successfully connected to Discord.")

bot.run(botconfig.config['token'])
