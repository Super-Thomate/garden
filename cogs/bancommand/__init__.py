from .bancommand import Bancommand


async def setup(bot):
  await bot.add_cog(Bancommand(bot))
