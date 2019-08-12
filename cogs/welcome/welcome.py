import discord
from discord.ext import commands
from datetime import datetime
from ..logs import Logs
from database import Database
from Utils import Utils


class Welcome(commands.Cog):
 
  """
  PublicWelcome:
  setwelcomechannel [channel_id]
  setwelcomemessage message
  setwelcomerole role_id
  """
  def __init__(self, bot):
    self.bot = bot
    self.utils = Utils()
    self.logger = Logs(self.bot)
    self.db = Database()

  @commands.Cog.listener()
  async def on_member_update(self, before, after):
    # guild id
    guild_id = before.guild.id
    # all roles to listen
    select = f"select role_id from welcome_role where guild_id='{guild_id}'"
    fetched = self.db.fetch_all_line (select)
    for line in fetched:
      role_id = line [0]
      if (     not self.utils.has_role (before, role_id)
           and self.utils.has_role (after, role_id)
         ):
        # The member obtained the role
        print ('The member obtained the role')
        # get the channel
        channel = None
        select = f"select channel_id from welcome_channel where guild_id='{guild_id}'"
        fetched = self.db.fetch_one_line (select)
        if fetched:
           channel_id = fetched [0]
           channel = before.guild.get_channel (int(channel_id))
        if not channel:
          print ('Not channel')
          channel = before.guild.system_channel
        # get the message
        select = f"select message from welcome_message where guild_id='{guild_id}'"
        fetched = self.db.fetch_one_line (select)
        if fetched:
           message = (fetched [0]).replace("$member", before.mention)
        else:
           message = f"Welcome {before.mention} !"
        # send
        await channel.send (message)

  @commands.command(name='setwelcomerole', aliases=['swr', 'welcomerole'])
  async def set_welcome_role(self, ctx, *, role: discord.Role = None):
    """
    Set welcome role
    @params discord.Role role
    """
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (ctx.author, guild_id):
      print ("Missing permissions")
      return
    if not role:
      # error
      await cx.send ("A role is required.")
      await self.logger.log('nickname_log', ctx.author, ctx.message, True)
      return
    role_id = role.id
    select = f"select role_id from welcome_role where guild_id='{guild_id}'"
    fetched = self.db.fetch_one_line (select)
    if fetched:
      sql = f"update welcome_role set role_id='{role_id}' where guild_id='{guild_id}' "
    else:
      sql = f"insert into welcome_role values ('{role_id}', '{guild_id}')"
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
    # await self.logger.log('welcome_log', ctx.author, ctx.message, error) # no logs    

  @commands.command(name='setwelcomechannel', aliases=['swc', 'welcomechannel', 'wc'])
  async def set_welcome(self, ctx, *, channel: discord.TextChannel = None):
    """
    Set the welcome channel
    @params discord.TextChannel channel
    The text channel for the welcome message.
    If not provided, the current channel.
    """
    channel = channel or ctx.channel
    guild_id = ctx.guild.id
    if not self.utils.is_authorized (ctx.author, guild_id):
      print ("Missing permissions")
      return
    error = False
    select = f"select * from welcome_channel where guild_id='{guild_id}''"
    fetched = self.db.fetch_one_line (select)
    if not fetched:
      sql = f"insert into welcome_channel values ('{channel.id}', '{guild_id}')"
    else:
      sql = f"update welcome_channel set channel_id='{channel.id}' where guild_id='{guild_id}'"
    try:
      self.db.execute_order (sql, [])
    except Exception as e:
      await message.channel.send (f'Inscription en db fail !')
      print (f'{type(e).__name__} - {e}')
      error = True
    # Log my change
    if error:
      await ctx.message.add_reaction('❌')
    else:
      await ctx.message.add_reaction('✅')
    # await self.logger.log('welcome_log', ctx.author, ctx.message, error) # no logs    

  @commands.command(name='setwelcomemessage', aliases=['welcomemessage', 'swm'])
  async def set_welcome_message(self, ctx, *args):
    guild_id = ctx.message.guild.id
    member = ctx.author
    if not self.utils.is_authorized (member, guild_id):
      print ("Missing permissions")
      return
    message = ' '.join(arg for arg in args)
    # message = re.escape(message)
    sql = f"select message from welcome_message where guild_id='{guild_id}'"
    prev_galerie_message = self.db.fetch_one_line (sql)
    if not prev_galerie_message:
      sql = f"INSERT INTO welcome_message VALUES (?, '{guild_id}')"
    else:
      sql = f"update welcome_message set message=? where guild_id='{guild_id}'"
    print (sql)
    try:
      self.db.execute_order(sql, [message])
    except Exception as e:
      print (f"{type(e).__name__} - {e}")
    await ctx.channel.send (f"Nouveau message : `{message}`")
    # await self.logger.log('welcome_log', ctx.author, ctx.message, error) # no logs