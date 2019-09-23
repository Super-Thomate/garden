import discord
import sys
import os
from discord.ext import commands
import botconfig
from database import Database
import time
from datetime import datetime
import math

bot                          = discord.Client()
"""
AUTOBOT
Manages all recurrent tasks
Repeat itself every 60 seconds
## TODO
# Close proposition phase
# Close edit phase
# Close vote phase

"""
run_boy_run                  = True
sleepy_time                  = 60
@bot.event
async def on_ready():
  print (  ( "------\n"+
             "AUTOBOT AS\n"+
            f"{bot.user.name}\n"+
            f"{bot.user.id}\n"+
             "------"
           )
        )
  while run_boy_run:
    print (f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Running task")
    await vote_tasks()
    await utip_tasks ()
    time.sleep(sleepy_time)
    # sys.exit(0)

async def vote_tasks ():
  try:
    db                       = Database ()
    guilds                   = bot.guilds
    # print (f"guilds: {guilds}")
    # CLOSE PHASES"
    for guild in guilds:
      guild_id               = guild.id
      select                 = ( "select   message_id"+
                                 "       , channel_id"+
                                 "       , month"+
                                 "       , year"+
                                 "       , author_id"+
                                 "       , closed "+
                                 "from vote_message"+
                                 " where "+
                                f" guild_id='{guild_id}' and (closed <> 3) ;"
                               )
      fetched_all            = db.fetch_all_line (select)
      if fetched_all:
        # print (f"fetched_all: {fetched_all}")
        for line in fetched_all:
          # XX_ended_at > today => close
          # print (f"line: {line}")
          message_id         = int(line [0])
          channel_id         = int(line [1])
          author_id          = int(line [4])
          proposition_phase  = (line [5] == 0)
          edit_phase         = (line [5] == 1)
          vote_phase         = (line [5] == 2)
          # do i have to close it ?
          sql                = ( "select proposition_ended_at,edit_ended_at,"+
                                 "vote_ended_at from vote_time where "+
                                f"message_id='{message_id}' ;"
                               )
          fetch_ended_at     = db.fetch_one_line (sql)
          # print (f"fetch_ended_at: {fetch_ended_at}")
          if fetch_ended_at:
            proposition_ended_at       = fetch_ended_at [0]
            edit_ended_at    = fetch_ended_at [1]
            vote_ended_at    = fetch_ended_at [2]
            """
            print (f"vote_ended_at: {vote_ended_at}")
            print (f"time: {math.floor (time.time())}")
            if vote_ended_at:
              print (f"res: {vote_ended_at <= math.floor (time.time())}")
            """
            if (     (proposition_ended_at)
                 and (proposition_ended_at <= math.floor (time.time()))
                 and (proposition_phase)
               ):
              print ("close proposition")
              try:
                #print (f"guild: {guild.channels}")
                vote_channel = guild.get_channel (channel_id)
              except Exception as e:
                print (f"Error on guild.get_channel: {type(e).__name__} - {e}")
              if vote_channel:
                vote_message = None
                try:
                  vote_message         = await vote_channel.fetch_message (message_id)
                except Exception as e:
                  print (f"Error on vote_channel.fetch_message: {type(e).__name__} - {e}")
                if  vote_message:
                  print ("vote_channel and vote_message OK")
                  embed      = vote_message.embeds[0]
                  colour     = discord.Colour(0)
                  colour     = colour.from_rgb(56, 255, 56)
                  embed.colour         = colour
                  embed.set_footer(text=f"{line[2]}/{line[3]} Phase de "+
                                         "proposition terminée"
                                  )
                  await vote_message.edit (embed=embed)
                  update     = ( "update vote_message set closed = 1 where "+
                                f"message_id='{message_id}' ;"
                               )
                  db.execute_order(update)
                  #send feedback
                  select     = ( "select a.role_id, b.channel_id"+
                                 " from vote_role as a, vote_channel as b"+
                                 " where"+
                                 " a.guild_id=b.guild_id"+
                                 " and"+
                                f" a.guild_id='{guild_id}' ;"
                               )
                  # print (f"select: {select}")
                  fetched    = db.fetch_one_line(select)
                  # print (f"fetched: {fetched}")
                  if fetched:
                    feedback_role_id   = int (fetched [0])
                    feedback_channel_id          = int (fetched [1])
                    feedback_channel   = guild.get_channel (feedback_channel_id)
                    await feedback_channel.send (f"<@&{feedback_role_id}>"+
                                                  " La phase de proposition"+
                                                  " est terminée."
                                                )
                  else:
                    # nothing => send DM to author
                    await guild.get_member(author_id).send (
                          "La phase de proposition est terminée.\n"+
                          "Vous recevez ce message car le salon et/ou le rôle "+
                          "de vote ne sont pas correctements définis ou manquants."
                                                           )
                else:
                  print ("ERROR: NO MESSAGE FOUND")
              else:
                print ("ERROR: NO CHANNEL FOUND")
            if (     (vote_ended_at)
                 and (vote_ended_at <= math.floor (time.time()))
               ):
              print ("close vote")
              try:
                #print (f"guild: {guild.channels}")
                vote_channel = guild.get_channel (channel_id)
              except Exception as e:
                print (f"Error on guild.get_channel: {type(e).__name__} - {e}")
              if vote_channel:
                vote_message = None
                try:
                  vote_message         = await vote_channel.fetch_message (message_id)
                except Exception as e:
                  print (f"Error on vote_channel.fetch_message: {type(e).__name__} - {e}")
                if  vote_message:
                  embed      = vote_message.embeds[0]
                  colour     = discord.Colour(0)
                  colour     = colour.from_rgb(255, 71, 71)
                  embed.colour         = colour
                  embed.set_footer(text=f"{line[2]}/{line[3]} "+
                                         "Phase de vote terminée"
                                  )
                  embed      = embed_get_result (message_id, guild_id, embed)
                  await vote_message.edit (embed=embed)
                  update     = (f"update vote_message set closed = 3 "+
                                f"where message_id='{message_id}' ;"
                               )
                  db.execute_order(update)
                  #send feedback
                  select     = ( "select a.role_id, b.channel_id"+
                                 " from vote_role as a, vote_channel as b"+
                                f" where a.guild_id=b.guild_id and a.guild_id='{guild_id}' ;"
                               )
                  # print (f"select: {select}")
                  fetched    = db.fetch_one_line(select)
                  # print (f"fetched: {fetched}")
                  if fetched:
                    feedback_role_id   = int (fetched [0])
                    feedback_channel_id          = int (fetched [1])
                    feedback_channel   = guild.get_channel (feedback_channel_id)
                    await feedback_channel.send (f"<@&{feedback_role_id}> La phase de vote est terminée.")
                  else:
                    # nothing => send DM to author
                    await guild.get_member(author_id).send (
                          "La phase de vote est terminée.\n"+
                          "Vous recevez ce message car le salon et/ou le rôle de vote ne sont pas"+
                          " correctements définis ou manquants."
                                                           )
                else:
                  print ("ERROR: NO MESSAGE FOUND")
              else:
                print ("ERROR: NO CHANNEL FOUND")
  except Exception as e:
    print (f"auto task {type(e).__name__} - {e}")

async def utip_tasks ():
  try:
    db                       = Database ()
    guilds                   = bot.guilds
    # print (f"guilds: {guilds}")
    # CLOSE PHASES"
    for guild in guilds:
      guild_id               = guild.id
      select                 = ( "select   user_id"+
                                 "       , until"+
                                 " from utip_timer "+
                                 " where "+
                                f" guild_id='{guild_id}'"+
                                 " and "+
                                 " (until is not null and until <>0) "+
                                 " ;"
                               )
      fetched_all            = db.fetch_all_line (select)
      if fetched_all:
        select_role          = f"select role_id from utip_role where guild_id='{guild_id}' ;"
        fetched_role         = db.fetch_one_line (select_role)
        role_utip            = guild.get_role (int (fetched_role [0]))
        for utiper in fetched_all:
          user_id            = int (utiper [0])
          until              = utiper [1]
          if  math.floor(time.time()) > until:
            delete           = (  "delete from utip_timer "+
                                 f" where user_id='{user_id}'"+
                                  " and "+
                                 f" guild_id='{guild_id}' ;"+
                                  ""
                               )
            member           = guild.get_member (user_id)
            if member:
              await member.remove_roles(role_utip)
              await member.send("Vous n'avez plus le rôle de backers."+
                                " Si vous souhaitez le récupérer, faîtes une nouvelle demande."
                               )
              db.execute_order(delete)
              
  except Exception as e:
    print (f"auto task {type(e).__name__} - {e}")

def embed_get_result (message_id, guild_id, embed):
  db                         = Database ()
  field                      = embed.fields [0]
  select                     = ( "select proposition_id,emoji,proposition,ballot"+
                                 " from vote_propositions"+
                                f" where message_id='{message_id}' order by proposition_id asc ;"
                                )
  fetched                    = db.fetch_all_line (select)
  if not fetched:
    new_value                = "\uFEFF"
  else:
    print (f"fetched: {fetched}")
    for line in fetched:
      proposition_id         = line [0]
      emoji                  = line [1]
      proposition            = line [2]
      ballot                 = line [3]
      if proposition_id == 1:
        new_value            = "- "+emoji+" "+proposition+" ("+str(ballot)+")"
      else:
        new_value            = new_value +"\n - "+emoji+" "+proposition+" ("+str(ballot)+")"
  field                      = embed.fields [0]
  embed.clear_fields()
  embed.add_field (name=field.name, value=new_value, inline=False)
  return embed



bot.run(botconfig.config['token'])