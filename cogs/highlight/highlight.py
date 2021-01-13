import discord
from discord.ext import commands

import Utils
import database
import typing


class Highlight(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        return commands.guild_only() and \
               Utils.is_loaded(self.qualified_name.lower(), ctx.guild.id) and \
               Utils.is_authorized(ctx.author, ctx.guild.id) and \
               not Utils.is_banned(ctx.command, ctx.author, ctx.guild.id)

    @commands.group(invoke_without_command=True, aliases=['hl'])
    async def highlight(self, ctx: commands.Context):
        pass

    @highlight.command(name='listen', aliases=['l'])
    async def add_channel_to_listener(self, ctx: commands.Context, channel: discord.TextChannel):
        sql = "SELECT 1 FROM highlight_channel_listener WHERE channel_id=? AND guild_id=? ;"
        is_already_listening = database.fetch_one_line(sql, [channel.id, ctx.guild.id])

        if is_already_listening:
            sql = "DELETE FROM highlight_channel_listener WHERE channel_id=? AND guild_id=? ;"
            await ctx.send(Utils.get_text(ctx.guild.id, 'highlight_stop_channel_listen').format(channel.mention))
        else:
            sql = "INSERT INTO highlight_channel_listener VALUES (?, ?)"
            await ctx.send(Utils.get_text(ctx.guild.id, 'highlight_channel_listen').format(channel.mention))
        database.execute_order(sql, [channel.id, ctx.guild.id])

    @highlight.command(name='add', aliases=['a'])
    async def add_emoji_to_channel_link(self, ctx: commands.Context, emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str], channel: discord.TextChannel):
        sql = "INSERT INTO highlight_emoji_channel VALUES (?, ?, ?) ;"
        emoji_id = emoji.id if isinstance(emoji, (discord.Emoji, discord.PartialEmoji)) else emoji
        database.execute_order(sql, [emoji_id, channel.id, ctx.guild.id])
        await ctx.send(Utils.get_text(ctx.guild.id, 'highlight_emoji_channel_added').format(emoji, channel.mention))

    @highlight.command(name='remove', aliases=['r'])
    async def remove_emoji_to_channel_link(self, ctx: commands.Context, emoji: typing.Union[discord.Emoji, discord.PartialEmoji, str]):
        sql = "DELETE FROM highlight_emoji_channel WHERE emoji_id=? AND guild_id=? ;"
        emoji_id = emoji.id if isinstance(emoji, (discord.Emoji, discord.PartialEmoji)) else emoji
        database.execute_order(sql, [emoji_id, ctx.guild.id])
        await ctx.send(Utils.get_text(ctx.guild.id, 'highlight_emoji_channel_removed').format(emoji))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not Utils.is_loaded(self.qualified_name.lower(), payload.guild_id):
            return
        sql = "SELECT channel_id FROM highlight_channel_listener WHERE guild_id=? ;"
        channels = database.fetch_all_line(sql, [payload.guild_id])
        if not channels or str(payload.channel_id) not in channels[0]:
            return

        emoji_id = payload.emoji.id or str(payload.emoji)
        sql = "SELECT channel_id FROM highlight_emoji_channel WHERE emoji_id=? AND guild_id=? ;"
        channel_id = database.fetch_one_line(sql, [emoji_id, payload.guild_id])
        if not channel_id:
            return
        channel_id = channel_id[0]
        try:
            guild = self.bot.get_guild(payload.guild_id)
            source_channel = guild.get_channel(payload.channel_id)
            message = await source_channel.fetch_message(payload.message_id)
            embed = message.embeds[0] if len(message.embeds) != 0 else None
            dest_channel = guild.get_channel(int(channel_id))
            await dest_channel.send(content=message.content, embed=embed)
        except Exception:
            pass
