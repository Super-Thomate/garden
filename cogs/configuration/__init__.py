from .configuration import Configuration


def setup(bot):
  bot.add_cog(Configuration(bot))
