from .loader import Loader


async def setup(bot):
  await bot.add_cog(Loader(bot))
