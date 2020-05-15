import discord
from discord.ext import commands

from Utilitary import database, utils
from Utilitary.logger import log


class Loader(commands.Cog):
    DEFAULT_COGS = ('configuration', 'loader', 'help')

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=['ld'])
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def loader(self, ctx: commands.Context):
        """Display the availables sub-commands for the cog."""
        await ctx.send(utils.get_text(ctx.guild, "loader_subcommands").format(ctx.prefix))

    @loader.command(name='cogload')
    @commands.guild_only()
    @utils.require(['developer'])
    async def load_cog_bot(self, ctx: commands.Context, *, cog: str):
        """Load the cog `cog` for the bot. Need developer privileges."""
        cog = cog.lower()
        try:
            self.bot.load_extension(f'cogs.{cog}')
            await ctx.message.add_reaction('✅')
            log("Loader::load_cog_bot", f"Cog {cog} loaded")
        except Exception as e:
            await ctx.send(utils.get_text(ctx.guild, "misc_error_occured").format(type(e).__name__, e))
            await ctx.message.add_reaction('❌')

    @loader.command(name='cogunload')
    @commands.guild_only()
    @utils.require(['developer'])
    async def unload_cog_bot(self, ctx: commands.Context, *, cog: str):
        """Reload the cog `cog` for the bot. Need developer privileges."""
        cog = cog.lower()
        try:
            self.bot.unload_extension(f'cogs.{cog}')
            await ctx.message.add_reaction('✅')
            log("Loader::unload_cog_bot", f"Cog {cog} unloaded")
        except Exception as e:
            await ctx.send(utils.get_text(ctx.guild, "misc_error_occured").format(type(e).__name__, e))
            await ctx.message.add_reaction('❌')

    @loader.command(name='cogreload')
    @commands.guild_only()
    @utils.require(['developer'])
    async def reload_cog_bot(self, ctx: commands.Context, *, cog: str):
        """Reload the cog `cog` for the bot. Need developer privileges."""
        cog = cog.lower()
        try:
            self.bot.reload_extension(f'cogs.{cog}')
            await ctx.message.add_reaction('✅')
            log("Loader::reload_cog_bot", f"Cog {cog} reloaded")
        except Exception as e:
            await ctx.send(utils.get_text(ctx.guild, "misc_error_occured").format(type(e).__name__, e))
            await ctx.message.add_reaction('❌')

    @loader.command(name='coglist')
    @commands.guild_only()
    @utils.require(['developer'])
    async def list_cog_bot(self, ctx: commands.Context):
        """List the cogs loaded for the bot. Need developer privileges."""
        cog_list = ""
        for cog in self.bot.cogs.keys():
            cog_list += f"- **{cog}**\n"
        await ctx.send(cog_list)

    @loader.command(name='reloadlocale', aliases=['rlc'])
    @commands.guild_only()
    @utils.require(['developer'])
    async def reload_locale(self, ctx: commands.Context):
        """Reload the dictionnary containing the bot locale's."""
        utils.init_strings(self.bot)
        await ctx.message.add_reaction('✅')

    @loader.command(name='load')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def load_cog_guild(self, ctx: commands.Context, *, cog: str):
        """Load the cog `cog` for the guild."""
        cog = cog.lower()
        if cog in self.DEFAULT_COGS:
            await ctx.send(utils.get_text(ctx.guild, "loader_cannot_load_cog").format(cog))
            await ctx.message.add_reaction('❌')
            return
        if cog.capitalize() not in self.bot.cogs.keys():
            await ctx.send(utils.get_text(ctx.guild, "loader_cog_not_found").format(cog))
            await ctx.message.add_reaction('❌')
            return
        sql = "INSERT INTO config_cog(cog_name, status, guild_id) VALUES (:cog_name, 1, :guild_id) " \
              "ON CONFLICT(cog_name, guild_id) DO UPDATE SET status=1 WHERE cog_name=:cog_name AND guild_id=:guild_id ;"
        success = database.execute_order(sql, {"cog_name": cog, "guild_id": ctx.guild.id})
        if success:
            await ctx.message.add_reaction('✅')
            log("Loader::cog_guild_load", f"Cog {cog} loaded in guild {ctx.guild}")
        else:
            await ctx.message.add_reaction('💀')

    @loader.command(name='unload')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def unload_cog_guild(self, ctx: commands.Context, *, cog: str):
        """Unload the cog `cog` for the guild."""
        cog = cog.lower()
        if cog in self.DEFAULT_COGS:
            await ctx.send(utils.get_text(ctx.guild, "loader_cannot_load_cog").format(cog))
            await ctx.message.add_reaction('❌')
            return
        if cog.capitalize() not in self.bot.cogs.keys():
            await ctx.send(utils.get_text(ctx.guild, "loader_cog_not_found").format(cog))
            await ctx.message.add_reaction('❌')
            return
        sql = "INSERT INTO config_cog(cog_name, status, guild_id) VALUES (:cog_name, 0, :guild_id) " \
              "ON CONFLICT(cog_name, guild_id) DO UPDATE SET status=0 WHERE cog_name=:cog_name AND guild_id=:guild_id ;"
        success = database.execute_order(sql, {"cog_name": cog, "guild_id": ctx.guild.id})
        if success:
            await ctx.message.add_reaction('✅')
            log("Loader::cog_guild_unload", f"Cog {cog} unloaded in guild {ctx.guild}")
        else:
            await ctx.message.add_reaction('💀')

    @loader.command(name='unloadall')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def unload_all_cog_guild(self, ctx: commands.Context):
        """Unload all cogs in the guild."""
        sql = "UPDATE config_cog SET status=0 WHERE guild_id=? ;"
        success = database.execute_order(sql, [ctx.guild.id])
        if success:
            await ctx.message.add_reaction('✅')
            log("Loader::cog_guild_unload_all", f"All cogs unloaded in guild {ctx.guild}")
        else:
            await ctx.message.add_reaction('💀')

    @loader.command(name='listcogs')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def list_cog_guild(self, ctx: commands.Context):
        """List all loaded cog in the guild."""
        loaded_cog = ""
        for cog in self.DEFAULT_COGS:
            loaded_cog += f"- **{cog.capitalize()}** (default)\n"
        sql = "SELECT cog_name FROM config_cog WHERE status=1 AND guild_id=? ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        if response:
            for name in response:
                loaded_cog += f"- **{name[0].capitalize()}**\n"
        await ctx.send(loaded_cog)

    @loader.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """Displays help fot the cog."""
        embed = discord.Embed(title=utils.get_text(ctx.guild, "loader_cog_name"),
                              description=utils.get_text(ctx.guild, "loader_help_description"))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "loader_help_admin_command").format(ctx.prefix),
                        inline=False)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_developer_command"),
                        value=utils.get_text(ctx.guild, "loader_help_developer_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Loader(bot))
