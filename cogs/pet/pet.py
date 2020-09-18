import datetime

import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs
from core import logger

class Pet(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)
  
  @commands.command()
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def pet(self, ctx):
    await ctx.send ("https://cdn.discordapp.com/attachments/597091535242395649/756476304580411392/Pat_pat.png")