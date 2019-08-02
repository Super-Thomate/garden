import math
import botconfig


class Utils():
  def has_role (self, member, guild_id):
    # if perm administrator => True
    for perm, value in member.guild_permissions:
      if perm == "administrator" and value:
        return True
    # else roles allowed
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
    return to_ret

