from .pwet import Pwet


async def setup(bot):
  await bot.add_cog(Pwet(bot))
