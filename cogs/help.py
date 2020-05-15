import typing
import discord
from discord.ext import commands
from Utilitary import utils


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=['h'])
    @commands.guild_only()
    @utils.require(['not_banned'])
    async def help(self, ctx: commands.Context, cog_name: typing.Optional[str]):
        """Find the help subcommand of the `cog_name` group and call it.
        If `cog_name` is not provided, display the general help.
        """
        if cog_name is not None and cog_name.lower() != 'help':
            cog_name = cog_name.lower()
            help_command = self.bot.get_command(f"{cog_name} help")
            if help_command is None:
                await ctx.send(utils.get_text(ctx.guild, "help_cog_not_found").format(cog_name))
                return
            await help_command.callback(self, ctx)
            return
        else:
            cog_list = []
            for cog_name in self.bot.cogs:
                loaded = '✅' if utils.is_loaded(cog_name.lower(), ctx.guild, self.bot) else '❌'
                short_description = utils.get_text(ctx.guild, f"{cog_name.lower()}_short_help")
                cog_list.append(f"- **{cog_name.capitalize()}** {loaded} - _{short_description}_")
            cog_list.sort()
            embed = discord.Embed(title=utils.get_text(ctx.guild, "help_title"),
                                  color=discord.Color.green())
            embed.add_field(name=utils.get_text(ctx.guild, "help_info_title"),
                            value=utils.get_text(ctx.guild, "help_info_description").format(ctx.prefix),
                            inline=False)
            embed.add_field(name=utils.get_text(ctx.guild, "help_cogs_title_1"),
                            value='\n'.join(cog_list[:9]),
                            inline=False)
            embed.add_field(name=utils.get_text(ctx.guild, "help_cogs_title_2"),
                            value='\n'.join(cog_list[9:]),
                            inline=False)
            embed.add_field(name=utils.get_text(ctx.guild, "help_ending_title"),
                            value=utils.get_text(ctx.guild, "help_ending_description").format(ctx.prefix),
                            inline=False)
            await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
