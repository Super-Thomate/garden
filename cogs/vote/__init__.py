from .vote import Vote


async def setup(bot):
  await bot.add_cog(Vote(bot))
