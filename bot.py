import discord
import sys
import os
from discord.ext import commands
import botconfig


def get_prefix(bot, message):
    """A callable Prefix for our bot."""
    prefixes = botconfig.config[str(message.guild.id)]['prefixes']
    return commands.when_mentioned_or(*prefixes)(bot, message)

initial_extensions = []

# Define all of our cogs
initial_extensions = [   'cogs.loader'
                       , 'cogs.logs'
                       , 'cogs.invitation'
                       , 'cogs.help'
                     ]

bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command("help") # we used our own help command

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
  for extension in initial_extensions:
    bot.load_extension(extension)


@bot.event
async def on_ready():
  print('------')
  print('Logged in as')
  print(bot.user.name)
  print(bot.user.id)
  print('------')
  print('Discord.py version')
  print(discord.__version__)
  print('------')
  try:
    await bot.change_presence(activity=discord.Game(name=botconfig.config['activity']))
  except TypeError as type_err:
    print ("Error TypeError : {}".format(type_err))
    sys.exit(0)
  except Exception as e:
    print (f"{type(e).__name__} - {e}")
    sys.exit(0)

bot.run(botconfig.config['token'])