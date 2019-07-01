from .loader import Loader

def setup(bot):
  bot.add_cog(Loader(bot))