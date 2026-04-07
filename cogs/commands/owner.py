from __future__ import annotations
from discord.ext import commands
from utils.config import BotName
from utils.Tools import *
from discord import *
import os
#os.system("pip install Pillow")
from utils.config import OWNER_IDS, No_Prefix
import json, discord
from typing import *
import sqlite3
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageChops
import typing
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
import time, datetime
from typing import Optional
#from PIL import Image, ImageFont, ImageDraw, ImageChops




class Owner(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.staff = set()
    self.np_cache = []
    self.db_path = 'database/np.db'
    self.color = 0x2f3136
    
  async def setup_database(self):
    async with aiosqlite.connect(self.db_path) as db:
        await db.execute('''
          CREATE TABLE IF NOT EXISTS staff (
              id INTEGER PRIMARY KEY
          )
        ''')
        await db.commit()
      
    async def load_staff(self):
        await self.client.wait_until_ready()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT id FROM staff') as cursor:
                self.staff = {row[0] for row in await cursor.fetchall()}

  @commands.command(name="staff_add", aliases=["staffadd", "addstaff"], help="Adds a user to the staff list.")
  @commands.is_owner()
  async def staff_add(self, ctx, user: discord.User):
    if user.id in self.staff:
      darky = discord.Embed(description=f"{user} is already in the staff list.", color=0x000000)
      await ctx.reply(embed=darky, mention_author=False)
    else:
      self.staff.add(user.id)
      async with aiosqlite.connect(self.db_path) as db:
        await db.execute('INSERT OR IGNORE INTO staff (id) VALUES (?)', (user.id,))
        await db.commit()
        sonu2 = discord.Embed(description=f"Added {user} to the staff list.", color=0x000000)
        await ctx.reply(embed=sonu2, mention_author=False)

  @commands.command(name="staff_remove", aliases=["staffremove", "removestaff"], help="Removes a user from the staff list.")
  @commands.is_owner()
  async def staff_remove(self, ctx, user: discord.User):
    if user.id not in self.staff:
      sonu = discord.Embed(description=f"{user} is not in the staff list.", color=0x000000)
      await ctx.reply(embed=sonu, mention_author=False)
    else:
      self.staff.remove(user.id)
      async with aiosqlite.connect(self.db_path) as db:
        await db.execute('DELETE FROM staff WHERE id = ?', (user.id,))
        await db.commit()
        sonu2 = discord.Embed(description=f"Removed {user} from the staff list.", color=0x000000)
        await ctx.reply(embed=sonu2, mention_author=False)

  @commands.command(name="staff_list", aliases=["stafflist", "liststaff", "staffs"], help="Lists all staff members.")
  @commands.is_owner()
  async def staff_list(self, ctx):
    if not self.staff:
      await ctx.send("The staff list is currently empty.")
    else:
      member_list = []
      for staff_id in self.staff:
        member = await self.client.fetch_user(staff_id)
        member_list.append(f"{member.name}#{member.discriminator} (ID: {staff_id})")
        staff_display = "\n".join(member_list)
        sonu = discord.Embed(description=f"\n{staff_display}", color=0x000000)
        await ctx.send(embed=sonu)
            
  @commands.command(name="cypher.restart", help="Restarts the client.")
  @commands.is_owner()
  async def _restart(self, ctx: Context):
      await ctx.reply("Restarting Cypher.")
      restart_program()
    
  @commands.command(name="slist")
  @commands.is_owner()
  async def _slist(self, ctx):
    vg = ["Void's Hub"]
    hasanop = ([hasan for hasan in self.client.guilds])
    hasanop = sorted(hasanop,
                     key=lambda hasan: hasan.member_count,
                     reverse=True)
    entries = [
      f"`[{i}]` | [{f'{BotName}’s Hub' if g.name in vg else g.name}](https://discord.com/channels/{g.id}) - {g.member_count} (ID: `{g.id}`)"
      for i, g in enumerate(hasanop, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      description="",
      title=f"Server List of {self.client.user.name} - {len(self.client.guilds)}",
      color=self.color,
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @commands.command(name="cypher.restart", help="Restarts the client.")
  @commands.is_owner()
  async def _restart(self, ctx):
    embed = discord.Embed(
        description=f"| Restarting {self.client.user.name} .",
        color=discord.Colour(self.color))
    embed.set_author(name=ctx.author,icon_url=ctx.author.display_avatar.url)
    restart_program()
    await ctx.reply(embed=embed, mention_author=False)




  @commands.command(name="owners")
  @commands.is_owner()
  async def own_list(self, ctx):
    with open("info.json") as f:
      np = json.load(f)
      nplist = np["OWNER_IDS"]
      npl = ([await self.client.fetch_user(nplu) for nplu in nplist])
      npl = sorted(npl, key=lambda nop: nop.created_at)
      entries = [
        f"`[{no}]` | [{mem}](https://discord.com/users/{mem.id}) (ID: {mem.id})"
        for no, mem in enumerate(npl, start=1)
      ]
      paginator = Paginator(source=DescriptionEmbedPaginator(
        entries=entries,
        title=f"Owner list of {self.client.user.name} - {len(nplist)}",
        description="",
        per_page=10,
        color=self.color),
                            ctx=ctx)
      await paginator.paginate()



  @commands.command()
  @commands.is_owner()
  async def dm(self, ctx, user: discord.User, *, message: str):
    """ DM the user of your choice """
    try:
      await user.send(message)
      await ctx.send(
        f"✅ | Successfully Sent a DM to **{user}**"
      )
    except discord.Forbidden:
      await ctx.send("This user might DMs blocked or it's a bot account")

  @commands.group()
  @commands.is_owner()
  async def change(self, ctx):
    if ctx.invoked_subcommand is None:
      await ctx.send_help(str(ctx.command))

  @change.command(name="nickname")
  @commands.is_owner()
  async def change_nickname(self, ctx, *, name: str = None):
    """ Change nickname. """
    try:
      await ctx.guild.me.edit(nick=name)
      if name:
        await ctx.send(
          f"✅ | Successfully changed nickname to **{name}**"
        )
      else:
        await ctx.send(
          "✅ | Successfully removed nickname")
    except Exception as err:
      await ctx.send(err)


                
  @commands.command(name="sleave")
  @commands.is_owner()
  async def l(self, ctx, *, guild_id: int):
        g = self.client.get_guild(guild_id)
        if g is None:
            return await ctx.send(f"Guild with ID `{guild_id}` not found or the bot is not a member.")
        await g.leave()
        await ctx.send(f"Successfully left guild: `{g.name}` (ID: {g.id})")


async def setup(client):
    await client.add_cog(Owner(client))