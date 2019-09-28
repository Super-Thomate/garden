import discord
from discord.ext import commands
from Utils import Utils
from ..logs import Logs
from database import Database
from datetime import date
from datetime import datetime
from dateutil import parser
import time
import math

class Vote(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()
    self.language_code = 'fr'


  @commands.command(name='createvote', aliases=['vote'])
  @commands.guild_only()
  async def create_vote(self, ctx, *args):
    """ Create a vote
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    # date
    today = date.today()
    month = str (today.month) if today.month > 9 else "0"+str(today.month)
    year = str(today.year)
    # reason
    reason = ' '.join(arg for arg in args)
    reason = reason or "Vote pour le changement de nom du rôle des membres"
    # description
    description = "Aucune description"
    error = False
    # Embed capturing our vote
    embed = self.create_embed(reason, description, month, year)
    poll = await ctx.send(content=None, embed=embed)
    # insert into vote_message values ('message_id', 'channel_id', 'month', 'year', 'closed', 'author_id', guild_id', 'vote_type')
    sql = f"insert into vote_message (`message_id`, `channel_id`, `month`, `year`, `closed`, `author_id`, `guild_id`, `vote_type`) values ('{poll.id}', '{ctx.channel.id}', '{month}', '{year}', 0, '{author.id}', '{guild_id}', 'vote')"
    self.db.execute_order (sql, [])
    started_at = math.floor (time.time())
    sql = f"insert into vote_time (`message_id`, `started_at`, `proposition_ended_at`, `edit_ended_at`, `vote_ended_at`, `guild_id`) values ('{poll.id}', '{started_at}', NULL, NULL, NULL, '{guild_id}') ;"
    self.db.execute_order (sql, [])
    # await ctx.send (f"`{sql}`")
    await self.logger.log('vote_log', author, ctx.message, error)
    await ctx.message.delete(delay=0.5)

  @commands.command(name='setvotetype', aliases=['svt'])
  @commands.guild_only()
  async def set_vote_type(self, ctx, message_id: str = None, type_vote: str = None):
    """ Set a type for a vote message
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not message_id:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<messageID>'))
      return
    try:
      message_id = int (message_id)
    except Exception as e:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<messageID>'))
      return
    if not type_vote:
      type_vote = "vote"
    sql = f"update vote_message set vote_type=? where message_id=?"
    try:
      self.db.execute_order(sql, [type_vote, message_id])
    except Exception as e:
      await ctx.send(self.utils.get_text(self.language_code, "error_occured"))
      await ctx.message.add_reaction ('❌')
      await self.logger.log('vote_log', author, ctx.message, True)
      return
    await ctx.message.add_reaction ('✅')
    await self.logger.log('vote_log', author, ctx.message, False)
    await ctx.message.delete(delay=0.5)

  @commands.command(name='setdescription', aliases=['setdesc', 'desc', 'sd'])
  @commands.guild_only()
  async def set_description(self, ctx, message_id: str = None):
    """ Set a description for a vote message
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await self.handle_result (ctx, message_id, "description", True)

  @commands.command(name='settitle', aliases=['title', 'st'])
  @commands.guild_only()
  async def set_title(self, ctx, message_id: str = None):
    """ Set a title for a vote message
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await self.handle_result (ctx, message_id, "title", True)

  @commands.command(name='addproposition', aliases=['add', 'addprop', 'ap'])
  @commands.guild_only()
  async def add_proposition(self, ctx, message_id_vote_type: str = None):
    """
    Add a proposition
    """
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not message_id_vote_type:
      # search for the lastest vote in that channel
      select = f"select message_id from vote_message where channel_id={ctx.channel.id} and closed=0"
      fetched = self.db.fetch_one_line (select)
      if not fetched:
        await ctx.send(self.utils.get_text(self.language_code, "no_valid_vote_message_found"))
        await self.logger.log('vote_log', ctx.author, ctx.message, True)
        await ctx.message.add_reaction ('❌')
        return
      message_id = fetched [0]
    else:
      # is it a message_id or vote_type
      try:
        message_id = int (message_id_vote_type)
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        # vote_type
        select = f"select message_id from vote_message where guild_id='{ctx.guild.id}' and closed=0 and vote_type=?"
        fetched = self.db.fetch_one_line (select, [message_id_vote_type])
        if not fetched:
          await ctx.send(self.utils.get_text(self.language_code, "no_valid_vote_message_found"))
          await self.logger.log('vote_log', ctx.author, ctx.message, True)
          await ctx.message.add_reaction ('❌')
          return
        message_id = fetched [0]
    # Get proposition and handle it
    await self.handle_result (ctx, message_id, "proposition_line", False)

  @commands.command(name='editproposition', aliases=['edit', 'editprop', 'ep'])
  @commands.guild_only()
  async def edit_proposition(self, ctx, message_id_vote_type: str = None):
    """
    Edit a proposition
    """
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not message_id_vote_type:
      # search for the lastest vote in that channel
      select = f"select message_id from vote_message where channel_id={ctx.channel.id} and closed=0"
      fetched = self.db.fetch_one_line (select)
      if not fetched:
        await ctx.send(self.utils.get_text(self.language_code, "no_valid_vote_message_found"))
        await self.logger.log('vote_log', ctx.author, ctx.message, True)
        await ctx.message.add_reaction ('❌')
        return
      message_id = fetched [0]
    else:
      # is it a message_id or vote_type
      try:
        message_id = int (message_id_vote_type)
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        print (f"Votetype: {message_id_vote_type}")
        # vote_type
        select = f"select message_id from vote_message where guild_id='{ctx.guild.id}' and closed=0 and vote_type=?"
        fetched = self.db.fetch_one_line (select, [message_id_vote_type])
        if not fetched:
          await ctx.send(self.utils.get_text(self.language_code, "no_valid_vote_message_found"))
          await self.logger.log('vote_log', ctx.author, ctx.message, True)
          await ctx.message.add_reaction ('❌')
          return
        message_id = fetched [0]
    # Get proposition and handle it
    await self.handle_result (ctx, message_id, "edit_proposition", False)

  @commands.command(name='removeproposition', aliases=['remove', 'removeprop', 'rp'])
  @commands.guild_only()
  async def remove_proposition(self, ctx, message_id_vote_type: str = None):
    """
    Remove a proposition
    """
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not message_id_vote_type:
      # search for the lastest vote in that channel
      select = f"select message_id from vote_message where channel_id={ctx.channel.id} and closed=0"
      fetched = self.db.fetch_one_line (select)
      if not fetched:
        await ctx.send(self.utils.get_text(self.language_code, "no_valid_vote_message_found"))
        await self.logger.log('vote_log', ctx.author, ctx.message, True)
        await ctx.message.add_reaction ('❌')
        return
      message_id = fetched [0]
    else:
      # is it a message_id or vote_type
      try:
        message_id = int (message_id_vote_type)
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        print (f"Votetype: {message_id_vote_type}")
        # vote_type
        select = f"select message_id from vote_message where guild_id='{ctx.guild.id}' and closed=0 and vote_type=?"
        fetched = self.db.fetch_one_line (select, [message_id_vote_type])
        if not fetched:
          await ctx.send(self.utils.get_text(self.language_code, "no_valid_vote_message_found"))
          await self.logger.log('vote_log', ctx.author, ctx.message, True)
          await ctx.message.add_reaction ('❌')
          return
        message_id = fetched [0]
    # Get proposition and handle it
    await self.handle_result (ctx, message_id, "remove_proposition", False)

  """
  3 phases
  Phase1: Member's propositions
  Phase2: Modo's clean
  Phase3: Vote
  Member can add propositions during Phase 1
  Modos and + cand add propositions during Phase 1 & Phase 2
  0      = Phase 1
  0 -> 1 = End Phase 1
  1      = Phase 2
  1 -> 2 = End Phase 2
  2      = Phase 3
  2 -> 3 = End Phase 3
  """


  @commands.command(name='closeproposition', aliases=['cp'])
  @commands.guild_only()
  async def close_proposition(self, ctx, message_id: str = None):
    """
    Close propositions
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await self.handle_result (ctx, message_id, "end_proposition", True)

  @commands.command(name='closeedit', aliases=['ce'])
  @commands.guild_only()
  async def close_edit(self, ctx, message_id: str = None):
    """
    Close edit phase
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await self.handle_result (ctx, message_id, "end_edit", True)

  @commands.command(name='closevote', aliases=['cv'])
  @commands.guild_only()
  async def close_vote(self, ctx, message_id: str = None):
    """
    Close vote
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await self.handle_result (ctx, message_id, "close_vote", True)

  @commands.command(name='closepropositionat', aliases=['cpa'])
  @commands.guild_only()
  async def close_proposition_at(self, ctx, message_id: str = None):
    """
    Close propositions at a given date
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await self.handle_result (ctx, message_id, "end_proposition_at", True)

  @commands.command(name='closevoteat', aliases=['cva'])
  @commands.guild_only()
  async def end_vote_at(self, ctx, message_id: str = None):
    """
    Close vote at a given date
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await self.handle_result (ctx, message_id, "end_vote_at", True)

  @commands.command(name='closeallvote', aliases=['cav'])
  @commands.guild_only()
  async def close_all_vote(self, ctx, message_id: str = None):
    """
    Close all vote
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      await ctx.message.add_reaction ('❌')
      return
    select = f"select message_id, month, year from vote_message where guild_id='{guild_id}' and closed <> 3 ;"
    fetched = self.db.fetch_all_line (select)
    if fetched:
      for message in fetched:
        message_id = message[0]
        update = f"update vote_message set closed=3 where message_id='{message_id}' ;"
        try:
          vote_msg = await ctx.channel.fetch_message (message_id)
        except Exception as e:
          if type(e).__name__ == "NotFound":
            await ctx.send(self.utils.get_text(self.language_code, "no_valid_vote_message_found"))
          elif type(e).__name__ == "Forbidden":
            await ctx.send(self.utils.get_text(self.language_code, "permission_denied"))
          else:
            await ctx.send(self.utils.get_text(self.language_code, "unknow_error").format(type(e).__name__, e))
          await self.logger.log('vote_log', author, ctx.message, True)
          await ctx.message.add_reaction ('❌')
          return
        embed = vote_msg.embeds[0]
        self.db.execute_order (update)
        colour = discord.Colour(0)
        colour = colour.from_rgb(255, 71, 71)
        embed.colour=colour
        embed.set_footer(text=f"{message[1]}/{message[2]} Phase de vote terminée")
        await vote_msg.edit (embed=embed)

      await ctx.message.add_reaction ('✅')

  @commands.command(name='setvotechannel', aliases=['svc'])
  @commands.guild_only()
  async def set_vote_channel(self, ctx, channel_id: str = None):
    """
    Set a channel to ping end of phases
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    channel_id = channel_id or ctx.channel.id
    guild_id = ctx.guild.id
    try:
      channel_id = int (channel_id)
    except Exception as e:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<channelID>'))
      await ctx.message.add_reaction ('❌')
      return
    select = f"select * from vote_channel where guild_id='{guild_id}' ;"
    fetched = self.db.fetch_one_line (select)
    if fetched:
      sql = f"update vote_channel set channel_id='{channel_id}' where guild_id='{guild_id}'"
    else:
      sql = f"insert into vote_channel values ('{channel_id}', '{guild_id}') ;"
    try:
      self.db.execute_order(sql)
    except Exception as e:
      await ctx.send(self.utils.get_text(self.language_code, "error_occured"))
      await ctx.message.add_reaction ('❌')
      return
    await ctx.message.add_reaction ('✅')

  @commands.command(name='setvoterole', aliases=['svr'])
  @commands.guild_only()
  async def set_vote_role(self, ctx, role_id: str = None):
    """
    Set a role to ping end of phases
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not role_id:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<roleID>'))
      await ctx.message.add_reaction ('❌')
      return
    try:
      role_id = int (role_id)
    except Exception as e:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<roleID>'))
      await ctx.message.add_reaction ('❌')
      return
    guild_id = ctx.guild.id
    print ("select")
    select = f"select * from vote_role where guild_id='{guild_id}' ;"
    try:
      fetched = self.db.fetch_one_line (select)
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.send(self.utils.get_text(self.language_code, "error_occured"))
      await ctx.message.add_reaction ('❌')
      return
    print ("fetched")
    if fetched:
      sql = f"update vote_role set role_id='{role_id}' where guild_id='{guild_id}' ;"
    else:
      sql = f"insert into vote_role values ('{role_id}', '{guild_id}') ;"
    print ("sql: "+sql)
    try:
      self.db.execute_order(sql)
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.send(self.utils.get_text(self.language_code, "error_occured"))
      await ctx.message.add_reaction ('❌')
      return
    await ctx.message.add_reaction ('✅')



  @commands.command(name='resetvote', aliases=['rv'])
  @commands.guild_only()
  async def reset_vote(self, ctx, message_id: str = None):
    """
    Reset a vote
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (author, guild_id):
      print ("No permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    await self.handle_result (ctx, message_id, "reset_vote", True)





  async def handle_result (self, ctx, message_id, handle, permission_needed):
    author = ctx.author
    guild_id = ctx.guild.id
    error = False
    is_authorized = self.utils.is_authorized (author, guild_id)
    if permission_needed and not is_authorized:
      print ("No permissions")
      return
    if not message_id:
      # search for the lastest vote in that channel
      select = f"select message_id from vote_message where channel_id={ctx.channel.id} and closed=0 ;"
      fetched = self.db.fetch_one_line (select)
      if not fetched:
        await ctx.send(self.utils.get_text(self.language_code, "no_valid_vote_message_found"))
        await self.logger.log('vote_log', author, ctx.message, True)
        await ctx.message.add_reaction ('❌')
        return    # Send 'Hi what is your proposition'
      message_id = fetched [0]
    if not message_id:
      await ctx.send (self.utils.get_text('fr', 'parameter_is_mandatory').format('<messageID>'))
      await ctx.message.add_reaction ('❌')
      await self.logger.log('vote_log', author, ctx.message, True)
      return
    try:
      message_id = int (message_id)
    except Exception as e:
      await ctx.send (self.utils.get_text('fr', 'message_id_format_not_valid'))
      await ctx.message.add_reaction ('❌')
      await self.logger.log('vote_log', author, ctx.message, True)
      return
    # valid message saved ?
    sql = f"select channel_id,closed,month,year from vote_message where message_id='{message_id}' and guild_id='{guild_id}'"
    fetched = self.db.fetch_one_line (sql)
    if not fetched:
      await ctx.send(self.utils.get_text(self.language_code, "message_not_found_in_channel").format(message_id))
      await self.logger.log('vote_log', author, ctx.message, True)
      await ctx.message.add_reaction ('❌')
      return
    # vote closure status
    channel_id               = int (fetched [0])
    closure_status           = fetched [1]
    end_proposition          = (fetched [1] == 1)
    end_edit                 = (fetched [1] == 2)
    vote_closed              = (fetched [1] == 3)
    month                    = fetched [2]
    year                     = fetched [3]
    # get the message
    try:
      channel                = ctx.guild.get_channel (channel_id)
      vote_msg               = await channel.fetch_message (message_id)
    except Exception as e:
      if type(e).__name__ == "NotFound":
        await ctx.send(self.utils.get_text(self.language_code, "message_not_found_in_channel").format(message_id))
      elif type(e).__name__ == "Forbidden":
        await ctx.send(self.utils.get_text(self.language_code, "permission_denied"))
      else:
        await ctx.send(self.utils.get_text(self.language_code, "unknow_error").format(type(e).__name__, e))
      await self.logger.log('vote_log', author, ctx.message, True)
      await ctx.message.add_reaction ('❌')
      return
    embed = vote_msg.embeds[0]

    if handle == "description":
      ask = await ctx.send(self.utils.get_text(self.language_code, "ask_new_vote_description"))
    elif handle == "title":
      ask = await ctx.send(self.utils.get_text(self.language_code, "ask_new_vote_title"))
    elif handle == "proposition_line":
      if (end_proposition and not is_authorized) or end_edit or vote_closed:
        await ctx.send(self.utils.get_text(self.language_code, "proposition_phase_end"))
        return
      ask = await ctx.send(self.utils.get_text(self.language_code, "ask_proposition"))
    elif handle == "end_proposition":
      if closure_status > 0:
        await ctx.message.add_reaction ('❌')
        feedback             = await ctx.send(self.utils.get_text(self.language_code, "cant_close_proposition_phase"))
        await ctx.message.delete (delay=0.5)
        await feedback.delete (delay=1.5)
        return
      update = f"update vote_message set closed=1 where message_id='{message_id}'"
      self.db.execute_order (update, [])
      proposition_ended_at = math.floor (time.time())
      update = f"update vote_time set proposition_ended_at='{proposition_ended_at}' where message_id='{message_id}'"
      self.db.execute_order (update, [])
      colour = discord.Colour(0)
      colour = colour.from_rgb(20, 20, 255)
      embed.colour=colour
      embed.set_footer(text=f"{month}/{year} Phase de proposition terminée")
      await vote_msg.edit (embed=embed)
      await ctx.message.add_reaction ('✅')
      await ctx.message.delete (delay=0.5)
      return
    elif handle == "end_edit":
      if closure_status > 1:
        await ctx.message.add_reaction ('❌')
        feedback             = await ctx.send(self.utils.get_text(self.language_code, "cant_close_edition_phase"))
        await ctx.message.delete (delay=0.5)
        await feedback.delete (delay=1.5)
        return
      update = f"update vote_message set closed=2 where message_id='{message_id}'"
      self.db.execute_order (update, [])
      edit_ended_at = math.floor (time.time())
      update = f"update vote_time set edit_ended_at='{edit_ended_at}' where message_id='{message_id}'"
      self.db.execute_order (update, [])
      colour = discord.Colour(0)
      colour = colour.from_rgb(56, 255, 56)
      embed.colour=colour
      embed.set_footer(text=f"{month}/{year} Phase de vote")
      await vote_msg.edit (embed=embed)
      await ctx.message.add_reaction ('✅')
      await ctx.message.delete (delay=0.5)
      return
    elif handle == "close_vote":
      if closure_status > 2:
        await ctx.message.add_reaction ('❌')
        feedback             = await ctx.send(self.utils.get_text(self.language_code, "cant_close_vote_phase"))
        await ctx.message.delete (delay=0.5)
        await feedback.delete (delay=1.5)
        return
      update = f"update vote_message set closed=3 where message_id='{message_id}'"
      self.db.execute_order (update, [])
      vote_ended_at = math.floor (time.time())
      update = f"update vote_time set vote_ended_at='{vote_ended_at}' where message_id='{message_id}'"
      self.db.execute_order (update, [])
      colour = discord.Colour(0)
      colour = colour.from_rgb(255, 71, 71)
      embed.colour=colour
      embed.set_footer(text=f"{month}/{year} Phase de vote terminée")
      embed = self.embed_get_result(message_id, guild_id, embed)
      await vote_msg.edit (embed=embed)
      await ctx.message.add_reaction ('✅')
      await ctx.message.delete (delay=0.5)
      return
    elif handle == "end_proposition_at":
      ask = await ctx.send(self.utils.get_text(self.language_code, "close_proposition_at"))
    elif handle == "end_vote_at":
      ask = await ctx.send(self.utils.get_text(self.language_code, "close_vote_at"))
    elif handle == "remove_proposition":
      if end_edit or vote_closed:
        await ctx.send(self.utils.get_text(self.language_code, "cant_close_proposition_phase_2"))
        return
      ask = await ctx.send(self.utils.get_text(self.language_code, "ask_prosition_to_delete"))
    elif handle == "edit_proposition":
      if end_edit or vote_closed:
        await ctx.send(self.utils.get_text(self.language_code, "cant_close_proposition_phase_3"))
        return
      ask = await ctx.send(self.utils.get_text(self.language_code, "ask_prosition_to_edit"))
    elif handle == "reset_vote":
      if closure_status < 2:
        await ctx.message.add_reaction ('❌')
        feedback             = await ctx.send(self.utils.get_text(self.language_code, "cant_reset_vote"))
        await ctx.message.delete (delay=0.5)
        await feedback.delete (delay=1.5)
        return
      # reset all ballots
      self.reset_all_ballots (message_id)
      # reset all reactions
      for reaction in vote_msg.reactions:
        async for user in reaction.users():
          if user.id != self.bot.user.id:
            await reaction.remove (user)
      # repoen vote
      update                 = f"update vote_message set closed=2 where message_id='{message_id}'"
      self.db.execute_order (update)
      edit_ended_at          = math.floor (time.time())
      update                 = f"update vote_time set edit_ended_at='{edit_ended_at}', vote_ended_at=NULL where message_id='{message_id}'"
      self.db.execute_order (update)
      colour                 = discord.Colour(0)
      colour                 = colour.from_rgb(56, 255, 56)
      embed.colour           = colour
      embed.set_footer(text=f"{month}/{year} Phase de vote")
      embed                  = self.embed_get_no_result (message_id, guild_id, embed)
      await vote_msg.edit (embed=embed)
      await ctx.message.add_reaction ('✅')
      await ctx.message.delete (delay=0.5)
      return
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    if handle == "proposition_line":
      proposition = msg.content
      ask_emoji = await ctx.send(self.utils.get_text(self.language_code, "ask_emoji"))
      msg_emoji = await self.bot.wait_for('message', check=check)
      emoji = msg_emoji.content
      # test if emoji already exists
      select = f"select emoji from vote_propositions where message_id='{message_id}' and emoji='{emoji}' ;"
      fetched = self.db.fetch_one_line (select)
      if fetched:
        err_feedback = await ctx.send(self.utils.get_text(self.language_code, "emoji_already_used_add"))
        await err_feedback.delete(delay=1)
        error = True
      else:
        # test emoji by using it in reaction
        try:
          await vote_msg.add_reaction (emoji)
        except Exception as e:
          feedback = await ctx.send(self.utils.get_text(self.language_code, "emoji_invalid"))
          error = True
          print (f"{type(e).__name__} - {e}")
          await feedback.delete (delay=2)
        else:
          field = embed.fields [0]
          # get last id
          select = f"select proposition_id from vote_propositions where message_id='{message_id}' order by proposition_id desc limit 1 ;"
          fetched = self.db.fetch_one_line (select)
          if not fetched:
            last_id = 0
          else:
            last_id = int(fetched [0])
          #insert proposition : `proposition`,`emoji` , `proposition_id` ,`author_id` , `message_id`
          sql = f"insert into vote_propositions values (?, ?, {last_id+1}, '{ctx.author.id}', '{message_id}', 0) ;"
          try:
            self.db.execute_order (sql, [proposition, emoji])
          except Exception as e:
            print (f"{type(e).__name__} - {e}")
          else:
            # create line
            if last_id == 0:
              new_value = "["+str(last_id+1)+"] - "+emoji+" "+proposition
            else:
              new_value = field.value +"\n["+str(last_id+1)+"] - "+emoji+" "+proposition
            print (f"new_value: {new_value}")
            embed.clear_fields()
            embed.add_field (name=field.name, value=new_value, inline=False)
            await vote_msg.edit (embed=embed)
      await msg_emoji.delete(delay=0.5)
      await ask_emoji.delete(delay=0.5)
    elif handle == "description":
      embed.description = msg.content
    elif handle == "title":
      embed.title = msg.content
    elif handle == "end_proposition_at" or handle == "end_vote_at":
      try:
        date_time = parser.parse(msg.content, dayfirst=True)
        timestamp = datetime.timestamp(date_time)
        print (f"timestamp: {timestamp}")
        if timestamp < math.floor (time.time()):
          error_message = await ctx.send(self.utils.get_text(self.language_code, "date_is_before_now"))
          await error_message.delete(delay=1)
          error = True
        else:
          update = f"update vote_time set "
          if handle == "end_proposition_at":
            update = update + "proposition_ended_at "
          else:
            update = update + "vote_ended_at "
          update = update + f"= '{timestamp}' where message_id='{message_id}'"
          self.db.execute_order (update)
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        error_message = await ctx.send(self.utils.get_text(self.language_code, "date_format_error"))
        await error_message.delete(delay=1)
        error = True
    elif handle == "remove_proposition":
      try:
        proposition_id = int (msg.content)
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        await ctx.send(self.utils.get_text(self.language_code, "need_integer_parameter"))
        error = True
      else:
        if end_proposition or is_authorized:
          # modo
          select =  f"select emoji from vote_propositions where message_id='{message_id}' and proposition_id={proposition_id} ;"
        else:
          # user
          select = f"select emoji from vote_propositions where message_id='{message_id}' and author_id='{ctx.author.id}' and proposition_id={proposition_id} ;"
        fetched_proposition = self.db.fetch_one_line (select) ;
        if fetched_proposition:
           delete = f"delete from vote_propositions where message_id='{message_id}' and proposition_id={proposition_id} ;"
           update = f"update vote_propositions set proposition_id=proposition_id-1 where message_id='{message_id}' and proposition_id>{proposition_id} ;"
           try:
             self.db.execute_order (delete)
             self.db.execute_order (update)
             new_value = ""
             select = f"select proposition_id,emoji,proposition from vote_propositions where message_id='{message_id}' ;"
             fetched = self.db.fetch_all_line (select)
             await vote_msg.remove_reaction (fetched_proposition[0], self.bot.user) # remove emoji
             if not fetched:
               new_value = "\uFEFF"
             else:
               print (f"fetched: {fetched}")
               for line in fetched:
                 proposition_id = line [0]
                 emoji = line [1]
                 proposition = line [2]
                 if proposition_id == 1:
                   new_value = "["+str(proposition_id)+"] - "+emoji+" "+proposition
                 else:
                   new_value = new_value +"\n["+str(proposition_id)+"] - "+emoji+" "+proposition
             field = embed.fields [0]
             embed.clear_fields()
             embed.add_field (name=field.name, value=new_value, inline=False)
           except Exception as e:
             await ctx.message.add_reaction ('❌')
             print (f"{type(e).__name__} - {e}")
             await ctx.send(self.utils.get_text(self.language_code, "error_occured"))
             error = True
        else:
          error = True
          await ctx.send(self.utils.get_text(self.language_code, "proposition_not_found").format(f'#{proposition_id}'))
    elif handle == "edit_proposition":
      try:
        proposition_id = int (msg.content)
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        await ctx.send(self.utils.get_text(self.language_code, "need_integer_parameter"))
        error = True
      else:
        if end_proposition or self.utils.is_authorized (ctx.author, guild_id):
          # modo
          select =  f"select emoji from vote_propositions where message_id='{message_id}' and proposition_id={proposition_id} ;"
        else:
          # user
          select = f"select emoji from vote_propositions where message_id='{message_id}' and author_id='{ctx.author.id}' and proposition_id={proposition_id} ;"
        fetched_proposition = self.db.fetch_one_line (select) ;
        if fetched_proposition:
           ask_line = await ctx.send(self.utils.get_text(self.language_code, "ask_new_proposition"))
           msg_line = await self.bot.wait_for('message', check=check)
           ask_emoji = await ctx.send(self.utils.get_text(self.language_code, "ask_new_emoji"))
           msg_emoji = await self.bot.wait_for('message', check=check)
           proposition = msg_line.content
           emoji = msg_emoji.content
           # test if emoji already exists
           select = f"select emoji from vote_propositions where message_id='{message_id}' and emoji='{emoji}' and proposition_id <> {proposition_id} ;"
           fetched = self.db.fetch_one_line (select)
           if fetched:
             err_feedback = await ctx.send(self.utils.get_text(self.language_code, "emoji_already_used_edit"))
             await err_feedback.delete(delay=1)
             error = True
           else:
             # test emoji by using it in reaction
             try:
               await vote_msg.remove_reaction (fetched_proposition[0], self.bot.user) # remove emoji
               await vote_msg.add_reaction (emoji)
             except Exception as e:
               feedback = await ctx.send(self.utils.get_text(self.language_code, "emoji_invalid"))
               error = True
               await vote_msg.add_reaction (fetched_proposition[0])
               print (f"{type(e).__name__} - {e}")
               await feedback.delete (delay=2)
             else:
               field = embed.fields [0]
               # get last id
               select = f"select proposition_id from vote_propositions where message_id='{message_id}' order by proposition_id desc limit 1 ;"
               fetched = self.db.fetch_one_line (select)
               if not fetched:
                 last_id = 0
               else:
                 last_id = int(fetched [0])
               update = f"update vote_propositions set proposition=?, emoji=? where message_id='{message_id}' and proposition_id={proposition_id} ;"
               try:
                 self.db.execute_order (update, [proposition, emoji])
                 new_value = ""
                 select = f"select proposition_id,emoji,proposition from vote_propositions where message_id='{message_id}' order by proposition_id asc ;"
                 fetched = self.db.fetch_all_line (select)
                 if not fetched:
                   new_value = "\uFEFF"
                 else:
                   print (f"fetched: {fetched}")
                   for line in fetched:
                     proposition_id = line [0]
                     emoji = line [1]
                     proposition = line [2]
                     if proposition_id == 1:
                       new_value = "["+str(proposition_id)+"] - "+emoji+" "+proposition
                     else:
                       new_value = new_value +"\n["+str(proposition_id)+"] - "+emoji+" "+proposition
                 field = embed.fields [0]
                 embed.clear_fields()
                 embed.add_field (name=field.name, value=new_value, inline=False)
               except Exception as e:
                 await ctx.message.add_reaction ('❌')
                 print (f"{type(e).__name__} - {e}")
                 await ctx.send(self.utils.get_text(self.language_code, "error_occured"))
                 error = True
           await msg_line.delete(delay=0.5)
           await ask_line.delete(delay=0.5)
           await msg_emoji.delete(delay=0.5)
           await ask_emoji.delete(delay=0.5)
        else:
          error = True
          await ctx.send(self.utils.get_text(self.language_code, "proposition_not_found").format(f'#{proposition_id}'))

    await vote_msg.edit (embed=embed)
    if error:
      await ctx.message.add_reaction ('❌')
    else:
      await ctx.message.add_reaction ('✅')
    await self.logger.log('vote_log', author, ctx.message, error)
    await self.logger.log('vote_log', author, msg, error)
    await ask.delete(delay=0.5)
    await msg.delete(delay=0.5)
    await ctx.message.delete(delay=0.5)

  def create_embed(self, reason, description, month, year):
    colour = discord.Colour(0)
    colour = colour.from_rgb(56, 255, 56)
    embed = discord.Embed(colour=colour)
    embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.display_name)
    embed.title = reason
    embed.description = description
    embed.add_field (name='Propositions', value='\uFEFF', inline=False)
    embed.set_footer(text=f"{month}/{year}")
    return embed


  ## VOTE LISTENER
  @commands.Cog.listener()
  async def on_reaction_add(self, reaction, user):
    if not reaction.message.guild:
      return
    message_id               = reaction.message.id
    guild_id                 = reaction.message.guild.id
    emoji                    = reaction.emoji
    status_message           = self.is_vote_message (message_id, guild_id)
    if status_message == -1: # not a vote message
      return
    if status_message != 2: # not a vote phase
      if user.id != self.bot.user.id:
        await reaction.remove (user)
      return
    # handler
    self.update_ballot (message_id, emoji, True)

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    message_id               = payload.message_id
    guild_id                 = payload.guild_id
    channel_id               = payload.channel_id
    emoji                    = payload.emoji
    user_id                  = payload.user_id
    status_message           = self.is_vote_message (message_id, guild_id)
    if status_message == -1: # not a vote message
      return
    if status_message != 2: # not a vote phase
      if user_id != self.bot.user.id:
        channel          = await self.bot.fetch_channel (channel_id)
        message          = await channel.fetch_message (message_id)
        await message.remove_reaction (emoji, message.guild.get_member (user_id))
      return
    # handler
    self.update_ballot (message_id, emoji, True)

  @commands.Cog.listener()
  async def on_reaction_remove(self, reaction, user):
    message_id               = reaction.message.id
    guild_id                 = reaction.message.guild.id
    emoji                    = reaction.emoji
    status_message           = self.is_vote_message (message_id, guild_id)
    if status_message != 2: # not a vote message or not a vote phase
      return
    # handler
    self.update_ballot (message_id, emoji, False)

  @commands.Cog.listener()
  async def on_raw_reaction_remove(self, payload):
    message_id               = payload.message_id
    guild_id                 = payload.guild_id
    channel_id               = payload.channel_id
    emoji                    = payload.emoji
    status_message           = self.is_vote_message (message_id, guild_id)
    if status_message != 2: # not a vote phase
      return
    # handler
    self.update_ballot (message_id, emoji, False)

  def is_vote_message (self, message_id, guild_id):
    # check if message = vote
    select = f"select closed from vote_message where message_id='{message_id}' and guild_id='{guild_id}' ;"
    fetched = self.db.fetch_one_line (select)
    if not fetched:
      return -1
    """
    if closed != 2:  # not in vote phase
      return False
    """
    return fetched [0]

  def is_correct_emoji (self, message_id, guild_id, emoji):
    # check if message = vote
    select = f"select ballot from vote_propositions where message_id='{message_id}' and guild_id='{guild_id}' and emoji='{emoji}' ;"
    fetched = self.db.fetch_one_line (select)
    if not fetched:
      print (f"Invalid emoji: {emoji} on message {message_id} in {guild_id}")
      return False
    return True

  def update_ballot (self, message_id, emoji, add_or_remove):
    # check if  emoji is valid
    select_proposition = f"select ballot from vote_propositions where message_id='{message_id}' and emoji='{emoji}' ;"
    fetched_proposition = self.db.fetch_one_line (select_proposition)
    if not fetched_proposition:
      print (f"Invalid emoji: {emoji} on message {message_id}")
      return -1
    # update ballot
    ballot = int (fetched_proposition [0])
    if add_or_remove:
      ballot = ballot+1
    else:
      ballot = ballot-1
    ballot                   = 0 if ballot < 0 else ballot
    update = f"update vote_propositions set ballot={ballot} where message_id='{message_id}' and emoji='{emoji}' ;"
    try:
      self.db.execute_order (update)
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      return -1
    return ballot

  def reset_all_ballots (self, message_id):
    update                   = f"update vote_propositions set ballot=0 where  message_id='{message_id}' ;"
    try:
      self.db.execute_order (update)
    except Exception as e:
      print (f"{type(e).__name__} - {e}")

  def embed_get_result (self, message_id, guild_id, embed):
    # valid message saved ?
    sql = f"select channel_id,closed,month,year from vote_message where message_id='{message_id}' and guild_id='{guild_id}'"
    fetched = self.db.fetch_one_line (sql)
    if not fetched:
      print ("impossibru")
      return
    # vote closure status
    channel_id = int (fetched[0])
    end_proposition = (fetched [1] == 1)
    end_edit = (fetched [1] == 2)
    vote_closed = (fetched [1] == 3)
    month = fetched [2]
    year = fetched [3]
    field = embed.fields [0]
    select = f"select proposition_id,emoji,proposition,ballot from vote_propositions where message_id='{message_id}' order by proposition_id asc ;"
    fetched = self.db.fetch_all_line (select)
    if not fetched:
      new_value = "\uFEFF"
    else:
      print (f"fetched: {fetched}")
      for line in fetched:
        proposition_id = line [0]
        emoji = line [1]
        proposition = line [2]
        ballot = line [3]
        if proposition_id == 1:
          new_value = "- "+emoji+" "+proposition+" ("+str(ballot)+")"
        else:
          new_value = new_value +"\n - "+emoji+" "+proposition+" ("+str(ballot)+")"
    field = embed.fields [0]
    embed.clear_fields()
    embed.add_field (name=field.name, value=new_value, inline=False)
    return embed

  def embed_get_no_result (self, message_id, guild_id, embed):
    # valid message saved ?
    sql = f"select channel_id,closed,month,year from vote_message where message_id='{message_id}' and guild_id='{guild_id}'"
    fetched = self.db.fetch_one_line (sql)
    if not fetched:
      print ("impossibru")
      return
    # vote closure status
    channel_id = int (fetched[0])
    end_proposition = (fetched [1] == 1)
    end_edit = (fetched [1] == 2)
    vote_closed = (fetched [1] == 3)
    month = fetched [2]
    year = fetched [3]
    field = embed.fields [0]
    select = f"select proposition_id,emoji,proposition,ballot from vote_propositions where message_id='{message_id}' order by proposition_id asc ;"
    fetched = self.db.fetch_all_line (select)
    if not fetched:
      new_value = "\uFEFF"
    else:
      print (f"fetched: {fetched}")
      for line in fetched:
        proposition_id = line [0]
        emoji = line [1]
        proposition = line [2]
        ballot = line [3]
        if proposition_id == 1:
          new_value = "- "+emoji+" "+proposition
        else:
          new_value = new_value +"\n - "+emoji+" "+proposition
    field = embed.fields [0]
    embed.clear_fields()
    embed.add_field (name=field.name, value=new_value, inline=False)
    return embed