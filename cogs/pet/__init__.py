from .pet import Pet


def setup(bot):
  bot.add_cog(Pet(bot))
