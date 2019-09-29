from datetime import datetime

import discord
from discord.ext import commands

from Utils import Utils


class Help(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()

  @commands.command(name='help')
  @Utils.require(required=['not_banned'])
  async def help(self, ctx, *, cog: str = None):
    """Display help"""
    cog = cog or "global"
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send ("Vous n'êtes pas autorisé à utiliser cette commande pour le moment.")
      return
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

  def help_vote (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**VOTE COG HELP**")
    embed.description = ":warning: MessageID fait référence à l'identifiant du message embed de vote"
    embed.add_field (   name="**Commandes utilisateur :**"
                      , value="- `!addproposition (add) [<MessageID|votetype>]` - ajouter une proposition au vote en cours ayant soit l'ID `MessageID`, soit le type `votetype`, soit le premier vote compatible trouvé.\n"+
                              "- `!editproposition (edit) [<MessageID|votetype>]` - modifier une proposition au vote en cours ayant soit l'ID `MessageID`, soit le type `votetype`, soit le premier vote compatible trouvé."+
                              " Aucune confirmation n'est demandée.\n"+
                              "- `!removeproposition (remove) [<MessageID|votetype>]` - retirer une proposition au vote en cours ayant soit l'ID `MessageID`, soit le type `votetype`, soit le premier vote compatible trouvé."+
                              " Aucune confirmation n'est demandée.\n"+
                              ""
                      , inline=False)
    embed.add_field (   name="**Commandes admin/modérateur** *Configuration* **:**"
                      , value="- `!createvote (vote) [<titre>]` - créer un embed de vote avec un titres\n"+
                              "- `!setdescription (setdesc) <MessageID>` - définir la description du vote\n"+
                              "- `!settitle (title) <MessageID>` - définir le titre du vote\n"+
                              "- `!setvotetype (svt) <MessageID> <votetype>` - définir le type de vote (par défaut `vote`). `votetype` est une chaîne de caractères sans espaces.\n"+
                              "- `!setvoterole (svr) <MessageID> <role>` - définir le rôle à prévenir en cas de fermeture de la phase de proposition.\n"+
                              "- `!setvotechannel (svc) <MessageID> <channel>` - définir le salon où prévenir en cas de fermeture de la phase de proposition.\n"+
                              ""
                      , inline=False)
    embed.add_field (   name="**Commandes admin/modérateur** *Phases* **:**"
                      , value="- `!closeproposition (cp) <MessageID>` - fermer la phase de proposition. Plus aucun `addproposition/editproposition/removeproposition` ne sera accepté de la part des non modérateurs.\n"+
                              "- `!closepedit (ce) <MessageID>` - fermer la phase de modération. Plus aucun `addproposition/editproposition/removeproposition` ne sera accepté.\n"+
                              "- `!closevote (cv) <MessageID>` - fermer la phase de vote. Plus aucun vote ne sera accepté.\n"+
                              "- `!closepropositionat (cpa) <MessageID>` - fermer la phase de proposition à la date renseignée. Plus aucun `addproposition/editproposition/removeproposition` ne sera accepté de la part des non modérateurs après cette date.\n"+
                              "- `!closevoteat (cva) <MessageID>` - fermer la phase de vote à la date renseignée. Plus aucun vote ne sera accepté après cette date.\n"+
                              "- `!resetvote (rv) <MessageID>` - reset la phase de vote pour le message (remet les votes à 0).\n"+
                              ""
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_bancommand (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**BANCOMMAND COG HELP**")
    embed.description = "Ce cog n'est disponible que pour les rôles autorisés"
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
    embed.add_field (   name="**Commandes admin/modérateur :**"
                      , value= ("- `!bancommanduser <command> <user> [<time>]` - empêche l'utilisateur d'utiliser une commande pendant la période `time` ou de façon permanente si pas préciser.\n"+
                                "- `!unbancommanduser <command> <user>` - réinstaure immédiatement à l'utilisateur le droit d'utiliser une commande.\n"+
                                "- `!isbanuser <user>` - affiche les commandes pour lesquelles l'utilisateur est banni.\n"+
                                "- `!listbanuser [<command>]` - liste les utilisateurs bannis par commandes ou pour la commande si elle est précisée.\n"+
                                "- `!bancommandrole <command> <role> [<time>]` - empêche le rôle d'utiliser une commande pendant la période `time` ou de façon permanente si pas préciser.\n"+
                                "- `!unbancommandrole <command> <role>` - réinstaure immédiatement au rôle le droit d'utiliser une commande.\n"+
                                "- `!isbanrole <role>` - affiche les commandes pour lesquelles le rôle est banni.\n"+
                                "- `!listbanrole [<command>]` - liste les rôles bannis par commandes ou pour la commande si elle est précisée.\n"+
                                "- `!help bancommand ` - montre ce message"
                               )
                      , inline=False
                    )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_welcome (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**PUBLIC WELCOME COG HELP**")
    embed.description = "*Les commandes de ce cog ne sont utilisables que par les admins ou modérateurs spécifiés au bot.*"
    embed.add_field (   name="**Commandes admin/modérateur :**"
                      , value="- `!setwelcomechannel (swc) [<channelID>]` - définir le channel de bienvenue (aucun ID spécifié = channel courant )\n"+
                              "- `!setwelcomemessage (swm) <RoleID>` - définir le message de bienvenue pour RoleID\n"+
                              "- `!setwelcomerole (swr) <RoleID>` - définir un rôle qui déclenche le *Public Welcome*\n"+
                              "- `!updatewelcome (uw)` - enregistre l'information de bienvenue pour tous les rôles de tous les users ayant un rôle qui déclenche la bienvenue.\n"+
                              "- `!clearwelcome (cw) [<user>]` - reset l'information de bienvenue pour le user ou soi-même."+
                              ""
                      , inline=False)
    embed.add_field (   name="**Variables message :**"
                      , value="- `$member` - mentionne l'utilisateur venant de déclencher le *Public Welcome*\n"+
                              "- `$role` - mentionne le rôle venant de déclencher le *Public Welcome*\n"+
                              "- `{ }` -  marque le début et la fin de l'aléatoire à l'intérieur du message\n"+
                              "- `|` - marque la séparation entre les différents arguments aléatoiresn"+
                              ""
                      , inline=False
                     )
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_roledm (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**ROLEDM COG HELP**")
    embed.description = "Ce cog n'est disponible que pour les rôles autorisés"
    """
    * setroledm role
    * unsetroledm role
    * setroledmmessage role
    * displayroledmmessage role
    """
    embed.add_field (   name="**Commandes admin/modérateur :**"
                      , value= ("- `!setroledm (sr) <role>` - définit un rôle à écouter pour Garden.\n"+
                                "- `!unsetroledm (ur) <role>` - retire le rôle de la liste de Garden.\n"+
                                "- `!setroledmmessage (srm) <role>` - définit le message à envoyer à la prise du rôle.\n"+
                                "- `!displayroledmmessage (drm) <role>` - affiche le message courant du rôle s'il existe.\n"+
                                "- `!help roledm` - montre ce message"
                               )
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_utip (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**UTIP COG HELP**")
    """
    * utip
    * setutipchannel channel
    * setutiplog channel
    * setutiprole role
    * setutipmessage
    * setutipdelay
    """
    embed.add_field (   name="**Commandes membre :**"
                      , value= ("- `!utip` - poste une demande pour le rôle Utip."+
                                " Le bot vous demandera les pièces nécessaires dans le salon.\n"+
                                ""
                                )
                      , inline=False)
    embed.add_field (   name="**Commandes admin/modérateur :**"
                      , value= ("- `!setutipchannel (suc) [<channel>]` - définit le channel de modération de Utip.\n"+
                                "- `!setutiplog (sul) [<channel>]` - définit le channel de log de Utip.\n"+
                                "- `!setutiprole (sur) <role>` - définit le rôle à donner.\n"+
                                "- `!setutipmessage (sum)` - éditeur pour le message à envoyer lors de la demande.\n"+
                                "- `!setutipdelay (sud)` - éditeur pour le temps que le rôle Utip est conservé.\n"+
                                "- `!help utip` - montre ce message"
                               )
                      , inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed

  def help_birthday (self):
    infos = self.bot.user
    colour = discord.Colour(0)
    colour = colour.from_rgb(176, 255, 176)
    embed = discord.Embed(colour=colour, title="**BIRTHDAY COG HELP**")
    embed.description = "*Certaine commandes de ce cog ne sont utilisables que par les admins ou modérateurs spécifiés au bot.*"
    embed.add_field (name="**Birthday :cake: :**", value="- `-setbirthday (-bd)` - Définir la date d'anniversaire d'un membre. Format jj/mm\n"
                                                         "- `-setbirthdaychannel (-sbc) <channelID>` - Définir un channel pour le souhait des anniversaires (pas de paramètre signifie channel actuel)\n"
                                                         "- `-setbirthdaylog (-sbl) <channelID>` - Définir un channel pour le log des anniversaires (pas de paramètre signifie channel actuel)\n"
                                                         "- `-resetbirthday (-rb) <memberID>` - Supprime un membre de la table des anniversaire afin qu'iel puisse reset sa date d'anniversaire", inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed
  
  def help_global (self):
    line_cogs = ""
    line_cogs_2 = ""
    all_cogs = {
             "Birthday": {"status":0, "desc": "Enregistre l'anniversaire d'un membre pour le lui souhaiter"}
      ,    "Bancommand": {"status":0, "desc": "Empêche un utilisateur ou un role d'utiliser une commande Garden"}
      , "Configuration": {"status":0, "desc": "Configuration pour Garden"}
      ,          "Help": {"status":0, "desc": "Affiche l'aide de Garden"}
      ,     "Highlight": {"status":0, "desc": "Gère les mises en valeurs de message"}
      ,    "Invitation": {"status":0, "desc": "Gère les invitations/jetons"}
      ,          "Link": {"status":0, "desc": "Gère les liens entre rôles"}
      ,        "Loader": {"status":0, "desc": "Chargement des différents cogs"}
    }
    all_cogs_2               = {
                 "Logs": {"status":0, "desc": "Gère les logs des différents cogs"}
      ,      "Nickname": {"status":0, "desc": "Gère le changement de surnom (nickname)"}
      ,    "Moderation": {"status":0, "desc": "Modération divers"}
      ,        "RoleDM": {"status":0, "desc": "Gère l'envoie d'un message privé à la prise d'un rôle"}
      ,        "Turing": {"status":0, "desc": "Moteur d'intelligence artificiel du bot [En test]"}
      ,          "Utip": {"status":0, "desc": "Gère le rôle pour les backers Utip"}
      ,          "Vote": {"status":0, "desc": "Automatisation des votes"}
      ,       "Welcome": {"status":0, "desc": "Gère l'envoie d'un message dans un channel définit à la prise d'un rôle"}
    }
    for name in self.bot.cogs.keys():
      if name in all_cogs :
        all_cogs [name]["status"] = 1
      elif  name in all_cogs_2 :
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
    embed = discord.Embed(colour=colour, title="**GARDEN HELP**")
    embed.description = "*Ce bot est séparé en différents **cogs**. Choisissez quelle aide vous souhaitez afficher.*"
    embed.add_field (name="__**Général**__", value="- `-help <NomDuCog>` - Montre l'aide du cog spécifié\n- `-load <NomDuCog>` - Charge le cog spécifié ( :white_check_mark: )\n- `-unload <NomDuCog>` - Décharge le cog spécifié ( :x: )", inline=False)
    embed.add_field (name="__**Cogs Disponibles (1/2)**__", value=line_cogs, inline=False)
    embed.add_field (name="__**Cogs Disponibles (2/2)**__", value=line_cogs_2, inline=False)
    embed.set_author(icon_url=infos.avatar_url, name=str(infos))
    embed.timestamp = datetime.today()
    return embed