import discord
from discord.ext import commands
from Utilitary.logger import log
from Utilitary import database, utils
import typing
import datetime


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def get_rule_for_emoji(emoji: typing.Union[int, str], guild: discord.Guild) -> typing.Optional[str]:
        sql = "SELECT rule FROM rules_table WHERE (emoji_id=:emoji OR emoji_str=:emoji) AND guild_id=:guild_id ;"
        response = database.fetch_one(sql, {"emoji": emoji, "guild_id": guild.id})
        if response is None:
            return None
        return utils.parse_random_string(response[0])

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def rules(self, ctx: commands.Context, emoji: utils.EmojiOrUnicodeConverter):
        if isinstance(emoji, discord.Emoji):
            rule = self.get_rule_for_emoji(emoji.id, ctx.guild)
        else:
            # noinspection PyTypeChecker
            rule = self.get_rule_for_emoji(emoji, ctx.guild)
        if rule is None:
            await ctx.send(utils.get_text(ctx.guild, "rules_not_found").format(emoji))
            return
        await ctx.send(rule)

    @rules.command(name='addrule', aliases=['adr'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def add_rule(self, ctx: commands.Context, emoji: utils.EmojiOrUnicodeConverter, *, rule: str):
        if isinstance(emoji, discord.Emoji):
            sql = "INSERT INTO rules_table(emoji_id, rule, guild_id) VALUES (:emoji_id, :rule, :guild_id) " \
                  "ON CONFLICT(emoji_id, emoji_str, guild_id) DO " \
                  "UPDATE SET rule=:rule WHERE emoji_id=:emoji_id AND guild_id=:guild_id ;"
            success = database.execute_order(sql, {"emoji_id": emoji.id, "rule": rule, "guild_id": ctx.guild.id})
        else:
            sql = "INSERT INTO rules_table(emoji_str, rule, guild_id) VALUES (:emoji_str, :rule, :guild_id) " \
                  "ON CONFLICT(emoji_id, emoji_str, guild_id) DO " \
                  "UPDATE SET rule=:rule WHERE emoji_str=:emoji_str AND guild_id=:guild_id ;"
            success = database.execute_order(sql, {"emoji_str": emoji, "rule": rule, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @rules.command(name='removerule', aliases=['rmr'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def remove_rule(self, ctx: commands.Context, emoji: utils.EmojiOrUnicodeConverter):
        if isinstance(emoji, discord.Emoji):
            sql = "DELETE FROM rules_table WHERE emoji_id=:emoji_id AND guild_id=:guild_id ;"
            success = database.execute_order(sql, {"emoji_id": emoji.id, "guild_id": ctx.guild.id})
        else:
            sql = "DELETE FROM rules_table WHERE emoji_str=:emoji_str AND guild_id=:guild_id ;"
            success = database.execute_order(sql, {"emoji_str": emoji, "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @rules.command(name='setlogchannel', aliases=['slc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
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
        sql = "SELECT emoji_id, emoji_str, rule FROM rules_table WHERE guild_id=? ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "rules_info_empty"))
            return
        to_send = ""
        for line in response:
            emoji_id, emoji_str, rule = line
            emoji = emoji_str or self.bot.get_emoji(emoji_id) or utils.get_text(ctx.guild, "misc_invalid_emoji") \
                .format(emoji_id)
            to_send += f"- {emoji} | `{rule}`\n"
        await ctx.send(to_send)

    @rules.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """
        Display the help for the `rules` cog
        """
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
        guild = self.bot.get_guild(payload.guild_id)
        author = guild.get_member(payload.user_id)
        if not utils.is_loaded(self.qualified_name.lower(), guild) \
                or not utils.is_authorized(author) \
                or author.bot \
                or not payload.guild_id:
            return

        # Check if message hasn't already been warned
        sql = "SELECT * FROM rules_warned WHERE message_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [payload.message_id, guild.id])
        if response is not None:
            return

        # Warn user
        emoji = payload.emoji.id or str(payload.emoji)
        rule_message = self.get_rule_for_emoji(emoji, guild)
        if rule_message is None:
            return
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        member = message.author
        await member.send(f"> {message.content}\n{rule_message}")

        # Add message as warned
        sql = "INSERT INTO rules_warned(message_id, guild_id) VALUES (?, ?)"
        database.execute_order(sql, [payload.message_id, guild.id])

        # Log warning
        sql = "SELECT log_channel_id FROM rules_config WHERE guild_id=? ;"
        response = database.fetch_one(sql, [guild.id])
        if response is None or response[0] is None:
            log("Rules::on_raw_reaction_add", f"WARNING Log channel not set for guild {guild.name}")
        log_channel = guild.get_channel(response[0])
        if log_channel is None:
            log("Rules::on_raw_reaction_add", f"ERROR Log channel invalid for guild {guild.name}")
        embed = discord.Embed(title=utils.get_text(guild, "rules_log_title").format(member, payload.emoji),
                              description=message.content)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.set_footer(text=member.display_name, icon_url=member.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        await log_channel.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Rules(bot))
