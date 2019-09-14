import math
import botconfig
from database import Database
import time
import sys
import inspect


class Utils():
  def is_authorized (self, member, guild_id):
    # admin can't be blocked
    if self.is_admin(member):
      return True
    # if perm
    return self.is_allowed (member, guild_id)

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
      if (    (obj_role.id in self.get_roles_modo (guild_id))
           or (obj_role.name in botconfig.config[str(guild_id)]['roles'])
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
    try:
      for obj_role in member.roles:
        if obj_role.id == int(role_id):
          return True
    except Exception as e:
      print (f" {type(e).__name__} - {e}")
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

  def get_roles_modo (self, guild_id):
    db                       = Database()
    all_roles                = []
    select                   = (  "select   role_id "+
                                  "from     config_role "+
                                  "where "+
                                  "          permission=1 "+
                                  "      and "+
                                 f"          guild_id='{guild_id}' "+
                                  ";"+
                                  ""
                               )
    try:
      fetched                  = db.fetch_all_line (select)
    except Exception as e:
      print (f"get_roles_modo {type(e).__name__} - {e}")
    if fetched:
      for role_fetched in fetched:
        all_roles.append(role_fetched [0])
    return all_roles

  def debug(self, message):
    """
    Debug function, to use rather than print (message)
    https://stackoverflow.com/questions/6810999/how-to-determine-file-function-and-line-number
    """
    info                     = inspect.getframeinfo((inspect.stack()[1])[0])
    print (sys._getframe().f_lineno)
    print (info.filename, 'func=%s' % info.function, 'line=%s:' % info.lineno, message)

  def do_invite (self, guild_id):
    db                       = Database ()
    select                   = (  "select   do "+
                                  "       , type_do"+
                                  "from     config_do "+
                                  "where "+
                                  "          type_do='invite' "+
                                  "      and "+
                                 f"          guild_id='{guild_id}' "+
                                  ";"+
                                  ""
                               )
    fetched                  = db.fetch_one_line (select)
    if fetched:
      return (fetched [0] == 1)
    return False

  def do_token (self, guild_id):
    db                       = Database ()
    select                   = (  "select   do "+
                                  "       , type_do"+
                                  "from     config_do "+
                                  "where "+
                                  "          type_do='token' "+
                                  "      and "+
                                 f"          guild_id='{guild_id}' "+
                                  ";"+
                                  ""
                               )
    fetched                  = db.fetch_one_line (select)
    if fetched:
      return (fetched [0] == 1)
    return False

  def invite_delay (self, guild_id):
    db                       = Database ()
    select                   = (  "select   delay "+
                                  "       , type_delay"+
                                  "from     config_delay "+
                                  "where "+
                                  "          type_delay='invite' "+
                                  "      and "+
                                 f"          guild_id='{guild_id}' "+
                                  ";"+
                                  ""
                               )
    fetched                  = db.fetch_one_line (select)
    if fetched:
      return fetched [0]
    return None

  def nickname_delay (self, guild_id):
    db                       = Database ()
    select                   = (  "select   delay "+
                                  "       , type_delay"+
                                  "from     config_delay "+
                                  "where "+
                                  "          type_delay='nickname' "+
                                  "      and "+
                                 f"          guild_id='{guild_id}' "+
                                  ";"+
                                  ""
                               )
    fetched                  = db.fetch_one_line (select)
    if fetched:
      return fetched [0]
    return None

  def invite_url (self, guild_id):
    db                       = Database ()
    select                   = (  "select   url "+
                                  "       , type_url"+
                                  "from     config_url "+
                                  "where "+
                                  "          type_url='invite' "+
                                  "      and "+
                                 f"          guild_id='{guild_id}' "+
                                  ";"+
                                  ""
                               )
    fetched                  = db.fetch_one_line (select)
    if fetched:
      return fetched [0]
    return ""

  def token_url (self, guild_id):
    db                       = Database ()
    select                   = (  "select   url "+
                                  "       , type_url"+
                                  "from     config_url "+
                                  "where "+
                                  "          type_url='token' "+
                                  "      and "+
                                 f"          guild_id='{guild_id}' "+
                                  ";"+
                                  ""
                               )
    fetched                  = db.fetch_one_line (select)
    if fetched:
      return fetched [0]
    return ""