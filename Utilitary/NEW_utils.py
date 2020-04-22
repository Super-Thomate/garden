import discord
from discord.ext import commands
import typing
from Utilitary.logger import log
from Utilitary import database
import os
import json
from datetime import datetime


current_directory = os.path.dirname(__file__) + '/'
language_files_directory = current_directory + '../data/language_files/'
strings = {}


def init_strings():
    """
    Initiate the `strings` global variable which contains the language keys and text for multiple languages
    """
    global strings
    sql = "SELECT language_code FROM config_lang ;"
    language_codes = database.fetch_all(sql)
    if language_codes is None:
        return
    for code in language_codes:
        try:
            with open(f'{language_files_directory}{code}.json', 'r') as file:
                strings[code] = json.load(file)
        except FileNotFoundError:
            continue


def get_text(guild: discord.Guild, key: str) -> str:
    """
    Return the string refering to `key` in the correct language according to the current language setting of the guild

    :param guild: Guild | The current guild
    :param key: str | The key to retrieve the string from
    :return: str | The string refered by `key` in the language of the guild
    """
    sql = "SELECT language_code FROM config_lang WHERE guild_id=? ;"
    language_code = database.fetch_one(sql, [guild.id])
    try:
        return strings[language_code][key]
    except KeyError:
        return f"**KeyError** for `{key}` in language `{language_code}`\nShow this message to a moderator"


def require(required: typing.List[str]):
    """
    A decorator used to wrap a command that run a few check before calling said command.
    Accepted arguments are:
     - `cog_loaded` to check if the cog is loaded on the guild
     - `not_banned` to check if the user is not banned from using the command
     - `authorized` to check if the user has enough permission to use the command

    :param required: List[str] | A list of string referring to the checks to run.
    """
    def decorator(f):
        async def wrapped(*args, **kwargs):
            ctx = args[1]
            if 'cog_loaded' in required:
                if not is_loaded(ctx.cog.qualified_name.lower(), ctx.guild.id):
                    await ctx.send(get_text(ctx.guild.id, "not_loaded")
                                   .format(ctx.command, ctx.cog.qualified_name.lower()))
                    await ctx.message.add_reaction('❌')
                    return False
            if 'not_banned' in required:
                if is_banned_from_command(ctx.command, ctx.author):
                    log("Utils::require::is_command_ban",
                        f"Member {ctx.author} can't use command {ctx.command.name}")
                    return
            if 'authorized' in required:
                if not is_authorized(ctx.author):
                    log("Utils::require::is_authorized",
                        f"Member {ctx.author} misses permissions for command {ctx.command.name}")
                    return
            return await f(*args, **kwargs)
        return wrapped
    return decorator


def is_loaded(cog_name: str, guild: discord.Guild) -> bool:
    """
    Return wether a cog is loaded in a guild

    :param cog_name: str | The name of the cog
    :param guild: Guild | The current guild
    :return: True if the cog is loaded, else False
    """
    sql = "SELECT status FROM config_cog WHERE cog_name=? AND guild_id=? ;"
    status = database.fetch_one(sql, [cog_name, guild.id])
    return True if status else False


def member_is_banned_from_command(command: commands.Command, member: discord.Member):
    """
    Check if a member is banned from using a command

    :param command: Command | The command to be checked
    :param member: Member | The member to be checked
    :return: True if the user is banned from using the command, else False
    """
    now = int(datetime.now().timestamp())
    sql = "SELECT ends_at FROM config_command_banned_user WHERE member_id=? AND command=? AND guild_id=? ;"
    ends_at = database.fetch_one(sql, [member.id, command.name, member.guild.id])
    if ends_at is not None:
        if ends_at > now:
            return True
        else:
            sql = "DELETE FROM config_command_banned_user WHERE member_id=? AND command=? AND guild_id=? ;"
            database.execute_order(sql, [member.id, command.name, member.guild.id])
    return False


def member_has_role_banned_from_command(command: commands.Command, member: discord.Member):
    """
    Check if a member has a role that is banned from using a command

    :param command: Command | The command to be checked
    :param member: Member | The member to be checked
    :return: True if the user has a role that is banned, else False
    """
    now = int(datetime.now().timestamp())
    sql = "SELECT role_id, ends_at FROM config_command_banned_role WHERE command=? AND guild_id=? ;"
    response = database.fetch_all(sql, [command.name, member.guild.id])
    if response is not None:
        for role_id, ends_at in response:
            if ends_at > now:
                role = member.guild.get_role(role_id)
                if role in member.roles:
                    return True
            else:
                sql = "DELETE FROM config_command_banned_role WHERE role_id=? AND command=? AND guild_id=? ;"
                database.execute_order(sql, [member.id, command.name, member.guild.id])
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

    :param member: The member to be checked
    :return: True if the member is authorized, else False
    """
    if member.guild.id == 494812563016777729:
        return True
    if is_admin(member):
        return True
    return is_allowed(member)


def is_admin(member: discord.Member) -> bool:
    """
    Check if a member is an administrator of the guild

    :param member: The member to be checked
    :return: True if the member is an administrator, else False
    """
    if member == discord.Permissions.administrator:
        return True
    else:
        return False


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
    return response


if __name__ == '__main__':
    test = database.fetch_one("SELECT command, ends_at, member_id, guild_id "
                              "FROM config_command_banned_user")
    print(type(test), test)
    test = database.fetch_all("SELECT command, ends_at, member_id, guild_id "
                              "FROM config_command_banned_user")
    print(type(test), test)
