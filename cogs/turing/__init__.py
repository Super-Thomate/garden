from .turing import Turing


async def setup(bot):
  await bot.add_cog(Turing(bot))
