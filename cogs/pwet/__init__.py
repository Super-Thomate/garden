from .pwet import Pwet


def setup(bot):
  bot.add_cog(Pwet(bot))
