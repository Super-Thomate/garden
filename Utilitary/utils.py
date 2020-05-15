import asyncio
import datetime
import json
import os
import random
import re
import typing
from functools import wraps

import aiohttp
import discord
import emoji
import pytz
from babel.dates import format_datetime, format_timedelta
from discord.ext import commands
from dotenv import load_dotenv

from Utilitary import database
from Utilitary.logger import log

load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

LANGUAGE_FILE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                       os.getenv('LANGUAGE_FILE_PATH')))

log("Utils", f"Language files directory : {LANGUAGE_FILE_DIRECTORY}")

strings: typing.Dict[str, typing.Dict[str, str]]


def init_strings(bot: commands.Bot):
    """Initiate the `strings` global dict which contains the locales for multiple languages."""
    global strings
    strings = {}
    config_cog = bot.get_cog('Configuration')
    langs = config_cog.AVAILABLE_LANGUAGES
    for lang_code in langs:
        file_path = f"{LANGUAGE_FILE_DIRECTORY}/{lang_code}.json"
        try:
            with open(file_path, 'r') as file:
                strings[lang_code] = json.load(file)
            log("Utils::init_strings", f"Number of keys for '{lang_code}.json' : {len(strings[lang_code])}")
        except FileNotFoundError:
            log('Utils::init_strings', f"ERROR File {file_path} not found")
            continue


def get_text(guild: discord.Guild, key: str) -> str:
    """Return the string refering to `key` in the correct language.

    The language is chosen according to the guild language's configuration.

    Args:
        guild: The current guild.
        key: The key to retrieve the string from.

    Returns:
        str: The string refered by `key` in the guild's chosen language.
    """
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    response = database.fetch_one(sql, [guild.id])
    language_code = response[0] if response else 'en'
    if response is None:
        log('Utils::get_text', f"language_code is not set for guild {guild.name} !! "
                               f"English set by default")
    try:
        return strings[language_code][key]
    except KeyError:
        log('Utils::get_text', f"KeyError for {key} in language {language_code} !!!")
        return f"**KeyError** for `{key}` in language `{language_code}`\nShow this message to a moderator"


def require(required: typing.List[str]):
    """A decorator used to wrap a command that run a few check before calling said command.

    The command won't be executed if one of the check fails.
    Accepted arguments are::
        - 'cog_loaded': If the cog is loaded on the guild.
        - 'not_banned': If the user is not banned from using the command.
        - 'authorized': If the user has enough permission to use the command.
        - 'developer': If the user is part of the dev team.

    Args:
        required: The checks to run

    Returns:
        The decorated function if the checks are passed, else Nothing
    """

    def decorator(f):
        @wraps(f)
        async def wrapped(*args, **kwargs):
            ctx: commands.Context = args[1]
            if 'cog_loaded' in required:
                if not is_loaded(ctx.cog.qualified_name.lower(), ctx.guild, ctx.bot):
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


def is_loaded(cog_name: str, guild: discord.Guild, bot: commands.Bot) -> bool:
    """Return wether a cog is loaded in a guild.

    Args:
        cog_name: The name of the cog.
        guild: The guild where the command was called.
        bot: The bot instance.

    Returns:
        True if the cog is loaded in the guild, else False.
    """
    if not guild:
        return False
    loader_cog = bot.get_cog('Loader')
    default_cogs = loader_cog.DEFAULT_COGS
    if cog_name in default_cogs:
        return True
    sql = "SELECT status FROM config_cog WHERE cog_name=? AND guild_id=? ;"
    response = database.fetch_one(sql, [cog_name, guild.id])
    status: bool = response[0] if response else False
    return status


def member_is_banned_from_command(command: commands.Command, member: discord.Member) -> bool:
    """Check if a member is banned from using a command in the member's guild.

    Args:
        command: The command.
        member: The member.

    Returns:
        True if the user is banned from using the command, else False.
    """
    now = int(datetime.datetime.utcnow().timestamp())
    sql = "SELECT * FROM bancommand_banned_user WHERE member_id=? AND command=? AND ends_at>? AND guild_id=? ;"
    response = database.fetch_one(sql, [member.id, command.name, now, member.guild.id])
    return response is not None


def member_has_role_banned_from_command(command: commands.Command, member: discord.Member) -> bool:
    """Check if a member has a role that is banned from using a command.

    Args:
        command: The command.
        member: The member.

    Returns:
        True if the user has a role that is banned, else False.
    """
    now = int(datetime.datetime.utcnow().timestamp())
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
    """Check wether a member is banned from using a command or has a role that is banned from using a command.

    Args:
        command: The command.
        member: The member.

    Returns:
        True if the user can't use the command, else False.
    """
    if is_admin(member):
        return False
    if member_is_banned_from_command(command, member):
        return True
    if member_has_role_banned_from_command(command, member):
        return True
    return False


def is_authorized(member: discord.Member) -> bool:
    """Check if a member has enough permissions to use a command.

    Args:
        member: The member.

    Returns:
        True if the member is authorized, else False.
    """
    if member.guild.id == 494812563016777729:  # Test server bypasses
        return True
    if is_admin(member):  # Admin can't be blocked
        return True
    return is_allowed(member)


def is_admin(member: discord.Member) -> bool:
    """Check if a member is an administrator in it's guild.

    Args:
        member: The member to be checked.

    Returns:
        True if the member is an administrator, else False.
    """
    return member.guild_permissions.administrator


def is_allowed(member: discord.Member) -> bool:
    """Check wether a member has a role that is considered a *moderator* role.

    *moderator* roles are allowed to use *admins* commands.

    Args:
        member: The member to be checked.

    Returns:
        True if has a *moderator* role, else False.
    """
    moderator_roles = get_moderator_role_id(member.guild)
    for role in member.roles:
        if role.id in moderator_roles:
            return True
    return False


def get_moderator_role_id(guild: discord.Guild) -> typing.List[int]:
    """Retrieve the ID of the roles that are considered as *moderator* roles.

    Args:
        guild: The guild to retrieve the *moderator* roles from.

    Returns:
        The *moderator* roles' IDs
    """
    sql = "SELECT role_id FROM config_role WHERE permission=? AND guild_id=? ;"
    response = database.fetch_all(sql, [1, guild.id])
    if response is None:
        return []
    return [value[0] for value in response]


def is_developer(member: discord.Member) -> bool:
    """Check if the member is part of the developer team.

    For now, these members are 'Thomate', 'Shampu', 'Tatlin' and 'Galtea'.

    Args:
        member: The member to check.

    Returns:
        True if the member is in the developer team, else False
    """
    return member.id in (103907580723617792, 232733740084887553, 70528117403295744, 154337017294094336)


def parse_time_string(time_string: str) -> typing.Optional[int]:
    """Parse a `time_string` into it's integer equivalent.

    A `time_string` is a string in the ``time string`` format **XdXhXmXs**
    (example: '2d5h25m12s'), not all units are required.

    Args:
        time_string: The time string.

    Returns:
        The `time_string` converted in seconds or None if `time_string` is invalid.

    Raises:
        AttributeError: if `time_string` is not in the correct format.
    """
    data = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    if not re.fullmatch(r"(\d+[dhms])+", time_string, flags=re.IGNORECASE):
        raise AttributeError
    total = 0
    tokens = list(filter(None, re.split(r"(\d+[dhms])", time_string, flags=re.IGNORECASE)))
    for token in tokens:
        value, unit = tuple(filter(None, re.split(r"(\d+)", token, flags=re.IGNORECASE)))
        value = int(value)
        unit = unit.lower()
        total += value * data[unit]
    return total


def get_bot_commands(bot: commands.Bot) -> typing.List[str]:
    """Return a list containing every Group and command along with their respective aliases.

    Args:
        bot: The bot instance.

    Returns:
        A list containing the bot's commands, groups and aliases.
    """
    all_command = []
    for bot_command in bot.walk_commands():
        all_command.append(bot_command.name)
        all_command.extend(bot_command.aliases)
    return list(set(all_command))  # Casting to set() to remove any duplicated values


async def delete_messages(messages: typing.List[discord.Message], delay: float = 0):
    """Singlely delete every message in `messages` after `delay`.

    Args:
        messages: The messages to delete.
        delay: The delay after which every message will effectively be deleted.
    """
    for message in messages:
        try:
            await message.delete(delay=delay)
        except discord.NotFound:
            continue


async def is_image_url(url: str) -> bool:
    """Checl if `url` is leading to an image.

    Images are file which header's 'Content-Type' section is ('png', 'jpeg', 'jpg', 'gif').

    Args:
        url: The url.

    Returns:
        True if the url is valid and links to an image, else False.
    """
    async with aiohttp.ClientSession() as cs:
        try:
            async with cs.get(url) as response:
                return response.headers['Content-Type'] in ("image/png", "image/jpeg", "image/jpg", "image/gif")
        except aiohttp.InvalidURL:
            return False


def duration_to_date(duration: int, guild: discord.Guild) -> str:
    """Convert a duration (in seconds) into the a **UTC** date in the guild's language.

    Examples:
        If we are 'May 4th 17:00 2020'. Giving a duration of 3600 seconds will display 'May 4th 18:00 2020'.
        The date format change according to the guild configuration's language.
        In a French guild, the date will be displayed in French.

    Args:
        duration: A duration in seconds.
        guild: The guild the date will be sent to.

    Returns:
        A date in the guild's language.
    """
    date = datetime.datetime.utcnow() + datetime.timedelta(seconds=duration)
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    response = database.fetch_one(sql, [guild.id])
    locale = response[0] if response else 'en'
    return format_datetime(date, locale=locale, tzinfo=pytz.UTC) + " (UTC)"


def duration_to_string(duration: int, guild: discord.Guild) -> str:
    """Convert a duration (in seconds) into a string.

    Examples:
        Giving a duration of 3300 seconds will return '55 minutes'.
        The returned string changes according to the guild configuration's language.

    Args:
        duration: A delay in seconds.
        guild: The guild the time will be sent to.

    Returns:
        The duration formated as a string in the guild's language.
    """
    time = datetime.timedelta(seconds=duration)
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    response = database.fetch_one(sql, [guild.id])
    locale = response[0] if response else 'en'
    return format_timedelta(time, locale=locale).capitalize()


def timestamp_to_string(timestamp: int, guild: discord.Guild) -> str:
    """Convert a timestamp into a string in the guild's language.

    Args:
        timestamp: A timestamp.
        guild: The guild the time will be sent to.

    Returns:
        The timestamp converted into a string of how much time is elapsed since or remanining for this timestamp.
    """
    delay = timestamp - datetime.datetime.utcnow().timestamp()
    delta = datetime.timedelta(seconds=delay)
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    response = database.fetch_one(sql, [guild.id])
    locale = response[0] if response else 'en'
    return format_timedelta(delta, locale=locale, add_direction=True).capitalize()


def parse_random_string(string: str, member_name: str = None) -> str:
    """Parse a string the standard random format into a normal string.

    The standard random format look for '{A|B|C}' patterns and return exclusively one of the value enclosed by '|'.
    It also replace any occurence of '$member' by `member_name`.

    Examples:
        Giving '{A|B|C}$member' will return either ('A', 'B' or 'C') + '`member_name`'.

    Args:
        string: The string to parse.
        member_name: What to replace '$member' with.

    Returns:
        The parsed string.
    """
    if member_name is not None:
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
    """Check if `member` has the role identified by `role_id`.

    Args:
        member: The member.
        role_id: The id of the role to check.

    Returns:
        True if the member has the role, else False.
    """
    role = member.guild.get_role(role_id)
    if not role:
        log("Utils::member_has_role", f"WARNING role_id invalid for guild {member.guild.name}")
        return False
    return role in member.roles


async def ask_confirmation(ctx: commands.Context, comfirm_key: str, formating: typing.Optional[list] = None) -> bool:
    """Send a confirmation message and wait for the member to add a reaction to confirm action.

    The confirmation message will be sent in the context's channel and will wait for the member
    that called the command to react to confirm the action.

    Args:
        ctx: The context of the called command.
        comfirm_key: The key to be passed to ``get_text()`` to get the confirmation message's body.
        formating: A list that will be passed to ``format()`` to format the confirmation message's body.

    Returns:
        True if the member confirmed, False if the member didn't confirm or if the demand timed out (after 60s)
    """
    if formating is None:
        formating = []
    confirm_message = get_text(ctx.guild, comfirm_key).format(*formating)
    msg = await ctx.send(confirm_message)
    await msg.add_reaction('✅')
    await msg.add_reaction('❌')

    def check(r: discord.Reaction, u: discord.User):
        return r.message == msg and u == ctx.author and str(r.emoji) in ('✅', '❌')

    try:
        reaction, _ = await ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)
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


class EmojiOrUnicodeConverter(commands.Converter):
    """Custom ``discord.Converter`` that try to convert the argument into a discord.Emoji or into an unicode emoji.

    Returns:
        Union[str, Emoji]: A ``discord.Emoji`` or a string.

    Raises:
        BadArgument: if the argument can't be converted to an emoji.
    """

    async def convert(self, ctx: commands.Context, argument: str) -> typing.Union[discord.Emoji, str]:
        if argument in emoji.UNICODE_EMOJI:
            return argument
        return await commands.EmojiConverter().convert(ctx, argument)


class DurationConverter(commands.Converter):
    """Custom ``discord.Converter`` that try to convert the argument in a duration.

    The converter expect a string in the ``time string`` format **XdXhXmXs**
    (example: '2d5h25m12s'), not all units are required.

    Raises:
        BadArgument: if the argument can't be converted to an duration.
    """

    async def convert(self, ctx: commands.Context, argument: str) -> int:
        try:
            return parse_time_string(argument)
        except commands.BadArgument:
            raise commands.BadArgument(get_text(ctx.guild, "misc_delay_invalid"))
