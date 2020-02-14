import sys

import discord
from discord.ext import commands

import botconfig
import database
# IMPORT FOR AUTOBOT
from core import run_task, logger

DISCORD_CRON_CRONTAB         = {   "vote": "* * * * *"
                                 , "utip": "* * * * *"
                                 , "birthday": "* * * * *"
                               }

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
  , 'cogs.timer'
                      ]

bot = commands.Bot(command_prefix=get_prefix)
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
  login                      = (   "--------------------------------\n"
                                   "| Logged in as                 |\n"
                                   "| {0} [{1}] |\n"
                                   "--------------------------------\n"
                                   "| Discord.py version {2}     |\n"
                                   "--------------------------------\n"
                               ).format (bot.user.name, bot.user.id, discord.__version__)
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
      bot.loop.create_task (run_task (bot, task, interval))
  except Exception as e:
    logger ("bot::on_ready::autobot", f"{type(e).__name__} - {e}")
    sys.exit(0)

bot.run(botconfig.config['token'])
