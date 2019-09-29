import math
import time
from datetime import datetime

import discord
from discord.ext import commands

from Utils import Utils
from database import Database
from ..logs import Logs


class Bancommand(commands.Cog):

  """
  Bancommand:
  * bancommanduser command user [time]
  * unbancommanduser command user
  * isbanuser user
  * listbanuser [command]
  * bancommandrole command role [time]
  * unbancommandrole command role
  * listbanrole [command]
  * isbanrole role
  """
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.command(name='bancommanduser', aliases=['bcu'])
  @Utils.require(required=['authorized'])
  async def ban_command_user(self, ctx, command: str = None, user: discord.Member = None, timer: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    # Check if command exists
    all_commands = self.bot.commands
    cont_after = False
    for garden_command in all_commands:
      if command == garden_command.name or command in garden_command.aliases:
        command = garden_command.name
        cont_after = True
      if cont_after:
        break
    if not cont_after:
      await ctx.send (f"La commande {command} n'est pas connue.")
      await ctx.message.add_reaction('❌')
      return
    # Check if user exists
    if not user:
      await ctx.send (f"User manquant.")
      await ctx.message.add_reaction('❌')
      return
    # Parse time
    timestamp = None
    if timer:
      timestamp = math.floor (time.time()) + self.utils.parse_time (timer)
    print (f"timestamp: {timestamp}")
    if not timestamp:
      timestamp = "NULL"
    # Insert/Update
    # CREATE TABLE IF NOT EXISTS `ban_command_user` (`command` VARCHAR(256) NOT NULL, `until` INTEGER, `user_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`command`, `user_id`, `guild_id`)) ;
    select = f"select until from ban_command_user where command='{command}' and user_id='{user.id}' and guild_id='{guild_id}' ;"
    fetched = self.db.fetch_one_line (select)
    if fetched:
      """
      await ctx.send (f"L'utilisateur {user.display_name} est déjà banni pour la commande {command}. Souhaitez-vous:\n1) Prolonger le banissement de {timer}\n2) Modifier la durée du bannissement à {timer} à partir de maintenant\n3) Annuler")
      check = lambda m: m.channel == ctx.channel and m.author == ctx.author
      msg = await self.bot.wait_for('message', check=check)
      if msg.content == '1':
        if not fetched [0]:
          await ctx.send ("L'utilisateur est déjà banni permanent.")
          timestamp = "NULL"
        elif timestamp == "NULL":
          await ctx.send ("L'utilisateur est donc banni permanent.")
        else:
          timestamp = fetched [0] + self.utils.parse_time (timer)
      elif msg.content == '2':
        timestamp = timestamp
      else:
        if msg.content == '3':
          return_message = "Annulation de la commande"
        else:
          return_message = f"`{msg.content}` non reconnu. Annulation de la commande"
        await ctx.send (return_message)
        return
      """
      sql = f"update ban_command_user set until={timestamp} where command='{command}' and user_id='{user.id}' and guild_id='{guild_id}' ;"
    else:
      sql = f"insert into ban_command_user values ('{command}', {timestamp}, '{user.id}', '{guild_id}');"
    try:
      self.db.execute_order (sql)
      await ctx.send(f"{user.display_name} ne peut plus utiliser la commande `{command}` pour la durée: {timer or '**permanent**'}")
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f'{type(e).__name__} - {e}')
      await ctx.message.add_reaction('❌')

  @commands.command(name='unbancommanduser', aliases=['ucu'])
  @Utils.require(required=['authorized'])
  async def unban_command_user(self, ctx, command: str = None, user: discord.Member = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    # Check if command exists
    all_commands = self.bot.commands
    cont_after = False
    for garden_command in all_commands:
      if command == garden_command.name or command in garden_command.aliases:
        command = garden_command.name
        cont_after = True
      if cont_after:
        break
    if not cont_after:
      await ctx.send (f"La commande {command} n'est pas connue.")
      await ctx.message.add_reaction('❌')
      return
    # Check if user exists
    if not user:
      await ctx.send (f"User manquant.")
      await ctx.message.add_reaction('❌')
      return
    # Delete
    delete = f"delete from ban_command_user where command='{command}' and user_id='{user.id}' and guild_id='{guild_id}' ;"
    try:
      self.db.execute_order (delete)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f'{type(e).__name__} - {e}')
      await ctx.message.add_reaction('❌')

  @commands.command(name='isbanuser', aliases=['ibu'])
  @Utils.require(required=['authorized'])
  async def is_ban_user(self, ctx, user: discord.Member = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not user:
      await ctx.send ("Paramètre user manquant")
    select = (   "select command, until, user_id from ban_command_user "+
                f"where guild_id='{guild_id}' "+
                f"and user_id='{user.id}'"+
                 "order by command ASC"+
                 " ;"
             )
    fetched = self.db.fetch_all_line (select)
    if not fetched:
      await ctx.send ("Aucune commande bannie pour l'utilisateur.")
      return
    to_ret = []
    user_name = (user.name+" a.k.a."+user.display_name) if user else "user inconnu"
    to_ret_string = f"**{user_name}**\n"
    for line in fetched:
      command = line[0]
      until = line [1]
      temp = ""
      # parse until
      if until:
        # date = self.utils.format_time (until)
        date = datetime.utcfromtimestamp(until).strftime("%d/%m/%Y %H:%M:%S")
      else:
        date = "Permanent"
      temp = ( f"{command} ["+
               f"{date}]"
             )
      if len (to_ret_string) + len (temp) >= 2000:
        to_ret.append (to_ret_string)
        to_ret_string = f"**{user_name}**\n"
      to_ret_string = to_ret_string + temp + "\n"
    if len (to_ret_string):
      to_ret.append (to_ret_string)
  
    for message_to_ret in to_ret:
      await ctx.send (message_to_ret)
    print (f"to_ret: {to_ret}")
    
  @commands.command(name='listbanuser', aliases=['lbu'])
  @Utils.require(required=['authorized'])
  async def list_ban_user(self, ctx, command: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if command:
      # Check if command exists
      all_commands = self.bot.commands
      cont_after = False
      for garden_command in all_commands:
        if command == garden_command.name or command in garden_command.aliases:
          command = garden_command.name
          cont_after = True
        if cont_after:
          break
      if not cont_after:
        await ctx.send (f"La commande {command} n'est pas connue.")
        return
    select = (   "select command, until, user_id from ban_command_user "+
                f"where guild_id='{guild_id}' "+
                 (f" and command = '{command}' " if command else "")+
                 "order by command ASC"+
                 " ;"
             )
    fetched = self.db.fetch_all_line (select)
    if not fetched:
      await ctx.send ("Aucune commande bannie pour les utilisateurs."if not command else f"Aucun utilisateur banni pour la commande **{command}**.")
      return
    to_ret = []
    to_ret_string = ""
    current_command = ""
    for line in fetched:
      command = line[0]
      until = line [1]
      user_id = int (line[2])
      if not current_command == command:
        current_command = command
        to_ret_string = to_ret_string+ f"\n**{current_command}**\n"
      temp = ""
      user = ctx.guild.get_member(user_id)
      user_name = (user.name+" a.k.a."+user.display_name) if user else "user inconnu"
      # parse until
      if until:
        # date = self.utils.format_time (until)
        date = datetime.utcfromtimestamp(until).strftime("%d/%m/%Y %H:%M:%S")
      else:
        date = "Permanent"
      temp = ( f"{user_name} ["+
               f"{date}]"
             )
      if len (to_ret_string) + len (temp) >= 2000:
        to_ret.append (to_ret_string)
        to_ret_string = f"**{current_command}**\n"
      to_ret_string = to_ret_string + temp + "\n"
    if len (to_ret_string):
      to_ret.append (to_ret_string)
  
    for message_to_ret in to_ret:
      await ctx.send (message_to_ret)
    print (f"to_ret: {to_ret}")

  @commands.command(name='bancommandrole', aliases=['bcr'])
  @Utils.require(required=['authorized'])
  async def ban_command_role(self, ctx, command: str = None, role: discord.Role = None, timer: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    # Check if command exists
    all_commands = self.bot.commands
    cont_after = False
    for garden_command in all_commands:
      if command == garden_command.name or command in garden_command.aliases:
        command = garden_command.name
        cont_after = True
      if cont_after:
        break
    if not cont_after:
      await ctx.send (f"La commande {command} n'est pas connue.")
      await ctx.message.add_reaction('❌')
      return
    # Check if user exists
    if not role:
      await ctx.send (f"Rôle manquant.")
      await ctx.message.add_reaction('❌')
      return
    # Parse time
    timestamp = None
    if timer:
      timestamp = math.floor (time.time()) + self.utils.parse_time (timer)
    if not timestamp:
      timestamp = "NULL"
    # Insert/Update
    # CREATE TABLE IF NOT EXISTS `ban_command_user` (`command` VARCHAR(256) NOT NULL, `until` INTEGER, `user_id` VARCHAR(256) NOT NULL, `guild_id` VARCHAR(256) NOT NULL, PRIMARY KEY (`command`, `user_id`, `guild_id`)) ;
    select = f"select until from ban_command_role where command='{command}' and role_id='{role.id}' and guild_id='{guild_id}' ;"
    fetched = self.db.fetch_one_line (select)
    if fetched:
      sql = f"update ban_command_role set until={timestamp} where command='{command}' and role_id='{role.id}' and guild_id='{guild_id}' ;"
    else:
      sql = f"insert into ban_command_role values ('{command}', {timestamp}, '{role.id}', '{guild_id}');"
    try:
      self.db.execute_order (sql)
      await ctx.send(f"{role.name} ne peut plus utiliser la commande `{command}` pour la durée: {timer or '**permanent**'}")
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f'{type(e).__name__} - {e}')
      await ctx.message.add_reaction('❌')
    
  @commands.command(name='unbancommandrole', aliases=['ucr'])
  @Utils.require(required=['authorized'])
  async def unban_command_role(self, ctx, command: str = None, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    # Check if command exists
    all_commands = self.bot.commands
    cont_after = False
    for garden_command in all_commands:
      if command == garden_command.name or command in garden_command.aliases:
        command = garden_command.name
        cont_after = True
      if cont_after:
        break
    if not cont_after:
      await ctx.send (f"La commande {command} n'est pas connue.")
      await ctx.message.add_reaction('❌')
      return
    # Check if role exists
    if not role:
      await ctx.send (f"Role manquant.")
      await ctx.message.add_reaction('❌')
      return
    # Delete
    delete = f"delete from ban_command_role where command='{command}' and role_id='{role.id}' and guild_id='{guild_id}' ;"
    try:
      self.db.execute_order (delete)
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f'{type(e).__name__} - {e}')
      await ctx.message.add_reaction('❌')
    
    
  @commands.command(name='isbanrole', aliases=['ibr'])
  @Utils.require(required=['authorized'])
  async def is_ban_role(self, ctx, role: discord.Member = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if not role:
      await ctx.send ("Paramètre role manquant")
    select = (   "select command, until, role_id from ban_command_role "+
                f"where guild_id='{guild_id}' "+
                f"and role_id='{role.id}'"+
                 "order by command ASC"+
                 " ;"
             )
    fetched = self.db.fetch_all_line (select)
    if not fetched:
      await ctx.send ("Aucune commande bannie pour l'utilisateur.")
      return
    to_ret = []
    role_name = role.name
    to_ret_string = f"**{role_name}**\n"
    for line in fetched:
      command = line[0]
      until = line [1]
      temp = ""
      # parse until
      if until:
        # date = self.utils.format_time (until)
        date = datetime.utcfromtimestamp(until).strftime("%d/%m/%Y %H:%M:%S")
      else:
        date = "Permanent"
      temp = ( f"{command} ["+
               f"{date}]"
             )
      if len (to_ret_string) + len (temp) >= 2000:
        to_ret.append (to_ret_string)
        to_ret_string = f"**{role_name}**\n"
      to_ret_string = to_ret_string + temp + "\n"
    if len (to_ret_string):
      to_ret.append (to_ret_string)
  
    for message_to_ret in to_ret:
      await ctx.send (message_to_ret)
    print (f"to_ret: {to_ret}")
    
  @commands.command(name='listbanrole', aliases=['lbr'])
  @Utils.require(required=['authorized'])
  async def list_ban_role(self, ctx, command: str = None):
    guild_id = ctx.message.guild.id
    author = ctx.author
    if command:
      # Check if command exists
      all_commands = self.bot.commands
      cont_after = False
      for garden_command in all_commands:
        if command == garden_command.name or command in garden_command.aliases:
          command = garden_command.name
          cont_after = True
        if cont_after:
          break
      if not cont_after:
        await ctx.send (f"La commande {command} n'est pas connue.")
        return
    select = (   "select command, until, role_id from ban_command_role "+
                f"where guild_id='{guild_id}' "+
                 (f" and command = '{command}' " if command else "")+
                 "order by command ASC"+
                 " ;"
             )
    fetched = self.db.fetch_all_line (select)
    if not fetched:
      await ctx.send ("Aucune commande bannie pour les utilisateurs."if not command else f"Aucun utilisateur banni pour la commande **{command}**.")
      return
    to_ret = []
    to_ret_string = ""
    current_command = ""
    for line in fetched:
      command = line[0]
      until = line [1]
      role_id = int (line[2])
      if not current_command == command:
        current_command = command
        to_ret_string = to_ret_string+ f"\n**{current_command}**\n"
      temp = ""
      role = ctx.guild.get_role(role_id)
      role_name = role.name
      # parse until
      if until:
        # date = self.utils.format_time (until)
        date = datetime.utcfromtimestamp(until).strftime("%d/%m/%Y %H:%M:%S")
      else:
        date = "Permanent"
      temp = ( f"{role_name} ["+
               f"{date}]"
             )
      if len (to_ret_string) + len (temp) >= 2000:
        to_ret.append (to_ret_string)
        to_ret_string = f"**{current_command}**\n"
      to_ret_string = to_ret_string + temp + "\n"
    if len (to_ret_string):
      to_ret.append (to_ret_string)
  
    for message_to_ret in to_ret:
      await ctx.send (message_to_ret)
    print (f"to_ret: {to_ret}")
    
  """  
  # parse_time
  @commands.command(name='test', aliases=['t'])
  async def test(self, ctx, timer: str = None):
    seconds = self.utils.parse_time (timer)
  """