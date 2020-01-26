import discord
from discord.ext import commands


class Permissions(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='perms', aliases=['perms_for', 'permissions'])
  @commands.guild_only()
  async def check_permissions(self, ctx, *, member: discord.Member = None):
    """ Checks a members Guild Permissions
    """
    member = member or ctx.author
    # Here we check if the value of each permission is True.
    perms = '\n'.join(perm for perm, value in member.guild_permissions if value)
    # And to make it look nice, we wrap it in an Embed.
    embed = discord.Embed(title='Permissions for:', description=ctx.guild.name, colour=member.colour)
    embed.set_author(icon_url=member.avatar_url, name=str(member))
    embed.add_field(name='\uFEFF', value=perms)
    # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
    await ctx.send(content=None, embed=embed)
