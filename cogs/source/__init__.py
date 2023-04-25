from .source import Source


async def setup(bot):
  await bot.add_cog(Source(bot))
