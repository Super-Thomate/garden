from .utip import Utip


async def setup(bot):
  await bot.add_cog(Utip(bot))
