import discord
from discord.ext import commands
from Utilitary import database, utils
from Utilitary.logger import log
from dotenv import load_dotenv
import os


load_dotenv()
bot = commands.Bot(command_prefix=utils.get_prefix)
bot.remove_command("help")
bot_extensions = ['NEW_cogs.configuration',
                  'NEW_cogs.loader',
                  'NEW_cogs.bancommand']


@bot.event
async def on_ready():
    log('Lion::on_ready', f'Discord version : {discord.__version__}')
    log('Lion::on_ready', f'Logged in as {bot.user.name} [{bot.user.id}]')
    await bot.change_presence(activity=discord.Game(name=os.getenv('BOT_ACTIVITY')))


@bot.event
async def on_guild_join(guild: discord.Guild):
    log('Lion::on_guild_join', f"JOINED NEW GUILD : {guild.name}")
    sql_list = ["INSERT INTO config_prefix(prefix, guild_id) VALUES ('!', ?) ;",
                "INSERT INTO config_lang(language_code, guild_id) VALUES ('en', ?) ;"]
    for sql in sql_list:
        database.execute_order(sql, [guild.id])


@bot.event
async def on_command_error(ctx: commands.Context, exception: str):
    log('Lion::on_command_error', f"Message : `{ctx.message.content}`")
    log('Lion::on_command_error', f"Arguments : `{ctx.args}`")
    log('Lion::on_command_error', f"Exception : `{exception}`")
    if ctx.command:
        await ctx.send(exception)


if __name__ == '__main__':
    for extension in bot_extensions:
        bot.load_extension(extension)
    bot.run(os.getenv('BOT_TOKEN'))
