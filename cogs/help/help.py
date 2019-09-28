import discord
from datetime import datetime
from discord.ext import commands
from Utils import Utils

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.language_code = 'fr'

  @commands.command(name='help')
  async def help(self, ctx, *, cog: str = None):
    """Display help"""
    cog = cog or "global"
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    try:
      method = getattr(self, "help_"+cog.lower())
      embed = method()
      await ctx.channel.send (content=None, embed=embed)
    except AttributeError as e:
      await ctx.channel.send (self.utils.get_text(self.language_code, "unknow_cog").format(cog))
      print (f"{type(e).__name__} - {e}")
    except Exception as e:
      await ctx.channel.send (self.utils.get_text(self.language_code, "error_occured").format(type(e).__name__, e))


  def help_invitation (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_invitation_title'))
    embed.description = self.utils.get_text(self.language_code, 'help_invitation_description')
    embed.add_field (name="**SUF :**", value=self.utils.get_text(self.language_code, 'help_invitation_suf'), inline=False)
    embed.add_field (name="**AR :**", value=self.utils.get_text(self.language_code, 'help_invitation_ar'), inline=False)
    embed.add_field (name="**Général :**", value=self.utils.get_text(self.language_code, 'help_invitation_general'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_logs (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_logs_title'))
    embed.description = self.utils.get_text(self.language_code, 'help_logs_description')
    embed.add_field (name="**SUF :**", value=self.utils.get_text(self.language_code, 'help_logs_suf'), inline=False)
    embed.add_field (name="**AR :**", value=self.utils.get_text(self.language_code, 'help_logs_ar'), inline=False)
    embed.add_field (name="**Général :**", value=self.utils.get_text(self.language_code, 'help_logs_general'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_nickname (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_nickname_title'))
    embed.add_field (name=self.utils.get_text(self.language_code, 'help_nickname_user_command'), inline=False)
    embed.add_field (name=self.utils.get_text(self.language_code, 'help_nickname_admin_command'), inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_vote (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_vote_title'))
    embed.description = self.utils.get_text(self.language_code, 'help_vote_description')
    embed.add_field (   name=self.utils.get_text(self.language_code, 'help_user_command')
                      , value=self.utils.get_text(self.language_code, 'help_vote_user_command')
                      , inline=False)
    embed.add_field (   name=self.utils.get_text(self.language_code, 'help_admin_command_config')
                      , value=self.utils.get_text(self.language_code, 'help_vote_admin_command_config')
                      , inline=False)
    embed.add_field (   name=self.utils.get_text(self.language_code, 'help_admin_command_phase')
                      , value=self.utils.get_text(self.language_code, 'help_vote_admin_command_phase')
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_bancommand (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_ban_title'))
    embed.description = self.utils.get_text(self.language_code, 'help_ban_description')
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
    embed.add_field (   name=self.utils.get_text(self.language_code, 'help_admin_command')
                      , value=self.utils.get_text(self.language_code, 'help_ban_admin_command')
                      , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_welcome (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_welcome_title'))
    embed.description = self.utils.get_text(self.language_code, 'help_welcome_description')
    embed.add_field (   name=self.utils.get_text(self.language_code, 'user_unauthorized_use_command')
                      , value=self.utils.get_text(self.language_code, 'user_unauthorized_use_command')
                      , inline=False)
    embed.add_field (   name=self.utils.get_text(self.language_code, 'help_admin_command')
                      , value=self.utils.get_text(self.language_code, 'help_welcome_admin_command')
                      , inline=False
                     )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_roledm (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_roleDM_title'))
    embed.description = self.utils.get_text(self.language_code, 'help_roleDM_description')
    """
    * setroledm role
    * unsetroledm role
    * setroledmmessage role
    * displayroledmmessage role
    """
    embed.add_field (   name=self.utils.get_text(self.language_code, 'help_admin_command')
                      , value=self.utils.get_text(self.language_code, 'help_roleDM_admin_command')
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_utip (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_utip_title'))
    """
    * utip
    * setutipchannel channel
    * setutiplog channel
    * setutiprole role
    * setutipmessage
    * setutipdelay
    """
    embed.add_field (   name=self.utils.get_text(self.language_code, 'help_user_command')
                      , value=self.utils.get_text(self.language_code, 'help_utip_user_command')
                      , inline=False)
    embed.add_field (   name=self.utils.get_text(self.language_code, 'help_admin_command')
                      , value=self.utils.get_text(self.language_code, 'help_utip_admin_command')
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_birthday (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_birthday_title'))
    embed.add_field (name=self.utils.get_text(self.language_code, 'help_user_command'),
                     value=self.utils.get_text(self.language_code, 'help_birthday_user_command'),
                     inline=False)
    embed.add_field (name=self.utils.get_text(self.language_code, 'help_admin_command'),
                     value=self.utils.get_text(self.language_code, 'help_birthday_admin_command'),
                     inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed
  
  def help_global (self):
    line_cogs = ""
    line_cogs_2 = ""
    all_cogs = {
             "Birthday": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_birthday_description')}
      ,    "Bancommand": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_bancommand_description')}
      , "Configuration": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_config_description')}
      ,          "Help": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_help_description')}
      ,     "Highlight": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_highlight_description')}
      ,    "Invitation": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_invitation_description')}
      ,          "Link": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_link_description')}
      ,        "Loader": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_loader_description')}
    }
    all_cogs_2               = {
                 "Logs": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_logs_description')}
      ,      "Nickname": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_nickname_description')}
      ,    "Moderation": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_moderation_description')}
      ,        "RoleDM": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_roleDM_description')}
      ,        "Turing": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_turing_description')}
      ,          "Utip": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_utip_description')}
      ,          "Vote": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_vote_description')}
      ,       "Welcome": {"status":0, "desc": self.utils.get_text(self.language_code, 'cog_welcome_description')}
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
    embed = discord.Embed(colour=colour, title=self.utils.get_text(self.language_code, 'help_global_title'))
    embed.description = self.utils.get_text(self.language_code, 'help_global_description')
    embed.add_field (name=self.utils.get_text(self.language_code, 'help_global_field_general'), value=self.utils.get_text(self.language_code, 'help_global_field_general_value'), inline=False)
    embed.add_field (name=self.utils.get_text(self.language_code, 'help_global_field_available_1'), value=line_cogs, inline=False)
    embed.add_field (name=self.utils.get_text(self.language_code, 'help_global_field_available_2'), value=line_cogs_2, inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed