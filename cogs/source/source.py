import random
import re
from datetime import datetime

import discord
import tldextract
from discord.ext import commands

import Utils
import database
from ..logs import Logs
from core import logger


class Source(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)


  @commands.group(invoke_without_command=True)
  @commands.guild_only()
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def source(self, ctx: commands.Context):
    """
    !source

    Print the valid subcommands
    """
    await ctx.send(Utils.get_text(ctx.guild.id, "TODO")) #TODO: edit locale


  @source.command(name='message')
  async def source_message(self, ctx: commands.Context):
    """
    !source message

    Set the message for source demands
    """
    ask_msg = await ctx.send(Utils.get_text(ctx.guild.id, "ask_message"))
    msg = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    message = msg.content

    sql = f"SELECT message FROM source_message WHERE guild_id=? ;"
    prev_source_message = database.fetch_one_line(sql, [ctx.guild.id])
    if not prev_source_message:
      sql = f"INSERT INTO source_message (message, guild_id) VALUES (?, ?) ;"
    else:
      sql = f"UPDATE source_message SET message=? WHERE guild_id=? ;"
    success = database.execute_order(sql, [message, ctx.guild.id])
    if success is not True:
      logger ("source::source_message", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    else:
      await ctx.channel.send(Utils.get_text(ctx.guild.id, 'display_new_message').format(message))


  @source.group(invoke_without_command=True, name='channel')
  async def source_channel(self, ctx: commands.Context):
    """
    !source channel

    Print valid subcommands
    """
    await ctx.send(Utils.get_text(ctx.guild.id, "TODO")) #TODO: edit locale


  @source_channel.command(name='add')
  async def source_channel_add(self, ctx: commands.Context, channel: discord.TextChannel = None):
    """
    !source channel add

    Add a channel to monitor for source demands
    :param channel: The channel to monitor for source. None means current
    """
    if not channel:
      channel = ctx.channel
    sql = f"INSERT INTO source_channel (channel_id, guild_id) VALUES (?, ?) ;"
    success = database.execute_order(sql, [channel.id, ctx.guild.id])
    if success is not True:
      logger ("Source::source_channel_add", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, 'source_channel_added').format(f'<#{channel_id}>'))


  @source_channel.command(name='remove')
  async def source_channel_remove(self, ctx: commands.Context, channel: discord.TextChannel = None):
    """
    !source channel remove

    Remove a channel from monitoring
    :param channel: The channel to monitor for source. None means current
    """
    if not channel:
      channel = ctx.channel
    sql = f"DELETE FROM source_channel WHERE channel_id=? and guild_id=? ;"
    success = database.execute_order(sql, [channel.id, ctx.guild.id])
    if success is not True:
      logger ("source::source_channel_remove", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, 'source_channel_removed').format(channel.mention))


  @source_channel.group(invoke_without_command=True, name='list')
  async def source_list(self, ctx: commands.Context):
    """
    !source list

    Print valid subcommands
    """
    await ctx.send(Utils.get_text(ctx.guild.id, "TODO")) #TODO: edit locale


  @source_list.command(name='channel')
  async def source_list_channel(self, ctx: commands.Context):
    """
    !source list channel

    List monitored channels
    """
    sql = f"SELECT channel_id FROM source_channel WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    embed = discord.Embed(colour=discord.Colour(0).from_rgb(176, 255, 176),
                          title=Utils.get_text(ctx.guild.id, 'source_list_channel_title')) #TODO: edit locale
    for channel_id in response:
      channel = ctx.get_channel(int(channel_id[0]))
      embed.add_field(name=Utils.get_text(ctx.guild.id, "source_list_channel_field"), value=channel.mention, inline=False)
    await ctx.send(content=None, embed=embed)


  @source_list.command(name='domain')
  async def source_list_domain(self, ctx: commands.Context):
    """
    !source list domain

    List blacklisted domains
    """
    sql = "SELECT domain FROM source_domain WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    embed = discord.Embed(colour=discord.Colour(0).from_rgb(176, 255, 176),
                          title=Utils.get_text(ctx.guild.id, 'source_list_domain_title')) #TODO: edit locale
    for channel_id in response:
      channel = ctx.get_channel(int(channel_id[0]))
      embed.add_field(name=Utils.get_text(ctx.guild.id, "source_list_domain_field"),
                      value=channel.mention,
                      inline=False)
    await ctx.send(content=None, embed=embed)


  @source_list.command(name='pattern')
  async def source_list_pattern(self, ctx: commands.Context):
    """
    !source list pattern

    List positive and negative patterns
    """
    # Get positive patterns ----------------------------------------------
    sql = "SELECT rowid, pattern FROM source_source_pattern WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    text = ""
    embed1 = discord.Embed(colour=discord.Colour(0).from_rgb(176, 255, 176),
                           title=Utils.get_text(ctx.guild.id, 'source_list_pattern_title_1')) #TODO: edit locale
    for pattern in response:
      text += f"{pattern[0]} - {pattern[1]}\n"
    embed1.add_field(name=Utils.get_text(ctx.guild.id, 'source_list_pattern_filed_1'), #TODO: edit locale
                     value=text,
                     inline=False)
    embed1.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
    embed1.timestamp = datetime.today()

    # Get negative patterns -----------------------------------------------
    sql = "SELECT rowid, pattern FROM source_source_no_pattern WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    text = ""
    embed2 = discord.Embed(colour=discord.Colour(0).from_rgb(176, 255, 176),
                           title=Utils.get_text(ctx.guild.id, 'source_list_pattern_title_2')) #TODO: edit locale
    for pattern in response:
      text += f"{pattern[0]} - {pattern[1]}\n"
    embed2.add_field(name=Utils.get_text(ctx.guild.id, 'source_list_pattern_filed_2'), #TODO: edit locale
                     value=text,
                     inline=False)
    embed2.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.name)
    embed2.timestamp = datetime.today()

    # Send the embeds
    await ctx.send(content=None, embed=embed1)
    await ctx.send(content=None, embed=embed2)


  @source.group(invoke_without_command=True, name='domain')
  async def source_domain(self, ctx: commands.Context):
    """
    !source domain

    Print valid subcommands
    """
    await ctx.send(Utils.get_text(ctx.guild.id, "TODO")) #TODO: edit locale


  @source_domain.command(name='add')
  async def source_domain_add(self, domain: str):
    """
    !source domain add

    Add a domain to blacklist
    """
    if "." in domain:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_wrong_format"))
      return

    # Check if domain is already blacklisted
    sql = f"SELECT domain FROM source_domain WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    if domain in [domain[0] for domain in response]:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_already_blacklisted").format(domain))
      await ctx.message.add_reaction('❌')
      return

    #add domain to database
    sql = f"INSERT INTO source_domain VALUES (?, ?) ;"
    success = database.execute_order(sql, [domain, ctx.guild.id])
    if success is not True:
      logger ("Source::source_domain_add", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_blacklisted").format(domain))


  @source_domain.command(name='remove')
  async def source_domain_remove(self, ctx: commands.Context, domain: str):
    """
    !source domain remove

    Remove a domain from blacklist
    """
    sql = f"DELETE FROM source_domain WHERE domain=? and guild_id=? ;"
    success = database.execute_order(sql, [domain, ctx.guild.id])
    if success is not True:
      logger ("Source::source_domain_remove", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, "source_domain_removed").format(domain))


  @source.group(invoke_without_command=True, name='pattern')
  async def source_pattern(self, ctx: commands.Context):
    """
    !source pattern

    Print valid subcommands
    """
    await ctx.send(Utils.get_text(ctx.guild.id, "TODO")) #TODO: edit locale


  @pattern.group(invoke_without_command=True, name='add')
  async def source_pattern_add(self, ctx: commands.Context):
    """
    !source pattern add

    Print valid subcommands
    """
    await ctx.send(Utils.get_text(ctx.guild.id, "TODO")) #TODO: edit locale


  @source_pattern_add.command(name='yes')
  async def source_pattern_add_positive(self, ctx: commands.Context, *, pattern: str):
    """
    !source pattern add yes

    Add a positive pattern
    """
    #check if pattern is already in database
    sql = f"SELECT pattern FROM source_source_pattern WHERE pattern=? AND guild_id=? ;"
    response = database.fetch_all_line(sql, [pattern, ctx.guild.id])
    if pattern in [pattern[0] for pattern in response]:
      await ctx.send(Utils.get_text(ctx.guild.id, "already_in_database").format('<pattern>'))
      return

    sql = f"INSERT INTO source_source_pattern VALUES (?, ?) ;"
    success = database.execute_order(sql, [pattern, ctx.guild.id])
    if success is not True:
      logger ("Source::source_pattern_add_positive", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    #TODO: add locale


  @source_pattern_add.command(name='no')
  async def source_pattern_add_negative(self, ctx: commands.Context, *, pattern: str):
    """
    !source pattern add no

    Add a negative pattern
    """
    #check if pattern is already in database
    sql = f"SELECT pattern FROM source_source_no_pattern WHERE pattern=? AND guild_id=? ;"
    response = database.fetch_all_line(sql, [pattern, ctx.guild.id])
    if pattern in [pattern[0] for pattern in response]:
      await ctx.send(Utils.get_text(ctx.guild.id, "already_in_database").format('<pattern>'))
      return

    sql = f"INSERT INTO source_source_no_pattern VALUES (?, ?) ;"
    success = database.execute_order(sql, [pattern, ctx.guild.id])
    if success is not True:
      logger ("Source::source_pattern_add_negative", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    #TODO: add locale


  @source_pattern.group(invoke_without_command=True, name='remove')
  async def source_pattern_remove(self, ctx: commands.Context):
    """
    !source pattern delete

    Print valid subcommands
    """
    await ctx.send(Utils.get_text(ctx.guild.id, "TODO")) #TODO: edit locale


  @source_pattern_remove.command(name='yes')
  async def source_pattern_remove_positive(self, ctx: commands.Context, rowid: int):
    """
    !source pattern remove yes

    Remove a positive pattern
    :param rowid: The rowid given by the list_pattern command
    """
    sql = "DELETE from source_source_pattern WHERE rowid=? AND guild_id=? ;"
    success = database.execute_order(sql, [rowid, ctx.guild.id])
    if success is not True:
      logger ("Source::source_pattern_remove_positive", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    #TODO: add locale


  @source_pattern_remove.command(name='no')
  async def source_pattern_remove_negative(self, ctx: commands.Context, rowid: int):
    """
    !source pattern remove no

    Remove a negative pattern
    :param rowid: The rowid given by the list_pattern command
    """
    sql = "DELETE from source_source_no_pattern WHERE rowid=? AND guild_id=? ;"
    success = database.execute_order(sql, [rowid, ctx.guild.id])
    if success is not True:
      logger ("Source::source_pattern_remove_negative", f"{type(success).__name__} - {success}")
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
    #TODO: add locale


  @commands.Cog.listener('on_message')
  async def ask_for_source(self, message: discord.Message):
    """
    Listen for messages and determinate if the author should give a source

    :param message: The posted message
    """
    pass




  # def __get_source_message(self, member_id, guild_id):
  #   select = f"SELECT message FROM source_message WHERE guild_id=? ;"
  #   fetched = database.fetch_one_line(select, [guild_id])
  #   if not fetched:
  #     raise RuntimeError('source message is not set !')
  #   text = ""
  #   # split around '{'
  #   text_rand = (fetched[0]).split('{')
  #   for current in text_rand:
  #     parts = current.split('}')
  #     for part in parts:
  #       all_rand = part.split("|")
  #       current_part = all_rand[random.randint(0, len(all_rand) - 1)]
  #       text = text + current_part
  #   return text.replace("$member", f"<@{member_id}>")
  #
  # def __is_blacklisted(self, urls: list, guild_id):
  #   sql = f"SELECT domain FROM source_domain WHERE guild_id=? ;"
  #   response = database.fetch_all_line(sql, [guild_id])
  #   domains = [domain[0] for domain in response]
  #   for url in urls:
  #     ext = tldextract.extract(url)
  #     if ext.domain in domains:
  #       return True
  #   return False
  #
  # def __get_pattern(self, table, guild_id):
  #   sql = f"SELECT pattern FROM {table} WHERE guild_id=? ;"
  #   response = database.fetch_all_line(sql, [guild_id])
  #   return [pattern[0] for pattern in response]
  #
  # def __is_message_in_source_channel(self, message: discord.Message):
  #   sql = "SELECT channel_id from source_channel WHERE guild_id=? ;"
  #   response = database.fetch_all_line(sql, [message.guild.id])
  #   channels = [channel[0] for channel in response]
  #   return str(message.channel.id) in channels
  #
  # def __is_source_triggered(self, message: discord.Message):
  #   urls = re.findall("(?P<url>https?://[^\s]+)", message.content)
  #   if len(urls) == 0 and len(message.attachments) == 0:
  #     return False
  #   if not self.__is_message_in_source_channel(message):
  #     return
  #   source = self.__get_pattern('source_source_pattern', message.guild.id)
  #   source = [pattern for pattern in source if pattern in message.content.lower()]
  #   no_source = self.__get_pattern('source_source_no_pattern', message.guild.id)
  #   no_source = [pattern for pattern in no_source if pattern in message.content.lower()]
  #   if len(message.attachments) != 0:
  #     if len(source) != 0 and len(no_source) == 0:
  #       return False
  #     elif len(source) == 0 and len(no_source) != 0:
  #       return True
  #     elif len(source) == 0 and len(no_source) == 0:
  #       return True
  #     elif len(source) != 0 and len(no_source) != 0:
  #       return True
  #   elif len(urls) != 0:
  #     if self.__is_blacklisted(urls, message.guild.id):
  #       return True
  #     elif len(source) != 0 and len(no_source) == 0:
  #       return False
  #     elif len(source) == 0 and len(no_source) != 0:
  #       return True
  #     elif len(source) == 0 and len(no_source) == 0:
  #       return True
  #     elif len(source) != 0 and len(no_source) != 0:
  #       return True
  #
  #
  # @commands.Cog.listener('on_message')
  # async def ask_for_source(self, message: discord.Message):
  #   if not message.guild:
  #     return
  #   if not Utils.is_loaded("source", message.guild.id):
  #     return
  #   if self.__is_source_triggered(message):
  #     logger("cog::source", f"Asked source to member {message.author}")
  #     await message.channel.send(self.__get_source_message(message.author.id, message.guild.id))
