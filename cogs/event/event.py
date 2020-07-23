import json
import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs
from core import logger, box, embed_info
from datetime import datetime
import uuid

"""
TABLE
event
  guild_id
  owner_id
  event_id -- varchar (64)
  name
  desc
  date
  finished   -- if finished delete event_reminder
  PRIMARY KEY (guild_id, event_id)
event_roles
  guild_id
  event_id
  role_id
  invited -- bool
  PRIMARY KEY (guild_id, event_id, role_id)
event_reminder
  guild_id
  event_id
  order  -- order of reminder
  date  -- date to send
  where  -- DM,CHANNEL,BOTH
  channel_id -- nullable
  PRIMARY KEY (guild_id, event_id, order)

event config
event_id
name
desc
date


METHODS
event => start event creation
event edit [event_id] => edit an existing event


check = lambda m: m.channel == ctx.channel and m.author == ctx.author
"""
emojis                       = ["✔️", "❌"]
class Event (commands.Cog):
  def __init__ (self, bot):
    self.bot                 = bot
    self.logger              = Logs (self.bot)

  @commands.group ()
  @commands.guild_only ()
  @Utils.require (required = ['not_banned', 'cog_loaded'])
  async def event (self, ctx: commands.Context):
    """
    Do nothing
    """
    return

  @event.command ()
  async def create (self, ctx: commands.Context):
    """
    Create an event
    """
    guild_id                 = ctx.guild.id
    new_event                = {     "event_id": str (uuid.uuid4())
                                 ,     "author": ctx.author
                                 ,       "name": "No name"
                                 ,       "desc": "No description"
                                 ,   "datetime": "00/00/0000 00:00:00"
                                 ,         "tz": "-"
                                 ,       "role": ""
                                 ,    "channel": ctx.channel
                                 ,     "colour": ""
                                 ,   "finished": 0
                                 , "message_id": 0
                               }
    #logger ("event::create", "new_event : {}".format (new_event))
    check                    = lambda m: m.channel == ctx.channel and m.author == ctx.author
    # NAME
    ask_message              = await ctx.send (Utils.get_text (guild_id, "event_get_name"))
    message                  = await self.bot.wait_for('message', check=check)
    new_event       ['name'] = message.content
    await ask_message.delete ()
    await message.delete ()
    
    # CHANNEL
    ask_message              = await ctx.send (Utils.get_text (guild_id, "event_get_channel"))
    message                  = await self.bot.wait_for('message', check=check)
    try:
      event_channel          = await Utils.get_text_channel (ctx, message.content)
    except Exception as e:
      logger ("event::create::channel", f"{type(e).__name__} - {e}")
      event_channel          = ctx.channel
    new_event    ['channel'] = event_channel
    await ask_message.delete ()
    await message.delete ()

    # DATE
    try:
      tz                     = Utils.get_time_delta (guild_id)
    except Exception as e:
      logger ("event::create::datetime", f"{type(e).__name__} - {e}")
      await ctx.send (Utils.get_text (guild_id, "error_occured").format (type(e).__name__, e))
      await Utils.confirm_command (ctx.message, False)
      return
    ask_message              = await ctx.send (Utils.get_text (guild_id, "event_get_datetime"))
    message                  = await self.bot.wait_for('message', check=check)
    content                  = message.content
    new_event         ['tz'] = tz
    new_event   ['datetime'] = content
    await ask_message.delete ()
    await message.delete ()
    
    # CONTENT
    ask_message              = await ctx.send (Utils.get_text (guild_id, "event_get_content"))
    message                  = await self.bot.wait_for('message', check=check)
    new_event       ['desc'] = message.content
    await ask_message.delete ()
    await message.delete ()
    
    # ROLE
    ask_message              = await ctx.send (Utils.get_text (guild_id, "event_get_role"))
    message                  = await self.bot.wait_for('message', check=check)
    try:
      event_role             = await Utils.get_role (ctx, message.content)
    except commands.BadArgument as e:
      logger ("event::create::channel", f"{type(e).__name__} - {e}")
      await ctx.send (Utils.get_text(guild_id, "error_bad_role").format (message.content))
      await ask_message.delete ()
      await message.delete ()
      await Utils.confirm_command (ctx.message, False)
      return
    except Exception as e:
      logger ("event::create::channel", f"{type(e).__name__} - {e}")
      await ctx.send (Utils.get_text (guild_id, "error_occured").format (type(e).__name__, e))
      await ask_message.delete ()
      await message.delete ()
      await Utils.confirm_command (ctx.message, False)
      return
    new_event       ['role'] = event_role
    await ask_message.delete ()
    await message.delete ()
    
    # COLOR
    ask_message              = await ctx.send (Utils.get_text (guild_id, "event_get_color"))
    message                  = await self.bot.wait_for('message', check=check)
    try:
      event_colour           = await Utils.get_colour (ctx, message.content)
    except commands.BadArgument as e:
      logger ("event::create::channel", f"{type(e).__name__} - {e}")
      await ctx.send (Utils.get_text(guild_id, "error_bad_color").format (message.content))
      await ask_message.delete ()
      await message.delete ()
      await Utils.confirm_command (ctx.message, False)
      return
    except Exception as e:
      logger ("event::create::channel", f"{type(e).__name__} - {e}")
      await ctx.send (Utils.get_text (guild_id, "error_occured").format (type(e).__name__, e))
      await ask_message.delete ()
      await message.delete ()
      await Utils.confirm_command (ctx.message, False)
      return
    new_event     ['colour'] = event_colour
    await ask_message.delete ()
    await message.delete ()
    
    # logger ("event::create", "new_event : {}".format (new_event))
    embed                    = self.event_embed_info (guild_id, new_event)
    message                  = await event_channel.send (embed=embed)
    new_event ['message_id'] = message.id
    # SAVE IN DB
    order                    = "insert into event (guild_id, owner_id, event_id, finished, event_info) values (?, ?, ?, ?, ?) ;"
    logger ("event::create::new_event", json.dumps(new_event))
    # database.execute_order (order, [guild_id, ctx.author.id, new_event ["event_id"], 0, json.dumps(new_event)])

  @event.command ()
  async def edit (self, ctx: commands.Context, event_id: str):
    """
    Edit an event
    """
    return

  @event.command ()
  async def list (self, ctx: commands.Context):
    """
    List all event for me
    """
    select                   = "select event_info, finished from event where guild_id=? and owner_id=? ;"
    all_fetched              = database.fetch_all_line (select, [ctx.guild.id, ctx.author.id])
    result                   = ""
    logger ("event::list::all_fetched", f"{all_fetched}")
    for event in all_fetched:
      event_info             = event [1]
      event_message          = await event_info ["channel"].fetch_message (event_info ["message_id"]) 
      result                += "* "+event_info["name"]+(" (finished)" if event[0] else "")+" ("+event_message.jump_url+")\n"
    logger ("event::list::result", f"{result}")
    if len(result) :
      result                 = "```"+result+"```"
    else:
      result                 = "0 event"
    await ctx.send (result)
    return

  @event.command ()
  @Utils.require (required = ['authorized'])
  async def listall (self, ctx: commands.Context):
    """
    List all event
    """
    return
  def event_embed_info (self, guild_id, event):
    colour                   = event ["colour"]
    embed                    = embed_info (   colour
                                              , Utils.get_text(guild_id, "event_infos_embed_title")
                                                     .format(event ["name"])
                                              , Utils.get_text(guild_id, "event_infos_description")
                                                     .format(   event ["event_id"]
                                                              , event ["desc"]
                                                            )
                                              , str (event ["author"])
                                              , "{0} ({1})".format (event ["datetime"], event ["tz"])
                                            )
    value_role               = event ["role"]
    embed.add_field (     name = Utils.get_text(guild_id, "event_invited_role")
                      ,  value = value_role.name
                      , inline = False
                    )
    return embed

  def update_event (self, guild_id, event):
    update                   = (   "update  `event` "+
                                   "set   name=?, desc=?, date=?, finished=? "+
                                   "where "+
                                   "guild_id=?, owner_id=?, event_id=?"+
                                   ""
                               )
    database.execute_order (insert, [event ["name"], event ["desc"], event ["date"], event ["finished"], guild_id, event ["owner_id"], event ["event_id"]])