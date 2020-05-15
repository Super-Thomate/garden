import os
import typing

import discord
from discord.ext import commands

from Utilitary import database, utils
from Utilitary.logger import log


def get_prefix(current_bot: commands.Bot, message: discord.Message) -> typing.List[str]:
    """Set the prefixes to be looked for in the message according to it's guild.

    This function is to passed to the bot's instance ``command_prefix`` argument.

    Args:
        current_bot: The bot in it's current state.
        message: The sent message.

    Returns:
        list(str): A list containing the prefixes to look for.
    """
    if not message.guild:
        return commands.when_mentioned_or(*['!'])(current_bot, message)
    sql = "SELECT prefix FROM config_prefix WHERE guild_id=? ;"
    response = database.fetch_all(sql, [message.guild.id])
    if response is None:
        return commands.when_mentioned_or(*['!'])(current_bot, message)
    prefixes = [prefix[0] for prefix in response]
    return commands.when_mentioned_or(*prefixes)(current_bot, message)


bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command("help")
bot_extensions = ['cogs.configuration',
                  'cogs.loader',
                  'cogs.bancommand',
                  'cogs.utip',
                  'cogs.birthday',
                  'cogs.moderation',
                  'cogs.welcome',
                  'cogs.turing',
                  'cogs.pwet',
                  'cogs.rules',
                  'cogs.vote',
                  'cogs.nickname',
                  'cogs.help']


@bot.event
async def on_ready():
    """Called when the bot is ready. Log the bot's username and ID along with the `discord.py` version."""
    log('Lion::on_ready', f'Discord version : {discord.__version__}')
    log('Lion::on_ready', f'Logged in as {bot.user.name} [{bot.user.id}]')
    await bot.change_presence(activity=discord.Game(name=os.getenv('BOT_ACTIVITY')))


@bot.event
async def on_command_error(ctx: commands.Context, exception: str):
    """Default callback of command's errors. Send the exception in the context's channel and log it."""
    log('Lion::on_command_error',
        f"EXCEPTION : `{exception}` ON COMMAND : `{ctx.message.content}`")
    if ctx.command:
        await ctx.message.add_reaction('❌')
        await ctx.send(exception)


if __name__ == '__main__':
    for extension in bot_extensions:
        bot.load_extension(extension)
    utils.init_strings(bot)  # Init the dictionary containing the language files
    bot.run(os.getenv('BOT_TOKEN'))
