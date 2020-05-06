import discord
from discord.ext import commands, tasks
from Utilitary.logger import log
from Utilitary import database, utils
import datetime
import typing


class Vote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def update_vote(self, ctx: commands.Context, vote_name: str, guild: discord.Guild):
        sql = "SELECT vote_channel_id, vote_message_id FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_one(sql, [vote_name, guild.id])
        if response is None:
            return
        message = await commands.MessageConverter().convert(ctx, f"{response[0]}-{response[1]}")
        old_embed = message.embeds[0]
        new_embed = discord.Embed(title=old_embed.title, description=old_embed.description, color=old_embed.color)

        propositions_dict = self.get_proposition(vote_name, guild)
        if propositions_dict is not None:
            propositions = ""
            for key, value in propositions_dict.items():  # Add reactions that need to be added
                propositions += f"- [{key}] : {value}\n"
                await message.add_reaction(key)
            for reaction in message.reactions:  # Delete reactions that are no longer needed
                if str(reaction) not in propositions_dict.keys():
                    await message.clear_reaction(reaction)
        else:
            propositions = utils.get_text(guild, "misc_not_set")

        new_embed.add_field(name=utils.get_text(guild, "vote_field_proposition_title"), value=propositions)
        await message.edit(embed=new_embed)

    def get_proposition(self, vote_name: str, guild: discord.Guild) -> typing.Optional[typing.Dict[str, str]]:
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

    async def end_vote_by_name(self, vote_name: str, guild: discord.Guild):
        sql = "SELECT vote_channel_id, vote_message_id, end_role_id, end_channel_id " \
              "FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_one(sql, [vote_name, guild.id])
        if response is None:
            log("Vote::end_vote_by_name", f"ERROR Vote {vote_name} not found for guild {guild} ({guild.id})")
            return
        vote_channel_id, vote_message_id, end_role_id, end_channel_id = response

        vote_channel = guild.get_channel(vote_channel_id)
        vote_message = await vote_channel.fetch_message(vote_message_id)
        end_channel = guild.get_channel(end_channel_id)
        end_role = guild.get_role(end_role_id)

        propositions = self.get_proposition(vote_name, guild)
        reactions = sorted(vote_message.reactions, key=lambda r: r.count, reverse=True)
        results = ""
        for index, reaction in enumerate(reactions):
            results += f"**{index}** ({reaction.count}) -> [{reaction}] : {propositions[reaction]}\n"

        await end_channel.send(utils.get_text(guild, "vote_ended").format(end_role.mention, vote_name, results))

        sql = "UPDATE vote_table SET ends_at=-1 WHERE vote_message_id=? AND guild_id=? ;"
        database.execute_order(sql, [vote_message_id, guild.id])

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def vote(self, ctx: commands.Context, name: str, title: str, description: str,
                   end_channel: discord.TextChannel, end_role: discord.Role):

        # Send vote embed
        embed = discord.Embed(title=title, description=description, color=discord.Color.green())
        embed.add_field(name=utils.get_text(ctx.guild, "vote_field_proposition_title"),
                        value=utils.get_text(ctx.guild, "misc_not_set"))
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

    @vote.command(name='addproposition', aliases=['ap'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def add_proposition(self, ctx: commands.Context, vote_name: str,
                              emoji: utils.EmojiOrUnicodeConverter, proposition: str):
        parameters = {"proposition": proposition, "vote_name": vote_name, "guild_id": ctx.guild.id}
        if isinstance(emoji, discord.Emoji):
            sql = "INSERT INTO vote_proposition(emoji_id, proposition, vote_name, guild_id) " \
                  "VALUES (:emoji_id, :proposition, :vote_name, :guild_id) " \
                  "ON CONFLICT(emoji_id, emoji_str, vote_name, guild_id) DO " \
                  "UPDATE SET proposition=:proposition " \
                  "WHERE emoji_id=:emoji_id AND vote_name=:vote_name AND guild_id=:guild_id ;"
            parameters['emoji_id'] = emoji.id
        else:
            sql = "INSERT INTO vote_proposition(emoji_str, proposition, vote_name, guild_id) " \
                  "VALUES (:emoji_str, :proposition, :vote_name, :guild_id) " \
                  "ON CONFLICT(emoji_id, emoji_str, vote_name, guild_id) DO " \
                  "UPDATE SET proposition=:proposition " \
                  "WHERE emoji_str=:emoji_str AND vote_name=:vote_name AND guild_id=:guild_id ;"
            parameters['emoji_str'] = emoji

        success = database.execute_order(sql, parameters)
        await self.update_vote(ctx, vote_name, ctx.guild)
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='removeproposition', aliases=['rp'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def remove_proposition(self, ctx: commands.Context, vote_name: str, emoji: utils.EmojiOrUnicodeConverter):
        if isinstance(emoji, discord.Emoji):
            sql = "DELETE FROM vote_proposition WHERE emoji_id=? AND vote_name=? AND guild_id=? ;"
            success = database.execute_order(sql, [emoji.id, vote_name, ctx.guild.id])
        else:
            sql = "DELETE FROM vote_proposition WHERE emoji_str=? AND vote_name=? AND guild_id=? ;"
            success = database.execute_order(sql, [emoji, vote_name, ctx.guild.id])
        await self.update_vote(ctx, vote_name, ctx.guild)
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='setvoteend', aliases=['sve'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_vote_end(self, ctx: commands.Context, vote_name: str, delay: utils.DelayConverter):
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
    async def set_vote_channel(self, ctx: commands.Context, vote_name: str, channel: discord.TextChannel):
        sql = "UPDATE vote_table SET end_channel_id=? WHERE vote_name=? AND guild_id=? ;"
        success = database.execute_order(sql, [channel.id, vote_name, ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='setvoterole', aliases=['svr'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def set_vote_role(self, ctx: commands.Context, vote_name: str, role: discord.Role):
        sql = "UPDATE vote_table SET end_role_id=? WHERE vote_name=? AND guild_id=? ;"
        success = database.execute_order(sql, [role.id, vote_name, ctx.guild.id])
        if success is True:
            await ctx.message.add_reaction('✅')
        else:
            await ctx.message.add_reaction('💀')

    @vote.command(name='endvote', aliases=['ev'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def end_vote(self, ctx: commands.Context, vote_name: str):
        await self.end_vote_by_name(vote_name, ctx.guild)
        await ctx.message.add_reaction('✅')

    @vote.command(name='resetvote', aliases=['rv'])
    @commands.guild_only()
    @utils.require(['authorized', 'cog_loaded', 'not_banned'])
    async def reset_vote(self, ctx: commands.Context, vote_name: str):
        sql = "SELECT vote_channel_id, vote_message_id FROM vote_table WHERE vote_name=? AND guild_id=? ;"
        response = database.fetch_one(sql, [vote_name, ctx.guild.id])
        if response is None:
            await ctx.send(utils.get_text(ctx.guild, "vote_not_found").format(vote_name))
            return
        message = await commands.MessageConverter().convert(ctx, f"{response[0]}-{response[1]}")
        await message.clear_reactions()
        await self.update_vote(ctx, vote_name, ctx.guild)
        await ctx.message.add_reaction('✅')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        author = guild.get_member(payload.user_id)
        if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot) \
                or author == self.bot.user \
                or not payload.guild_id:
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
    async def vote_loop(self):
        now = datetime.datetime.utcnow().timestamp()
        for guild in self.bot.guilds:
            if not utils.is_loaded(self.qualified_name.lower(), guild, self.bot):
                continue
            sql = "SELECT vote_name FROM vote_table WHERE ends_at<? AND guild_id=? ;"
            response = database.fetch_all(sql, [now, guild.id])
            if response is None:
                continue
            for line in response:
                await self.end_vote_by_name(line[0], guild)


def setup(bot: commands.Bot):
    bot.add_cog(Vote(bot))
