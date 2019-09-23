from .utip import Utip

def setup(bot):
  bot.add_cog(Utip(bot))