import discord
from discord.ext import commands
from Utilitary.logger import log
from Utilitary import utils, database


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=['wc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def welcome(self, ctx: commands.Context):
        """
        Display the availables sub-commands for the cog
        """
        await ctx.send(utils.get_text(ctx.guild, "welcome_subcommands").format(ctx.prefix))

    @welcome.command(name='addwelcome', aliases=['awc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def add_welcome(self, ctx: commands.Context, role: discord.Role,
                          channel: discord.TextChannel, *, message: str):
        """
        Add a welcome for role `role` in channel `channel` with message `message`
        """
        sql = "INSERT INTO welcome_config(role_id, channel_id, message, guild_id) " \
              "VALUES (:role_id, :channel_id, :message, :guild_id) " \
              "ON CONFLICT(role_id, channel_id, guild_id) DO " \
              "UPDATE SET message=:message WHERE role_id=:role_id AND channel_id=:channel_id AND guild_id=:guild_id ;"
        response = database.execute_order(sql, {"role_id": role.id,
                                                "channel_id": channel.id,
                                                "message": message,
                                                "guild_id": ctx.guild.id})
        if response is True:
            await ctx.message.add_reaction('✅')
            log("Welcome::add_welcome",
                f"Added welcome for role {role.name} in channel {channel.name} "
                f"with message `{message}` in guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @welcome.command(name='removewelcome', aliases=['rwc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def remove_welcome(self, ctx: commands.Context, role: discord.Role, channel: discord.TextChannel):
        """
        Remove welcome for role `role` in channel `channel`
        """
        sql = "DELETE FROM welcome_config WHERE role_id=? AND channel_id=? AND guild_id=? ;"
        response = database.execute_order(sql, [role.id, channel.id, ctx.guild.id])
        if response is True:
            await ctx.message.add_reaction('✅')
            log("Welcome::remove_welcome",
                f"Removed welcome for role {role.name} in channel {channel.name} in guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @welcome.command(name='resetwelcome', aliases=['rswc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def reset_welcome(self, ctx: commands.Context, role: discord.Role,
                            channel: discord.TextChannel = None, member: discord.Member = None):
        """
        Reset the welcome status of a member for the role `role` in the channel `channel`
        If `channel` is not given reset the status for all the channels.
        If `member` is not given, reset the status of everyone
        """
        if member is None:
            if not await utils.ask_confirmation(ctx, "welcome_reset_ask_confirmation", formating=[role.mention]):
                return
        sql = "DELETE FROM welcome_user WHERE role_id=? AND guild_id=? "
        parameters = [role.id, ctx.guild.id]
        if member is not None:
            parameters.append(member.id)
            sql += "AND member_id=? "
        if channel is not None:
            parameters.append(channel.id)
            sql += "AND channel_id=? "
        sql += ";"
        response = database.execute_order(sql, parameters)
        if response is True:
            await ctx.message.add_reaction('✅')
            log("Welcome::reset_welcome",
                f"Reset welcome for member {member} with role {role} "
                f"and channel {channel} in guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @welcome.command(name='info')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def info(self, ctx: commands.Context):
        sql = "SELECT role_id, channel_id, message FROM welcome_config WHERE guild_id=? ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        if not response:
            await ctx.send(utils.get_text(ctx.guild, "welcome_info_empty"))
        description = ""
        for line in response:
            role_id, channel_id, message = line
            role = ctx.guild.get_role(role_id)
            role = role.mention if role else utils.get_text(ctx.guild, "misc_invalid_role").format(role_id)
            channel = ctx.guild.get_channel(channel_id)
            channel = channel.mention if channel \
                else utils.get_text(ctx.guild, "misc_invalid_channel").format(channel_id)
            description += f"- {role} | {channel} | `{message}`\n"

        embed = discord.Embed(title=utils.get_text(ctx.guild, "welcome_info_title"), description=description)
        await ctx.send(embed=embed)

    @welcome.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(title=utils.get_text(ctx.guild, "welcome_cog_name"),
                              description=utils.get_text(ctx.guild, "welcome_help_description").format(ctx.prefix))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_user_command"),
                        value=utils.get_text(ctx.guild, "welcome_help_admin_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener('on_member_update')
    async def print_welcome_message(self, before: discord.Member, after: discord.Member):
        """
        Whenever a member takes a role, checks if the role is in the welcome list
        and if the member hasn't already been welcomed for this role. If not, welcome the user.
        """
        guild = before.guild
        if not utils.is_loaded(self.qualified_name.lower(), guild):
            return
        sql = "SELECT role_id, channel_id, message FROM welcome_config WHERE guild_id=? ORDER BY role_id ASC ;"
        response = database.fetch_all(sql, [guild.id])
        if not response:
            return
        for line in response:
            role_id, channel_id, message = line
            if not (not utils.member_has_role(before, role_id) and utils.member_has_role(after, role_id)):
                continue  # member didn't get role
            sql = "SELECT * FROM welcome_user WHERE role_id=? AND member_id=? AND channel_id=? AND guild_id=? ;"
            response = database.fetch_one(sql, [role_id, before.id, channel_id, guild.id])
            if response is not None:
                continue  # member was already welcomed for this role
            role = guild.get_role(role_id)
            channel = guild.get_channel(channel_id)
            if not role or not channel:
                log("Welcome::print_welcome_update", f"ERROR - Role or channel invalid in guild {guild.name}")
                continue
            message = utils.parse_random_string(message, member_name=before.mention)
            await channel.send(message)
            sql = "INSERT INTO welcome_user(role_id, channel_id, member_id, guild_id) VALUES (?, ?, ?, ?) ;"
            database.execute_order(sql, [role_id, channel_id, before.id, guild.id])


def setup(bot: commands.Bot):
    bot.add_cog(Welcome(bot))
