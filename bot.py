import discord
import sys
import os
from discord.ext import commands
from database import Database
import botconfig


def get_prefix(bot, message):
    """A callable Prefix for our bot."""
    prefixes = []
    if message.guild:
      prefixes = botconfig.config[str(message.guild.id)]['prefixes']
      db                     = Database ()
      select                 = (   "select   prefix "+
                                   "from     config_prefix "+
                                   " where "+
                                  f"guild_id='{message.guild.id}' ;"+
                                   ""
                               )
      fetched                = db.fetch_all_line (select)
      if fetched:
        for line in fetched:
          prefixes.append (line [0])
    if not len (prefixes):
      prefixes               = ['!']
    return commands.when_mentioned_or(*prefixes)(bot, message)

# Define all of our cogs
initial_extensions = [   'cogs.loader'
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
                     #  , 'cogs.birthday'
                       , 'cogs.gallery'
                       , 'cogs.utip'
                     ]

bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command("help") # we used our own help command

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
  for extension in initial_extensions:
    bot.load_extension(extension)

@bot.event
async def on_guild_join(guild):
  guild_id                   = guild.id
  # Create default config
  insert                     = [
     f"insert into config_prefix (`prefix`, `guild_id`) values ('!', '{guild_id}')"
   , f"insert into config_delay (`delay`, `type_delay`, `guild_id`) values (0, 'nickname', '{guild_id}')"
   , f"insert into config_delay (`delay`, `type_delay`, `guild_id`) values (0, 'invite', '{guild_id}')"
   , f"insert into config_delay (`delay`, `type_delay`, `guild_id`) values (0, 'utip_role', '{guild_id}')"
                               ]
"""
, "494812563016777729": {"roles":["ModoBot","Bénévoles","Modosdudiscord","Fondateur-admin","Pèsedanslegame","Modosstagiaires","Touristesbienveillant.e.s","Equipedelaplateforme"],"prefixes":["!","?","-"],"create_url":{"invitation":"https://admin.realms-of-fantasy.net/bot.php","gallery":"https://admin.realms-of-fantasy.net/bot-AR.php?"},"invite_delay":"6 months","do_invite":1,"do_token":1,"nickname_delay":"7 days"}
"""
  
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