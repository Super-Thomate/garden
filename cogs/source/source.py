import random
import re

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
    sql = f"INSERT INTO source_channel VALUES ('{channel_id}', '{ctx.guild.id}') ;"
    try:
      database.execute_order(sql, [])
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      print(f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, 'source_channel_added').format(f'<#{channel_id}>'))

  @commands.command(name='removesourcechannel', aliases=['rsc'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def remove_source_channel(self, ctx, channel_id: int = None):
    channel_id = channel_id or ctx.channel.id
    sql = f"DELETE FROM source_channel WHERE channel_id='{channel_id}' and guild_id='{ctx.guild.id}';"
    try:
      database.execute_order(sql, [])
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
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def list_source_channels(self, ctx):
    message = ""
    sql = f"SELECT channel_id FROM source_channel WHERE guild_id='{ctx.guild.id}'"
    channels = [channel[0] for channel in database.fetch_all_line(sql)]  # get the list of the channels' id
    if len(channels) == 0:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_channel_list_empty"))
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
    sql = f"SELECT domain FROM source_domain WHERE guild_id='{ctx.guild.id}' ;"
    if domain in [domain[0] for domain in database.fetch_all_line(sql)]:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_already_blacklisted").format(domain))
      await ctx.message.add_reaction('❌')
      return
    sql = f"INSERT INTO source_domain VALUES ('{domain}', '{ctx.guild.id}') ;"
    try:
      database.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_blacklisted").format(domain))

  @commands.command(name='removedomain', aliases=['rmd'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def remove_domain(self, ctx: commands.Context, domain: str = None):
    if not domain:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format("domain"))
      return
    sql = f"SELECT domain FROM source_domain WHERE guild_id='{ctx.guild.id}' ;"
    if domain not in [domain[0] for domain in database.fetch_all_line(sql)]:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_not_found").format(domain))
      await ctx.message.add_reaction('❌')
      return
    sql = f"DELETE FROM source_domain WHERE domain='{domain}' and guild_id='{ctx.guild.id}' ;"
    try:
      database.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_removed").format(domain))

  @commands.command(name='listdomains', aliases=['lsd'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def list_domains(self, ctx):
    message = ""
    sql = f"SELECT domain FROM source_domain WHERE guild_id='{ctx.guild.id}'"
    domains = [domain[0] for domain in database.fetch_all_line(sql)]  # get the list of the domain
    if len(domains) == 0:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_no_blacklist"))
    for domain in domains:
      message += f"- **{domain}**\n"
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

  def is_url_in_blacklist(self, url: str, guild_id: str):
    if not Utils.is_valid_url(url):
      return False
    sql = f"SELECT domain FROM source_domain WHERE guild_id='{guild_id}' ;"
    ext = tldextract.extract(url)
    return ext.domain in [domain[0] for domain in database.fetch_all_line(sql)]

  @commands.Cog.listener('on_message')
  async def ask_for_source(self, message: discord.Message):
    url = re.search("(?P<url>https?://[^\s]+)", message.content)
    url = url.group("url") if url else None
    if "source" in message.content.lower():
      return
    if len(message.attachments) == 0 and (
            not url or not (self.is_url_in_blacklist(url, message.guild.id or Utils.is_url_image(url)))):
      return
    sql = f"SELECT channel_id FROM source_channel WHERE guild_id='{message.guild.id}' ;"
    if not str(message.channel.id) in [channel[0] for channel in database.fetch_all_line(sql)]:
      return
    response = self.get_source_message(message.author.id, message.guild.id)
    await message.channel.send(response)
