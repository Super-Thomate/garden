from discord.ext import commands
from ..logs import Logs
import Utils

rules = {
  "1⃣": "1",
  "2⃣": "2",
  "3⃣": "3",
  "4⃣": "4",
  "5⃣": "5",
  "6⃣": "6",
  "7⃣": "7",
  "8⃣": "8",
  "9⃣": "9",
  "🔟": "10",
}
reacted_message = []

class Moderation(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.logger = Logs(self.bot)


  @commands.Cog.listener('on_message')
  async def all_caps_emoji(self, message):
    if (message.guild is None):
      return
    if (message.author.id == self.bot.user.id):
      return
    if not Utils.is_loaded ("moderation", message.guild.id):
      return
    if len (message.content) > 5 and message.content.isupper():
      await message.add_reaction ("<:CapsLock:621629196359303168>")
    return

  @commands.Cog.listener('on_message_edit')
  async def all_caps_emoji_edit(self, before, after):
    if (before.guild is None) or (after.guild is None):
      return
    if (before.author.id == self.bot.user.id):
      return
    if not Utils.is_loaded ("moderation", before.guild.id):
      return
    if len (after.content) > 5 and after.content.isupper():
      await after.add_reaction ("<:CapsLock:621629196359303168>")
    if (     (len (before.content) > 5 and before.content.isupper())
         and (not after.content.isupper())
       ):
      await after.remove_reaction ("<:CapsLock:621629196359303168>", self.bot.user)
    return

  @commands.Cog.listener('on_raw_reaction_add')
  async def display_rule(self, payload):
    # member = self.bot.get_user(payload.user_id)
    # Attention get_user renvoie un discord.User qui n'est pas la même chose
    # qu'un discord.Member. Notamment un User n'a pas de rôle, on ne peut donc
    # pas appeler is_authorized dessus.
    guild                    = self.bot.get_guild (payload.guild_id)
    member                   = guild.get_member (payload.user_id)
    if not payload.guild_id or not Utils.is_authorized(member, payload.guild_id):
      return
    try:
      rule_number = rules[payload.emoji.name]
    except KeyError:
      return
    if (payload.message_id, rule_number) in reacted_message:
      print(f"Message {payload.message_id} has already been rule-reacted by a moderator")
      return
    channel = self.bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    await message.author.send(Utils.get_text(payload.guild_id, f"rule{rule_number}"))
    reacted_message.append((payload.message_id, rule_number))
    print(f'Sent DM about rule number {rule_number} to {message.author.display_name}')