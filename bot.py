import discord
import sys
import os
from discord.ext import commands
import botconfig

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    prefixes = botconfig.config['prefixes']
    return commands.when_mentioned_or(*prefixes)(bot, message)

# Define all of our cogs
initial_extensions = [   'cogs.loader'
                       , 'cogs.logs'
                       , 'cogs.invitation'
                     ]

bot = commands.Bot(command_prefix=get_prefix)

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
    await bot.change_presence(activity=discord.Game(name=" gardening"))
  except TypeError as type_err:
    print ("Error TypeError : {}".format(type_err))
    sys.exit(0)
  except :
    print ("Error {}".format(sys.exc_info()[0]))
    sys.exit(0)

# instance = sys.argv[1]

bot.run(botconfig.config['tokens'][sys.argv[1]])