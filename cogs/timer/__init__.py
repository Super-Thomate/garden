from .timer import Timer


def setup(bot):
  bot.add_cog(Timer(bot))
