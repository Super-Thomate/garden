import discord
from discord.ext import commands
import typing
from Utilitary import database
import os
import json
import datetime
from Utilitary.logger import log
from functools import wraps
from dotenv import load_dotenv
import aiohttp
import asyncio
import re
from babel.dates import format_datetime, format_timedelta
import random

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
LANGUAGE_FILE_DIRECTORY = os.path.join(os.path.dirname(__file__), '..', os.getenv('LANGUAGE_FILE_PATH'))
strings: typing.Dict[str, typing.Dict[str, str]] = {}


def __init_strings():
    """
    Initiate the `strings` global dict which contains the locales for multiple languages
    """
    global strings
    sql = "SELECT language_code FROM config_lang ;"
    response = database.fetch_all(sql)
    if response is None:
        return
    for data in response:
        code: str = data[0]
        file_path = LANGUAGE_FILE_DIRECTORY + code + ".json"
        try:
            with open(file_path, 'r') as file:
                strings[code] = json.load(file)
        except FileNotFoundError:
            log('utils::__init_strings', f"File {file_path} not found !!")
            continue


__init_strings()


def get_text(guild: discord.Guild, key: str) -> str:
    """
    Return the string refering to `key` in the correct language according to the current language setting of the guild

    :param guild: Guild | The current guild
    :param key: str | The key to retrieve the string from
    :return: str | The string refered by `key` in the language of the guild
    """
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    response = database.fetch_one(sql, [guild.id])
    language_code = response[0] if response else 'en'
    if response is None:
        log('utils::get_text', f"language_code is not set for guild {guild.name} ({guild.id}) !! "
                               f"English set by default")
    try:
        return strings[language_code][key]
    except KeyError:
        log('utils::get_text', f"KeyError for {key} in language {language_code} !!!")
        return f"**KeyError** for `{key}` in language `{language_code}`\nShow this message to a moderator"


def require(required: typing.List[str]):
    """
    A decorator used to wrap a command that run a few check before calling said command.
    The command won't be executed if one of the check fails.
    Accepted arguments are:
     - `cog_loaded` to check if the cog is loaded on the guild
     - `not_banned` to check if the user is not banned from using the command
     - `authorized` to check if the user has enough permission to use the command
     - `developer` to check if the user is part of the dev team

    :param required: List[str] | A list of string referring to the checks to run.
    """

    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            ctx: commands.Context = args[1]
            if 'cog_loaded' in required:
                if not is_loaded(ctx.cog.qualified_name.lower(), ctx.guild):
                    await ctx.send(get_text(ctx.guild, "misc_not_loaded")
                                   .format(ctx.command, ctx.cog.qualified_name.lower()))
                    await ctx.message.add_reaction('❌')
                    return
            if 'not_banned' in required:
                if is_banned_from_command(ctx.command, ctx.author):
                    log("Utils::require::is_command_ban",
                        f"Member {ctx.author} can't use command {ctx.command.name} in guild {ctx.guild}")
                    return
            if 'authorized' in required:
                if not is_authorized(ctx.author):
                    log("Utils::require::is_authorized",
                        f"Member {ctx.author} misses permissions for command {ctx.command.name} in guild {ctx.guild}")
                    return
            if 'developer' in required:
                if not is_developer(ctx.author):
                    log("Utils::require::is_developer",
                        f"Member {ctx.author} tried to use a dev command in guild {ctx.guild}")
                    return
            return await f(*args, **kwargs)

        return wrapped

    return decorator


def is_loaded(cog_name: str, guild: discord.Guild) -> bool:
    """
    Return wether a cog is loaded in a guild

    :param cog_name: str | The name of the cog
    :param guild: Guild | The current guild
    :return: True if the cog is loaded in the guild, else False
    """
    if cog_name in ('configuration', 'loader'):  # Same value as Loader.DEFAULT_COGS
        return True
    sql = "SELECT status FROM config_cog WHERE cog_name=? AND guild_id=? ;"
    response = database.fetch_one(sql, [cog_name, guild.id])
    status: bool = response[0] if response else False
    return status


def member_is_banned_from_command(command: commands.Command, member: discord.Member):
    """
    Check if a member is banned from using a command

    :param command: Command | The command to be checked
    :param member: Member | The member to be checked
    :return: True if the user is banned from using the command, else False
    """
    now = int(datetime.datetime.now().timestamp())
    sql = "SELECT * FROM bancommand_banned_user WHERE member_id=? AND command=? AND ends_at>? AND guild_id=? ;"
    response = database.fetch_one(sql, [member.id, command.name, now, member.guild.id])
    return response is not None


def member_has_role_banned_from_command(command: commands.Command, member: discord.Member):
    """
    Check if a member has a role that is banned from using a command

    :param command: Command | The command to be checked
    :param member: Member | The member to be checked
    :return: True if the user has a role that is banned, else False
    """
    now = int(datetime.datetime.now().timestamp())
    sql = "SELECT role_id FROM bancommand_banned_role WHERE command=? AND ends_at>? AND guild_id=? ;"
    response = database.fetch_all(sql, [command.name, now, member.guild.id])
    if response is None:  # No data found -> no banned role
        return False
    for role_id in response:
        role = member.guild.get_role(role_id)
        if role in member.roles:  # User has banned role
            return True
    return False


def is_banned_from_command(command: commands.Command, member: discord.Member) -> bool:
    """
    Check wether a member is banned from using a command or has a role that is banned from using a command

    :param command: Command | The command to be checked
    :param member: Member | The member to be checked
    :return: True if the user can't use the command, else False
    """
    if is_admin(member):
        return False
    if member_is_banned_from_command(command, member):
        return True
    if member_has_role_banned_from_command(command, member):
        return True
    return False


def is_authorized(member: discord.Member) -> bool:
    """
    Check if a member has enough permissions to use a command

    :param member: Member | The member to be checked
    :return: True if the member is authorized, else False
    """
    if member.guild.id == 494812563016777729:  # Test server bypasses
        return True
    if is_admin(member):  # Admin can't be blocked
        return True
    return is_allowed(member)


def is_admin(member: discord.Member) -> bool:
    """
    Check if a member is an administrator of the guild

    :param member: Member | The member to be checked
    :return: True if the member is an administrator, else False
    """
    return member.guild_permissions.administrator


def is_allowed(member: discord.Member) -> bool:
    """
    Check wether a member has a role that is considered as a `moderator` role
    and thus is allowed to use moderator commands

    :param member: Member | The member to be checked
    :return: True if the user is allowed to use moderator commands, else False
    """
    moderator_roles = get_moderator_role_id(member.guild)
    for role in member.roles:
        if role.id in moderator_roles:
            return True
    return False


def get_moderator_role_id(guild: discord.Guild) -> typing.List[int]:
    """
    Retrieve the ID of the roles that are considered as `moderator` roles
    :param guild: Guild | The guild to retrieve the roles from
    :return: List[int] | A list of the `moderator` roles' ID
    """
    sql = "SELECT role_id FROM config_role WHERE permission=? AND guild_id=? ;"
    response = database.fetch_all(sql, [1, guild.id])
    if response is None:
        return []
    return [value[0] for value in response]


def get_prefix(bot: commands.Bot, message: discord.Message):
    """
    Used when creating the bot instance.
    Return the prefixes to watch according to the guild where the message comes from.
    By default, the prefix is `!` on any guild
    """
    if not message.guild:
        return commands.when_mentioned_or(*['!'])(bot, message)
    sql = "SELECT prefix FROM config_prefix WHERE guild_id=? ;"
    response = database.fetch_all(sql, [message.guild.id])
    if response is None:
        return commands.when_mentioned_or(*['!'])(bot, message)
    prefixes = [prefix[0] for prefix in response]
    return commands.when_mentioned_or(*prefixes)(bot, message)


def is_developer(member: discord.Member) -> bool:
    """
    Check if the member is part of the dev team.
    :param member: Member | The member to check
    :return: True if the member is a developer, else False
    """
    return member.id in (103907580723617792, 232733740084887553, 70528117403295744, 154337017294094336)


def parse_time(timecode: str) -> typing.Optional[int]:
    """
    Convert a special string into a delay

    :param timecode: str | A string of the form `XdXhXmXs` where X is an integer. `Example: 2d5h2m`
    :return: int or None | The timecode parsed into a delay (in seconds)
        The function returns None if the `timecode` string is invalid
    """
    data = {"d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1}
    if not re.fullmatch(r"(\d+[dhms])+", timecode, flags=re.IGNORECASE):
        return None
    total = 0
    tokens = list(filter(None, re.split(r"(\d+[dhms])", timecode, flags=re.IGNORECASE)))
    for token in tokens:
        value, unit = tuple(filter(None, re.split(r"(\d+)", token, flags=re.IGNORECASE)))
        value = int(value)
        unit = unit.lower()
        total += value * data[unit]
    return total


def get_bot_commands(bot: commands.Bot) -> typing.List[str]:
    """
    Return a list containing every Group and command and their respective aliases of the bot

    :param bot: Bot | The bot instance
    :return: List[str] | A list of the bot's Groups, commands and aliases
    """
    all_command = []
    for bot_command in bot.walk_commands():
        all_command.append(bot_command.name)
        all_command.extend(bot_command.aliases)
    return list(set(all_command))


async def delete_messages(messages: typing.List[discord.Message], delay: int = 0):
    """
    Delete the message in `messages` with a user defined delay (default 2s)

    :param messages: List[Message] - The messages to delete
    :param delay: int | The delay in seconds to wait before deleting the messages (default 2s)
    """
    for message in messages:
        await message.delete(delay=delay)


async def is_image_url(url: str) -> bool:
    """
    Non-blocking request to check if an url links to an image

    :param url: str | The url to check
    :return: bool | True if the url is valid and links to an image, else False
    """
    async with aiohttp.ClientSession() as cs:
        try:
            async with cs.get(url) as response:
                return response.headers['Content-Type'] in ("image/png", "image/jpeg", "image/jpg", "image/gif")
        except Exception as e:
            log("Utils::is_url_image", f"{type(e).__name__} - {e}")
            return False


def delay_to_date(delay: int, guild: discord.Guild) -> str:
    """
    Convert a delay into a date in the guild's language

    :param delay: int | A delay in secoonds
    :param guild: Guild | The guild the date will be sent to
    :return: str - A date formatted according to the guild language's locale
    """
    date = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    response = database.fetch_one(sql, [guild.id])
    locale = response[0] if response else 'en'
    return format_datetime(date, locale=locale) + " (CET)"


def delay_to_time(delay: int, guild: discord.Guild) -> str:
    """
    Convert a delay into a time `(example: 2 days)` in the guild's language

    :param delay: int | A delay in secoonds
    :param guild: Guild | The guild the time will be sent to
    :return: str - A time formatted according to the guild language's locale
    """
    time = datetime.timedelta(seconds=delay)
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    response = database.fetch_one(sql, [guild.id])
    locale = response[0] if response else 'en'
    return format_timedelta(time, locale=locale)


def timestamp_to_time(timestamp: int, guild: discord.Guild) -> str:
    """
    Convert a delay into a time `(example: 2 days)` in the guild's language

    :param timestamp: int | A delay in secoonds
    :param guild: Guild | The guild the time will be sent to
    :return: str | A time formatted according to the guild language's locale
    """
    time = datetime.datetime.fromtimestamp(timestamp) - datetime.datetime.now()
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    response = database.fetch_one(sql, [guild.id])
    locale = response[0] if response else 'en'
    return format_timedelta(time, locale=locale, add_direction=True)


def parse_random_string(string: str, member_name: str = None) -> str:
    """
    Parse a "random" string into a normal string.
    A string is considered "random" when it contains one or more `{A|B}` patterns
    where A and B are 2 choices that will be exclusively chosen.

    Example : `Hello {A|B}` will randomly return `Hello A` or `Hello B`

    :param string: str | The base string
    :return: str | The parsed string
    """
    if member_name is None:
        member_name = ""
    string = string.replace("$member", member_name)
    random_parts = re.findall(r"{.*?}", string)
    if len(random_parts) == 0:
        return string
    chosen_values = []
    for value in random_parts:
        choices = value[1:-1].split('|')
        chosen = random.choice(choices)
        chosen_values.append(chosen.strip())
    new_message = re.sub(r"{.*?}", "{}", string).format(*chosen_values)
    return new_message


def member_has_role(member: discord.Member, role_id: int) -> bool:
    """
    Check wether `member` has the role `role`
    :param member: Member | The memeber to check roles from
    :param role_id: int | The id of the role to check
    :return: bool | True if the member has the role, else False
    """
    role = member.guild.get_role(role_id)
    if not role:
        return False
    return role in member.roles


async def ask_confirmation(ctx: commands.Context, comfirm_key: str, formating: list = None) -> bool:
    """
    Send a confirmation message and wait for the member to add a reaction to confirm action

    :param ctx: Context | The context in which the confirmation is asked
    :param comfirm_key: str | The key to be fecthed in the language file. The result will be send as confirm message
    :param formating: list or None | A list containing the necessary formating for confirmation message
    :return: True if the member confirmed, False if the member didn't confirm or if the demand timed out (60s)
    """
    if formating is None:
        formating = []
    confirm_message = get_text(ctx.guild, comfirm_key).format(*formating)
    msg = await ctx.send(confirm_message)
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')
    try:
        reaction, _ = await ctx.bot.wait_for('reaction_add', timeout=60.0,
                                             check=lambda r, u: str(r.emoji) in ('✅', '❌') and u == ctx.author)
        if str(reaction.emoji) == '❌':
            await ctx.send(get_text(ctx.guild, "misc_cancel"), delete_after=2.0)
            return False
        else:
            await ctx.send(get_text(ctx.guild, "misc_confirm"), delete_after=2.0)
            return True
    except asyncio.TimeoutError:
        await ctx.send(get_text(ctx.guild, "misc_timeout"), delete_after=5.0)
        return False
    finally:
        await msg.delete()
