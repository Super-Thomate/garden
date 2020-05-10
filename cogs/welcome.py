import discord
from discord.ext import commands
from Utilitary.logger import log
from Utilitary import utils, database
import typing


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=['wc'])
    @commands.guild_only()
    @utils.require(['authorize', 'cog_loaded', 'not_banned'])
    async def welcome(self, ctx: commands.Context):
        """
        Print the valid subcommands for the cog
        """
        await ctx.send(utils.get_text(ctx.guild, "welcome_subcommands"))

    @welcome.command(name='addwelcome', aliases=['awc'])
    @commands.guild_only()
    @utils.require(['authorize', 'cog_loaded', 'not_banned'])
    async def add_welcome(self, ctx: commands.Context, role: discord.Role,
                          channel: typing.Optional[discord.TextChannel], *, message: str):
        """
        Add a public welcome for `role` in `channel` with `message`
        """
        if channel is None:  # Add a private welcome
            sql = "INSERT INTO welcome_private(role_id, message, guild_id) " \
                  "VALUES (:role_id, :message, :guild_id) " \
                  "ON CONFLICT(role_id, guild_id) DO " \
                  "UPDATE SET message=:message WHERE role_id=:role_id AND guild_id=:guild_id ;"
            success = database.execute_order(sql, {"role_id": role.id, "message": message, "guild_id": ctx.guild.id})
        else:  # Add a public welcome
            sql = "INSERT INTO welcome_public(role_id, channel_id, message, guild_id) " \
                  "VALUES (:role_id, :channel_id, :message, :guild_id) " \
                  "ON CONFLICT(role_id, guild_id) DO " \
                  "UPDATE SET message=:message, channel_id=:channel_id WHERE role_id=:role_id AND guild_id=:guild_id ;"
            success = database.execute_order(sql, {"role_id": role.id,
                                                   "channel_id": channel.id,
                                                   "message": message,
                                                   "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @welcome.command(name='removewelcome', aliases=['rwc'])
    @commands.guild_only()
    @utils.require(['authorize', 'cog_loaded', 'not_banned'])
    async def remove_welcome(self, ctx: commands.Context, role: discord.Role):
        """
        Remove the public and private welcome for `role`
        """
        sql = "DELETE FROM welcome_public WHERE role_id=? AND guild_id=? ;"
        success = database.execute_order(sql, [role.id, ctx.guild.id])
        sql2 = "DELETE FROM welcome_private WHERE role_id=? AND guild_id=? ;"
        success2 = database.execute_order(sql2, [role.id, ctx.guild.id])
        if success is True and success2 is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @welcome.command(name='reset')
    @commands.guild_only()
    @utils.require(['authorize', 'cog_loaded', 'not_banned'])
    async def reset_welcome(self, ctx: commands.Context, member: typing.Optional[discord.Member],
                            role: typing.Optional[discord.Role]):
        """
        Reset the welcome for `member` with `role`. If one of `role` and `member` isn't provided, the reset is wider
        """
        if member is None and role is None:
            await ctx.send(utils.get_text(ctx.guild, "welcome_reset_parameters").format(ctx.prefix))
            return
        sql = "DELETE FROM welcome_user WHERE guild_id=? "
        parameters = [ctx.guild.id]
        if member is not None:
            sql += "AND member_id=? "
            parameters.append(member.id)
        if role is not None:
            sql += "AND role_id=? "
            parameters.append(role.id)
        sql += ";"
        if member is None or role is None:
            formating = [member.mention] if member else [role.mention] if role else None
            if not await utils.ask_confirmation(ctx, "welcome_reset_confirm", formating=formating):
                return
        success = database.execute_order(sql, parameters)
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @welcome.command(name='info')
    @commands.guild_only()
    @utils.require(['authorize', 'cog_loaded', 'not_banned'])
    async def info(self, ctx: commands.Context):
        """
        Display the public and private welcome roles, channels and messages
        """
        # Get public welcomes
        sql = "SELECT role_id, channel_id, message FROM welcome_public WHERE guild_id=? ORDER BY role_id ;"
        public_welcome = ""
        response = database.fetch_all(sql, [ctx.guild.id])
        if response is not None:
            for line in response:
                role_id, channel_id, message = line
                role = ctx.guild.get_role(role_id)
                role = role.mention if role else utils.get_text(ctx.guild, "misc_invalid_role")
                channel = ctx.guild.get_channel(channel_id)
                channel = channel.mention if channel else utils.get_text(ctx.guild, "misc_invalid_channel") \
                    .format(channel_id)
                public_welcome += f"- {role} | {channel} | `{message}`\n"
        else:
            public_welcome += utils.get_text(ctx.guild, "welcome_info_none")

        # Get private welcomes
        sql = "SELECT role_id, message FROM welcome_private WHERE guild_id=? ORDER BY role_id ;"
        private_welcome = ""
        response = database.fetch_all(sql, [ctx.guild.id])
        if response is not None:
            for line in response:
                role_id, message = line
                role = ctx.guild.get_role(role_id)
                role = role.mention if role else utils.get_text(ctx.guild, "misc_invalid_role").format(role_id)
                private_welcome += f"- {role} | `{message}`\n"
        else:
            private_welcome += utils.get_text(ctx.guild, "welcome_info_none")

        embed = discord.Embed(title=utils.get_text(ctx.guild, "welcome_info_title"),
                              description=utils.get_text(ctx.guild, "welcome_info_description")
                              .format(public_welcome, private_welcome))
        await ctx.send(embed=embed)

    @welcome.command(name='help')
    @commands.guild_only()
    @utils.require(['authorize', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """
        Display the help for the `welcome` cog
        """
        embed = discord.Embed(title=utils.get_text(ctx.guild, "welcome_cog_name"),
                              description=utils.get_text(ctx.guild, "welcome_help_description").format(ctx.prefix))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "welcome_help_admin_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """
        Check if the member obtained a role that need to be welcomed
        then check if the member has not already been welcomed for this role then welcome the user
        """
        guild = after.guild
        if len(before.roles) >= len(after.roles):
            return  # Member didn't get a new role
        if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot):
            return
        # Python trick to get the role that was obtained
        role = next(list((set(before.roles) | set(after.roles)) - (set(before.roles) & set(after.roles))), None)

        # Check if member hasn't already been welcomed for this role
        sql = "SELECT * FROM welcome_user WHERE member_id=? AND role_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [after.id, role.id, role.guild.id])
        if response is not None:
            return

        # Get public welcomes
        sql = "SELECT channel_id, message FROM welcome_public WHERE role_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [role.id, role.guild.id])
        if response is not None:
            channel_id, message = response
            channel = role.guild.get_channel(channel_id)
            message = utils.parse_random_string(message, member_name=after.mention)
            if channel is not None:
                await channel.send(message)
            else:
                log("Welcome::on_member_update",
                    f"ERROR Welcome channel invalid for role {role.name} in guild {role.guild.name}")

        # Get public welcomes
        sql = "SELECT message FROM welcome_private WHERE role_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [role.id, role.guild.id])
        if response is not None:
            message = utils.parse_random_string(response[0], member_name=after.mention)
            await after.send(message)

        # Set member as welcomed for this role
        sql = "INSERT INTO welcome_user(role_id, member_id, guild_id) VALUES (?, ?, ?) ;"
        database.execute_order(sql, [role.id, after.id, role.guild.id])


def setup(bot: commands.Bot):
    bot.add_cog(Welcome(bot))
