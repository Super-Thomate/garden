import random

import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs
from core import logger


class Rules(commands.Cog):
  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.warned_messages = []
    self.logger = Logs(self.bot)

  async def is_emoji_valid(self, msg_emoji: discord.Message):
    try:
      await msg_emoji.add_reaction(msg_emoji.content)
      await msg_emoji.remove_reaction(msg_emoji.content, self.bot.user)
      return True
    except Exception as e:
      logger ("rules::is_emoji_valid", f"{type(e).__name__} - {e}")
      await msg_emoji.channel.send(Utils.get_text(msg_emoji.guild.id, "rules_emoji_invalid").format(msg_emoji.content))
      return False

  @commands.command(name='addrule', aliases=['adr'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def add_rule(self, ctx: commands.Context):
    guild_id = ctx.guild.id
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    ask_rule = await ctx.send(Utils.get_text(guild_id, "rules_ask_rule"))
    msg_rule = await self.bot.wait_for('message', check=check)
    rule = msg_rule.content
    ask_emoji = await ctx.send(Utils.get_text(guild_id, "rules_ask_emoji"))
    msg_emoji = await self.bot.wait_for('message', check=check)
    emoji_text = msg_emoji.content

    await Utils.delete_messages(ask_rule, msg_rule, ask_emoji, msg_emoji, ctx.message)
    # Try to react with the emoji
    if not await self.is_emoji_valid(msg_emoji):
      return
    sql = "SELECT rule FROM rules_table WHERE emoji_text=? and guild_id= ? ;"
    fetched = database.fetch_one_line(sql, [emoji_text, guild_id])
    if fetched:
      await ctx.send(Utils.get_text(ctx.guild.id, "rules_already_exist").format(emoji_text))
      await ctx.message.add_reaction('❌')
      return
    custom_emoji_id = Utils.is_custom_emoji(emoji_text)
    if custom_emoji_id:
      sql = f"INSERT INTO rules_table (`rule`, `emoji_id`, `guild_id`) VALUES(?, '{custom_emoji_id}', ?) ;"
    else:
      sql = f"INSERT INTO rules_table (`rule`, `emoji_text`, `guild_id`) VALUES(?, '{emoji_text}', ?) ;"
    try:
      database.execute_order(sql, [rule, guild_id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("rules::add_rule", f"{type(e).__name__} - {e}")
    confirm = await ctx.send(Utils.get_text(ctx.guild.id, "rules_registered"))
    await confirm.delete(delay=2)

  @commands.command(name='removerule', aliases=['rmr'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def remove_rule(self, ctx: commands.Context, emoji_text: str = None):
    if not emoji_text:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<emoji>'))
      await ctx.message.add_reaction('❌')
      return
    custom_emoji_id = Utils.is_custom_emoji(emoji_text)
    sql = f"SELECT * FROM rules_table WHERE (emoji_text='{emoji_text}' OR emoji_id='{custom_emoji_id}') AND guild_id='{ctx.guild.id}';"
    fetched = database.fetch_one_line(sql, [])
    if not fetched:
      await ctx.send(Utils.get_text(ctx.guild.id, "rules_not_found").format(emoji_text))
      await ctx.message.add_reaction('❌')
      return
    sql = f"DELETE FROM rules_table WHERE (emoji_text='{emoji_text}' OR emoji_id='{custom_emoji_id}') and guild_id='{ctx.guild.id}';"
    try:
      database.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("rules::remove_rule", f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, "rules_deleted"))

  @commands.command(name='editrule', aliases=['edr'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def edit_rule(self, ctx: commands.Context, emoji_text: str = None):
    if not emoji_text:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<emoji>'))
      await ctx.message.add_reaction('❌')
      return
    custom_emoji_id = Utils.is_custom_emoji(emoji_text)
    sql = f"SELECT * FROM rules_table WHERE (emoji_text='{emoji_text}' OR emoji_id='{custom_emoji_id}') and guild_id=?;"
    fetched = database.fetch_one_line(sql, [ctx.guild.id])
    if not fetched:
      await ctx.send(Utils.get_text(ctx.guild.id, "rules_not_found").format(emoji_text))
      await ctx.message.add_reaction('❌')
      return
    await ctx.send(Utils.get_text(ctx.guild.id, "ask_message"))
    msg = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    message = msg.content
    sql = f"UPDATE rules_table SET rule=? WHERE (emoji_text='{emoji_text}' OR emoji_id='{custom_emoji_id}') and guild_id=?;"
    try:
      database.execute_order(sql, [message, ctx.guild.id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      logger ("rules::edit_rule", f"{type(e).__name__} - {e}")
    await ctx.send(Utils.get_text(ctx.guild.id, "rules_edited").format(emoji_text))

  @commands.command(name='listrules', aliases=['lrs'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def list_rules(self, ctx: commands.Context):
    guild_id = ctx.guild.id
    sql = f"SELECT rule, emoji_text, emoji_id FROM rules_table WHERE guild_id= ? ;"
    rules = database.fetch_all_line(sql, [guild_id])
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'rules_list'))
    array_rule = []
    line_rule = ""
    for rule in rules:
      rule_text = rule[0]
      emoji = None
      if rule[1]:
        emoji = rule[1]
      else:
        for guild in self.bot.guilds:
          try:
            emoji = str(await guild.fetch_emoji(int(rule[2])))
          except Exception as e:
            logger ("rules::list_rules", f"{type(e).__name__} - {e}")
          else:
            break
      if not emoji:
        raise Exception('Emoji not found', f'id = {rule[2]}')
      if (len(rule_text) > 500):
        rule_text = rule_text[:500] + "[...]"
      current_line = f"[{emoji}] {rule_text}\n"
      if len(line_rule + current_line) > 1024:
        array_rule.append(line_rule)
        line_rule = ""
      line_rule += current_line
    if len(line_rule) == 0:
      await ctx.send(content=None, embed=embed)
      return
    array_rule.append(line_rule)
    total_field = len(array_rule)
    current_field = 1
    for field in array_rule:
      embed.add_field(name=Utils.get_text(guild_id, 'rules_list_title').format(current_field, total_field)
                      , value=field
                      , inline=False
                      )
      current_field += 1
    await ctx.send(content=None, embed=embed)

  @commands.command(name='rule', aliases=['r'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def get_rule(self, ctx: commands.Context, emoji_text: str = None):
    guild_id = ctx.guild.id
    await ctx.message.delete()
    if not emoji_text:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_no_parameter").format('<emoji>'))
      return
    custom_emoji_id = Utils.is_custom_emoji(emoji_text)
    sql = f"SELECT rule FROM rules_table WHERE (emoji_text='{emoji_text}' OR emoji_id='{custom_emoji_id}') and guild_id=?;"
    fetched = database.fetch_one_line(sql, [guild_id])
    if not fetched:
      response = await ctx.send(Utils.get_text(ctx.guild.id, "rules_not_found").format(emoji_text))
      await response.add_reaction('❌')
      await response.delete(delay=2)
      return
    try:
      rule = fetched[0]
      await ctx.send(">>> " + rule)
    except Exception as e:
      logger ("rules::get_rule", f"{type(e).__name__} - {e}")

  @commands.command(name='setruleslog', aliases=['srl'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_rules_log(self, ctx: commands.Context, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    success = Utils.set_log_channel('rules_log', channel.id, ctx.guild.id)
    if success:
      await ctx.send(Utils.get_text(ctx.guild.id, "rules_log_channel"))
    else:
      await ctx.send(Utils.get_text(ctx.guild.id, "error_database_writing"))

  def get_rule_message(self, emoji: discord.Emoji, message, guild_id):
    sql = f"SELECT rule FROM rules_table WHERE (emoji_text='{emoji.name}' OR emoji_id='{emoji.id}') and guild_id=?;"
    fetched = database.fetch_one_line(sql, [guild_id])
    if not fetched:
      return None
    text = ""
    # split around '{'
    text_rand = (fetched[0]).split('{')
    for current in text_rand:
      parts = current.split('}')
      for part in parts:
        all_rand = part.split("|")
        current_part = all_rand[random.randint(0, len(all_rand) - 1)]
        text = text + current_part
    return text.replace("$member", f"<@{message.author.id}>").replace("$message", message.content)

  def set_already_warned_messages(self, message_id, emoji, guild_id):
    # cursor.execute('CREATE TABLE IF NOT EXISTS `rules_message` (`message_id` TEXT NOT NULL, `emoji_text` VARCHAR(64) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`, `emoji_text`, `guild_id`)) ;')
    insert = ("insert into rules_message " +
              " (`message_id`, `emoji_text`, `guild_id`) " +
              " values " +
              " (?, ?, ?)" +
              ""
              )
    database.execute_order(insert, [message_id, emoji, guild_id])

  def is_already_warned_messages(self, message_id, emoji, guild_id):
    # cursor.execute('CREATE TABLE IF NOT EXISTS `rules_message` (`message_id` TEXT NOT NULL, `emoji_text` VARCHAR(64) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`message_id`, `emoji_text`, `guild_id`)) ;')
    select = ("select emoji_text " +
              " from rules_message " +
              " where " +
              " message_id=? " +
              " and " +
              " emoji_text=? " +
              " and " +
              " guild_id=? " +
              ""
              )
    fetched = database.fetch_one_line(select, [message_id, emoji, guild_id])
    return (fetched and fetched[0])

  @commands.Cog.listener('on_raw_reaction_add')
  async def send_rule(self, payload: discord.RawReactionActionEvent):
    guild = self.bot.get_guild(payload.guild_id)
    if guild is None:
      return
    author = guild.get_member(payload.user_id)
    if author is None:
      return
    if (not Utils.is_loaded("rules", payload.guild_id)
            or not Utils.is_authorized(author, payload.guild_id)
            or author.bot
            or not payload.guild_id
    ):
      return
    if self.is_already_warned_messages(payload.message_id, str(payload.emoji), payload.guild_id):
      url_message = ("https://discordapp.com/channels/" +
                     str(payload.guild_id) +
                     "/" +
                     str(payload.channel_id) +
                     "/" +
                     str(payload.message_id)
                     )
      # await author.send(Utils.get_text(guild.id, "already_warned_rule").format(url_message))
      # logger ("rules::send_rule", f'Message {url_message} has already been warned by a rule')
      return
    channel = self.bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    rule = self.get_rule_message(payload.emoji, message, payload.guild_id)
    if not rule:
      return
    await message.author.send(">>> " + message.content)
    await message.author.send(rule)
    self.set_already_warned_messages(payload.message_id, str(payload.emoji), payload.guild_id)
    message_warned_content = len(message.content)
    if message_warned_content > 512:
      message_warned_content = message_warned_content[:512] + "[...]"
    message.content = f"**Member {message.author} warned**:\n{message.content}\nReaction: {payload.emoji}"
    await self.logger.log('rules_log', author, message, False)