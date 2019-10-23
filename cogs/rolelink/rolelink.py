import discord
from discord.ext import commands

import Utils
import database
from ..logs import Logs


class RoleLink(commands.Cog):

  """
  RoleLink:
  * setrolelink role
  * unsetrolelink role
  * displayrolelinkmessage role
  """
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)

  """
  How rolelink works ?
  => create_role_link
    Manages the creation of a link between roles.
    At the creation we are asked for a link_name that is used
    to identify a specific link. This name must be unique on a
    guild.
    After having set the link_name, we are asked to add roles
    in one of the two category: role_parent and role_child.
    role_parent are the roles that triggers the event and
    role_child the roles to add or remove on the trigger.
    On adding a role_child we are asked to select if the
    role is to be added (default) or removed.
    Whenever you feel like you have finished enter done to
    validate your creation or cancel to cancel it (no recuperation).
  => edit_role_link
  """
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    # guild id
    guild_id = before.guild.id
    if not Utils.is_loaded ("rolelink", guild_id):
      return
    # all roles to listen
    select = f"select role_id from rolelink_role where guild_id='{guild_id}'"
    fetched = database.fetch_all_line (select)
    for line in fetched:
      role_id = line [0]
      if (     not Utils.has_role (before, role_id)
           and Utils.has_role (after, role_id)
         ):
        # The member obtained the role
        print ('The member obtained the role')
        select = f"select message from rolelink_message where guild_id='{guild_id}'and role_id='{role_id}' ;"
        fetched = database.fetch_one_line (select)
        if fetched:
          message = (fetched [0]).replace("$member", before.mention).replace("$role", f"<@&{role_id}>")
        else:
          message = Utils.get_text(guild_id, 'welcome_user_welcome_message_not_found').format(before.mention)
        # send
        await before.send (message)

  @commands.command(name='setrolelink', aliases=['rolelink'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_rolelink_role(self, ctx, *, link_id: str = None):
    """
    Set rolelink role
    @params discord.Role role
    """
    guild_id                 = ctx.guild.id
    print ("HELLO")
    if not link_id:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<link_id>'))
      await ctx.message.add_reaction('❌')
      return
    check_text               = lambda m: m.channel == ctx.channel and m.author == ctx.author
    ask_role                 = await ctx.send(Utils.get_text(guild_id, "ask_role_linked"))
    msg_role                 = await self.bot.wait_for('message', check=check_text)
    role                     = Utils.get_role (msg_role)
    if not role:
      await ctx.send(Utils.get_text(ctx.guild.id, "bad_role").format(msg_role.content))
      await ctx.message.add_reaction('❌')
      return
    role_id                  = role.id
    validate                 = False
    cancel                   = False
    roles_linked             = []
    instruction              = await ctx.send(Utils.get_text(guild_id, "instruction_role_linked"))
    while not validate and not cancel:
      ask                    = await ctx.send(Utils.get_text(guild_id, "ask_role_linked"))
      msg                    = await self.bot.wait_for('message', check=check_text)
      if msg.content.lower() in ["cancel", "annuler"]:
        cancel               = True
      elif msg.content.lower() in ["valider", "done"]:
        validate             = True
      else:
        role_to_link         = Utils.get_role (msg)
        if not role_to_link:
          await ctx.send (Utils.get_text(guild_id, "bad_role").format(msg.content))
        else:
          roles_linked.append(role_to_link)
      await ask.delete (delay=0.2)
      await msg.delete (delay=0.2)
    await instruction.delete (delay=0.5)
    if cancel:
       await ctx.send("**KO**")
       await ctx.message.add_reaction('❌')
       return
    error                    = False
    for role_linked in roles_linked:
      select_num             = (   "select MAX(link_num) "+
                                   "from rolelink_role "+
                                   "where "+
                                   "link_id = ? "+
                                   "and "+
                                   "guild_id = ? "+
                                   ";"
                               )
      fetch_num              = database.select_one_line(select_num, [link_id, guild_id])
      link_num               = 0
      if fetch_num:
        link_num             = fetch_num + 1
      insert                 = ("insert into rolelink_role "+
                                "(`link_id`, `link_num`, `role_id`, `role_linked`, `guild_id`)"+
                                " values "+
                                "(?, ?, ?, ?, ?) ;"
                               )
      try:
        database.execute_order(sql, [link_id, link_num, role_id, role_linked.id, guild_id])
      except Exception as e:
        error                = True
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')

  @commands.command(name='unsetrolelink')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def unset_rolelink_role(self, ctx):
    """
    Unset rolelink complete
    """
    guild_id = ctx.guild.id
    await ctx.send(Utils.get_text(guild_id, "instruction_unset_rolelink").format())
    try:
      database.execute_order(sql, [])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      error = True
      await ctx.message.add_reaction('❌')

  @commands.command(name='displayrolelink')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def display_rolelink_message(self, ctx, *, role: discord.Role = None):
    guild_id = ctx.message.guild.id
    if not role:
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<role>'))
      await ctx.message.add_reaction('❌')
      return
    role_id = role.id
    sql = f"select message from rolelink_message where guild_id='{guild_id}' and role_id='{role_id}' ;"
    prev_rolelink_message = database.fetch_one_line (sql)
    if not prev_rolelink_message:
      await ctx.channel.send(Utils.get_text(ctx.guild.id, "no_message_defined_for_role").format(role.name))
    else:
      await ctx.channel.send (prev_rolelink_message[0])
  """
  ## VOTE LISTENER
  @commands.Cog.listener()
  async def on_reaction_add(self, reaction, user):
    if not reaction.message.guild:
      return
    message_id               = reaction.message.id
    guild_id                 = reaction.message.guild.id
    emoji                    = reaction.emoji

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    message_id               = payload.message_id
    guild_id                 = payload.guild_id
    channel_id               = payload.channel_id
    emoji                    = payload.emoji
    user_id                  = payload.user_id
  """