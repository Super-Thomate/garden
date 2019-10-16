import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs


class RoleDM(commands.Cog):

  """
  RoleDM:
  * setroledm role
  * unsetroledm role
  * setroledmmessage role
  * displayroledmmessage role
  """
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    # guild id
    guild_id = before.guild.id
    print (   "roledm on_member_update => "+
             f"{before.display_name}\n"+
             "  Before:\n"+
            f"    Status: {before.status}\n"+
            f"    Activity: {before.activities}\n"+
            f"    Nickname: {before.nick}\n"+
            f"    Roles: {before.roles}\n"+
             "  After:\n"+
            f"    Status: {after.status}\n"+
            f"    Activity: {after.activities}\n"+
            f"    Nickname: {after.nick}\n"+
            f"    Roles: {after.roles}\n"+
             ""
          )
    if not Utils.is_loaded ("roledm", guild_id):
      return
    # all roles to listen
    select = f"select role_id from roledm_role where guild_id='{guild_id}'"
    fetched = database.fetch_all_line (select)
    for line in fetched:
      role_id = line [0]
      if (     not Utils.has_role (before, role_id)
           and Utils.has_role (after, role_id)
         ):
        # The member obtained the role
        print ('The member obtained the role')
        select = f"select message from roledm_message where guild_id='{guild_id}'and role_id='{role_id}' ;"
        fetched = database.fetch_one_line (select)
        if fetched:
          message = (fetched [0]).replace("$member", before.mention).replace("$role", f"<@&{role_id}>")
        else:
          message = Utils.get_text(guild_id, 'welcome_user_welcome_message_not_found').format(before.mention)
        # send
        await before.send (message)

  @commands.command(name='setroledm', aliases=['sr', 'roledm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_roledm_role(self, ctx, *, role: discord.Role = None):
    """
    Set roledm role
    @params discord.Role role
    """
    guild_id = ctx.guild.id
    if not role:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    role_id = role.id
    sql = f"insert into roledm_role values ('{role_id}', '{guild_id}')"
    error = False
    print (sql)
    try:
      database.execute_order(sql, [])
    except Exception as e:
      error = True
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='unsetroledm', aliases=['ur', 'uroledm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def unset_roledm_role(self, ctx, *, role: discord.Role = None):
    """
    Unset roledm role
    @params discord.Role role
    """
    guild_id = ctx.guild.id
    if not role:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    role_id = role.id
    sql = f"delete roledm_role where guild_id='{guild_id}'and role_id='{role_id}' ;"
    error = False
    print (sql)
    try:
      database.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      error = True
      await ctx.message.add_reaction('❌')

  @commands.command(name='setroledmmessage', aliases=['roledmmessage', 'srm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_roledm_message(self, ctx, *, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not role:
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    await ctx.send(Utils.get_text(ctx.guild.id, "ask_new_welcome_message"))
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    message = msg.content
    role_id = role.id
    sql = f"select message from roledm_message where guild_id='{guild_id}' and role_id='{role_id}' ;"
    prev_roledm_message = database.fetch_one_line (sql)
    if not prev_roledm_message:
      sql = f"INSERT INTO roledm_message VALUES (?, '{role_id}', '{guild_id}') ;"
    else:
      sql = f"update roledm_message set message=? where guild_id='{guild_id}'and role_id='{role_id}' ;"
    print (sql)
    try:
      database.execute_order(sql, [message])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.channel.send (Utils.get_text(ctx.guild.id, 'display_new_message').format(message))
 
  @commands.command(name='displayroledmmessage', aliases=['drm'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def display_roledm_message(self, ctx, *, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    if not role:
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    role_id = role.id
    sql = f"select message from roledm_message where guild_id='{guild_id}' and role_id='{role_id}' ;"
    prev_roledm_message = database.fetch_one_line (sql)
    if not prev_roledm_message:
      await ctx.channel.send(Utils.get_text(ctx.guild.id, "no_message_defined_for_role").format(role.name))
    else:
      await ctx.channel.send (prev_roledm_message[0])