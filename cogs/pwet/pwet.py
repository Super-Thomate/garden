import re

from discord.ext import commands

import Utils


class Pwet(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="pwet")
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def say_pwet(self, ctx: commands.Context, *, msg: str = None):
    """Turn a message into pwets: Hello World -> pwet pwet"""
    if msg == None:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_no_parameter').format('<message>'))
      return

    print("PWET: " + msg)
    await ctx.message.delete()
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
    await ctx.send(to_send)
