from .welcome import Welcome

def setup(bot):
  bot.add_cog(Welcome(bot))