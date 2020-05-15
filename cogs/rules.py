import datetime
import typing

import discord
from discord.ext import commands

from Utilitary import database, utils
from Utilitary.logger import log


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def get_rule_for_emoji(emoji_id: typing.Optional[int], emoji_str: str, guild: discord.Guild) \
            -> typing.Optional[str]:
        """
        Retrieve the rule linked to the emoji `emoji`.

        Args:
            emoji_id: The id of the emoji if it has one. Optional if the emoji is unicode.
            emoji_str: The visual representation of the emoji.
            guild: The guild where it happens.

        Returns:
            Optional[str] | The rule if found, else None
        """
        sql = "SELECT rule FROM rules_table WHERE (emoji_id=? OR emoji_str=?) AND guild_id=? ;"
        response = database.fetch_one(sql, [emoji_id, emoji_str, guild.id])
        if response is None:
            return None
        return utils.parse_random_string(response[0])

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def rules(self, ctx: commands.Context, emoji: utils.EmojiOrUnicodeConverter):
        """Send the rule linked to `emoji` in the current channel."""
        emoji_id = emoji.id if isinstance(emoji, discord.Emoji) else None
        rule = self.get_rule_for_emoji(emoji_id, str(emoji), ctx.guild)
        if rule is None:
            await ctx.send(utils.get_text(ctx.guild, "rules_not_found").format(emoji))
            return
        await ctx.message.delete()
        await ctx.send(rule)

    @rules.command(name='addrule', aliases=['adr'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def add_rule(self, ctx: commands.Context, emoji: utils.EmojiOrUnicodeConverter, *, rule: str):
        """Add a new rule with `rule` as body and `emoji` as emoji."""
        emoji_id = emoji.id if isinstance(emoji, discord.Emoji) else None
        sql = "INSERT INTO rules_table(emoji_id, emoji_str, rule, guild_id) " \
              "VALUES (:emoji_id, :emoji_str, :rule, :guild_id) " \
              "ON CONFLICT(emoji_str, guild_id) DO " \
              "UPDATE SET rule=:rule, emoji_str=:emoji_str WHERE " \
              "(emoji_id=:emoji_id OR emoji_str=:emoji_str) AND guild_id=:guild_id ;"

        success = database.execute_order(sql, {"emoji_id": emoji_id,
                                               "emoji_str": str(emoji),
                                               "rule": rule,
                                               "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @rules.command(name='removerule', aliases=['rmr'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def remove_rule(self, ctx: commands.Context, emoji: utils.EmojiOrUnicodeConverter):
        """Remove the rule linked to `emoji`."""
        emoji_id = emoji.id if isinstance(emoji, discord.Emoji) else None
        sql = "DELETE FROM rules_table WHERE (emoji_id=? OR emoji_str=?) AND guild_id=? ;"
        success = database.execute_order(sql, [emoji_id, str(emoji), ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @rules.command(name='setlogchannel', aliases=['slc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the channel where the warning will be logged."""
        sql = "INSERT INTO rules_config(log_channel_id, guild_id) VALUES (:channel_id, :guild_id) " \
              "ON CONFLICT(guild_id) DO " \
              "UPDATE SET log_channel_id=:channel_id WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"channel_id": channel.id, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @rules.command(name='info')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def info(self, ctx: commands.Context):
        """Display the rules and their emoji."""
        sql = "SELECT emoji_id, emoji_str, rule FROM rules_table WHERE guild_id=? ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "rules_info_empty"))
            return
        to_send = ""
        for line in response:
            emoji_id, emoji_str, rule = line
            emoji = self.bot.get_emoji(emoji_id) or emoji_str
            to_send += f"[{emoji}] :\n{rule}\n\n"

        await ctx.send(embed=discord.Embed(title=utils.get_text(ctx.guild, "rules_info_title"), description=to_send))

    @rules.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """Display the help for the `rules` cog."""
        embed = discord.Embed(title=utils.get_text(ctx.guild, "rules_cog_name"),
                              description=utils.get_text(ctx.guild, "rules_help_description"))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "rules_help_admin_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Whenever a reaction is added to a message.

        Checks if the reaction is linked to a rule and if the person who reacted is a moderator
        then send the rule linked to the reaction in DM.
        """
        if not payload.guild_id:
            return
        guild = self.bot.get_guild(payload.guild_id)
        author = guild.get_member(payload.user_id)
        if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot) \
                or author.bot \
                or not utils.is_authorized(author):
            return

        # Check if message hasn't already been warned
        sql = "SELECT * FROM rules_warned WHERE (emoji_id=? OR emoji_str=?) AND message_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [payload.emoji.id, str(payload.emoji), payload.message_id, guild.id])
        if response is not None:
            return

        # Warn user
        rule_message = self.get_rule_for_emoji(payload.emoji.id, str(payload.emoji), guild)
        if rule_message is None:
            return
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = message.author
        if member.bot is True:
            return
        await member.send(f"> {message.content}\n{rule_message}")

        # Add message as warned
        sql = f"INSERT INTO rules_warned(message_id, emoji_id, emoji_str, guild_id) VALUES (?, ?, ?, ?) ;"
        database.execute_order(sql, [payload.message_id, payload.emoji.id, str(payload.emoji), guild.id])

        # Log warning
        sql = "SELECT log_channel_id FROM rules_config WHERE guild_id=? ;"
        response = database.fetch_one(sql, [guild.id])
        if response is None:
            log("Rules::on_raw_reaction_add", f"WARNING Rules log channel not set for guild {guild} ({guild.id})")
            return
        log_channel = guild.get_channel(response[0])
        if log_channel is None:
            log("Rules::on_raw_reaction_add", f"ERROR Log channel invalid for guild {guild} ({guild.id})")
            return
        embed = discord.Embed(title=utils.get_text(guild, "rules_log_title").format(member, payload.emoji),
                              description=message.content)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.set_footer(text=member.display_name, icon_url=member.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        await log_channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Rules(bot))
