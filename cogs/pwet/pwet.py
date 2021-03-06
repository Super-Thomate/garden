import re

import discord
from discord.ext import commands

import Utils
import database
from core import logger

class Pwet(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  def create_pwet(self, msg):
    words = re.split('(<:\w+:\d+>|.\uFE0F\u20E3)', msg)  # Separate server emojis and special emojis like :one:
    result = []
    for word in words:
      if re.match('(<:\w+:\d+>|.\uFE0F\u20E3)', word):
        result.append(word)
      else:
        result.extend(re.split('(\W)', word))  # Split the rest by non-word characters

    # Change word to pwet if it is not one of the 'special case'
    for index, token in enumerate(result):
      if token != '' and not re.match('(<:\w+:\d+>|.\uFE0F\u20E3|\W)', token):
        result[index] = 'pwet'

    to_send = "".join(result)
    if len(to_send) >= 2000:
      to_send = Utils.get_text(ctx.guild.id, "pwet_message_too_long")
    return to_send


  @commands.command(name="pwet")
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def say_pwet(self, ctx: commands.Context, *, msg: str = None):
    """Turn a message into pwets: Hello World -> pwet pwet"""
    if msg is None:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_no_parameter').format('<message>'))
      return
    logger ("pwet::say_pwet", "PWET: " + msg)
    try:
      await ctx.message.delete()
    except Exception as e:
      logger ("pwet::say_pwet", f"{type(e).__name__} - {e} \nHey ! Somebody already delete the message !!")
    await ctx.send(self.create_pwet(msg))

  @commands.command(name="addpwetreaction", aliases=['apr'])
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def add_reaction(self, ctx: commands.Context, emoji_text: str):
    if emoji_text is None:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_no_parameter').format('<emoji>'))
      return

    sql = "SELECT guild_id FROM pwet_reaction WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])
    custom_emoji_id = Utils.is_custom_emoji(emoji_text)
    if len(response) == 0:
      if custom_emoji_id:
        sql = f"INSERT INTO pwet_reaction (`emoji_id`, `guild_id`) VALUES('{custom_emoji_id}', ?) ;"
      else:
        sql = f"INSERT INTO pwet_reaction (`emoji_text`, `guild_id`) VALUES('{emoji_text}', ?) ;"
      database.execute_order(sql, [ctx.guild.id])
    else:
      if custom_emoji_id:
        sql = f"UPDATE pwet_reaction SET emoji_id='{custom_emoji_id}', emoji_text=null WHERE guild_id=? ;"
      else:
        sql = f"UPDATE pwet_reaction SET emoji_text='{emoji_text}', emoji_id=null WHERE guild_id=? ;"
      database.execute_order(sql, [ctx.guild.id])
    await ctx.send(Utils.get_text(ctx.guild.id, 'pwet_reaction_added'))

  @commands.command(name="removepwetreaction", aliases=['rpr'])
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def remove_reaction(self, ctx: commands.Context):
    sql = "DELETE FROM pwet_reaction WHERE guild_id=? ;"
    database.execute_order(sql, [ctx.guild.id])
    await ctx.send(Utils.get_text(ctx.guild.id, 'pwet_reaction_deleted'))


  @commands.Cog.listener('on_raw_reaction_add')
  async def pwet_message(self, payload: discord.RawReactionActionEvent):
    guild = self.bot.get_guild(payload.guild_id)
    if guild is None:
      return
    author = guild.get_member(payload.user_id)
    if author is None:
      return
    if Utils.is_authorized(author, guild.id): # Utils::is_authorized: AttributeError - 'NoneType' object has no attribute 'guild_permissions'
      sql = "SELECT emoji_text, emoji_id FROM pwet_reaction WHERE guild_id=? ;"
      response = database.fetch_one_line(sql, [guild.id])
      if response is None:
        return
      emoji_text, emoji_id = response[0], response[1]
      if emoji_text == payload.emoji.name or emoji_id == str(payload.emoji.id):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        for reaction in message.reactions:
          if (reaction.emoji == emoji_text or str(reaction.emoji.id) == emoji_id) and reaction.count > 1:
              return
        message = self.create_pwet(message.content)
        await channel.send(message)
