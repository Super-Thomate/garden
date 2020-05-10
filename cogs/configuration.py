import discord
from discord.ext import commands
from Utilitary import database, utils
from Utilitary.logger import log


class Configuration(commands.Cog):
    AVAILABLE_LANGUAGES = ['fr', 'en']

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=['config', 'cfg'])
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def configuration(self, ctx: commands.Context):
        """
        Display the availables sub-commands for the cog
        """
        await ctx.send(utils.get_text(ctx.guild, "configuration_subcommands").format(ctx.prefix))

    @configuration.command(name='addrolemodo', aliases=['arm'])
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def add_role_modo(self, ctx: commands.Context, role: discord.Role):
        """
        Add `role` to moderator roles' list
        """
        sql = "INSERT INTO config_role(role_id, permission, guild_id) VALUES (?, ?, ?) ;"
        success = database.execute_order(sql, [role.id, 1, ctx.guild.id])
        if success:
            await ctx.message.add_reaction('✅')
            log('configuration::add_role_modo', f"Role {role.name} added to moderator roles")
        else:
            await ctx.message.add_reaction('💀')

    @configuration.command(name='removerolemodo', aliases=['rrm'])
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def remove_role_modo(self, ctx: commands.Context, role: discord.Role):
        """
        Remove `role` from the modererator roles' list
        """
        sql = "DELETE FROM config_role WHERE role_id=? AND guild_id=? ;"
        success = database.execute_order(sql, [role.id, ctx.guild.id])
        if success:
            await ctx.message.add_reaction('✅')
            log('configuration::remove_role_modo', f"Role {role.name} removed from moderator roles")
        else:
            await ctx.message.add_reaction('💀')

    @configuration.command(name='addprefix', aliases=['ap'])
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def add_prefix(self, ctx: commands.Context, prefix: str):
        """
        Add `prefix` to the guild prefixes
        """
        sql = "INSERT INTO config_prefix(prefix, guild_id) VALUES (?, ?) ;"
        success = database.execute_order(sql, [prefix, ctx.guild.id])
        if success:
            await ctx.message.add_reaction('✅')
            log('configuration::add_prefix', f"Added prefix `{prefix}` in guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @configuration.command(name='removeprefix', aliases=['rp'])
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def remove_prefix(self, ctx: commands.Context, prefix: str):
        """
        Remove `prefix` from the guild's prefixes
        """
        sql = "DELETE FROM config_prefix WHERE prefix=? AND guild_id=? ;"
        success = database.execute_order(sql, [prefix, ctx.guild.id])
        if success:
            await ctx.message.add_reaction('✅')
            log('configuration::remove_prefix', f"Removed prefix `{prefix}` in guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @configuration.command(name='setlanguage', aliases=['slg'])
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def set_language(self, ctx: commands.Context, language_code: str):
        """
        Set the guild's language. `language_code` must be in the AVAILABLE_LANGUAGES class attribute
        """
        language_code = language_code.lower()
        if language_code not in self.AVAILABLE_LANGUAGES:
            await ctx.send(utils.get_text(ctx.guild, "configuration_language_unavailable")
                           .format(language_code, self.AVAILABLE_LANGUAGES))
            await ctx.message.add_reaction('❌')
            return
        sql = ("INSERT INTO config_lang(language_code, guild_id) VALUES (:code, :guild_id) "
               "ON CONFLICT(guild_id) DO UPDATE SET language_code=:code WHERE guild_id=:guild_id ;")
        success = database.execute_order(sql, {'code': language_code, 'guild_id': ctx.guild.id})
        if success:
            await ctx.message.add_reaction('✅')
            log('configuration::set_language', f"Language `{language_code}` set for guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @configuration.command(name='info')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned'])
    async def display_info(self, ctx: commands.Context):
        """
        Display informations about the guild's configuration
        """
        embed = discord.Embed(title=utils.get_text(ctx.guild, "configuration_cog_name"))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)

        #  Get guild current language and display it, 'en' is the default value
        sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
        response = database.fetch_one(sql, [ctx.guild.id])
        language = f"`{response[0].upper()}`" if response else '`EN` (default)'
        embed.add_field(name=utils.get_text(ctx.guild, "configuration_language"), value=language)

        #  Get guild prefixes and display them, '!' is the default value
        sql = "SELECT prefix FROM config_prefix WHERE guild_id=? ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        prefixes = " | ".join([f"`{prefix[0]}`" for prefix in response]) if response else "`!` (default)"
        embed.add_field(name=utils.get_text(ctx.guild, "configuration_prefix"), value=prefixes)

        #  Get guild moderator roles and display them
        sql = "SELECT role_id FROM config_role WHERE permission=1 AND guild_id=? ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        roles = " ".join([role.mention for role in filter(None, [ctx.guild.get_role(value[0]) for value in response])])\
            if response else utils.get_text(ctx.guild, "misc_not_set")
        embed.add_field(name=utils.get_text(ctx.guild, "configuration_role"), value=roles)

        await ctx.send(embed=embed)

    @configuration.command(name='help')
    @commands.guild_only()
    @utils.require(['not_banned'])
    async def help(self, ctx: commands.Context):
        """
        Displays help fot the cog
        """
        embed = discord.Embed(title=utils.get_text(ctx.guild, "configuration_cog_name"),
                              description=utils.get_text(ctx.guild, "configuration_help_description"))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "configuration_help_admin_command").format(ctx.prefix))
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Configuration(bot))
