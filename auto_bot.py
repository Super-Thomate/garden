import discord
import sys
import os
from discord.ext import commands
import botconfig
from database import Database
import time
import math

bot                          = discord.Client()
"""
AUTOBOT
Manages all recurrent tasks
Launch by a cron 
* * * * * /usr/bin/python3 /path/to/garden/auto_bot.py Carotte 1>/path/to/garden/auto_bot_Carotte.log 2>/path/to/garden/auto_bot_Carotte.log.err
## TODO
# Close proposition phase
# Close edit phase
# Close vote phase

"""

@bot.event
async def on_ready():
  print (  ( "------\n"+
             "AUTOBOT AS\n"+
            f"{bot.user.name}\n"+
            f"{bot.user.id}\n"+
             "------"
           )
        )
  try:
    db                       = Database ()
    guilds                   = bot.guilds
    # print (f"guilds: {guilds}")
    # CLOSE PHASES"
    for guild in guilds:
      guild_id               = guild.id
      select                 = ( "select message_id,channel_id,month,year,"+
                                 "author_id,closed from vote_message where "+
                                f"guild_id='{guild_id}' and (closed <> 3) ;"
                               )
      fetched                = db.fetch_all_line (select)
      if fetched:
        # print (f"fetched: {fetched}")
        for line in fetched:
          # XX_ended_at > today => close
          message_id         = int(line [0])
          channel_id         = int(line [1])
          author_id          = int(line [4])
          proposition_phase  = (fetched [5] == 0)
          edit_phase         = (fetched [5] == 1)
          vote_phase         = (fetched [5] == 2)
          # do i have to close it ?
          sql                = ( "select proposition_ended_at,edit_ended_at,"+
                                 "vote_ended_at from vote_time where "+
                                f"message_id='{message_id}' ;"
                               )
          fetch_ended_at     = db.fetch_one_line (sql)
          proposition_ended_at         = fetch_ended_at [0]
          edit_ended_at      = fetch_ended_at [1]
          vote_ended_at      = fetch_ended_at [2]
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
              vote_channel   = guild.get_channel (channel_id)
            except Exception as e:
              print (f"Error on guild.get_channel: {type(e).__name__} - {e}")
              sys.exit(0)
            if vote_channel:
              vote_message   = await vote_channel.fetch_message (message_id)
              if  vote_message:
                print ("vote_channel and vote_message OK")
                embed        = vote_message.embeds[0]
                colour       = discord.Colour(0)
                colour       = colour.from_rgb(56, 255, 56)
                embed.colour = colour
                embed.set_footer(text=f"{line[2]}/{line[3]} Phase de "+
                                       "proposition terminée"
                                )
                await vote_message.edit (embed=embed)
                update       = ( "update vote_message set closed = 1 where "+
                                f"message_id='{message_id}' ;"
                               )
                db.execute_order(update)
                #send feedback
                select       = ( "select a.role_id, b.channel_id"+
                                 " from vote_role as a, vote_channel as b"+
                                 " where"+
                                 " a.guild_id=b.guild_id"+
                                 " and"+
                                f" a.guild_id='{guild_id}' ;"
                               )
                # print (f"select: {select}")
                fetched      = db.fetch_one_line(select)
                # print (f"fetched: {fetched}")
                if fetched:
                  feedback_role_id     = int (fetched [0])
                  feedback_channel_id  = int (fetched [1])
                  feedback_channel     = guild.get_channel (feedback_channel_id)
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
              vote_channel   = guild.get_channel (channel_id)
            except Exception as e:
              print (f"Error on guild.get_channel: {type(e).__name__} - {e}")
              sys.exit(0)
            if vote_channel:
              vote_message   = await vote_channel.fetch_message (message_id)
              if  vote_message:
                embed        = vote_message.embeds[0]
                colour       = discord.Colour(0)
                colour       = colour.from_rgb(255, 71, 71)
                embed.colour = colour
                embed.set_footer(text=f"{line[2]}/{line[3]} "+
                                       "Phase de vote terminée"
                                )
                embed        = embed_get_result (message_id, guild_id, embed)
                await vote_message.edit (embed=embed)
                update       = (f"update vote_message set closed = 3 "+
                                "where message_id='{message_id}' ;"
                               )
                db.execute_order(update)
                #send feedback
                select       = ( "select a.role_id, b.channel_id"+
                                 " from vote_role as a, vote_channel as b"+
                                f" where a.guild_id=b.guild_id and a.guild_id='{guild_id}' ;"
                               )
                # print (f"select: {select}")
                fetched      = db.fetch_one_line(select)
                # print (f"fetched: {fetched}")
                if fetched:
                  feedback_role_id     = int (fetched [0])
                  feedback_channel_id  = int (fetched [1])
                  feedback_channel     = guild.get_channel (feedback_channel_id)
                  await feedback_channel.send (f"<@{feedback_role_id}> La phase de vote est terminée.")
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
    sys.exit(0)
  except Exception as e:
    print (f"{type(e).__name__} - {e}")
    sys.exit(0)

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