import discord
from discord.ext import commands
from datetime import datetime
from datetime import timezone
from ..logs import Logs
from database import Database
from Utils import Utils
import random
import time
import math


class Config(commands.Cog):

  """
  Config:
  * bancommanduser command user [time]
  """
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()
