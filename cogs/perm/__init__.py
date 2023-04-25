from .perm import Permissions


async def setup(bot):
  await bot.add_cog(Permissions(bot))
