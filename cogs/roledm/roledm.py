import discord
from discord.ext import commands
from Utils import Utils
from ..logs import Logs
from database import Database


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
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()
    self.language_code = 'fr'
  
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    # guild id
    guild_id = before.guild.id
    # all roles to listen
    select = f"select role_id from roledm_role where guild_id='{guild_id}'"
    fetched = self.db.fetch_all_line (select)
    for line in fetched:
      role_id = line [0]
      if (     not self.utils.has_role (before, role_id)
           and self.utils.has_role (after, role_id)
         ):
        # The member obtained the role
        print ('The member obtained the role')
        select = f"select message from roledm_message where guild_id='{guild_id}'and role_id='{role_id}' ;"
        fetched = self.db.fetch_one_line (select)
        if fetched:
          message = (fetched [0]).replace("$member", before.mention).replace("$role", f"<@&{role_id}>")
        else:
          message = self.utils.get_text(self.language_code, 'welcome_user_welcome_message_not_found').format(before.mention)
        # send
        await before.send (message)

  @commands.command(name='setroledm', aliases=['sr', 'roledm'])
  async def set_roledm_role(self, ctx, *, role: discord.Role = None):
    """
    Set roledm role
    @params discord.Role role
    """
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (ctx.author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not role:
      # error
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    role_id = role.id
    sql = f"insert into roledm_role values ('{role_id}', '{guild_id}')"
    error = False
    print (sql)
    try:
      self.db.execute_order(sql, [])
    except Exception as e:
      error = True
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='unsetroledm', aliases=['ur', 'uroledm'])
  async def unset_roledm_role(self, ctx, *, role: discord.Role = None):
    """
    Unset roledm role
    @params discord.Role role
    """
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (ctx.author, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not role:
      # error
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    role_id = role.id
    sql = f"delete roledm_role where guild_id='{guild_id}'and role_id='{role_id}' ;"
    error = False
    print (sql)
    try:
      self.db.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      error = True
      await ctx.message.add_reaction('❌')

  @commands.command(name='setroledmmessage', aliases=['roledmmessage', 'srm'])
  async def set_roledm_message(self, ctx, *, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not role:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    await ctx.send(self.utils.get_text(self.language_code, "ask_new_welcome_message"))
    check = lambda m: m.channel == ctx.channel and m.author == ctx.author
    msg = await self.bot.wait_for('message', check=check)
    message = msg.content
    role_id = role.id
    sql = f"select message from roledm_message where guild_id='{guild_id}' and role_id='{role_id}' ;"
    prev_roledm_message = self.db.fetch_one_line (sql)
    if not prev_roledm_message:
      sql = f"INSERT INTO roledm_message VALUES (?, '{role_id}', '{guild_id}') ;"
    else:
      sql = f"update roledm_message set message=? where guild_id='{guild_id}'and role_id='{role_id}' ;"
    print (sql)
    try:
      self.db.execute_order(sql, [message])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      return
    await ctx.channel.send (self.utils.get_text(self.language_code, 'display_new_message').format(message))
 
  @commands.command(name='displayroledmmessage', aliases=['drm'])
  async def display_roledm_message(self, ctx, *, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    if self.utils.is_banned (ctx.command, ctx.author, ctx.guild.id):
      await ctx.message.add_reaction('❌')
      await ctx.author.send(self.utils.get_text(self.language_code, "user_unauthorized_use_command"))
      return
    if not role:
      await ctx.send(self.utils.get_text(self.language_code, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    role_id = role.id
    sql = f"select message from roledm_message where guild_id='{guild_id}' and role_id='{role_id}' ;"
    prev_roledm_message = self.db.fetch_one_line (sql)
    if not prev_roledm_message:
      await ctx.channel.send (f"Aucun message de définit pour le role {role.name}")
    else:
      await ctx.channel.send (prev_roledm_message[0])