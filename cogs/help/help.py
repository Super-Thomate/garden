import discord
from datetime import datetime
from discord.ext import commands

class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name='help')
  async def help(self, ctx, *, cog: str = None):
    """Display help"""
    cog = cog or "global"
    try:
      method = getattr(self, "help_"+cog.lower())
      embed = method()
      await ctx.channel.send (content=None, embed=embed)
    except AttributeError as e:
      await ctx.channel.send (f"Cog **{cog}** unknown")
      print (f"{type(e).__name__} - {e}")
    except Exception as e:
      await ctx.channel.send (f"An error occured: {type(e).__name__} - {e}")


  def help_invitation (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**INVITATION COG HELP**")
    embed.description = "*Les commandes de ce cog ne sont utilisables que par les admins ou modérateurs spécifiés au bot.*"
    embed.add_field (name="**SUF :**", value="- `-setinvitechannel (-sic)` - définir le channel actuel pour la demande d'invitation des utilisateurs\n- `-setinvitelog (-sil)` - définir le channel actuel pour les logs des invitations\n- `-inviteuser (-iu) <UserID>` - envoie une invitation à l'utilisateur mentionné (ou a l'auteur si aucun ID n'est noté)\n- `-resetinvite (-ri) <UserID>` - reset le timer entre 2 messages à 0 pour l'utilisateur mentionné (ou a l'auteur si aucun ID n'est noté)", inline=False)
    embed.add_field (name="**AR :**", value="- `-setgallerychannel (-sgc)` - définir le channel actuel pour la demande de jeton des utilisateurs\n- `-setgallerylog (-sgl)` - définir le channel actuel pour les logs des jetons\n- `-token  <UserID>` - envoie un jeton à l'utilisateur mentionné (ou a l'auteur si aucun ID n'est noté)", inline=False)
    embed.add_field (name="**Général :**", value="- `-setgallerychannel (-sgc)` - définir le channel actuel pour la demande de jeton des utilisateurs\n- `-cleanchannel (-cc)` - *à effectuer dans le channel défini de demande d'invitation/jeton* - efface tous les massages du channel or messages pin\n- `-help invitation` - montre ce message - *à ne pas utiliser dans les channels publics*", inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_logs (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**LOGS COG HELP**")
    embed.description = "*Les commandes de ce cog ne sont utilisables que par les admins ou modérateurs spécifiés au bot.*"
    embed.add_field (name="**SUF :**", value="- `-setinvitelog (-sil)` - définir le channel actuel pour les logs des invitations", inline=False)
    embed.add_field (name="**AR :**", value="- `-setgallerylog (-sgl)` - définir le channel actuel pour les logs des jetons", inline=False)
    embed.add_field (name="**Général :**", value="- `-setnicknamelog (-snl)` - définir le channel actuel pour les logs des pseudos", inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_nickname (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**NICKNAME COG HELP**")
    embed.add_field (name="**Commandes utilisateur :**", value="- `nickname/pseudo <pseudo voulu> ` - définir le pseudo de l'utilisateur pour ce serveur\n- `next ` - montre le temps restant avant le prochain changement disponible\n- `help nickname ` - montre ce message", inline=False)
    embed.add_field (name="**Commandes admin/modérateur :**", value="- `resetnickname (rn) <UserID>` - remet à 0 le timer pour l'utilisateur défini\n- `setnickcd (ncd) <time>` - définir le temps entre chaque changement de pseudo (en jours)\n- `setnicknamelog (snl)` - définir le channel actuel pour les logs des changements de pseudo", inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_global (self):
    print (self.bot.cogs)
    line_cogs = ""
    all_cogs = {
        "Birthday": {"status":0, "desc": "Enregistre l'anniversaire d'un membre pour le lui souhaiter"}
      , "Help": {"status":0, "desc": "Affiche l'aide de Garden"}
      , "Highlight": {"status":0, "desc": "Gère les mises en valeurs de message"}
      , "Invitation": {"status":0, "desc": "Gère les invitations/jetons"}
      , "Link": {"status":0, "desc": "Gère les liens entre rôles"}
      , "Loader": {"status":0, "desc": "Chargement des différents cogs"}
      , "Logs": {"status":0, "desc": "Gère les logs des différents cogs"}
      , "Nickname": {"status":0, "desc": "Gère le changement de surnom (nickname)"}
      , "Utip": {"status":0, "desc": "Gère le rôle pour les backers Utip"}
    }
    for name in self.bot.cogs.keys():
      all_cogs [name]["status"] = 1
    for cog, dicog in all_cogs.items():
      emoji = ":white_check_mark:" if dicog["status"] else ":x:"
      line_cogs += f"-  **{cog}** {emoji}  - *{dicog ['desc']}*\n"

    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**GARDEN HELP**")
    embed.description = "*Ce bot est séparé en différents **cogs**. Choisissez quelle aide vous souhaitez afficher.*"
    embed.add_field (name="__**Général**__", value="- `-help <NomDuCog>` - Montre l'aide du cog spécifié\n- `-load <NomDuCog>` - Charge le cog spécifié ( :white_check_mark: )\n- `-unload <NomDuCog>` - Décharge le cog spécifié ( :x: )", inline=False)
    embed.add_field (name="__**Cogs Disponibles**__", value=line_cogs, inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed