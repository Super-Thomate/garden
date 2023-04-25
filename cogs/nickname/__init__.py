from .nickname import Nickname


async def setup(bot):
  await bot.add_cog(Nickname(bot))
