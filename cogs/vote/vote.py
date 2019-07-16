import discord
from discord.ext import commands
from Utils import Utils
from ..logs import Logs
from database import Database
from datetime import date

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
    # insert into vote_message values ('message_id', 'channel_id', 'month', 'year', 'guild_id')
    sql = f"insert into vote_message values ({poll.id}', '{ctx.channel.id}', '{month}', '{year}', '{guild_id}')"
    ctx.send (f"`{sql}`")
    await self.logger.log('vote_log', author, ctx.message, error)
  
  def create_embed(self, reason, description, month, year):
    colour = discord.Colour(0)
    colour = colour.from_rgb(231, 184, 255)
    embed = discord.Embed(colour=colour)
    embed.set_author(icon_url=self.bot.user.avatar_url, name=self.bot.user.display_name)
    embed.title = reason
    embed.description = description
    embed.set_footer(text=f"{month}/{year}")
    return embed
    
"""
cursor.execute('CREATE TABLE IF NOT EXISTS `vote_propositions` (`proposition` VARCHAR(512) NOT NULL,`emoji` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `author_id` VARCHAR(256) NOT NULL, `message_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`author_id`, `month`, `year`)) ;')
cursor.execute('CREATE TABLE IF NOT EXISTS `vote_colors` (`color` VARCHAR(6) NOT NULL,`emoji` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `author_id` VARCHAR(256) NOT NULL, `message_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`author_id`, `month`, `year`)) ;')
cursor.execute('CREATE TABLE IF NOT EXISTS `vote_message` (`message_id` VARCHAR(256) NOT NULL, `channel_id` VARCHAR(256) NOT NULL, `month` VARCHAR(2) NOT NULL, `year` VARCHAR(4) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`guild_id`, `month`, `year`)) ;')
"""

"""
print (args)
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
        print (f"arg: {arg} => current: {next_is}")
        if not next_is == "answer":
          current_anwser += 1
          answers.append (arg[1:])
          next_is = "answer"
        else:
          # emoji
          arg = arg[1:]
          next_is = "emoji"
      print (f"arg: {arg} => todo: {next_is}")
      # Now that i know what todo
      if next_is == "question":
        if not arg == "$q":
          question += arg+" "
      elif next_is == "answer":
        if not arg.startswith("$"):
          answers [current_anwser] += " "+arg
      elif next_is == "emoji":
        emojis.append (arg)
        answers [current_anwser] = f"\n- {arg} {answers [current_anwser] }"
        next_is = "nothing"

    if len(question) == 0:
      question = "ERROR NULL"
    if len(answers) == 0:
      answer = "ERROR NULL"
    else:
      answer = ' '.join(line for line in answers)
"""