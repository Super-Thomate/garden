from datetime import datetime

import discord
from discord.ext import commands

import Utils
from core import logger


class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='help')
  @Utils.require(required=['not_banned'])
  async def help(self, ctx, *, cog: str = None):
    """Display help"""
    cog = cog or "global"
    if Utils.is_banned(ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(Utils.get_text(ctx.guild.id, "error_user_unauthorized_command"))
      return
    try:
      method = getattr(self, "help_" + cog.lower())
      embed = method(ctx.guild.id)
      await ctx.channel.send(content=None, embed=embed)
    except AttributeError as e:
      await ctx.channel.send(Utils.get_text(ctx.guild.id, "error_unknown_cog").format(cog))
      logger ("help::help", f"{type(e).__name__} - {e}")
    except Exception as e:
      await ctx.channel.send(Utils.get_text(ctx.guild.id, "error_occured").format(type(e).__name__, e))

  def help_invitation(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_invitation_title'))
    embed.description = Utils.get_text(guild_id, 'help_moderator_only')
    embed.add_field(name="**SUF :**", value=Utils.get_text(guild_id, 'help_invitation_suf'), inline=False)
    embed.add_field(name="**AR :**", value=Utils.get_text(guild_id, 'help_invitation_ar'), inline=False)
    embed.add_field(name="**Général :**", value=Utils.get_text(guild_id, 'help_invitation_general'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_logs(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'logs_help_title'))
    embed.description = Utils.get_text(guild_id, 'help_moderator_only')
    embed.add_field(name="**SUF :**", value=Utils.get_text(guild_id, 'logs_help_suf'), inline=False)
    embed.add_field(name="**AR :**", value=Utils.get_text(guild_id, 'logs_help_ar'), inline=False)
    embed.add_field(name="**Général :**", value=Utils.get_text(guild_id, 'logs_help_admin_command'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_nickname(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'nickname_help_title'))
    embed.add_field(name=Utils.get_text(guild_id, 'help_user_command'),
                    value=Utils.get_text(guild_id, 'nickname_help_user_command'), inline=False)
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command'),
                    value=Utils.get_text(guild_id, 'nickname_help_admin_command'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_vote(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'vote_help_title'))
    embed.description = Utils.get_text(guild_id, 'help_vote_description')
    embed.add_field(name=Utils.get_text(guild_id, 'help_user_command')
                    , value=Utils.get_text(guild_id, 'vote_help_user_command')
                    , inline=False)
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command_config')
                    , value=Utils.get_text(guild_id, 'vote_help_admin_command_config')
                    , inline=False)
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command_phase')
                    , value=Utils.get_text(guild_id, 'vote_help_admin_command_phase')
                    , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_bancommand(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'bancommand_help_title'))
    embed.description = Utils.get_text(guild_id, 'bancommand_help_description')
    """
      * bancommanduser command user [time]
      * unbancommanduser command user
      * isbanuser user
      * listbanuser [command]
      * bancommandrole command role [time]
      * unbancommandrole command role
      * listbanrole [command]
      * isbanrole role
    """
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command')
                    , value=Utils.get_text(guild_id, 'bancommand_help_admin_command')
                    , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_welcome(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'welcome_help_title'))
    embed.description = Utils.get_text(guild_id, 'help_moderator_only')
    embed.add_field(name=Utils.get_text(guild_id, "help_variable_title")
                    , value=Utils.get_text(guild_id, "welcome_help_variables")
                    , inline=False
                    )
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command')
                    , value=Utils.get_text(guild_id, 'welcome_help_admin_command')
                    , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_roledm(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'roleDM_help_title'))
    embed.description = Utils.get_text(guild_id, 'roleDM_help_description')
    """
    * setroledm role
    * unsetroledm role
    * setroledmmessage role
    * displayroledmmessage role
    """
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command')
                    , value=Utils.get_text(guild_id, 'roleDM_help_admin_command')
                    , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_utip(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_utip_title'))
    """
    * utip
    * setutipchannel channel
    * setutiplog channel
    * setutiprole role
    * setutipmessage
    * setutipdelay
    """
    embed.add_field(name=Utils.get_text(guild_id, 'help_user_command')
                    , value=Utils.get_text(guild_id, 'utip_help_user_command')
                    , inline=False)
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command')
                    , value=Utils.get_text(guild_id, 'utip_help_admin_command')
                    , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_birthday(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_birthday_title'))
    embed.add_field(name=Utils.get_text(guild_id, 'help_variable_title'),
                    value=Utils.get_text(guild_id, 'help_help_variables'),
                    inline=False)
    embed.add_field(name=Utils.get_text(guild_id, 'help_user_command'),
                    value=Utils.get_text(guild_id, 'birthday_help_user_command'),
                    inline=False)
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command'),
                    value=Utils.get_text(guild_id, 'birthday_help_admin_command'),
                    inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_source(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'source_help_title'))
    embed.description = Utils.get_text(guild_id, 'help_moderator_only')
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command')
                    , value=Utils.get_text(guild_id, 'source_help_admin_command').format('!')
                    , inline=False
                    )

    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_rules(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'rules_help_title'))
    embed.description = Utils.get_text(guild_id, 'help_moderator_only')
    embed.add_field(name=Utils.get_text(guild_id, "help_variable_title")
                    , value=Utils.get_text(guild_id, "rules_help_user_command")
                    , inline=False
                    )
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command')
                    , value=Utils.get_text(guild_id, 'rules_help_admin_command').format("!")
                    , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_pwet(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'pwet_help_title'))
    embed.add_field(name=Utils.get_text(guild_id, 'help_user_command')
                    , value=Utils.get_text(guild_id, 'pwet_help_user_command').format("!")
                    , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_timer(self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'timer_help_title'))
    embed.add_field(name=Utils.get_text(guild_id, 'help_user_command')
                    , value=Utils.get_text(guild_id, 'timer_help_user_command').format("!")
                    , inline=False
                    )
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command')
                    , value=Utils.get_text(guild_id, 'timer_help_admin_command').format("!")
                    , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_configuration (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'timer_help_title'))
    embed.add_field(name=Utils.get_text(guild_id, 'help_user_command')
                    , value=""
                    , inline=False
                    )
    embed.add_field(name=Utils.get_text(guild_id, 'help_admin_command')
                    , value=""
                    , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_global(self, guild_id):
    line_cogs = ""
    all_lines = []
    all_cogs = {
      "Birthday": {"status": 0, "desc": Utils.get_text(guild_id, 'birthday_help_description')}
      , "Bancommand": {"status": 0, "desc": Utils.get_text(guild_id, 'bancommand_help_description')}
      , "Configuration": {"status": 0, "desc": Utils.get_text(guild_id, 'config_help_description')}
      , "Gallery": {"status": 0, "desc": Utils.get_text(guild_id, 'gallery_help_description')}
      , "Help": {"status": 0, "desc": Utils.get_text(guild_id, 'help_help_description')}
      , "Highlight": {"status": 0, "desc": Utils.get_text(guild_id, 'highlight_help_description')}
      , "Invitation": {"status": 0, "desc": Utils.get_text(guild_id, 'invitation_help_description')}
      , "Link": {"status": 0, "desc": Utils.get_text(guild_id, 'link_help_description')}
      , "Loader": {"status": 0, "desc": Utils.get_text(guild_id, 'loader_help_description')}
      , "Logs": {"status": 0, "desc": Utils.get_text(guild_id, 'logs_help_description')}
      , "Nickname": {"status": 0, "desc": Utils.get_text(guild_id, 'nickname_help_description')}
      , "Moderation": {"status": 0, "desc": Utils.get_text(guild_id, 'moderation_help_description')}
      , "RoleDM": {"status": 0, "desc": Utils.get_text(guild_id, 'roleDM_help_description')}
      , "Source": {"status": 0, "desc": Utils.get_text(guild_id, 'source_help_description')}
      , "Turing": {"status": 0, "desc": Utils.get_text(guild_id, 'turing_help_description')}
      , "Timer": {"status": 0, "desc": Utils.get_text(guild_id, 'timer_help_description')}
      , "Utip": {"status": 0, "desc": Utils.get_text(guild_id, 'utip_help_description')}
      , "Vote": {"status": 0, "desc": Utils.get_text(guild_id, 'vote_help_description')}
      , "Welcome": {"status": 0, "desc": Utils.get_text(guild_id, 'welcome_help_description')}
      , "Source": {"status": 0, "desc": Utils.get_text(guild_id, 'source_help_description')}
      , "Rules": {"status": 0, "desc": Utils.get_text(guild_id, 'rules_help_description')}
    }
    for name in all_cogs.keys():
      if Utils.is_loaded(name.lower(), guild_id):
        all_cogs[name]["status"] = 1

    for cog, dicog in all_cogs.items():
      emoji = ":white_check_mark:" if dicog["status"] else ":x:"
      line = f"-  **{cog}** {emoji}  - *{dicog['desc']}*\n"
      if (len(line_cogs) + len(line) > 1024):
        all_lines.append(line_cogs)
        line_cogs = ""
      line_cogs += line
    all_lines.append(line_cogs)

    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_global_title'))
    embed.description = Utils.get_text(guild_id, 'help_help_description_2')
    embed.add_field(name=Utils.get_text(guild_id, 'help_global_field_general'),
                    value=Utils.get_text(guild_id, 'help_global_field_general_value'), inline=False)
    num = 0
    for line_cogs in all_lines:
      num += 1
      embed.add_field(name=Utils.get_text(guild_id, 'help_global_field_available').format(num, len(all_lines)),
                      value=line_cogs, inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed
