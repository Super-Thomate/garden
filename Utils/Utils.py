import math
import botconfig
from database import Database
import time


class Utils():
  def is_authorized (self, member, guild_id):
    # admin can't be blocked
    if self.is_admin(member):
      return True
    # if perm
    for obj_role in member.roles:
      if (    (obj_role.name in botconfig.config[str(guild_id)]['roles'])
           or (obj_role.id in botconfig.config[str(guild_id)]['roles'])
         ):
        return True
    return False
  
  def is_banned (self, command, member, guild_id):
    # admin can't be blocked
    if self.is_admin(member):
      return False
    db = Database()
    # ban user
    select = f"select until from ban_command_user where guild_id='{guild_id}' and user_id='{member.id}' and command='{command}' ;"
    fetched = db.fetch_one_line (select)
    if fetched:
      try:
        until = int (fetched [0])
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        return True
      if until > math.floor (time.time()): # still ban
        return True
    # ban role
    select = f"select until,role_id from ban_command_role where guild_id='{guild_id}' and command='{command}' ;"
    fetched = db.fetch_all_line (select)
    if fetched:
      for line in fetched:
        try:
          role_id = int (line [1])
        except Exception as e:
          print (f"{type(e).__name__} - {e}")
          return True
        if self.has_role(role_id, member):
          try:
            until = int (line [0])
          except Exception as e:
            print (f"{type(e).__name__} - {e}")
            return True
          if until > math.floor (time.time()): # still ban
            return True
    # neither
    return False
  
  def is_banned_user (self, command, member, guild_id):
    db = Database()
    select = f"select until from ban_command_user where guild_id='{guild_id}' and user_id='{member.id}' and command='{command}' ;"
    fetched = db.fetch_one_line (select)
    if fetched:
      try:
        until = int (fetched [0])
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        return True
      return until > math.floor (time.time()) # still ban
    return False

  def is_banned_role (self, command, member, guild_id):
    db = Database()
    select = f"select until,role_id from ban_command_role where guild_id='{guild_id}' and command='{command}' ;"
    fetched = db.fetch_one_line (select)
    if fetched:
      try:
        role_id = int (fetched [1])
      except Exception as e:
        print (f"{type(e).__name__} - {e}")
        return True
      if self.has_role(role_id, member):
        try:
          until = int (fetched [0])
        except Exception as e:
          print (f"{type(e).__name__} - {e}")
          return True
        return until > math.floor (time.time()) # still ban
    return False
  
  def is_admin (self, member):
    # if perm administrator => True
    for perm, value in member.guild_permissions:
      if perm == "administrator" and value:
        return True
    return False
  
  def is_allowed (self, member, guild_id):
    for obj_role in member.roles:
      if (    (obj_role.name in botconfig.config[str(guild_id)]['roles'])
           or (obj_role.id in botconfig.config[str(guild_id)]['roles'])
         ):
        return True
    return False
  
  def format_time(self, timestamp):
    timer = [   ["j", 86400]
              , ["h", 3600]
              , ["m", 60]
              , ["s", 1]
            ]
    current = timestamp
    print (f"current: {current}")
    to_ret = ""
    for obj_time in timer:
      if math.floor (current/obj_time [1]) > 0:
        to_ret += str(math.floor (current/obj_time [1]))+obj_time[0]+" "
        current = current%obj_time [1]
    if not len(to_ret):
      print ("to ret is empty")
    return to_ret.strip()

  def has_role (self, member, role_id):
    for obj_role in member.roles:
      if obj_role.id == int(role_id):
        return True
    return False

  def parse_time(self, timestr):
    units = {   "j": 86400
              , "h": 3600
              , "m": 60
              , "s": 1
            }
    to_ret = 0
    number = 0
    for elem in timestr:
      try:
        cast = int (elem)
      except Exception as e:
        # is it a letter in units ?
        if not elem in units:
          raise Exception (f"Unknown element: {elem}")
          return -1
        to_ret = to_ret + number * units [elem]
      else:
        number = number*10 + cast
    return to_ret
