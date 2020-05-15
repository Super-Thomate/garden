import typing

import discord
from discord.ext import commands

from Utilitary import utils
from Utilitary.logger import log


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_caps_emoji(self) -> typing.Union[discord.Emoji, str]:
        """Get the `Caps` emoji used when reacting to a message with too much caps.

        The emoji is hosted on the `Future Industries` server.

        Returns:
            Union[Emoji, str]: The `Caps` emoji or a default unicode one if not found.
        """
        emoji = self.bot.get_emoji(621629196359303168)
        if emoji is None:
            emoji = '‼️'
            log("Moderation::get_caps_emoji", f"ERROR 'Caps' emoji not found !! Using default one: ‼️")
        return emoji

    @commands.group(invoke_without_command=True, name='moderation')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def moderation(self, ctx: commands.Context):
        """Print the subcommands for the cog."""
        await ctx.send(utils.get_text(ctx.guild, "moderation_subcommands").format(ctx.prefix))

    @moderation.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """Display the help for the `moderation` cog."""
        embed = discord.Embed(title=utils.get_text(ctx.guild, "moderation_cog_name"),
                              description=utils.get_text(ctx.guild, "moderation_help_description"))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "moderation_help_admin_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, aliases=['cc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def clean_channel(self, ctx: commands.Context, limit: int):
        """Delete `limit` messages in the channel.

        Limited to 100 messages max, use the `nolimit` subcommand to delete more than 100 messages
        """
        if limit > 100:
            limit = 100
        await ctx.message.delete()
        try:
            deleted = await ctx.channel.purge(limit=limit, check=lambda m: m.pinned is False)
            await ctx.send(utils.get_text(ctx.guild, "moderation_message_deleted").format(len(deleted)),
                           delete_after=2.0)
            log("Moderation::clean_channel",
                f"Deleted {len(deleted)} messages in channel {ctx.channel} in guild {ctx.guild.name}")
        except discord.NotFound:
            pass

    @clean_channel.command(name='nolimit')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def clean_channel_no_limit(self, ctx: commands.Context, limit: int):
        """Delete `limit` messages in the channel. The number of deleted messages is not limited."""
        await ctx.message.delete()
        try:
            deleted = await ctx.channel.purge(limit=limit, check=lambda m: m.pinned is False)
            await ctx.send(utils.get_text(ctx.guild, "moderation_message_deleted").format(len(deleted)),
                           delete_after=2.0)
            log("Moderation::clean_channel",
                f"Deleted {len(deleted)} messages in channel {ctx.channel} in guild {ctx.guild.name}")
        except discord.NotFound:
            pass

    @clean_channel.command(name='id')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def clean_channel_until_id(self, ctx: commands.Context, limit_message: discord.Message):
        """Delete all the message in channel that were posted after `limit_message` including `limit_message`."""
        await ctx.message.delete()
        try:
            deleted = await ctx.channel.purge(after=limit_message.created_at)
            await limit_message.delete()
            await ctx.send(utils.get_text(ctx.guild, "moderation_message_deleted").format(len(deleted)),
                           delete_after=2.0)
            log("Moderation::clean_channel",
                f"Deleted {len(deleted)} messages in channel {ctx.channel} in guild {ctx.guild.name}")
        except discord.NotFound:
            pass

    @commands.Cog.listener('on_message')
    async def all_caps_warning(self, message: discord.Message):
        """
        Add a reaction when a member uses too much caps in a message.
        """
        if not message.guild:
            return
        if message.author.bot is True:
            return
        if not utils.is_loaded(self.qualified_name.lower(), message.guild, self.bot):
            return
        if len(message.content) > 5 and message.content.isupper():
            await message.add_reaction(self.get_caps_emoji())

    @commands.Cog.listener('on_message_edit')
    async def all_caps_warning_edit(self, before: discord.Message, after: discord.Message):
        """
        Add a reaction when a member uses too much caps after editing a message.
        """
        if not before.guild:
            return
        if before.author.bot is True:
            return
        if not utils.is_loaded(self.qualified_name.lower(), before.guild, self.bot):
            return
        emoji = self.get_caps_emoji()
        if len(after.content) > 5 and after.content.isupper():
            await after.add_reaction(emoji)
        elif len(before.content) > 5 and before.content.isupper() and not after.content.isupper():
            await after.remove_reaction(emoji, self.bot.user)


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
