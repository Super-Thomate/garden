import asyncio
import typing
import discord
from discord.ext import commands
from Utilitary import utils, database
from Utilitary.logger import log
import datetime


class Turing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def send_logging_embed(title: str, description: str, message: discord.Message,
                                 guild: discord.Guild, author: discord.Member):
        """
        Send a logging embed in turing's logging channel
        """
        embed = discord.Embed(title=title, description=description)
        embed.set_author(name=author.name, icon_url=author.avatar_url)
        embed.set_footer(text=f"ID: {message.channel.id}-{message.id}", icon_url=message.author.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        if message.guild:
            embed.add_field(name=utils.get_text(guild, "turing_log_message_link"), value=message.jump_url)

        sql = "SELECT log_channel_id FROM turing_config WHERE guild_id=? ;"
        response = database.fetch_one(sql, [guild.id])
        if not response or not response[0]:
            log("Turing::send_logging_embed", f"WARNING Turing log channel not set for guild {guild.name}")
            return
        channel = guild.get_channel(response[0])
        if channel is None:
            log("Turing::send_logging_embed", f"ERROR Turing log channel invalid for guild {guild.name}")
            return
        await channel.send(embed=embed)

    @commands.command(name='talk', aliases=['speak', 'say'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing_speak(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        """
        Send the message `message` in channel `channel`
        """
        sent_message = await channel.send(message)
        await ctx.message.delete()
        log_title = utils.get_text(ctx.guild, "turing_talk_log_title").format(channel.name)
        await self.send_logging_embed(log_title, message, sent_message, ctx.guild, ctx.author)

    @commands.command(name='answer', aliases=['reply'])
    @commands.guild_only()
    @utils.require(['developer'])
    async def turing_reply(self, ctx: commands.Context, user: discord.User, *, message: str):
        """
        Answer to user `user` DMs by sending the message `messsage`
        For now, this command is developer-only because of unwanted side effects
        """
        sent_message = await user.send(message)
        await ctx.message.delete()
        log_title = utils.get_text(ctx.guild, "turing_reply_log_title").format(user)
        await self.send_logging_embed(log_title, message, sent_message, ctx.guild, ctx.author)

    @commands.command(name='editmessage')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing_edit_message(self, ctx: commands.Context, message: discord.Message):
        """
        Edit the message `message`, ask the member for the new message content.
        `message` must be from the bot
        """
        ask_message = await ctx.send(utils.get_text(ctx.guild, "turing_old_message_content").format(message.content))
        old_message_content = message.content
        try:
            new_message = await self.bot.wait_for('message',
                                                  check=lambda m: m.channel == ctx.channel and m.author == ctx.author,
                                                  timeout=60.0)
            await message.edit(content=new_message.content)
        except asyncio.TimeoutError:
            await ctx.send(utils.get_text(ctx.guild, "misc_timeout"), delete_after=5.0)
            await utils.delete_messages([ctx.message, ask_message])
            return
        except discord.Forbidden:
            await ctx.send(utils.get_text(ctx.guild, "turing_forbidden"))
            return
        await utils.delete_messages([ctx.message, ask_message, new_message])
        log_title = utils.get_text(ctx.guild, "turing_edit_log_title").format(message.channel.name)
        log_description = utils.get_text(ctx.guild, "turing_edit_log_description") \
            .format(old_message_content, new_message.content)
        await self.send_logging_embed(log_title, log_description, message, ctx.guild, ctx.author)

    @commands.command(name='deletemessage')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing_delete_message(self, ctx: commands.Context, message: discord.Message):
        """
        Delete the message `message`
        """
        await message.delete()
        await ctx.message.delete()
        log_title = utils.get_text(ctx.guild, "turing_delete_log_title") \
            .format(message.author.name, message.channel.name)
        await self.send_logging_embed(log_title, message.content, message, ctx.guild, ctx.author)

    @commands.command(name='react')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing_react(self, ctx: commands.Context, message: discord.Message,
                           emoji: typing.Union[discord.Emoji, str]):
        """
        Add the emoji `emoji` to the message `message` as reaction
        """
        await message.add_reaction(emoji)
        await ctx.message.delete()
        log_title = utils.get_text(ctx.guild, "turing_react_log_title").format(str(emoji))
        await self.send_logging_embed(log_title, message.content, message, ctx.guild, ctx.author)

    @commands.command(name='unreact')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing_unreact(self, ctx: commands.Context, message: discord.Message,
                             emoji: typing.Union[discord.Emoji, str]):
        """
        Remove the bot's `emoji` reaction to the message `message`
        """
        await message.remove_reaction(emoji, self.bot.user)
        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=2.0)

    @commands.command(name='lmute', aliases=['lionmute'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing_lion_mute(self, ctx: commands.Context):
        """
        Send a message in the current channel faking that Liøn has been muted
        """
        await ctx.send(utils.get_text(ctx.guild, "turing_lion_muted"))
        await ctx.message.add_reaction('✅')

    @commands.command(name='lstart', aliases=['lionstart'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing_lion_start(self, ctx: commands.Context):
        """
        Send a message in the current channel faking that Liøn resumed replying to users
        """
        await ctx.send(utils.get_text(ctx.guild, "turing_lion_started"))
        await ctx.message.add_reaction('✅')

    @commands.command(name='sethumor', aliases=['sethumour'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing_set_humor(self, ctx: commands.Context, amount: int):
        """
        Send a message faking that Liøn humor has been set to `amount` percent
        """
        await ctx.send(utils.get_text(ctx.guild, "turing_set_humor").format(amount))
        await ctx.message.add_reaction('✅')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def turing(self, ctx: commands.Context):
        await ctx.send(utils.get_text(ctx.guild, "turing_subcommands"))

    @turing.command(name='setlogchannel', aliases=['sc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        sql = "INSERT INTO turing_config(log_channel_id, guild_id) VALUES (:channel_id, :guild_id) " \
              "ON CONFLICT(guild_id) DO " \
              "UPDATE SET log_channel_id=:channel_id WHERE guild_id=:guild_id ;"
        success = database.execute_order(sql, {"channel_id": channel.id, "guild_id": ctx.guild.id})
        if success:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @turing.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        embed = discord.Embed(title=utils.get_text(ctx.guild, "turing_cog_name"),
                              description=utils.get_text(ctx.guild, "turing_help_description").format(ctx.prefix))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "turing_help_admin_command").format(ctx.prefix),
                        inline=False)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_developer_command"),
                        value=utils.get_text(ctx.guild, "turing_help_developer_command").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not isinstance(message.channel, discord.DMChannel):
            return
        if message.author.bot is True:
            return
        log("Turing::on_message", f"Got DM from {message.author}")
        # TODO: Put SUF server ID instead of test server
        guild = self.bot.get_guild(636292952087461888)  # DMs are sent only in SUF server
        log_title = utils.get_text(guild, "turing_log_direct_message") \
            .format(f"{message.author.name}#{message.author.discriminator} [{message.author.id}]")
        await self.send_logging_embed(log_title, message.content, message, guild, message.author)


def setup(bot: commands.Bot):
    bot.add_cog(Turing(bot))
