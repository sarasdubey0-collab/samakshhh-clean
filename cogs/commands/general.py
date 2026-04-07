import asyncio
import discord
from discord.ext import commands, tasks
from discord.utils import get
import datetime
import random
import requests
from discord import app_commands
from discord import Interaction, Embed
import aiohttp
import re
from discord.ext.commands.errors import BadArgument
from discord.ext.commands import Cog
from PIL import Image, ImageDraw, ImageFont
from discord.colour import Color
import hashlib
from utils.Tools import *
from traceback import format_exception
import discord
from discord.ext import commands
import datetime
from discord.ui import Button, View
import psutil
import time
from datetime import datetime, timezone, timedelta
import sqlite3
from typing import *

password = [
  '1838812`', '382131847', '231838924', '218318371', '3145413', '43791',
  '471747183813474', '123747019', '312312318'
]
class AvatarView(View):
  def __init__(self, user, member, author_id):
    super().__init__()
    self.user = user
    self.member = member
    self.author_id = author_id


  async def interaction_check(self, interaction: discord.Interaction) -> bool:
    if interaction.user.id != self.author_id:
        embed = discord.Embed()
        embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return False
    return True

  @discord.ui.button(label='User Avatar', style=discord.ButtonStyle.secondary, custom_id='user_avatar_button')
  async def user_avatar(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        embed.set_image(url=self.user.avatar.url)
        await interaction.response.edit_message(embed=embed)

  @discord.ui.button(label='Server Avatar', style=discord.ButtonStyle.secondary, custom_id='server_avatar_button')
  async def server_avatar(self, interaction: discord.Interaction, button: Button):
    if not self.member.guild_avatar:
      await interaction.response.send_message(
        "This user doesn't have a different guild avatar.",
        ephemeral=True
      )
    else:
      embed = interaction.message.embeds[0]
      embed.set_image(url=self.member.guild_avatar.url)
      await interaction.response.edit_message(embed=embed)
    

    

class General(commands.Cog):

  def __init__(self, bot, *args, **kwargs):
    self.bot = bot

    self.aiohttp = aiohttp.ClientSession()
    self._URL_REGEX = r'(?P<url><[^: >]+:\/[^ >]+>|(?:https?|steam):\/\/[^\s<]+[^<.,:;\"\'\]\s])'
    self.color = 0x2f3136
         
        
  @commands.command(usage="<channel>", aliases=['firstmsg'], description="get the first message from a certain channel")
  @commands.cooldown(1, 6, commands.BucketType.user)
  async def firstmessage(self, ctx: commands.Context, *, channel: discord.TextChannel=None): 
    channel = channel or ctx.channel
    message = [m async for m in channel.history(oldest_first=True, limit=1)][0]
    embed = discord.Embed(color=0x6d827d, title=f"first message in {channel.name}", description=message.content, timestamp=message.created_at)
    embed.set_author(name=message.author, icon_url=message.author.display_avatar.url)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="jump to message", url=message.jump_url))
    await ctx.reply(embed=embed, view=view) 

  @commands.command(
    usage="Avatar [member]",
    name='avatar',
    aliases=['av'],
    help="""Get any member's avatar
Aliases""")
  @blacklist_check()
  @ignore_check()
  async def _user(self,
                  ctx,
                  member: Optional[Union[discord.Member,
                                         discord.User]] = None):
    if member == None or member == "":
      member = ctx.author
    user = await self.bot.fetch_user(member.id)
    webp = user.avatar.replace(format='webp')
    jpg = user.avatar.replace(format='jpg')
    png = user.avatar.replace(format='png')
    embed = discord.Embed(
      color=self.color,
      description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
      if not user.avatar.is_animated() else
      f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({user.avatar.replace(format='gif')})"
    )
    embed.set_author(name=f"{member}",
                     icon_url=member.avatar.url
                     if member.avatar else member.default_avatar.url)
    embed.set_image(url=user.avatar.url)
    embed.set_footer(text=f"Requested By {ctx.author}",
                     icon_url=ctx.author.avatar.url
                     if ctx.author.avatar else ctx.author.default_avatar.url)
    view = AvatarView(user, member, ctx.author.id)

    await ctx.send(embed=embed, view=view)

  @commands.command(name="servericon",
                           help="Shows the server icon",
                           usage="Servericon")
  @blacklist_check()
  @ignore_check()
  async def servericon(self, ctx: commands.Context):
    server = ctx.guild
    webp = server.icon.replace(format='webp')
    jpg = server.icon.replace(format='jpg')
    png = server.icon.replace(format='png')
    avemb = discord.Embed(
      color=self.color,
      title=f"{server}'s Icon",
      description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
      if not server.icon.is_animated() else
      f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp}) | [`GIF`]({server.icon.replace(format='gif')})"
    )
    avemb.set_image(url=server.icon.url)
    avemb.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=avemb)

  @commands.command(name="membercount",
                           help="Get total member count of the server",
                           usage="membercount",
                           aliases=["mc"])
  @blacklist_check()
  @ignore_check()
  async def membercount(self, ctx: commands.Context):
    online = 0
    offline = 0
    dnd = 0
    idle = 0
    bots = 0
    for member in ctx.guild.members:
      if member.status == discord.Status.online:
        online += 1
      if member.status == discord.Status.offline:
        offline += 1
      if member.status == discord.Status.dnd:
        dnd += 1
      if member.status == discord.Status.idle:
        idle += 1
      if member.bot:
        bots += 1
    embed = discord.Embed(color=self.color)
    embed.set_author(name = "Members Count", icon_url = ctx.bot.user.avatar.url)
    embed.description=(
            f"> <:MekoArrowRight:1449445989436887090> Total Members: {len(ctx.guild.members)}\n"
            f"> <:bot_icon:1449451094693642291> Bots: {bots}\n"
            f"> <:online:1449451100691496991> Online: {online}\n"
            f"> <:offline:1449451107049799784> Offline: {offline}\n"
            f"> <:idle:1449451113660284969> Idle: {idle}\n"
            f"> <:dnd:1449451120987734228> Do Not Disturb: {dnd}\n"
            )
    embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)
    
async def setup(client):
    await client.add_cog(General(client))