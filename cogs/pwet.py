import re

import discord
from discord.ext import commands

from Utilitary import database, utils


class Pwet(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def create_pwet(string: str, guild: discord.Guild) -> str:
        """Replace every word in `string` by 'pwet'.

        The function preserves discord emojis and unicode emojis.

        Args:
            string: the string to be pweted.
            guild: the guild where the command was called.

        Returns:
            The pweted string.
        """
        words = re.split(r"(<:\w+:\d+>|.\uFE0F\u20E3)", string)  # Separate server emojis and special emojis like :one:
        result = []
        for word in words:
            if re.match(r"(<:\w+:\d+>|.\uFE0F\u20E3)", word):
                result.append(word)
            else:
                result.extend(re.split(r"(\W)", word))  # Split the rest by non-word characters

        # Change word to pwet if it is not one of the 'special case'
        for index, token in enumerate(result):
            if token != '' and not re.match(r"(<:\w+:\d+>|.\uFE0F\u20E3|\W)", token):
                result[index] = 'pwet'

        to_send = "".join(result)
        if len(to_send) >= 2000:
            to_send = utils.get_text(guild, "pwet_message_too_long")
        return to_send

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def pwet(self, ctx: commands.Context, *, message: str):
        """Send a pweted version of `message` and delete the message that called the command."""
        await ctx.message.delete()
        pwet_message = self.create_pwet(message, ctx.guild)
        await ctx.send(pwet_message)

    @pwet.command(name='setreaction', aliases=['sr'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_emoji(self, ctx: commands.Context, emoji: utils.EmojiOrUnicodeConverter):
        """Set the emoji that will trigger a pweting og the reacted message."""
        sql = "INSERT INTO pwet_table(emoji_str, guild_id) " \
              "VALUES (:emoji_str, :guild_id) " \
              "ON CONFLICT(guild_id) DO " \
              "UPDATE SET emoji_str=:emoji_str WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"emoji_str": str(emoji),
                                               "guild_id": ctx.guild.id})
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('❌')

    @pwet.command(name='info')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def info(self, ctx: commands.Context):
        """Show informations about the cog. Here, the emoji that pwets a message"""
        sql = "SELECT emoji_str FROM pwet_table WHERE guild_id=? ;"
        response = database.fetch_one(sql, [ctx.guild.id])
        if response is not None:
            emoji_str = response[0]
            emoji = ctx.guild.get_emoji(int(emoji_str)) if emoji_str.isnumeric() else emoji_str
        else:
            emoji = utils.get_text(ctx.guild, "misc_not_set")
        await ctx.send(utils.get_text(ctx.guild, "pwet_info").format(emoji))

    @pwet.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """Display the help for the cog."""
        embed = discord.Embed(title=utils.get_text(ctx.guild, "pwet_cog_name"),
                              description=utils.get_text(ctx.guild, "pwet_help_description").format(ctx.prefix))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "pwet_help_admin_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Called whenever a reaction is added to a message.

        Check if the author of the reaction is a moderator and that they reacted with the `pwet` emoji.
        If so, pwets the message.
        """
        if not payload.guild_id:
            return
        guild = self.bot.get_guild(payload.guild_id)
        author = guild.get_member(payload.user_id)
        if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot) \
                or author.bot \
                or not utils.is_authorized(author):
            return
        sql = "SELECT * FROM pwet_table WHERE emoji_str=? AND guild_id=? ;"
        response = database.fetch_one(sql, [str(payload.emoji), guild.id])
        if response is None:
            return
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        pwet_message = self.create_pwet(message.content, guild)
        await channel.send(pwet_message)


def setup(bot: commands.Bot):
    bot.add_cog(Pwet(bot))
