import discord
from discord.ext import commands

import Utils
import database
import core._Timer as _Timer
from ..logs import Logs
import time
import asyncio
from core import logger

class Timer(commands.Cog):
  """
  Timer:
  """

  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  @commands.group()
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def timer (self, ctx: commands.Context):
    """
    
    """
    if ctx.invoked_subcommand is None:
      prefix                   = ctx.prefix
      await ctx.send(Utils.get_text(ctx.guild.id, "error_get_help").format (prefix,"timer"))
      return
  
  @timer.command(name="launch")
  async def launch (self, ctx: commands.Context, duration_str: str):
    try:
      duration               = Utils.parse_time(duration_str)
      if duration < 1:
        await ctx.send (Utils.get_text(ctx.guild.id, "timer_duration_positive"))
        return
      if duration > 120:
        await ctx.send (Utils.get_text(ctx.guild.id, "timer_duration_max").format (120))
        return
      in_loop                = True
      start                  = time.time()
      guild_id               = ctx.guild.id ;
      # GET EMOJI
      select                 = "select emoji from timer_emoji where guild_id=? ;"
      fetched                = database.fetch_one_line(select, [guild_id])
      if not fetched:
        emoji                = Utils.emojize (":red_circle:")
      else:
        emoji                = await Utils.get_emoji (ctx, fetched [0])
      # GET END MESSAGE
      select                 = "select end_message from timer_end_message where guild_id=? ;"
      fetched                = database.fetch_one_line(select, [guild_id])
      if not fetched:
        end_message          = "**Time's Up !**"
      else:
        end_message          = fetched [0]
      # GET DO FIRST EMOJI
      select                 = "select do from config_do where type_do=? and guild_id=? ;"
      fetched                = database.fetch_one_line(select, ["first_emoji", guild_id])
      if not fetched:
        do_first_emoji       = False
      else:
        do_first_emoji       = fetched [0]
      # GET FIRST EMOJI
      first_emoji            = None
      if (do_first_emoji):
        select               = "select emoji from timer_first_emoji where guild_id=? ;"
        fetched              = database.fetch_one_line(select, [guild_id])
        if not fetched:
          first_emoji        = Utils.emojize (":green_circle:")
        else:
          first_emoji        = await Utils.get_emoji (ctx, fetched [0])
      
      global emoji_row_length
      emoji_row_length       = duration if duration <= 10 else 10
      if first_emoji :
        emoji_row_length    -= 1
      emoji_row              = (str(first_emoji) if first_emoji else "") + (str (emoji)+" " ) * emoji_row_length
      msg_timer              = await ctx.send (emoji_row)
      lag                    = 0.2
      interval               = duration / emoji_row_length - lag

      async def times_up():
        logger ("timer::launch", "times_up -> time : {:.1f}s".format(time.time()-start))
        await ctx.send  (end_message)
        # await msg_timer.edit (content=end_message)

      async def times_up_2():
        logger ("timer::launch", "Time's up ! -> time : {:.1f}s".format(time.time()-start))
        await ctx.send ("Time's up ! -> time : {:.1f}s".format(time.time()-start))

      async def rebuild ():
        #proc_start = time.time()
        global emoji_row_length
        emoji_row_length     =  emoji_row_length - 1
        emoji_row            = (str(first_emoji) if first_emoji else "") + (str (emoji)+" " ) * emoji_row_length
        if emoji_row_length or first_emoji:
          await msg_timer.edit (content=emoji_row)
          if time.time()-start < duration:
            next_task         = _Timer (interval, rebuild)
        else:
          logger ("timer::launch", "rebuild -> time : {:.1f}s".format(time.time()-start))
        #logger ("timer::launch", time.time()-proc_start)
      #reftimer               = _Timer (duration, times_up_2) # Reference Timer 
      timer                  = _Timer (duration, times_up)
      next_task              = _Timer (interval, rebuild)
      await ctx.message.delete(delay=0.5)
    except Exception as e:
      await ctx.send (f"{type(e).__name__} - {e}")
      return

  @commands.group()
  @commands.guild_only()
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def timerset (self, ctx: commands.Context):
    """
    
    """
    guild_id                 = ctx.guild.id
    if ctx.invoked_subcommand is None:
      # display config
      # GET EMOJI
      select                 = "select emoji from timer_emoji where guild_id=? ;"
      fetched                = database.fetch_one_line(select, [guild_id])
      if not fetched:
        emoji                = Utils.emojize (":red_circle:")
      else:
        emoji                = await Utils.get_emoji (ctx, fetched [0])
      # GET END MESSAGE
      select                 = "select end_message from timer_end_message where guild_id=? ;"
      fetched                = database.fetch_one_line(select, [guild_id])
      if not fetched:
        end_message          = "**Time's Up !**"
      else:
        end_message          = fetched [0]
      # GET DO FIRST EMOJI
      select                 = "select do from config_do where type_do=? and guild_id=? ;"
      fetched                = database.fetch_one_line(select, ["first_emoji", guild_id])
      if not fetched:
        do_first_emoji       = False
      else:
        do_first_emoji       = fetched [0]
      # GET FIRST EMOJI
      select               = "select emoji from timer_first_emoji where guild_id=? ;"
      fetched              = database.fetch_one_line(select, [guild_id])
      if not fetched:
        first_emoji        = Utils.emojize (":green_circle:")
      else:
        first_emoji        = await Utils.get_emoji (ctx, fetched [0])
      message_to_send      = (   ">>> "
                                 "Emoji: {0}\n"
                                 "End Message: {1}\n"
                                 "First Emoji: {2}\n"
                                 "Do First Emoji: {3}\n"
                             ).format(   emoji 
                                       , end_message
                                       , first_emoji
                                       , Utils.str_bool (do_first_emoji)
                                     )
      await ctx.send (message_to_send) 
      return

  @timerset.command(name="emoji")
  async def set_emoji (self, ctx: commands.Context, emoji_input: str):
    """
    Set the emoji for the timer
    """
    guild_id                 = ctx.guild.id ;
    try:
      emoji                  = await Utils.get_emoji (ctx, emoji_input)
    except Exception as e:
      logger ("timer::set_emoji", f"{type(e).__name__} - {e}")
      await ctx.send(Utils.get_text(guild_id, "timer_not_emoji").format (emoji_input))
      return
    select                   = "select emoji from timer_emoji where guild_id=? ;"
    fetched                  = database.fetch_one_line(select, [guild_id])
    if not fetched:
      order                  = "insert into timer_emoji (emoji, guild_id) values (?, ?) ;"
    else:
      order                  = "update timer_emoji set emoji=? where guild_id=? ;"
    try:
      database.execute_order(order, [str(emoji), guild_id])
    except Exception as e:
      logger ("timer::set_emoji", f"{type(e).__name__} - {e}")
      return
      
    await ctx.send(Utils.get_text(guild_id, "timer_set_emoji").format (str (emoji)))
    await ctx.message.delete(delay=0.5)

  @timerset.command(name="message")
  async def set_message (self, ctx: commands.Context, *message: str):
    """
    Set the end message for the timer
    """
    guild_id                 = ctx.guild.id ;
    end_message              = ' '.join(part for part in message )
    if len (end_message) > 512:
      await ctx.send(Utils.get_text(guild_id, "error_string_max_length").format (512))
      return
    select                   = "select end_message from timer_end_message where guild_id=? ;"
    fetched                  = database.fetch_one_line(select, [guild_id])
    if not fetched:
      order                  = "insert into timer_end_message (end_message, guild_id) values (?, ?) ;"
    else:
      order                  = "update timer_end_message set end_message=? where guild_id=? ;"
    try:
      database.execute_order(order, [str(end_message), guild_id])
    except Exception as e:
      logger ("timer::set_message", f"{type(e).__name__} - {e}")
      return
      
    await ctx.send(Utils.get_text(guild_id, "timer_set_end_message").format (str (end_message)))
    await ctx.message.delete(delay=0.5)
  
  @timerset.command(name="firstemoji")
  async def set_first_emoji (self, ctx: commands.Context, emoji_input: str):
    """
    Set the first emoji for the timer
    """
    guild_id                 = ctx.guild.id ;
    try:
      emoji                  = await Utils.get_emoji (ctx, emoji_input)
    except Exception as e:
      logger ("timer::set_first_emoji", f"{type(e).__name__} - {e}")
      await ctx.send(Utils.get_text(guild_id, "timer_not_emoji").format (emoji_input))
      return
    select                   = "select emoji from timer_first_emoji where guild_id=? ;"
    fetched                  = database.fetch_one_line(select, [guild_id])
    if not fetched:
      order                  = "insert into timer_first_emoji (emoji, guild_id) values (?, ?) ;"
    else:
      order                  = "update timer_first_emoji set emoji=? where guild_id=? ;"
    try:
      database.execute_order(order, [str(emoji), guild_id])
    except Exception as e:
      logger ("timer::set_first_emoji", f"{type(e).__name__} - {e}")
      return
      
    await ctx.send(Utils.get_text(guild_id, "timer_set_first_emoji").format (str (emoji)))
    await ctx.message.delete(delay=0.5)
  
  @timerset.command(name="dofirstemoji")
  async def set_do_first_emoji (self, ctx: commands.Context, true_or_false: str):
    """
    Toggle the first emoji for the timer
    """
    guild_id                 = ctx.guild.id ;
    type_do                  = "first_emoji"
    do_first_emoji           = (true_or_false.lower() == "true")
    select                   = "select do from config_do where type_do=? and guild_id=? ;"
    fetched                  = database.fetch_one_line(select, [type_do, guild_id])
    if not fetched:
      order                  = "insert into config_do (do, type_do, guild_id) values (?, ?,  ?) ;"
    else:
      order                  = "update config_do set do=? where type_do=? and guild_id=? ;"
    try:
      database.execute_order(order, [do_first_emoji, type_do, guild_id])
    except Exception as e:
      logger ("timer::set_do_first_emoji", f"{type(e).__name__} - {e}")
      return
    if (do_first_emoji):
      await ctx.send(Utils.get_text(guild_id, "timer_set_do_first_emoji"))
    else:
      await ctx.send(Utils.get_text(guild_id, "timer_set_do_first_emoji_not"))
    await ctx.message.delete(delay=0.5)

