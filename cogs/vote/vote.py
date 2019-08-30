import discord
from discord.ext import commands
from Utils import Utils
from ..logs import Logs
from database import Database
from datetime import date
from datetime import datetime
import time
import math

class Vote(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()


  @commands.command(name='createvote', aliases=['vote'])
  @commands.guild_only()
  async def create_vote(self, ctx, *args):
    """ Create a vote
    """
    author = ctx.author
    guild_id = ctx.guild.id
    if not self.utils.has_role (author, guild_id):
      print ("No permissions")
      await ctx.message.add_reaction ('❌')
      return
    # date
    today = date.today()
    month = str (today.month) if today.month > 9 else "0"+str(today.month)
    year = str(today.year)
    # reason
    reason = ' '.join(arg for arg in args)
    reason = reason or "Vote pour le changement de nom du rôle des membres"
    # description
    description = "Test description"
    error = False
    # Embed capturing our vote
    embed = self.create_embed(reason, description, month, year)
    poll = await ctx.send(content=None, embed=embed)
    # insert into vote_message values ('message_id', 'channel_id', 'month', 'year', 'closed', 'guild_id')
    sql = f"insert into vote_message values ('{poll.id}', '{ctx.channel.id}', '{month}', '{year}', 0, '{guild_id}')"
    self.db.execute_order (sql, [])
    started_at = math.floor (time.time())
    sql = f"insert into vote_time values ('{poll.id}', '{started_at}', NULL, NULL, '{guild_id}')"
    self.db.execute_order (sql, [])
    # await ctx.send (f"`{sql}`")
    await self.logger.log('vote_log', author, ctx.message, error)

  @commands.command(name='setvotetype', aliases=['svt'])
  @commands.guild_only()
  async def set_vote_type(self, ctx, message_id: str = None, type_vote: str = None):
    """ Set a type for a vote message
    """
    if not message_id:
      await ctx.send ("Paramètre manquant: message_id")
      return
    try:
      message_id = int (message_id)
    except Exception as e:
      await ctx.send ("Paramètre manquant: message_id")
      return
    if not type_vote:
      type_vote = "vote"
    sql = f"update vote_message set vote_type=? where message_id=?"
    try:
      self.db.execute_order(sql, [type_vote, message_id])
    except Exception as e:
      await ctx.send ("An error occured !")
      await ctx.message.add_reaction ('❌')
      return
    await ctx.message.add_reaction ('✅')

  @commands.command(name='setdescription', aliases=['setdesc', 'desc', 'sd'])
  @commands.guild_only()
  async def set_description(self, ctx, message_id: str = None):
    """ Set a description for a vote message
    """
    await self.handle_result (ctx, message_id, "description", True)

  @commands.command(name='settitle', aliases=['title', 'st'])
  @commands.guild_only()
  async def set_title(self, ctx, message_id: str = None):
    """ Set a title for a vote message
    """
    await self.handle_result (ctx, message_id, "title", True)

  @commands.command(name='addproposition', aliases=['add'])
  @commands.guild_only()
  async def add_proposition(self, ctx, message_id: str = None):
    """
    Add a proposition
    """
    # Get proposition and handle it
    await self.handle_result (ctx, message_id, "proposition_line", False)

  @commands.command(name='closeproposition', aliases=['cp'])
  @commands.guild_only()
  async def close_proposition(self, ctx, message_id: str = None):
    """
    Close propositions
    """
    # Get proposition and handle it
    await self.handle_result (ctx, message_id, "end_proposition", True)

  @commands.command(name='closevote', aliases=['cv'])
  @commands.guild_only()
  async def close_vote(self, ctx, message_id: str = None):
    """
    Close vote
    """
    # Get proposition and handle it
    await self.handle_result (ctx, message_id, "close_vote", True)

  async def handle_result (self, ctx, message_id, handle, permission_neded):
    author = ctx.author
    guild_id = ctx.guild.id
    if permission_neded and not self.utils.has_role (author, guild_id):
      print ("No permissions")
      await ctx.message.add_reaction ('❌')
      return
    if not message_id:
      # search for the lastest vote in that channel
      select = f"select message_id from vote_message where channel_id={ctx.channel.id} and closed=0"
      fetched = self.db.fetch_one_line (select)
      if not fetched:
        await ctx.send (f"Aucun message de vote valide n'a été trouvé dans ce salon")
        await self.logger.log('vote_log', author, ctx.message, True)
        await ctx.message.add_reaction ('❌')
        return    # Send 'Hi what is your proposition'
      message_id = fetched [0]
    if not message_id:
      await ctx.send ('Missing parameters MessageID')
      await ctx.message.add_reaction ('❌')
      await self.logger.log('vote_log', author, ctx.message, True)
      return
    try:
      message_id = int (message_id)
    except Exception as e:
      await ctx.send ('Parameters MessageID must be an integer')
      await ctx.message.add_reaction ('❌')
      await self.logger.log('vote_log', author, ctx.message, True)
      return
    # valid message saved ?
    sql = f"select channel_id,closed,month,year from vote_message where message_id='{message_id}' and guild_id='{guild_id}'"
    fetched = self.db.fetch_one_line (sql)
    if not fetched:
      await ctx.send (f"MessageID {message_id} does not correspond to a vote")
      await self.logger.log('vote_log', author, ctx.message, True)
      await ctx.message.add_reaction ('❌')
      return
    # vote closed
    end_proposition = (fetched [1] == 1)
    vote_closed = (fetched [1] == 2)
    month = fetched [2]
    year = fetched [3]
    # get the message
    try:
      vote_msg = await ctx.channel.fetch_message (message_id)
    except Exception as e:
      if type(e).__name__ == "NotFound":
        await ctx.send (f"MessageID {message_id} does not correspond to a message on this channel")
      elif type(e).__name__ == "Forbidden":
        await ctx.send (f"Permission denied.")
      else:
        await ctx.send (f"Unknown error : {type(e).__name__} - {e}")
      await self.logger.log('vote_log', author, ctx.message, True)
      await ctx.message.add_reaction ('❌')
      return
    embed = vote_msg.embeds[0]

    if handle == "description":
      ask = await ctx.send ("Entrez la nouvelle description du vote :")
    elif handle == "title":
      ask = await ctx.send ("Entrez le nouveau titre du vote :")
    elif handle == "proposition_line":
      if end_proposition or vote_closed:
        await ctx.send ("La phase de proposition est terminée")
        return
      ask = await ctx.send ("Entrez la proposition :")
    elif handle == "end_proposition":
      await ctx.message.add_reaction ('✅')
      update = f"update vote_message set closed=1 where message_id='{message_id}'"
      self.db.execute_order (update, [])
      proposition_ended_at = math.floor (time.time())
      update = f"update vote_time set proposition_ended_at='{proposition_ended_at}' where message_id='{message_id}'"
      self.db.execute_order (update, [])
      colour = discord.Colour(0)
      colour = colour.from_rgb(56, 255, 56)
      embed.colour=colour
      embed.set_footer(text=f"{month}/{year} Phase de proposition terminée")
      await vote_msg.edit (embed=embed)
      return
    elif handle == "close_vote":
      await ctx.message.add_reaction ('✅')
      update = f"update vote_message set closed=2 where message_id='{message_id}'"
      self.db.execute_order (update, [])
      vote_closed_at = math.floor (time.time())
      update = f"update vote_time set vote_closed_at='{vote_closed_at}' where message_id='{message_id}'"
      self.db.execute_order (update, [])
      colour = discord.Colour(0)
      colour = colour.from_rgb(255, 71, 71)
      embed.colour=colour
      embed.set_footer(text=f"{month}/{year} Phase de vote terminée")
      await vote_msg.edit (embed=embed)
      return

    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)

    if handle == "description":
      embed.description = msg.content
    elif handle == "title":
      embed.title = msg.content
    elif handle == "proposition_line":
      field = embed.fields [0]
      new_value = field.value + "* "+msg.content+"\n"
      embed.clear_fields()
      embed.add_field (name=field.name, value=new_value, inline=False)

    await vote_msg.edit (embed=embed)
    await ctx.message.add_reaction ('✅')
    await self.logger.log('vote_log', author, ctx.message, False)
    await self.logger.log('vote_log', author, msg, False)
    await ask.delete(delay=0.5)
    await msg.delete(delay=0.5)
    await ctx.message.delete(delay=0.5)

  def create_embed(self, reason, description, month, year):
    colour = discord.Colour(0)
    colour = colour.from_rgb(20, 20, 255)
    embed = discord.Embed(colour=colour)
    embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.display_name)
    embed.title = reason
    embed.description = description
    embed.add_field (name='\uFEFF', value='\uFEFF', inline=False)
    embed.set_footer(text=f"{month}/{year}")
    return embed
