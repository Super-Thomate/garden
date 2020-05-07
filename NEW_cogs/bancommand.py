import discord
from discord.ext import commands, tasks
from Utilitary import database, utils
from Utilitary.logger import log
import datetime


class Bancommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.delete_obsolete_bans.start()

    @commands.group(invoke_without_command=True, aliases=['bc'])
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def bancommand(self, ctx: commands.Context):
        """
        Display the availables sub-commands for the cog
        """
        await ctx.send(utils.get_text(ctx.guild, "bancommand_subcommands").format(ctx.prefix))

    @bancommand.command(name='bancommanduser', aliases=['bcu'])
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def ban_command_user(self, ctx: commands.Context, command: str, member: discord.Member, time: str = None):
        """
        Ban the member `member` from the command `command` for `time` time
        """
        if command not in utils.get_bot_commands(self.bot):
            await ctx.send(utils.get_text(ctx.guild, "bancommand_command_not_found").format(command))
            await ctx.message.add_reaction('❌')
            return
        delay = utils.parse_time(time) if time else None
        if time is not None and delay is None:
            await ctx.send(utils.get_text(ctx.guild, "misc_delay_invalid"))
            await ctx.message.add_reaction('❌')
            return
        ends_at = int(datetime.datetime.utcnow().timestamp()) + delay if delay else None
        sql = "INSERT INTO bancommand_banned_user(command, ends_at, member_id, guild_id) " \
              "VALUES (:command, :ends_at, :member_id, :guild_id)" \
              "ON CONFLICT(command, member_id, guild_id) DO UPDATE SET ends_at=:ends_at " \
              "WHERE command=:command AND member_id=:member_id AND guild_id=:guild_id"
        success = database.execute_order(sql, {"command": command,
                                               "ends_at": ends_at,
                                               "member_id": member.id,
                                               "guild_id": ctx.guild.id})
        if success is True:
            duration = time or utils.get_text(ctx.guild, "misc_permanent")
            await ctx.send(utils.get_text(ctx.guild, "bancommand_banned")
                           .format(member.mention, command, duration))
            await ctx.message.add_reaction('✅')
            log("Bancommand::ban_command_user",
                f"Member {member} is banned from using command {command} "
                f"for {time or 'permanent'} on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @bancommand.command(name='unbancommanduser', aliases=['ucu'])
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def unban_command_user(self, ctx: commands.Context, command: str, member: discord.Member):
        """
        Unban the member `member` from the command `command`
        """
        if command not in utils.get_bot_commands(self.bot):
            await ctx.send(utils.get_text(ctx.guild, "bancommand_command_not_found").format(command))
            await ctx.message.add_reaction('❌')
            return
        sql = "DELETE FROM bancommand_banned_user WHERE command=? AND member_id=? AND guild_id=? ;"
        success = database.execute_order(sql, [command, member.id, ctx.guild.id])
        if success is True:
            await ctx.send(utils.get_text(ctx.guild, "bancommand_unbanned").format(member.mention, command))
            await ctx.message.add_reaction('✅')
            log("Bancommand::unban_command_user",
                f"Member {member} can use command {command} again on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @bancommand.command(name='bancommandrole', aliases=['bcr'])
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def ban_command_role(self, ctx: commands.Context, command: str, role: discord.Role, time: str = None):
        """
        Ban the role `role` from the command `command` for `time` time
        """
        if command not in utils.get_bot_commands(self.bot):
            await ctx.send(utils.get_text(ctx.guild, "bancommand_command_not_found").format(command))
            await ctx.message.add_reaction('❌')
            return
        delay = utils.parse_time(time) if time else None
        if time is not None and delay is None:
            await ctx.send(utils.get_text(ctx.guild, "misc_delay_invalid"))
            await ctx.message.add_reaction('❌')
            return
        ends_at = int(datetime.datetime.utcnow().timestamp()) + delay if delay else None
        sql = "INSERT INTO bancommand_banned_role(command, ends_at, role_id, guild_id) " \
              "VALUES (:command, :ends_at, :role_id, :guild_id)" \
              "ON CONFLICT(command, role_id, guild_id) DO UPDATE SET ends_at=:ends_at " \
              "WHERE command=:command AND role_id=:role_id AND guild_id=:guild_id"
        success = database.execute_order(sql, {"command": command,
                                               "ends_at": ends_at,
                                               "role_id": role.id,
                                               "guild_id": ctx.guild.id})
        if success is True:
            duration = time or utils.get_text(ctx.guild, "misc_permanent")
            await ctx.send(utils.get_text(ctx.guild, "bancommand_banned")
                           .format(role.mention, command, duration))
            await ctx.message.add_reaction('✅')
            log("Bancommand::ban_command_role",
                f"Role {role} is banned from using command {command} "
                f"for {time or 'permanent'} on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @bancommand.command(name='unbancommandrole', aliases=['ucr'])
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def unban_command_role(self, ctx: commands.Context, command: str, role: discord.Role):
        """
        Unban the role `role` from the command `command`
        """
        if command not in utils.get_bot_commands(self.bot):
            await ctx.send(utils.get_text(ctx.guild, "bancommand_command_not_found").format(command))
            await ctx.message.add_reaction('❌')
            return
        sql = "DELETE FROM bancommand_banned_role WHERE command=? AND role_id=? AND guild_id=? ;"
        success = database.execute_order(sql, [command, role.id, ctx.guild.id])
        if success is True:
            await ctx.send(utils.get_text(ctx.guild, "bancommand_unbanned").format(role.mention, command))
            await ctx.message.add_reaction('✅')
            log("Bancommand::unban_command_role",
                f"Role {role} can use command {command} again on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @bancommand.group(invoke_without_command=True, name='userinfo')
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def display_user_info(self, ctx: commands.Context):
        """
        Display the banned users and the commands they are banned from
        """
        if ctx.subcommand_passed != 'userinfo':
            await ctx.send(utils.get_text(ctx.guild, "bancommand_userinfo_subcommands").format(ctx.prefix))
            return
        sql = "SELECT command, ends_at, member_id FROM bancommand_banned_user WHERE guild_id=? ORDER BY command ASC ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "bancommand_no_info"))
            return
        to_send = ""
        for command, timestamp, member_id in response:
            banned_member = ctx.guild.get_member(member_id)
            banned_member = banned_member.mention if banned_member \
                else utils.get_text(ctx.guild, "bancommand_member_not_found").format(member_id)
            ends_at = utils.parse_timestamp(timestamp, ctx.guild) if timestamp \
                else utils.get_text(ctx.guild, "misc_permanent")
            to_send += f"{banned_member} | {command} | _{ends_at}_\n"
        embed = discord.Embed(title=utils.get_text(ctx.guild, "bancommand_embed_title"),
                              description=to_send)
        await ctx.send(embed=embed)

    @display_user_info.command(name='user')
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def display_user_info_by_user(self, ctx: commands.Context, member: discord.Member):
        """
        Display the command that the member `member` is banned from
        """
        sql = "SELECT command, ends_at FROM bancommand_banned_user " \
              "WHERE guild_id=? AND member_id=? ORDER BY command ASC ;"
        response = database.fetch_all(sql, [ctx.guild.id, member.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "bancommand_no_info"))
            return
        to_send = ""
        for command, timestamp in response:
            ends_at = utils.parse_timestamp(timestamp, ctx.guild) if timestamp \
                else utils.get_text(ctx.guild, "misc_permanent")
            to_send += f"{command} | _{ends_at}_\n"
        embed = discord.Embed(title=utils.get_text(ctx.guild, "bancommand_info_user").format(member.display_name),
                              description=to_send)
        await ctx.send(embed=embed)

    @display_user_info.command(name='command')
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def display_user_info_by_command(self, ctx: commands.Context, command: str):
        """
        Display the user banned from the command `command`
        """
        if command not in utils.get_bot_commands(self.bot):
            await ctx.send(utils.get_text(ctx.guild, "bancommand_command_not_found").format(command))
            await ctx.message.add_reaction('❌')
            return
        sql = "SELECT member_id, ends_at FROM bancommand_banned_user " \
              "WHERE guild_id=? AND command=? ORDER BY member_id ASC ;"
        response = database.fetch_all(sql, [ctx.guild.id, command])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "bancommand_no_info"))
            return
        to_send = ""
        for member_id, timestamp in response:
            banned_member = ctx.guild.get_member(member_id)
            banned_member = banned_member.mention if banned_member \
                else utils.get_text(ctx.guild, "bancommand_member_not_found").format(member_id)
            ends_at = utils.parse_timestamp(timestamp, ctx.guild) if timestamp \
                else utils.get_text(ctx.guild, "misc_permanent")
            to_send += f"{banned_member} | _{ends_at}_\n"
        embed = discord.Embed(title=utils.get_text(ctx.guild, "bancommand_info_command_user").format(command),
                              description=to_send)
        await ctx.send(embed=embed)

    @bancommand.group(invoke_without_command=True, name='roleinfo')
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def display_role_info(self, ctx: commands.Context):
        """
        Display the banned roles and the command they are banned from
        """
        if ctx.subcommand_passed != 'roleinfo':
            await ctx.send(utils.get_text(ctx.guild, "bancommand_roleinfo_subcommands").format(ctx.prefix))
            return
        sql = "SELECT command, ends_at, role_id FROM bancommand_banned_role WHERE guild_id=? ORDER BY role_id ASC ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "bancommand_no_info"))
            return
        to_send = ""
        for command, timestamp, role_id in response:
            banned_role = ctx.guild.get_role(role_id)
            banned_role = banned_role.mention if banned_role \
                else utils.get_text(ctx.guild, "bancommand_role_not_found").format(role_id)
            ends_at = utils.parse_timestamp(timestamp, ctx.guild) if timestamp \
                else utils.get_text(ctx.guild, "misc_permanent")
            to_send += f"{banned_role} | {command} | _{ends_at}_\n"
        embed = discord.Embed(title=utils.get_text(ctx.guild, "bancommand_embed_title"),
                              description=to_send)
        await ctx.send(embed=embed)

    @display_role_info.command(name='role')
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def display_role_info_by_role(self, ctx: commands.Context, role: discord.Role):
        """
        Display the command that the role `role` id banned from
        """
        sql = "SELECT command, ends_at FROM bancommand_banned_role WHERE guild_id=? AND role_id=? " \
              "ORDER BY command ASC ;"
        response = database.fetch_all(sql, [ctx.guild.id, role.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "bancommand_no_info"))
            return
        to_send = ""
        for command, timestamp in response:
            ends_at = utils.parse_timestamp(timestamp, ctx.guild) if timestamp \
                else utils.get_text(ctx.guild, "misc_permanent")
            to_send += f"{command} | _{ends_at}_\n"
        embed = discord.Embed(title=utils.get_text(ctx.guild, "bancommand_info_role").format(role.name),
                              description=to_send)
        await ctx.send(embed=embed)

    @display_role_info.command(name='command')
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def display_role_info_by_command(self, ctx: commands.Context, command: str):
        """
        Display the role that are banned from the command `command`
        """
        if command not in utils.get_bot_commands(self.bot):
            await ctx.send(utils.get_text(ctx.guild, "bancommand_command_not_found").format(command))
            await ctx.message.add_reaction('❌')
            return
        sql = "SELECT role_id, ends_at FROM bancommand_banned_role " \
              "WHERE guild_id=? AND command=? ORDER BY role_id ASC ;"
        response = database.fetch_all(sql, [ctx.guild.id, command])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "bancommand_no_info"))
            return
        to_send = ""
        for role_id, timestamp in response:
            banned_role = ctx.guild.get_role(role_id)
            banned_role = banned_role.mention if banned_role \
                else utils.get_text(ctx.guild, "bancommand_role_not_found").format(role_id)
            ends_at = utils.parse_timestamp(timestamp, ctx.guild) if timestamp \
                else utils.get_text(ctx.guild, "misc_permanent")
            to_send += f"{banned_role} | _{ends_at}_\n"
        embed = discord.Embed(title=utils.get_text(ctx.guild, "bancommand_info_command_role").format(command),
                              description=to_send)
        await ctx.send(embed=embed)

    @bancommand.command(name='help')
    @commands.guild_only()
    @utils.require(['cog_loaded', 'authorized', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """
        Display the help for the `bancommand` cog
        """
        embed = discord.Embed(title=utils.get_text(ctx.guild, "bancommand_cog_name"),
                              description=utils.get_text(ctx.guild, "bancommand_help_description"))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "bancommand_help_admin_command").format(ctx.prefix),
                        inline=False)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "bancommand_help_admin_command_2").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @tasks.loop(hours=1.0)
    async def delete_obsolete_bans(self):
        for guild in self.bot.guilds:
            if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot):
                continue
            log("Bancommand::delete_obsolete_bans", f"Deleting obsolete bans in guild {guild} ({guild.id})")
            now = int(datetime.datetime.utcnow().timestamp())
            sql_user = "DELETE FROM bancommand_banned_user WHERE ends_at<? AND guild_id=? ;"
            database.execute_order(sql_user, [now, guild.id])
            sql_role = "DELETE FROM bancommand_banned_role WHERE ends_at<? AND guild_id=? ;"
            database.execute_order(sql_role, [now, guild.id])

    def cog_unload(self):
        self.delete_obsolete_bans.cancel()


def setup(bot: commands.Bot):
    bot.add_cog(Bancommand(bot))
