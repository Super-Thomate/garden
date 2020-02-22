from datetime import datetime

import discord
from discord.ext import commands

import Utils
import database
from core import logger

class Megapin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  async def __try_fetch_message(self, id, guild: discord.Guild):
    try:
      id = int(id)
      sql = "SELECT channel_id FROM megapin_table WHERE message_id=? AND guild_id=? ;"
      response = database.fetch_one_line(sql, [id, guild.id])
      channel = guild.get_channel(int(response[0]))
      msg = await channel.fetch_message(id)
      return msg
    except Exception:
      return None

  @commands.command(name="addmegapin", aliases=['amp'])
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def add_megapin(self, ctx, channel: discord.TextChannel, span):
    try:
      span = int(span)
      if span < 1:
        raise ValueError
    except ValueError:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_span_invalid"))
      return

    ask_message = await ctx.send(Utils.get_text(ctx.guild.id, "megapin_ask_message"))
    response = await self.bot.wait_for('message', check=lambda m: m.channel == ctx.channel and m.author == ctx.author)
    msg = await channel.send(response.content)

    await Utils.delete_messages(ask_message, response, ctx.message)
    sql = "INSERT INTO megapin_table (`message_id`, `channel_id`, `span`, `preview`, `guild_id`, `last_pin`) VALUES (?, ?, ?, ?, ?, ?) ;"
    try:
      now = int(datetime.now().timestamp())
      database.execute_order(sql, [msg.id, channel.id, span, msg.content[:20] + "...", ctx.guild.id, now])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_add_success").format(channel.mention))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::add_megapin", f"{type(e).__name__} - {e}")

  @commands.command(name="deletemegapin", aliases=['dmp'])
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def delete_megapin(self, ctx, id):
    msg = await self.__try_fetch_message(id, ctx.guild)
    if not msg:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_id_invalid"))
      await ctx.message.add_reaction('❌')
      return

    sql = "DELETE FROM megapin_table WHERE message_id=? AND guild_id=? ;"
    try:
      database.execute_order(sql, [id, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_delete_success"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::delete_megapin", f"{type(e).__name__} - {e}")

  @commands.command(name="editmegapinchannel", aliases=['empc'])
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def edit_megapin_channel(self, ctx, id, channel: discord.TextChannel):
    msg = await self.__try_fetch_message(id, ctx.guild)
    if not msg:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_id_invalid"))
      await ctx.message.add_reaction('❌')
      return

    msg = await channel.send(msg.content)
    sql = "UPDATE megapin_table SET message_id=?, channel_id=? WHERE message_id=? AND guild_id=? ;"

    try:
      database.execute_order(sql, [msg.id, channel.id, id, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_edit_success"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::edit_megapin_channel", f"{type(e).__name__} - {e}")

  @commands.command(name="editmegapinspan", aliases=['emps'])
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def edit_megapin_span(self, ctx, id, span):
    try:
      span = int(span)
      if span < 1:
        raise ValueError
    except ValueError:
      await ctx.send(Utils.get_text(ctx.guild.id, "megapin_span_invalid"))
      return

    sql = "UPDATE megapin_table SET span=? WHERE message_id=? AND guild_id=? ;"
    try:
      database.execute_order(sql, [span, id, ctx.guild.id])
      await ctx.send(Utils.get_text(ctx.guild.id,  "megapin_edit_success"))
    except Exception as e:
      await ctx.send(Utils.get_text(ctx.guild.id, 'error_database_writing'))
      logger("megapin::edit_megapin_span", f"{type(e).__name__} - {e}")

  @commands.command(name="listmegapin", aliases=['lmp'])
  @commands.guild_only()
  @Utils.require(required=['not_banned', 'cog_loaded'])
  async def list_mega_pin(self, ctx):
    sql = "SELECT message_id, channel_id, span, preview FROM megapin_table WHERE guild_id=? ;"
    response = database.fetch_all_line(sql, [ctx.guild.id])

    embed = discord.Embed(colour=discord.Colour(0).from_rgb(176, 255, 176),
                          title=Utils.get_text(ctx.guild.id, 'megapin_list'))
    for megapin in response:
      channel = ctx.guild.get_channel(int(megapin[1]))
      text = f"{megapin[0]} | {channel.mention} | {megapin[2]} minute(s) | {megapin[3]}"
      embed.add_field(name=Utils.get_text(ctx.guild.id, 'megapin_field'), value=text, inline=False)

    await ctx.send(content=None, embed=embed)