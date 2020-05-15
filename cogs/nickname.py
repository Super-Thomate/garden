import datetime
import typing

import discord
from discord.ext import commands, tasks

from Utilitary import utils, database
from Utilitary.logger import log


class Nickname(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_next.start()

    @staticmethod
    async def rename_member(member: discord.Member, new_nickname: str, hard_rename: bool = False) -> bool:
        """Rename the member `member`. if `hard_rename` is True, add the renaming in the DB.

        Args:
            member: The member to rename.
            new_nickname: The member's new nickname.
            hard_rename: Wether or not the renaming shall be added to the DB.

        Returns:
            True if the SQL query was successful, else False.
        """
        await member.edit(nick=new_nickname)
        if hard_rename is True:
            sql = "INSERT INTO nickname_user(member_id, nickname, last_change, guild_id) " \
                  "VALUES (:member_id, :nickname, :last_change, :guild_id) " \
                  "ON CONFLICT(member_id, guild_id) DO " \
                  "UPDATE SET nickname=:nickname, last_change=:last_change " \
                  "WHERE member_id=:member_id AND guild_id=:guild_id ;"
            success = database.execute_order(sql, {"member_id": member.id,
                                                   "nickname": new_nickname,
                                                   "last_change": int(datetime.datetime.utcnow().timestamp()),
                                                   "guild_id": member.guild.id})
            return success
        return True

    @staticmethod
    def member_can_change_nickname(member: discord.Member) -> typing.Tuple[bool, typing.Optional[str]]:
        """Check if the member can change their nickname.

        If the member cannot, returns a string (`delay`) showing time left before the member can change nickname again.

        Args:
            member: The member to be checked.

        Returns:
            Tuple[bool, str]: (True, None) if the member can change nickname, (False, `delay`) if they can't.
        """
        sql = "SELECT nickname_delay FROM nickname_table WHERE guild_id=? ;"
        response = database.fetch_one(sql, [member.guild.id])
        delay = response[0] if response and response[0] else 1209600  # default 2 weeks

        sql = "SELECT last_change FROM nickname_user WHERE member_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [member.id, member.guild.id])
        last_change = response[0] if response else None

        now = int(datetime.datetime.utcnow().timestamp())
        if last_change is None or now > last_change + delay:
            return True, None
        else:
            return False, utils.timestamp_to_string(last_change + delay, member.guild)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.require(['not_banned', 'cog_loaded'])
    async def nickname(self, ctx: commands.Context, *, nickname: str = None):
        """Change the member's nickname."""
        if nickname is None:
            await ctx.send(utils.get_text(ctx.guild, "nickname_empty"))
            await ctx.message.add_reaction('❌')
            return

        member_can_change, until = self.member_can_change_nickname(ctx.author)
        if not member_can_change:
            await ctx.send(utils.get_text(ctx.guild, "nickname_changed_recently").format(until.lower()))
            await ctx.message.add_reaction('❌')
            return

        sql = "DELETE FROM nickname_warning WHERE member_id=? AND guild_id=? ;"
        database.execute_order(sql, [ctx.author.id, ctx.guild.id])

        try:
            success = await self.rename_member(ctx.author, nickname, hard_rename=True)
            await ctx.message.add_reaction('✅' if success else '💀')
        except discord.Forbidden:
            log("Nickname::nickname", f"Could not set {ctx.author}'s nickname to {nickname} on guild {ctx.guild}")
        except discord.HTTPException:
            await ctx.message.add_reaction('❌')
            await ctx.send(utils.get_text(ctx.guild, "nickname_too_long"))

    @nickname.command(name='reset')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned', 'cog_loaded'])
    async def reset_nickname(self, ctx: commands.Context, member: discord.Member = None):
        """Reset the nickname delay for the member."""
        if member is None:
            member = ctx.author
        sql = "UPDATE nickname_user SET last_change=? WHERE member_id=? AND guild_id=? ;"
        success = database.execute_order(sql, [None, member.id, ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @nickname.command(name='setdelay', aliases=['sd'])
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned', 'cog_loaded'])
    async def set_delay(self, ctx: commands.Context, delay: utils.DurationConverter):
        """Set the delay before a member can change nickname again."""
        sql = "INSERT INTO nickname_table(nickname_delay, guild_id) VALUES (:delay, :guild_id) " \
              "ON CONFLICT(guild_id) DO " \
              "UPDATE SET nickname_delay=:delay WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"delay": delay,
                                               "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @nickname.command(name='checknickname', aliases=['cn'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def check_nickname(self, ctx: commands.Context, member: discord.Member = None):
        """Display the member's nickname if they have one."""
        if member is None:
            member = ctx.author
        if member.nick:
            await ctx.send(utils.get_text(ctx.guild, "nickname_member_has_nickname").format(str(member), member.nick))
        else:
            await ctx.send(utils.get_text(ctx.guild, "nickname_member_has_no_nickname").format(str(member)))

    @nickname.command(name='settrollnickname', aliases=['stn'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_warn_nickname(self, ctx: commands.Context, *, warn_nick: str):
        """Set the 'troll' nickames."""
        sql = "INSERT INTO nickname_table(warning_nickname, guild_id) VALUES (:warn_nick, :guild_id) " \
              "ON CONFLICT(guild_id) DO " \
              "UPDATE SET warning_nickname=:warn_nick WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"warn_nick": warn_nick,
                                               "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @nickname.command(name='info')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned', 'cog_loaded'])
    async def info(self, ctx: commands.Context):
        """Display the delay and the 'troll' nicknames."""
        sql = "SELECT nickname_delay, warning_nickname FROM nickname_table WHERE guild_id=? ;"
        response = database.fetch_one(sql, [ctx.guild.id])
        not_set = utils.get_text(ctx.guild, "misc_not_set")
        if not response:
            delay = warn_nick = not_set
        else:
            delay = utils.duration_to_string(response[0], ctx.guild) if response[0] else not_set
            warn_nick = response[1] or utils.get_text(ctx.guild, "nickname_warned_nickname") + ' (default)'
        await ctx.send(utils.get_text(ctx.guild, "nickname_info").format(delay, warn_nick))

    @nickname.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'not_banned', 'cog_loaded'])
    async def help(self, ctx: commands.Context):
        """Display the help for the `nickname` cog."""
        embed = discord.Embed(title=utils.get_text(ctx.guild, "nickname_cog_name"),
                              description=utils.get_text(ctx.guild, "nickname_help_description").format(ctx.prefix))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_user_command"),
                        value=utils.get_text(ctx.guild, "nickname_help_user_command").format(ctx.prefix),
                        inline=False)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "nickname_help_admin_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='next')
    @commands.guild_only()
    @utils.require(['not_banned', 'cog_loaded'])
    async def next(self, ctx: commands.Context):
        """Display how much time is left before the member can change nickname again."""
        member_can_change, until = self.member_can_change_nickname(ctx.author)
        if member_can_change:
            sql = "INSERT INTO nickname_warning(member_id, warn_at, warned, guild_id) " \
                  f"VALUES (:member_id, :warn_at, {False}, :guild_id) " \
                  "ON CONFLICT(member_id, guild_id) DO " \
                  f"UPDATE SET warn_at=:warn_at, warned={True} WHERE member_id=:member_id AND guild_id=:guild_id ;"
            warn_at = int(datetime.datetime.utcnow().timestamp()) + 900  # Wait 15 minutes
            database.execute_order(sql, {"member_id": ctx.author.id,
                                         "warn_at": warn_at,
                                         "guild_id": ctx.guild.id})
            await ctx.send(utils.get_text(ctx.guild, "nickname_can_change"))
        else:
            await ctx.send(utils.get_text(ctx.guild, "nickname_cannot_change").format(until.lower()))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """If a member quit and re-join the guild, re-apply their old nickname."""
        sql = "SELECT nickname FROM nickname_user WHERE member_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [member.id, member.guild.id])
        if response is None:
            return
        try:
            await member.edit(nick=response[0])
        except discord.Forbidden or Exception:
            log("Nickname::on_member_join", f"Could not edit {member}'s nickname on guild {member.guild}")

    @tasks.loop(minutes=1.0)
    async def check_next(self):
        """Every minute, check if a member has to warned about for abusively the `next` command.

        By default, soft-rename the member. If they've already been warned hard rename them.
        """
        now = int(datetime.datetime.utcnow().timestamp())
        for guild in self.bot.guilds:
            if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot):
                continue
            sql = "SELECT member_id, warned FROM nickname_warning WHERE warn_at<? AND guild_id=? ;"
            response = database.fetch_one(sql, [now, guild.id])
            if response is None:
                continue
            member_id, hard_rename = response
            hard_rename = bool(hard_rename)
            member = guild.get_member(member_id)
            default_nickname = utils.get_text(guild, "nickname_warned_nickname")

            if hard_rename is False:
                nickname = default_nickname
            else:
                sql = "SELECT warning_nickname FROM nickname_table WHERE guild_id=? ;"
                response = database.fetch_one(sql, [guild.id])
                nickname = utils.parse_random_string(response[0]) if response and response[0] else default_nickname
            try:
                await self.rename_member(member, nickname, hard_rename=hard_rename)
            except Exception as e:
                log("Nickname::check_next", f"[{type(e).__name__} - {e}] "
                                            f"Could not set {member}'s nickname to "
                                            f"`{default_nickname}` on guild {guild}")
            finally:
                sql = "INSERT INTO nickname_warning(member_id, warn_at, warned, guild_id) " \
                      "VALUES (:member_id, :warn_at, :warned, :guild_id) " \
                      "ON CONFLICT(member_id, guild_id) DO " \
                      "UPDATE SET warn_at=:warn_at, warned=:warned " \
                      "WHERE member_id=:member_id AND guild_id=:guild_id ;"
                database.execute_order(sql, {"member_id": member.id,
                                             "warn_at": None,
                                             "warned": True,
                                             "guild_id": guild.id})

    def cog_unload(self):
        """Called when the cog is unloaded. Stop the `check_next` task"""
        self.check_next.cancel()


def setup(bot: commands.Bot):
    bot.add_cog(Nickname(bot))
