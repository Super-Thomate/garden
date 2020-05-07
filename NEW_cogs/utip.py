import discord
from discord.ext import commands, tasks
from Utilitary import database, utils
from Utilitary.logger import log
import asyncio
import datetime


class Utip(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.remove_utip_role_loop.start()

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.require(['cog_loaded', 'not_banned'])
    async def utip(self, ctx: commands.Context):
        """
        Ask the member for a proof that they watched all the ads they could on utip.
        Expect a screenshot given by URL or bu direct upload
        """
        if ctx.subcommand_passed is not None and utils.is_authorized(ctx.author):
            await ctx.send(utils.get_text(ctx.guild, "birthday_subcommands").format(ctx.prefix))
            return
        # Check if all the field are set and that the demands channel is valid
        sql = "SELECT mod_channel_id, log_channel_id, role_id, delay FROM utip_config WHERE guild_id=? ;"
        response = database.fetch_one(sql, [ctx.guild.id])
        if response is None or None in response:
            await ctx.send(utils.get_text(ctx.guild, "utip_field_not_set"))
            await ctx.message.add_reaction('❌')
            return
        mod_channel_id, log_channel_id, role_id, delay = response
        mod_channel = ctx.guild.get_channel(mod_channel_id)
        role = ctx.guild.get_role(role_id)
        log_channel = ctx.guild.get_channel(log_channel_id)
        if not mod_channel or not role or not log_channel:
            await ctx.send(utils.get_text(ctx.guild, "utip_channel_or_role_invalid"))
            await ctx.message.add_reaction('❌')
            return

        # Ask user for a screenshot, exit after 60s of waiting
        ask_message = await ctx.send(utils.get_text(ctx.guild, "utip_ask_screenshot"))
        try:
            member_answer = await self.bot.wait_for('message',
                                                    check=lambda m: m.channel == ctx.channel and m.author == ctx.author,
                                                    timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send(utils.get_text(ctx.guild, "utip_timeout"), delete_after=5.0)
            await utils.delete_messages([ctx.message, ask_message])
            return
        is_url_valid = await utils.is_image_url(member_answer.content)
        is_attachment = len(member_answer.attachments) > 0
        if is_attachment is False and is_url_valid is False:
            await ctx.send(utils.get_text(ctx.guild, "utip_image_invalid"), delete_after=5.0)
            await utils.delete_messages([ctx.message, ask_message, member_answer])
            return
        image_url = member_answer.attachments[0].proxy_url if is_attachment else member_answer.content

        # Send confirmation message to user
        await ctx.author.send(utils.get_text(ctx.guild, "utip_demand_pending").format(role.name))

        # Send demand to utip demand channel
        embed = discord.Embed(title=utils.get_text(ctx.guild, "utip_demand_title").format(ctx.author),
                              description=utils.get_text(ctx.guild, "utip_demand_description")
                              .format(ctx.author, role.name, image_url))
        embed.set_image(url=image_url)
        demand_message = await mod_channel.send(embed=embed)
        await demand_message.add_reaction('👍')
        await demand_message.add_reaction('👎')

        # Add dedmand to pending list
        sql = "INSERT INTO utip_pending(member_id, message_id, guild_id) VALUES (?, ?, ?)"
        success = database.execute_order(sql, [ctx.author.id, demand_message.id, ctx.guild.id])
        if success is not True:
            await ctx.message.add_reaction('💀')

        await utils.delete_messages([ctx.message, ask_message, member_answer], delay=5)
        await log_channel.send(
            embed=discord.Embed(title="UTIP DEMAND", description=f"{ctx.author.mention} : {image_url}"))

    @utip.command(name='setchannel', aliases=['sc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_utip_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Set the channel where the utip demand are displayed and treated
        """
        sql = "INSERT INTO utip_config(mod_channel_id, guild_id) VALUES (:mod_channel_id, :guild_id) " \
              "ON CONFLICT(guild_id) DO UPDATE SET mod_channel_id=:mod_channel_id WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"mod_channel_id": channel.id, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
            log("Utip::set_utip_channel", f"Utip channel set to {channel.name} on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @utip.command(name='setlogchannel', aliases=['slc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_utip_log(self, ctx: commands.Context, log_channel: discord.TextChannel):
        """
        Set the channel where the utip demands are logged
        """
        sql = "INSERT INTO utip_config(log_channel_id, guild_id) VALUES (:log_channel_id, :guild_id) " \
              "ON CONFLICT(guild_id) DO UPDATE SET log_channel_id=:log_channel_id WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"log_channel_id": log_channel.id, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
            log("Utip::set_utip_channel", f"Utip log set to {log_channel.name} on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @utip.command(name='setrole', aliases=['sr'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_utip_role(self, ctx: commands.Context, role: discord.Role):
        """
        Set the role given after a demand is accepted
        """
        sql = "INSERT INTO utip_config(role_id, guild_id) VALUES (:role_id, :guild_id) " \
              "ON CONFLICT(guild_id) DO UPDATE SET role_id=:role_id WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"role_id": role.id, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
            log("Utip::set_utip_channel", f"Utip role set to {role.name} on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @utip.command(name='setdelay', aliases=['sd'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_utip_delay(self, ctx: commands.Context, delay: str):
        """
        Set the delay before the utip role is be removed
        """
        timestamp = utils.parse_time(delay)
        if timestamp is None:
            await ctx.send(utils.get_text(ctx.guild, "misc_delay_invalid"))
            await ctx.message.add_reaction('❌')
            return
        sql = "INSERT INTO utip_config(delay, guild_id) VALUES (:delay, :guild_id) " \
              "ON CONFLICT(guild_id) DO UPDATE SET delay=:delay WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"delay": timestamp, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
            log("Utip::set_utip_channel", f"Utip delay set to '{delay}' on guild {ctx.guild.name}")
        else:
            await ctx.message.add_reaction('💀')

    @utip.command(name='info')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def info(self, ctx: commands.Context):
        """
        Display information about the utip cog configuration
        and the status of the members who received the utip role
        """
        not_set = utils.get_text(ctx.guild, "misc_not_set")
        sql = "SELECT mod_channel_id, log_channel_id, role_id, delay FROM utip_config WHERE guild_id=? ;"
        response = database.fetch_one(sql, [ctx.guild.id])
        if response is None:
            mod_channel = log_channel = role = delay = not_set
        else:
            mod_channel = ctx.guild.get_channel(response[0])
            mod_channel = mod_channel.mention if mod_channel else not_set
            log_channel = ctx.guild.get_channel(response[1])
            log_channel = log_channel.mention if log_channel else not_set
            role = ctx.guild.get_role(response[2])
            role = role.mention if role else not_set
            delay = utils.parse_delay(response[3], ctx.guild) if response[3] else not_set

        sql = "SELECT member_id, ends_at FROM utip_timer WHERE guild_id=? ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        if not response:
            utip_members = utils.get_text(ctx.guild, "utip_info_members_none")
        else:
            utip_members = ""
            for line in response:
                member = ctx.guild.get_member(line[0])
                member = member.mention if member else f"(Left server) <@{line[0]}>"
                role_end = utils.parse_timestamp(line[1], ctx.guild)
                utip_members += f"{member} | _{role_end}_\n"

        embed = discord.Embed(title=utils.get_text(ctx.guild, "utip_cog_name"))
        embed.add_field(name=utils.get_text(ctx.guild, "utip_info_config_title"),
                        value=utils.get_text(ctx.guild, "utip_info_config_text")
                        .format(mod_channel, log_channel, role, delay),
                        inline=False)
        embed.add_field(name=utils.get_text(ctx.guild, "utip_info_member_title"), value=utip_members, inline=False)
        await ctx.send(embed=embed)

    @utip.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """
        Display the help for the `utip` cog
        """
        embed = discord.Embed(title=utils.get_text(ctx.guild, "utip_cog_name"),
                              description=utils.get_text(ctx.guild, "utip_help_description").format(ctx.prefix))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_user_command"),
                        value=utils.get_text(ctx.guild, "utip_help_user_command").format(ctx.prefix),
                        inline=False)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "utip_help_admin_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @staticmethod
    async def give_utip_role(member: discord.Member, role: discord.Role, delay: int):
        """
        Give the member the role `role` and write it in the database.

        :param member: Member | The member to give role
        :param role:  Role | The role to give
        :param delay: int | The time before the role should be removed
        """
        sql = "INSERT INTO utip_timer(member_id, ends_at, guild_id) VALUES (:member_id, :ends_at, :guild_id) " \
              "ON CONFLICT(member_id, guild_id) DO " \
              "UPDATE SET ends_at=:ends_at WHERE member_id=:member_id AND guild_id=:guild_id ;"
        ends_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)
        ends_at = int(ends_at.timestamp())
        success = database.execute_order(sql, {"member_id": member.id,
                                               "ends_at": ends_at,
                                               "guild_id": member.guild.id})
        if success is True:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Check if the reacted message is a Utip demand and give utip role to member if demand is accepted
        """
        if not payload.guild_id:
            return
        if not str(payload.emoji) in ('👍', '👎'):
            return
        guild = self.bot.get_guild(payload.guild_id)
        author = guild.get_member(payload.user_id)
        if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot) \
                or author.bot \
                or not utils.is_authorized(author):
            return

        sql = "SELECT member_id FROM utip_pending WHERE message_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [payload.message_id, payload.guild_id])
        if response is None:
            return
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        utip_member = guild.get_member(response[0])
        sql = "SELECT role_id, delay FROM utip_config WHERE guild_id=? ;"
        response = database.fetch_one(sql, [payload.guild_id])
        role = guild.get_role(response[0]) if response else None
        delay = response[1] if response else None
        if not response or not role or not delay:
            await channel.send(utils.get_text(guild, "utip_role_or_delay_invalid"))
            return
        embed = message.embeds[0]
        if str(payload.emoji) == '👍':
            await self.give_utip_role(utip_member, role, delay)
            embed_footer_key = "utip_demand_accepted"
            demand_answer = utils.get_text(guild, "utip_demand_accepted_message") \
                .format(role.name, utils.delay_to_date(delay, guild))
        else:
            embed_footer_key = "utip_demand_refused"
            demand_answer = utils.get_text(guild, "utip_demand_refused_message")

        sql = "DELETE FROM utip_pending WHERE message_id=? AND guild_id=? ;"
        database.execute_order(sql, [payload.message_id, payload.guild_id])
        embed.set_footer(text=utils.get_text(guild, embed_footer_key).format(author))
        await message.edit(embed=embed)
        await utip_member.send(demand_answer)

    @tasks.loop(hours=1.0)
    async def remove_utip_role_loop(self):
        """
        Every hour, look for members who's Utip role is outdated, remove it and send them a message in MP
        """
        now = int(datetime.datetime.utcnow().timestamp())
        for guild in self.bot.guilds:
            if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot):
                continue
            sql = "SELECT role_id FROM utip_config WHERE guild_id=? ;"
            response = database.fetch_one(sql, [guild.id])
            utip_role = guild.get_role(response[0]) if response else None
            if not response or not utip_role:
                log("Utip::remove_utip_role_loop",
                    f"WARNING - No Utip role set or invalid role for guild {guild} ({guild.id})")
            sql = "SELECT member_id FROM utip_timer WHERE ends_at<? AND guild_id=? ;"
            response = database.fetch_all(sql, [now, guild.id])
            if response is None:
                continue
            for line in response:
                member = guild.get_member(line[0])
                if member is None:
                    continue
                log("Utip::remove_utip_role_loop", f"Removing utip role for member {member} on guild {guild} ({guild.id})")
                await member.remove_roles(utip_role)
                await member.send(utils.get_text(guild, "utip_lost_role").format(utip_role.name))
            sql = "DELETE FROM utip_timer WHERE ends_at<? AND guild_id=? ;"
            database.execute_order(sql, [now, guild.id])

    def cog_unload(self):
        """
        Called when the cog is unloaded.
        Stop the `remove_utip_role_loop` task
        """
        self.remove_utip_role_loop.cancel()


def setup(bot: commands.Bot):
    bot.add_cog(Utip(bot))
