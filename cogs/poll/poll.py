import discord
from discord.ext import commands

import Utils


class Poll(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='poll', aliases=['ask'])
  @commands.guild_only()
  @Utils.require(required=['authorized', 'not_banned'])
  async def do_poll(self, ctx, *args):
    """ Create a poll
    """
    author = ctx.author
    print(args)
    # 1 Extract question and answers
    next_is = "nothing"
    question = ""
    answers = []
    emojis = []
    current_anwser = -1
    for arg in args:
      if arg == "$q":
        # A question incoming
        next_is = "question"
      elif arg.startswith("$"):
        # answer or emoji incoming
        print(f"arg: {arg} => current: {next_is}")
        if not next_is == "answer":
          current_anwser += 1
          answers.append(arg[1:])
          next_is = "answer"
        else:
          # emoji
          arg = arg[1:]
          next_is = "emoji"
      print(f"arg: {arg} => todo: {next_is}")
      # Now that i know what todo
      if next_is == "question":
        if not arg == "$q":
          question += arg + " "
      elif next_is == "answer":
        if not arg.startswith("$"):
          answers[current_anwser] += " " + arg
      elif next_is == "emoji":
        emojis.append(arg)
        answers[current_anwser] = f"\n- {arg} {answers[current_anwser]}"
        next_is = "nothing"

    if len(question) == 0:
      question = "ERROR NULL"
    if len(answers) == 0:
      answer = "ERROR NULL"
    else:
      answer = ' '.join(line for line in answers)

    # Embed capturing our poll
    embed = discord.Embed(colour=156805)
    embed.set_author(icon_url=author.avatar_url, name=str(author))
    embed.add_field(name=question, value=answer)
    poll = await ctx.send(content=None, embed=embed)
    for emoji in emojis:
      await poll.add_reaction(emoji)
