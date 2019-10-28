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

  @commands.command(name='createrolelink', aliases=['createlink'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def create_rolelink_role(self, ctx, *, link_id: str):
    """
    Create rolelink link
    @params str link_id
    """
    guild_id                 = ctx.guild.id
    if not link_id:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<link_id>'))
      await ctx.message.add_reaction('❌')
      return
    select                   = "select count(*) from rolelink_link where link_id=? and guild_id=? ;"
    fetched                  = database.fetch_one_line (select, [link_id, guild_id])
    if fetched and fetched [0] > 0:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "rolelink_link_already").format(link_id))
      await ctx.message.add_reaction('❌')
      return
    insert                   = "insert into rolelink_link (`link_id`, `role_id`, `guild_id`) values (?, NULL, ?) ;"
    try:
      database.execute_order (insert, [link_id, guild_id])
    except Exception as e:
      print(f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      await ctx.send (Utils.get_text(ctx.guild.id, "rolelink_error").format(type(e).__name__))
    else:
      await ctx.message.add_reaction('✅')
      feedback               = await ctx.send (Utils.get_text(ctx.guild.id, "create_link_success").format(link_id))
      await feedback.delete (delay=2)
      await ctx.message.delete (delay=2)
      
  @commands.command(name='setroleparent', aliases=['setparent', 'setrolelinkparent'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def set_rolelink_parent_role(self, ctx, link_id: str, role_parent: discord.Role):
    """
    Set rolelink parent role
    @params str link_id
    @params discord.Role role_parent
    """
    guild_id                 = ctx.guild.id
    if not link_id:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<link_id>'))
      await ctx.message.add_reaction('❌')
      return
    if not role_parent:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<role_parent>'))
      await ctx.message.add_reaction('❌')
      return
    select                   = "select count(*) from rolelink_link where link_id=? and guild_id=? ;"
    fetched                  = database.fetch_one_line (select, [link_id, guild_id])
    if not fetched or fetched [0] == 0:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "rolelink_link_undefined").format(link_id))
      await ctx.message.add_reaction('❌')
      return
    update_link              = "update rolelink_link set role_id=? where link_id=? and guild_id=? ;"
    try:
      database.execute_order (update_link, [role_parent.id, link_id, guild_id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      await ctx.send (Utils.get_text(ctx.guild.id, "rolelink_error").format(type(e).__name__))
      
  @commands.command(name='addrolelink', aliases=['addrole', 'addrolelinkrole'])
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def add_rolelink_role(self, ctx, link_id: str, role_child: discord.Role):
    """
    Set rolelink parent role
    @params str link_id
    @params discord.Role role_child
    """
    guild_id                 = ctx.guild.id
    if not link_id:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<link_id>'))
      await ctx.message.add_reaction('❌')
      return
    if not role_child:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<role_parent>'))
      await ctx.message.add_reaction('❌')
      return
    select                   = "select role_id from rolelink_link where link_id=? and guild_id=? ;"
    fetched                  = database.fetch_one_line (select, [link_id, guild_id])
    if not fetched:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "rolelink_link_undefined").format(link_id))
      await ctx.message.add_reaction('❌')
      return
    if not fetched [0]:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "rolelink_parent_undefined").format(link_id))
      await ctx.message.add_reaction('❌')
      return
    role_id                  = fetched [0]
    if role_id == role_child.id:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "rolelink_parent_children").format(str(role_child)))
      await ctx.message.add_reaction('❌')
      return
      
    select                   = "select role_linked from rolelink_role where link_id=? and guild_id=? ;"
    fetched                  = database.fetch_all_line (select, [link_id, guild_id])
    if fetched:
      for role_id in fetched:
        if int(role_id[0]) == role_child.id:
           # error
           await ctx.send(Utils.get_text(ctx.guild.id, "rolelink_children_already").format(str(role_child)))
           await ctx.message.add_reaction('❌')
           return
    insert_roles             = "insert into rolelink_role (`link_id`, `role_linked`, `guild_id`) values (?, ?, ?) ;"
    try:
      database.execute_order (insert_roles, [link_id, role_child.id, guild_id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
      await ctx.message.add_reaction('❌')
      await ctx.send (Utils.get_text(ctx.guild.id, "rolelink_error").format(type(e).__name__))

  @commands.command(name='unsetrolelink')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def unset_rolelink_role(self, ctx, link_id: str):
    """
    Unset rolelink complete
    @params str role_link
    """
    guild_id                 = ctx.guild.id
    if not link_id:
      # error
      await ctx.send(Utils.get_text(ctx.guild.id, "parameter_is_mandatory").format('<link_id>'))
      await ctx.message.add_reaction('❌')
      return
    delete_link              = "delete from rolelink_link where link_id=? and guild_id=? ;"
    delete_role              = "delete from rolelink_role where link_id=? and guild_id=? ;"
    try:
      database.execute_order(delete_link, [link_id, guild_id])
      database.execute_order(delete_role, [link_id, guild_id])
      await ctx.message.add_reaction('✅')
    except Exception as e:
      await ctx.message.add_reaction('❌')
      await ctx.send (Utils.get_text(ctx.guild.id, "rolelink_error").format(type(e).__name__))

  @commands.command(name='displayrolelink')
  @Utils.require(required=['authorized', 'not_banned', 'cog_loaded'])
  async def display_rolelink_message(self, ctx, by_type: str, parameter: str=None):
    guild_id = ctx.message.guild.id
    if not by_type:
      await ctx.send(Utils.get_text(guild_id, "parameter_is_mandatory").format('<by_type>'))
      await ctx.message.add_reaction('❌')
      return
    if not by_type in ["all", "role", "link"]:
      await ctx.send(Utils.get_text(guild_id, "parameter_must_be").format("<by_type>", "`all`, `role`, `link`"))
      await ctx.message.add_reaction('❌')
      return
    number_of_field_max      = 25
    number_of_char_max       = 1024
    all_embeds               = []
    if by_type == "all":
      select                 = "select link_id, role_id from rolelink_link where guild_id=? ;"
      all_fetched            = database.fetch_all_line (select, [guild_id])
      if not all_fetched or len(all_fetched) == 0:
        await ctx.send(Utils.get_text(guild_id, "rolelink_no_link").format())
      else:
        embed                = self.create_embed (Utils.get_text(guild_id, "rolelink_display_link"))
        for line in all_fetched:
          link_id            = line [0]
          role_id            = line [1]
          select_role        = "select role_linked from rolelink_role where link_id=? and guild_id=? ;"
          fetched_role       = database.fetch_all_line (select_role, [link_id, guild_id])
          if (len (embed.fields) >= number_of_field_max):
            all_embeds.append(embed)
            embed            = self.create_embed (Utils.get_text(guild_id, "rolelink_display_link"))
          field_title        = "**"+link_id+"** "+str(ctx.guild.get_role(role_id)) or Utils.get_text(guild_id, "rolelink_no_role")
          field_value        = ""
          for line_role in fetched_role:
            item             = str (ctx.guild.get_role(line_role[0]))+"\n"
            if len(field_value)+len(item) > number_of_char_max:
              field_value   += "[...]\n"
            else:
              field_value   += item
          if len(field_value) == 0:
            field_value      = Utils.get_text(guild_id, "rolelink_no_role")
          embed.add_field(name=field_title, value=field_value, inline=False)
      all_embeds.append(embed)
      for one_embed in all_embeds:
        await ctx.send (embed=one_embed)
    elif by_type == "role":
      if not parameter:
        await ctx.send(Utils.get_text(guild_id, "parameter_is_mandatory").format('<role>'))
        await ctx.message.add_reaction('❌')
        return
      if not parameter.isnumeric():
        await ctx.send(Utils.get_text(guild_id, "parameter_be_numeric").format('<role>'))
        await ctx.message.add_reaction('❌')
        return
      select_parent          = "select link_id from rolelink_link where role_id=? and guild_id=? ;" 
      fetched_parent         = database.fetch_all_line(select_parent, [parameter, guild_id])
      if not fetched_parent:
        await ctx.send(Utils.get_text(guild_id, "rolelink_no_link_for_role").format(parameter))
      else:
         x = 1
    elif by_type == "link":
      if not parameter:
        await ctx.send(Utils.get_text(guild_id, "parameter_is_mandatory").format('<link_id>'))
        await ctx.message.add_reaction('❌')
        return
    
  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    # guild id
    guild_id = before.guild.id
    if not Utils.is_loaded ("rolelink", guild_id):
      return
    # all roles to listen
    select = f"select role_linked from rolelink_role where guild_id='{guild_id}'"
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


  def create_embed(self, title, description=""):
    colour                   = discord.Colour(0)
    colour                   = colour.from_rgb(56, 255, 56)
    embed                    = discord.Embed(colour=colour)
    embed.title              = title
    if len(description):
      embed.description      = description
    return embed


