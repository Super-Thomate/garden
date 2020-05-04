import discord
from discord.ext import commands, tasks
import datetime
from Utilitary.logger import log
from Utilitary import database, utils
import asyncio
import typing


class Birthday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.print_birthday_loop.start()

    @staticmethod
    def validate_date(date: str) -> typing.Optional[str]:
        """
        Check if `date` is a valid date in the format `day/month`

        :param date: str | The date to check
        :return: str or None | The date in 2-digits format or None if the date is invalid
        """
        if date in ('29/02', '29/2'):
            return "29/02"
        try:
            date_object = datetime.datetime.strptime(date, "%d/%m")
            return date_object.strftime("%d/%m")
        except ValueError:
            return None

    @commands.group(invoke_without_command=True, aliases=['bd'])
    @commands.guild_only()
    @utils.require(['cog_loaded', 'not_banned'])
    async def birthday(self, ctx: commands.Context):
        """
        Register a member's birthday in the database. Allow `d/m` format only
        """
        if ctx.subcommand_passed is not None and utils.is_authorized(ctx.author):
            await ctx.send(utils.get_text(ctx.guild, "birthday_subcommands").format(ctx.prefix))
            return
        # Check if user is already registered
        sql = "SELECT * FROM birthday_user WHERE member_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [ctx.author.id, ctx.guild.id])
        if response is not None:
            await ctx.send(utils.get_text(ctx.guild, "birthday_already_registered"), delete_after=5.0)
            await ctx.message.delete(delay=5)
            return
        # Ask the member their birthday date, timeout after 60s
        ask_message = await ctx.send(utils.get_text(ctx.guild, "birthday_ask_user"))
        try:
            member_answer = await self.bot.wait_for('message',
                                                    check=lambda m: m.channel == ctx.channel and m.author == ctx.author,
                                                    timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send(utils.get_text(ctx.guild, "utip_timeout"), delete_after=5.0)
            await utils.delete_messages([ctx.message, ask_message], delay=5)
            return
        # Check if date is valid
        date = self.validate_date(member_answer.content)
        if date is None:
            await ctx.send(utils.get_text(ctx.guild, "birthday_format_invalid"), delete_after=5.0)
            await utils.delete_messages([ctx.message, member_answer, ask_message], delay=5)
            return
        # Insert birthday in database
        sql = "INSERT INTO birthday_user(member_id, birthday, guild_id) VALUES (?, ?, ?) ;"
        success = database.execute_order(sql, [ctx.author.id, date, ctx.guild.id])
        if not success:
            await ctx.message.add_reaction('💀')
            await ctx.send(utils.get_text(ctx.guild, "misc_error_user"))
            log("Birthday::birthday", f"ERROR trying to register birthday in guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('✅')
            await ctx.send(utils.get_text(ctx.guild, "birthday_registered")
                           .format(ctx.author.mention), delete_after=5.0)
            await utils.delete_messages([ctx.message, ask_message, member_answer], delay=5)

    @birthday.command(name='setchannel', aliases=['sc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_birthday_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Set the channel where the birthdays are displayed
        """
        sql = "INSERT INTO birthday_config(bd_channel_id, guild_id) VALUES (:bd_channel_id, :guild_id) " \
              "ON CONFLICT(guild_id) DO UPDATE SET bd_channel_id=:bd_channel_id WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"bd_channel_id": channel.id, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
            log("Birthday::set_birthday_channel", f"Birthday channel set to {channel.name} on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @birthday.command(name='setmessage', aliases=['sm'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_birthday_message(self, ctx: commands.Context, *, message: str):
        """
        Set the birthday message
        """
        sql = "INSERT INTO birthday_config(message, guild_id) VALUES (:message, :guild_id) " \
              "ON CONFLICT(guild_id) DO UPDATE SET message=:message WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"message": message, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
            log("Birthday::set_birthday_message", f"Birthday message set to `{message}` on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @birthday.command(name='settiming', aliases=['st'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_birthday_timing(self, ctx: commands.Context, timing: int):
        """
        Set the birthday timing
        """
        if not 0 <= timing <= 23:
            await ctx.message.add_reaction('❌')
            return
        sql = "INSERT INTO birthday_config(timing, guild_id) VALUES (:timing, :guild_id) " \
              "ON CONFLICT(guild_id) DO UPDATE SET timing=:timing WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"timing": timing, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
            log("Birthday::set_birthday_message", f"Birthday timing set to {timing} on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @birthday.command(name='resetbirthday', aliases=['rb'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def reset_birthday(self, ctx: commands.Context, member: discord.Member = None):
        """
        Delete a member's birthday from database
        """
        if member is None:
            member = ctx.author
        sql = "DELETE FROM birthday_user WHERE member_id=? AND guild_id=? ;"
        success = database.execute_order(sql, [member.id, ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
            log("Birthday::reset_birthday", f"Reset birthday of member {member} in guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @birthday.command(name='info')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def info(self, ctx: commands.Context):
        """
        Display the birthday cog configuration
        """
        sql = "SELECT bd_channel_id, message, timing FROM birthday_config WHERE guild_id=? ;"
        response = database.fetch_one(sql, [ctx.guild.id])
        not_set = utils.get_text(ctx.guild, "misc_not_set")

        channel = ctx.guild.get_channel(response[0]) if response else None
        channel = channel.mention if channel else not_set
        message = f"`{response[1]}`" if response and response[1] \
            else f"`{utils.get_text(ctx.guild, 'birthday_default_message').format('$member')}` (default)"
        timing = response[2] if response and response[2] else None
        timing = f"`{timing}h (CET)`" if timing else "`12AM (CET)` (default)"
        embed = discord.Embed(title=utils.get_text(ctx.guild, "birthday_info_title"),
                              description=utils.get_text(ctx.guild, "birthday_info_text")
                              .format(channel, message, timing))
        await ctx.send(embed=embed)

    @birthday.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """
        Display the help for the `birthday` cog
        """
        embed = discord.Embed(title=utils.get_text(ctx.guild, "birthday_cog_name"),
                              description=utils.get_text(ctx.guild, "birthday_help_description").format(ctx.prefix))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_user_command"),
                        value=utils.get_text(ctx.guild, "birthday_help_user_command").format(ctx.prefix),
                        inline=False)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "birthday_help_admin_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @tasks.loop(minutes=1.0)
    async def print_birthday_loop(self):
        """
        Every minute. Check the timing is right to print birthdays and do so
        """
        now = datetime.datetime.now()
        date = now.strftime("%d/%m")
        for guild in self.bot.guilds:
            if not utils.is_loaded(self.qualified_name.lower(), guild):
                continue
            # Get birthday config for guild
            sql = "SELECT bd_channel_id, message, timing FROM birthday_config WHERE guild_id=? ;"
            response = database.fetch_one(sql, [guild.id])
            if not response:
                log("Birthday::print_birthday_loop", f"WARNING birthday config not set in guild {guild.name}")
                continue
            channel_id, message, timing = response
            channel = guild.get_channel(channel_id)
            if channel is None:
                log("Birthday::print_birthday_loop",
                    f"WARNING birthday channel not set or invalid in guild {guild.name}")
                continue
            if timing is not None and now.hour < timing:
                continue
            # Get member whose birthday is today
            sql = "SELECT member_id FROM birthday_user " \
                  "WHERE birthday=? AND (last_year!=? or last_year is NULL) AND guild_id=? ;"
            response = database.fetch_all(sql, [date, now.year, guild.id])
            if response is None:
                continue
            for line in response:
                member = guild.get_member(line[0])
                if member is None:
                    continue
                birthday_message = utils.parse_random_string(message, member_name=member.mention) if message \
                    else utils.get_text(guild, "birthday_default_message").format(member.mention)
                await channel.send(birthday_message)
                log("Birthday::print_birthday_loop", f"Wishing happy birthday to {member} in guild {guild.name}")
                sql = "UPDATE birthday_user SET last_year=? WHERE member_id=? AND guild_id=?"
                success = database.execute_order(sql, [now.year, member.id, guild.id])
                if not success:
                    log("Birthday::print_birthday_loop",
                        f"ERROR trying to update birthday year for member {member} in guild {guild.name}")

    def cog_unload(self):
        """
        Called when the cog is unloaded.
        Stop the `print_birthday_loop` task
        """
        self.print_birthday_loop.cancel()


def setup(bot: commands.Bot):
    bot.add_cog(Birthday(bot))
