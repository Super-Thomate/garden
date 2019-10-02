from datetime import datetime

import discord
from discord.ext import commands

import Utils


class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot


  @commands.command(name='help')
  @Utils.require(required=['not_banned'])
  async def help(self, ctx, *, cog: str = None):
    """Display help"""
    cog = cog or "global"
    if Utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(Utils.get_text(ctx.guild.id, "user_unauthorized_use_command"))
      return
    try:
      method = getattr(self, "help_"+cog.lower())
      embed = method(ctx.guild.id)
      await ctx.channel.send (content=None, embed=embed)
    except AttributeError as e:
      await ctx.channel.send (Utils.get_text(ctx.guild.id, "unknow_cog").format(cog))
      print (f"{type(e).__name__} - {e}")
    except Exception as e:
      await ctx.channel.send (Utils.get_text(ctx.guild.id, "error_occured").format(type(e).__name__, e))


  def help_invitation (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_invitation_title'))
    embed.description = Utils.get_text(guild_id, 'help_invitation_description')
    embed.add_field (name="**SUF :**", value=Utils.get_text(guild_id, 'help_invitation_suf'), inline=False)
    embed.add_field (name="**AR :**", value=Utils.get_text(guild_id, 'help_invitation_ar'), inline=False)
    embed.add_field (name="**Général :**", value=Utils.get_text(guild_id, 'help_invitation_general'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_logs (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_logs_title'))
    embed.description = Utils.get_text(guild_id, 'help_logs_description')
    embed.add_field (name="**SUF :**", value=Utils.get_text(guild_id, 'help_logs_suf'), inline=False)
    embed.add_field (name="**AR :**", value=Utils.get_text(guild_id, 'help_logs_ar'), inline=False)
    embed.add_field (name="**Général :**", value=Utils.get_text(guild_id, 'help_logs_general'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_nickname (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_nickname_title'))
    embed.add_field (name=Utils.get_text(guild_id, 'help_nickname_user_command'), inline=False)
    embed.add_field (name=Utils.get_text(guild_id, 'help_nickname_admin_command'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_vote (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_vote_title'))
    embed.description = Utils.get_text(guild_id, 'help_vote_description')
    embed.add_field (   name=Utils.get_text(guild_id, 'help_user_command')
                      , value=Utils.get_text(guild_id, 'help_vote_user_command')
                      , inline=False)
    embed.add_field (   name=Utils.get_text(guild_id, 'help_admin_command_config')
                      , value=Utils.get_text(guild_id, 'help_vote_admin_command_config')
                      , inline=False)
    embed.add_field (   name=Utils.get_text(guild_id, 'help_admin_command_phase')
                      , value=Utils.get_text(guild_id, 'help_vote_admin_command_phase')
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_bancommand (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_ban_title'))
    embed.description = Utils.get_text(guild_id, 'help_ban_description')
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
    embed.add_field (   name=Utils.get_text(guild_id, 'help_admin_command')
                      , value=Utils.get_text(guild_id, 'help_ban_admin_command')
                      , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_welcome (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_welcome_title'))
    embed.description = Utils.get_text(guild_id, 'help_welcome_description')
    embed.add_field (   name=Utils.get_text(guild_id, 'help_admin_command')
                      , value=Utils.get_text(guild_id, 'help_welcome_admin_command')
                      , inline=False
                     )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_roledm (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_roleDM_title'))
    embed.description = Utils.get_text(guild_id, 'help_roleDM_description')
    """
    * setroledm role
    * unsetroledm role
    * setroledmmessage role
    * displayroledmmessage role
    """
    embed.add_field (   name=Utils.get_text(guild_id, 'help_admin_command')
                      , value=Utils.get_text(guild_id, 'help_roleDM_admin_command')
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_utip (self, guild_id):
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
    embed.add_field (   name=Utils.get_text(guild_id, 'help_user_command')
                      , value=Utils.get_text(guild_id, 'help_utip_user_command')
                      , inline=False)
    embed.add_field (   name=Utils.get_text(guild_id, 'help_admin_command')
                      , value=Utils.get_text(guild_id, 'help_utip_admin_command')
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_birthday (self, guild_id):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_birthday_title'))
    embed.add_field (name=Utils.get_text(guild_id, 'help_user_command'),
                     value=Utils.get_text(guild_id, 'help_birthday_user_command'),
                     inline=False)
    embed.add_field (name=Utils.get_text(guild_id, 'help_admin_command'),
                     value=Utils.get_text(guild_id, 'help_birthday_admin_command'),
                     inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_global (self, guild_id):
    line_cogs = ""
    line_cogs_2 = ""
    all_cogs = {
             "Birthday": {"status":0, "desc": Utils.get_text(guild_id, 'cog_birthday_description')}
      ,    "Bancommand": {"status":0, "desc": Utils.get_text(guild_id, 'cog_bancommand_description')}
      , "Configuration": {"status":0, "desc": Utils.get_text(guild_id, 'cog_config_description')}
      ,          "Help": {"status":0, "desc": Utils.get_text(guild_id, 'cog_help_description')}
      ,     "Highlight": {"status":0, "desc": Utils.get_text(guild_id, 'cog_highlight_description')}
      ,    "Invitation": {"status":0, "desc": Utils.get_text(guild_id, 'cog_invitation_description')}
      ,          "Link": {"status":0, "desc": Utils.get_text(guild_id, 'cog_link_description')}
      ,        "Loader": {"status":0, "desc": Utils.get_text(guild_id, 'cog_loader_description')}
    }
    all_cogs_2               = {
                 "Logs": {"status":0, "desc": Utils.get_text(guild_id, 'cog_logs_description')}
      ,      "Nickname": {"status":0, "desc": Utils.get_text(guild_id, 'cog_nickname_description')}
      ,    "Moderation": {"status":0, "desc": Utils.get_text(guild_id, 'cog_moderation_description')}
      ,        "RoleDM": {"status":0, "desc": Utils.get_text(guild_id, 'cog_roleDM_description')}
      ,        "Turing": {"status":0, "desc": Utils.get_text(guild_id, 'cog_turing_description')}
      ,          "Utip": {"status":0, "desc": Utils.get_text(guild_id, 'cog_utip_description')}
      ,          "Vote": {"status":0, "desc": Utils.get_text(guild_id, 'cog_vote_description')}
      ,       "Welcome": {"status":0, "desc": Utils.get_text(guild_id, 'cog_welcome_description')}
    }
    for name in self.bot.cogs.keys():
      if name in all_cogs :
        all_cogs [name]["status"] = 1
      elif name in all_cogs_2:
        all_cogs_2 [name]["status"] = 1

    for cog, dicog in all_cogs.items():
      emoji = ":white_check_mark:" if dicog["status"] else ":x:"
      line_cogs += f"-  **{cog}** {emoji}  - *{dicog ['desc']}*\n"
    for cog, dicog in all_cogs_2.items():
      emoji = ":white_check_mark:" if dicog["status"] else ":x:"
      line_cogs_2 += f"-  **{cog}** {emoji}  - *{dicog ['desc']}*\n"

    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=Utils.get_text(guild_id, 'help_global_title'))
    embed.description = Utils.get_text(guild_id, 'help_global_description')
    embed.add_field (name=Utils.get_text(guild_id, 'help_global_field_general'), value=Utils.get_text(guild_id, 'help_global_field_general_value'), inline=False)
    embed.add_field (name=Utils.get_text(guild_id, 'help_global_field_available_1'), value=line_cogs, inline=False)
    embed.add_field (name=Utils.get_text(guild_id, 'help_global_field_available_2'), value=line_cogs_2, inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed