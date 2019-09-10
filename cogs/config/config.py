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
  "283243816448819200":
  {          "roles": [   580062847900450867
                        , 283247966490460160
                        , 283245747694993410
                        , 507978584342659082
                      ]
  ,       "prefixes": [   "!"
                        , "?"
                        , "-"
                      ]
  ,     "create_url": {   "invitation":"https://admin.realms-of-fantasy.net/bot.php"
                        , "gallery":"https://admin.realms-of-fantasy.net/bot-AR.php?"
                      }
  ,   "invite_delay": "6 months"
  ,      "do_invite": 1
  ,       "do_token": 0
  , "nickname_delay": "1 week"
  }
  """
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()
