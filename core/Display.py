import discord
import Utils
import database
import typing
from core import logger

def box (text: str, lang: str="") -> str:
   return (   "```{1}\n"
              "{0}\n"
              "```"
          ).format (text, lang)

def embed_info (   colour: typing.Union[discord.Colour, int]
                 , title:  str
                 , info:   str
                 , author: str
                 , date:   str
               ) -> discord.Embed:
  embed                      = discord.Embed (   colour = colour
                                               , title  = title
                                             )
  embed.description          = info
  embed.set_author (name = author)
  embed.set_footer (text = date)
  return embed