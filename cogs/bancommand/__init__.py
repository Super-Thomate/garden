from .bancommand import Bancommand


def setup(bot):
  bot.add_cog(Bancommand(bot))
