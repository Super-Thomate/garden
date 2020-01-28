import random
from datetime import datetime

import discord
import tldextract
from discord.ext import commands

import Utils
import database
from ..logs import Logs


class Source(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  @commands.command(name='addsourcechannel', aliases=['asc'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def add_source_channel(self, ctx, channel_id: int = None):
    channel_id = channel_id or ctx.channel.id
    sql = f"INSERT INTO source_channel VALUES (?, ?) ;"
    print(sql)
    try:
      database.execute_order(sql, [channel_id, ctx.guild.id])
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      print(f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, 'source_channel_added').format(f'<#{channel_id}>'))

  @commands.command(name='removesourcechannel', aliases=['rsc'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def remove_source_channel(self, ctx, channel_id: int = None):
    channel_id = channel_id or ctx.channel.id
    sql = f"DELETE FROM source_channel WHERE channel_id=? and guild_id=? ;"
    print(sql)
    try:
      database.execute_order(sql, [channel_id, ctx.guild.id])
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      print(f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, 'source_channel_removed').format(f'<#{channel_id}>'))

  @commands.command(name='setsourcemessage', aliases=['ssm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_source_message(self, ctx):
    await ctx.send(Utils.get_text(ctx.guild.id, "ask_message"))
    msg = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    message = msg.content
    sql = f"SELECT message FROM source_message WHERE guild_id=? ;"
    prev_source_message = database.fetch_one_line(sql, [ctx.guild.id])
    if not prev_source_message:
      sql = f"INSERT INTO source_message VALUES (?, ?) ;"
    else:
      sql = f"UPDATE source_message SET message=? WHERE guild_id=? ;"
    print(sql)
    try:
      database.execute_order(sql, [message, ctx.guild.id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.channel.send(Utils.get_text(ctx.guild.id, 'display_new_message').format(message))

  @commands.command(name='listsourcechannels', aliases=['lsc'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def list_source_channels(self, ctx):
    sql = f"SELECT channel_id FROM source_channel WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    channels = [channel[0] for channel in response]
    if len(channels) == 0:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_channel_list_empty"))
    message = ""
    for channel in channels:
      message += f"- **<#{channel}>**\n"
    await ctx.send(message)

  @commands.command(name='adddomain', aliases=['adm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def blacklist_domain(self, ctx: commands.Context, domain: str = None):
    if not domain:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format("domain"))
      return
    if "." in domain:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_wrong_format"))
      return
    sql = f"SELECT domain FROM source_domain WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    if domain in [domain[0] for domain in response]:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_already_blacklisted").format(domain))
      await ctx.message.add_reaction('❌')
      return
    sql = f"INSERT INTO source_domain VALUES (?, ?) ;"
    print(sql)
    try:
      database.execute_order(sql, [domain, ctx.guild.id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return

  @commands.command(name='removedomain', aliases=['rmd'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def remove_domain(self, ctx: commands.Context, domain: str = None):
    if not domain:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format("domain"))
      return
    sql = f"SELECT domain FROM source_domain WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    if domain not in [domain[0] for domain in response]:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_not_found").format(domain))
      await ctx.message.add_reaction('❌')
      return
    sql = f"DELETE FROM source_domain WHERE domain=? and guild_id=? ;"
    print(sql)
    try:
      database.execute_order(sql, [domain, ctx.guild.id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return

  @commands.command(name='listdomains', aliases=['lsd'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def list_domains(self, ctx):
    sql = "SELECT domain FROM source_domain WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    domains = [domain[0] for domain in response]
    if len(domains) == 0:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_no_blacklist"))
      return
    message = ""
    for domain in domains:
      message += f"- **{domain}**\n"
    await ctx.send(message)

  @commands.command(name='addsourcepattern', aliases=['asp'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def add_source_pattern(self, ctx: commands.Context, kind: str, *, pattern: str):
    """if kind.lower() not in ('y', 'n'):
      await ctx.send(Utils.get_text(ctx.guild.id, "source_no_kind"))
      return
    if not pattern:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<pattern>'))
      return"""
    table = "source_source_pattern" if kind.lower() == 'y' else "source_source_no_pattern"
    sql = f"SELECT pattern FROM {table} WHERE pattern=? AND guild_id=? ;"
    response = database.fetch_all_line(sql, [pattern, ctx.guild.id])
    if pattern in [pattern[0] for pattern in response]:
      await ctx.send(Utils.get_text(ctx.guild.id, "already_in_database").format('<pattern>'))
      return
    sql = f"INSERT INTO {table} VALUES (?, ?) ;"
    print(sql)
    try:
      database.execute_order(sql, [pattern, ctx.guild.id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return

  def get_list(self, table: str, guild_id: int):
    sql = f"SELECT rowid, pattern FROM {table} WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [guild_id])
    message = ""
    for pattern in response:
      message += f"{pattern[0]} - {pattern[1]}\n"
    return message

  @commands.command(name='listsourcepattern', aliases=['lsp'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def list_source_pattern(self, ctx: commands.Context):
    source_message = self.get_list('source_source_pattern', ctx.guild.id)
    no_source_message = self.get_list('source_source_no_pattern', ctx.guild.id)
    embed = discord.Embed(colour=discord.Color(0).from_rgb(176, 255 ,176), title="Source patterns")
    if not source_message and not no_source_message:
      embed.description = Utils.get_text(ctx.guild.id, "source_no_pattern")
    if source_message:
      embed.add_field(name=Utils.get_text(ctx.guild.id, "source_source_pattern"),
                      value=source_message,
                      inline=False)
    if no_source_message:
      embed.add_field(name=Utils.get_text(ctx.guild.id, "source_not_source_pattern"),
                      value=no_source_message,
                      inline=False)
    embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
    embed.timestamp = datetime.today()
    await ctx.send(content=None, embed=embed)


  @commands.command(name='removesourcepattern', aliases=['rsp'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def remove_source_pattern(self, ctx: commands.Context, kind: str, id: str):
    sql = "DELETE"

  def get_source_message(self, member_id, guild_id):
    select = f"SELECT message FROM source_message WHERE guild_id=? ;"
    fetched = database.fetch_one_line(select, [guild_id])
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

  def is_url_in_blacklist(self, url: str, guild_id: str):
    if not Utils.is_valid_url(url):
      return False
    sql = f"SELECT domain FROM source_domain WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [guild_id])
    ext = tldextract.extract(url)
    return ext.domain in [domain[0] for domain in response]

  @commands.Cog.listener('on_message')
  async def ask_for_source(self, message: discord.Message):
    pass