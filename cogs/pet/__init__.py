from .pet import Pet


async def setup(bot):
  await bot.add_cog(Pet(bot))
