from .logs import Logs


async def setup(bot):
  await bot.add_cog(Logs(bot))
