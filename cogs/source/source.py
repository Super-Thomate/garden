import random

from discord.ext import commands

import Utils
import database
from ..logs import Logs


class Source(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  @commands.command(name='addsourcechannel', aliases=['asc'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def add_source_channel(self, ctx, channel_id: int = None):
    channel_id = channel_id or ctx.channel.id
    sql = f"INSERT INTO source_channel VALUES ('{channel_id}', '{ctx.guild.id}') ;"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'database_writing_error'))
      print(f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, 'source_channel_added').format(f'<#{channel_id}>'))

  @commands.command(name='removesourcechannel', aliases=['rsc'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def remove_source_channel(self, ctx, channel_id: int = None):
    channel_id = channel_id or ctx.channel.id
    sql = f"DELETE FROM source_channel WHERE channel_id='{channel_id}' and guild_id='{ctx.guild.id}';"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'database_writing_error'))
      print(f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, 'source_channel_removed').format(f'<#{channel_id}>'))

  @commands.command(name='setsourcemessage', aliases=['ssm'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def set_source_message(self, ctx):
    await ctx.send(Utils.get_text(ctx.guild.id, "ask_new_message"))
    msg = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    message = msg.content
    sql = f"SELECT message FROM source_message WHERE guild_id='{ctx.guild.id}';"
    prev_source_message = database.fetch_one_line(sql)
    if not prev_source_message:
      sql = f"INSERT INTO source_message VALUES (?, '{ctx.guild.id}') ;"
    else:
      sql = f"UPDATE source_message SET message=? WHERE guild_id='{ctx.guild.id}';"
    print(sql)
    try:
      database.execute_order(sql, [message])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.channel.send(Utils.get_text(ctx.guild.id, 'display_new_message').format(message))

  @commands.command(name='listsourcechannels', aliases=['lsc'])
  @Utils.require(required=['authorized', 'not_banned'])
  async def list_source_channels(self, ctx):
    message = ""
    sql = f"SELECT channel_id FROM source_channel WHERE guild_id='{ctx.guild.id}'"
    channels = [channel[0] for channel in database.fetch_all_line(sql)]  # get the list of the channels' id
    if len(channels) == 0:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_channel_list_empty"))
    for channel in channels:
      message += f"- **<#{channel}>**\n"
    await ctx.send(message)

  def get_source_message(self, member_id, guild_id):
    select = f"SELECT message FROM source_message WHERE guild_id='{guild_id}';"
    fetched = database.fetch_one_line(select)
    if not fetched:
      raise RuntimeError('source message is not set !')
    text = ""
    # split around '{'
    text_rand = (fetched[0]).split('{')
    for current in text_rand:
      parts = current.split('}')
      for part in parts:
        all_rand = part.split("|")
        current_part = all_rand[random.randint(0, len(all_rand) - 1)]
        text = text + current_part
    return text.replace("$member", f"<@{member_id}>")

  @commands.Cog.listener('on_message')
  async def ask_for_source(self, message):
    if len(message.attachments) == 0:
      return
    sql = f"SELECT channel_id FROM source_channel WHERE guild_id='{message.guild.id}'"
    channels = [channel[0] for channel in database.fetch_all_line(sql)] # get the list of the channels' id
    if not str(message.channel.id) in channels:
      return
    response = self.get_source_message(message.author.id, message.guild.id)
    await message.channel.send(response)