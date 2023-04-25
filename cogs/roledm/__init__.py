from .roledm import RoleDM


async def setup(bot):
  await bot.add_cog(RoleDM(bot))
