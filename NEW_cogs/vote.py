import discord
from discord.ext import commands, tasks
from Utilitary.logger import log
from Utilitary import database, utils
import datetime
import typing


# noinspection PyTypeChecker
class Vote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.end_vote_loop.start()

    class VoteConverter(commands.Converter):
        async def convert(self, ctx: commands.Context, argument: str) -> str:
            if not Vote.vote_exists(argument, ctx.guild):
                raise commands.BadArgument(f"Vote \"{argument}\" not found")
            return argument

    @staticmethod
    def vote_exists(vote_name: str, guild: discord.Guild) -> bool:
        """
        Check if a vote with this name exists

        :param vote_name: str | The name of the vote
        :param guild: Guild | The guild where it happens
        :return: True if the vote exists, else false
        """
        sql = "SELECT * FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_one(sql, [vote_name, guild.id])
        return response is not None

    async def update_vote(self, ctx: commands.Context, vote_name: str, guild: discord.Guild):
        """
        Update the vote `vote_name`. Used to add or remove propositions from the vote

        :param ctx: Context | The context of the command that called the function
        :param vote_name: str | The name of the vote
        :param guild: Guild | The guild where it happens
        """
        sql = "SELECT vote_channel_id, vote_message_id FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_one(sql, [vote_name, guild.id])
        if response is None:
            return

        message = await commands.MessageConverter().convert(ctx, f"{response[0]}-{response[1]}")
        old_embed = message.embeds[0]
        new_embed = discord.Embed(title=old_embed.title,
                                  description=old_embed.description,
                                  color=old_embed.color)

        propositions_dict = self.get_proposition(vote_name, guild)
        if propositions_dict is not None:
            propositions = ""
            for key, value in propositions_dict.items():  # Add reactions that need to be added
                propositions += f"- [{key}] : {value}\n"
                await message.add_reaction(key)
            for reaction in message.reactions:  # Purge reactions that are no longer needed
                if str(reaction) not in propositions_dict.keys():
                    await message.clear_reaction(reaction)
        else:
            propositions = utils.get_text(guild, "misc_not_set")

        new_embed.add_field(name=utils.get_text(guild, "vote_field_proposition_title"), value=propositions)
        await message.edit(embed=new_embed)

    def get_proposition(self, vote_name: str, guild: discord.Guild) -> typing.Optional[typing.Dict[str, str]]:
        """
        Retrieve the propositions of vote `vote_name`

        :param vote_name: str | The name of the vote
        :param guild: Guild | The guild where it happens
        :return: Dict[str, str] | The propositions with the emojis as keys and the propositions as values
        """
        sql = "SELECT emoji_id, emoji_str, proposition FROM vote_proposition WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_all(sql, [vote_name, guild.id])
        if response is None:
            return None
        propositions = {}
        for line in response:
            emoji_id, emoji_str, proposition = line
            emoji = self.bot.get_emoji(emoji_id) or emoji_str
            propositions[str(emoji)] = proposition
        return propositions

    async def end_vote_by_name(self, vote_name: VoteConverter, guild: discord.Guild) -> bool:
        """
        Display the results of vote `vote_name` and cancel its delay in the DB

        :param vote_name: str | The name of the vote
        :param guild: Guild | The guild where it happens
        :return: True if the vote was ended, False if the vote wasn't found
        """
        if not self.vote_exists(vote_name, guild):
            log("Vote::end_vote_by_name", f"ERROR Vote {vote_name} not found for guild {guild} ({guild.id})")
            return False

        sql = "SELECT vote_channel_id, vote_message_id, end_role_id, end_channel_id " \
              "FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_one(sql, [vote_name, guild.id])
        vote_channel_id, vote_message_id, end_role_id, end_channel_id = response
        vote_channel = guild.get_channel(vote_channel_id)
        vote_message = await vote_channel.fetch_message(vote_message_id)
        end_channel = guild.get_channel(end_channel_id)
        end_role = guild.get_role(end_role_id)

        propositions = self.get_proposition(vote_name, guild)
        reactions = sorted(vote_message.reactions, key=lambda r: r.count, reverse=True)
        results = ""
        for index, reaction in enumerate(reactions):
            if index == 0:
                results += utils.get_text(guild, "vote_winner") \
                    .format(reaction.count - 1, str(reaction), propositions[str(reaction)])
            else:
                results += utils.get_text(guild, "vote_results") \
                    .format(index + 1, reaction.count - 1, str(reaction), propositions[str(reaction)])

        await end_channel.send(utils.get_text(guild, "vote_ended").format(end_role.mention, vote_name, results))

        sql = "UPDATE vote_table SET ends_at=? WHERE vote_message_id=? AND guild_id=? ;"
        database.execute_order(sql, [None, vote_message_id, guild.id])
        return True

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def vote(self, ctx: commands.Context, name: str, title: str, description: str,
                   end_channel: discord.TextChannel, end_role: discord.Role):
        """
        Create a new vote
        """
        # Send vote embed
        embed = discord.Embed(title=title, description=description, color=discord.Color.gold())
        embed.add_field(name=utils.get_text(ctx.guild, "vote_field_proposition_title"),
                        value=utils.get_text(ctx.guild, "misc_not_set"))
        embed.set_footer(text=utils.get_text(ctx.guild, "vote_name").format(name))
        msg = await ctx.send(embed=embed)

        # Insert data in DB
        sql = "INSERT INTO " \
              "vote_table(vote_channel_id, vote_message_id, vote_name, end_role_id, end_channel_id, guild_id) " \
              "VALUES (?, ?, ?, ?, ?, ?) ;"
        success = database.execute_order(sql, [ctx.channel.id, msg.id, name, end_role.id, end_channel.id, ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
            await ctx.message.delete(delay=2.0)
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='deletevote', aliases=['dv'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def delete_vote(self, ctx: commands.Context, vote_name: VoteConverter):
        sql = "SELECT vote_channel_id, vote_message_id FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_one(sql, [vote_name, ctx.guild.id])
        vote_channel_id, vote_message_id = response
        vote_message = await commands.MessageConverter().convert(ctx, f"{vote_channel_id}-{vote_message_id}")

        sql = "DELETE FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        database.execute_order(sql, [vote_name, ctx.guild.id])
        sql = "DELETE FROM vote_proposition WHERE vote_name=? AND guild_id=? ;"
        database.execute_order(sql, [vote_name, ctx.guild.id])

        await vote_message.delete()
        await ctx.message.add_reaction('✅')

    @vote.command(name='addproposition', aliases=['ap'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def add_proposition(self, ctx: commands.Context, vote_name: VoteConverter,
                              emoji: utils.EmojiOrUnicodeConverter, *, proposition: str):
        """
        Add the proposition `proposition` with emoji `emoji` to the vote
        """
        emoji_id = emoji.id if isinstance(emoji, discord.Emoji) else None
        sql = "INSERT INTO vote_proposition(emoji_id, emoji_str, proposition, vote_name, guild_id) " \
              "VALUES (:emoji_id, :emoji_str, :proposition, :vote_name, :guild_id) " \
              "ON CONFLICT (emoji_str, vote_name, guild_id) DO " \
              "UPDATE SET proposition=:proposition, emoji_str=:emoji_str " \
              "WHERE (emoji_id=:emoji_id OR emoji_str=:emoji_str) AND vote_name=:vote_name AND guild_id=:guild_id ;"
        success = database.execute_order(sql, {"emoji_id": emoji_id,
                                               "emoji_str": str(emoji),
                                               "proposition": proposition,
                                               "vote_name": vote_name,
                                               "guild_id": ctx.guild.id})
        await self.update_vote(ctx, vote_name, ctx.guild)
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='removeproposition', aliases=['rp'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def remove_proposition(self, ctx: commands.Context, vote_name: VoteConverter,
                                 emoji: utils.EmojiOrUnicodeConverter):
        """
        Remove the proposition linked to `emoji` from the vote
        """
        emoji_id = emoji.id if isinstance(emoji, discord.Emoji) else None
        sql = "DELETE FROM vote_proposition WHERE (emoji_id=? OR emoji_str=?) AND vote_name=? AND guild_id=? ;"
        success = database.execute_order(sql, [emoji_id, str(emoji), vote_name, ctx.guild.id])
        await self.update_vote(ctx, vote_name, ctx.guild)
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='setvoteend', aliases=['sve'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_vote_end(self, ctx: commands.Context, vote_name: VoteConverter, delay: utils.DelayConverter):
        """
        Set the delay of the vote (exemple: `2d5h`)
        """
        # noinspection PyTypeChecker
        vote_end = int(datetime.datetime.utcnow().timestamp()) + delay
        sql = "UPDATE vote_table SET ends_at=? WHERE vote_name=? AND guild_id=? ;"
        success = database.execute_order(sql, [vote_end, vote_name, ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='setvotechannel', aliases=['svc'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_vote_channel(self, ctx: commands.Context, vote_name: VoteConverter, channel: discord.TextChannel):
        """
        Set the channel in which the results will be displayed
        """
        sql = "UPDATE vote_table SET end_channel_id=? WHERE vote_name=? AND guild_id=? ;"
        success = database.execute_order(sql, [channel.id, vote_name, ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='setvoterole', aliases=['svr'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_vote_role(self, ctx: commands.Context, vote_name: VoteConverter, role: discord.Role):
        """
        Set the role that will be mentioned when the vote ends
        """
        sql = "UPDATE vote_table SET end_role_id=? WHERE vote_name=? AND guild_id=? ;"
        success = database.execute_order(sql, [role.id, vote_name, ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='endvote', aliases=['ev'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def end_vote(self, ctx: commands.Context, vote_name: VoteConverter):
        """
        Immediatly end vote and display results
        """
        if not await self.end_vote_by_name(vote_name, ctx.guild):
            await ctx.send(utils.get_text(ctx.guild, "vote_not_found").format(vote_name))
            return
        await ctx.message.add_reaction('✅')

    @vote.command(name='resetvote', aliases=['rv'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def reset_vote(self, ctx: commands.Context, vote_name: VoteConverter):
        """
        Reset the vote counts
        """
        sql = "SELECT vote_channel_id, vote_message_id FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_one(sql, [vote_name, ctx.guild.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "vote_not_found").format(vote_name))
            return
        message = await commands.MessageConverter().convert(ctx, f"{response[0]}-{response[1]}")
        await message.clear_reactions()
        await self.update_vote(ctx, vote_name, ctx.guild)
        await ctx.message.add_reaction('✅')

    @vote.command(name='info')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def info(self, ctx: commands.Context):
        sql = "SELECT vote_name, end_role_id, end_channel_id, ends_at FROM vote_table WHERE guild_id=? ;"
        response = database.fetch_all(sql, [ctx.guild.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "vote_info_empty"))
            return

        to_send = ""
        for line in response:
            vote_name, end_role_id, end_channel_id, ends_at = line
            end_channel = ctx.guild.get_channel(end_channel_id)
            end_channel = end_channel.mention if end_channel else utils.get_text(ctx.guild, "misc_channel_invalid") \
                .format(end_channel_id)
            end_role = ctx.guild.get_role(end_role_id)
            end_role = end_role.mention if end_role else utils.get_text(ctx.guild, "misc_role_invalid") \
                .format(end_role_id)
            ends_at = utils.parse_timestamp(ends_at, ctx.guild) if ends_at \
                else utils.get_text(ctx.guild, "misc_not_set")
            to_send += f"`{vote_name}` | {end_channel} | {end_role} | {ends_at}\n"

        await ctx.send(embed=discord.Embed(title=utils.get_text(ctx.guild, "vote_info_title"), description=to_send))

    @vote.command(name='help')
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def help(self, ctx: commands.Context):
        """
        Display the help for the `rules` cog
        """
        embed = discord.Embed(title=utils.get_text(ctx.guild, "vote_cog_name"),
                              description=utils.get_text(ctx.guild, "vote_help_description"))
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "vote_help_admin_command").format(ctx.prefix),
                        inline=False)
        embed.add_field(name=utils.get_text(ctx.guild, "misc_admin_command"),
                        value=utils.get_text(ctx.guild, "vote_help_admin_command_2").format(ctx.prefix),
                        inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Stop anyone from adding reactions that are not propositions on a vote message
        """
        if not payload.guild_id:
            return
        guild = self.bot.get_guild(payload.guild_id)
        author = guild.get_member(payload.user_id)
        if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot) or author == self.bot.user:
            return
        sql = "SELECT vote_name FROM vote_table WHERE vote_message_id=? AND guild_id=? ;"
        response = database.fetch_one(sql, [payload.message_id, guild.id])
        if response is None:
            return
        proposition_dict = self.get_proposition(response[0], guild)
        if str(payload.emoji) not in proposition_dict.keys():
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.clear_reaction(payload.emoji)

    @tasks.loop(minutes=1.0)
    async def end_vote_loop(self):
        """
        Check if a vote end is reached and print the results
        """
        now = int(datetime.datetime.utcnow().timestamp())
        for guild in self.bot.guilds:
            if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot):
                continue
            sql = "SELECT vote_name FROM vote_table WHERE ends_at<? AND guild_id=? ;"
            response = database.fetch_all(sql, [now, guild.id])
            if response is None:
                continue
            for line in response:
                if not await self.end_vote_by_name(line[0], guild):
                    log("Vote::vote_loop", f"Could not end vote {response[0]} in guild {guild} ({guild.id})")

    def cog_unload(self):
        """
        Called when the cog is unloaded.
        Stop the `end_vote_loop` task
        """
        self.end_vote_loop.cancel()


def setup(bot: commands.Bot):
    bot.add_cog(Vote(bot))
