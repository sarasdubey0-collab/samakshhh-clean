from discord.ext import commands, tasks
from discord import *
import discord
import aiosqlite
from typing import Optional
from datetime import datetime, timedelta
from discord.ui import View, Button, Select
from utils.config import OWNER_IDS
from utils import Paginator, DescriptionEmbedPaginator


async def is_staff(user, staff_ids):
    return user.id in staff_ids


async def is_owner_or_staff(ctx):
    return await is_staff(ctx.author, ctx.cog.staff) or ctx.author.id in OWNER_IDS



class TimeSelect(Select):
    def __init__(self, user, db_path, author):
        super().__init__(placeholder="Select the duration")
        self.user = user
        self.db_path = db_path
        self.author = author

        
        self.options = [
            SelectOption(label="12 Hours", description="No prefix for 12 hours", value="12h"),
            SelectOption(label="1 Week", description="No prefix for 1 week", value="1w"),
            SelectOption(label="1 Month", description="No prefix for 1 Month", value="1m"),
            SelectOption(label="6 Months", description="No prefix for 6 Months.", value="6m"),
            SelectOption(label="1 Year", description="No prefix for 1 Year.", value="1y"),
            SelectOption(label="Lifetime", description="No prefix Permanently.", value="lifetime"),
        ]

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            return await interaction.response.send_message("You can't select this option.", ephemeral=True)

        
        duration_mapping = {
            "12h": timedelta(hours=12),
            "1w": timedelta(weeks=1),
            "1m": timedelta(days=30),
            "6m": timedelta(days=180),
            "1y": timedelta(days=365),
            "lifetime": None
        }

        selected_duration = self.values[0]
        expiry_time = None

        if selected_duration != "lifetime":
            expiry_time = datetime.utcnow() + duration_mapping[selected_duration]
            expiry_str = expiry_time.isoformat()
        else:
            expiry_str = None

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT INTO np (id, expiry_time) VALUES (?, ?)", (self.user.id, expiry_str))
            await db.commit()

        expiry_text = "**Lifetime**" if selected_duration == "lifetime" else f"{expiry_time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        expiry_timestamp = "Infinite" if selected_duration == "lifetime" else f"<t:{int(expiry_time.timestamp())}:f>"

        
        guild = interaction.client.get_guild(1301490367945904189)
        if guild:
            member = guild.get_member(self.user.id)
            if member:
                role = guild.get_role(1329777273557225532)
                if role:
                    await member.add_roles(role, reason="No prefix added")

            

        log_channel = interaction.client.get_channel(1336378798425247834)
        if log_channel:
            embed = discord.Embed(
                title="User Added to No Prefix",
                description=f"**<:MekoUser:1449446018163806270> User**: [{self.user}](https://discord.com/users/{self.user.id})\n**<:MekoPing:1449446025206173807> User Mention**: {self.user.mention}\n**<:MekoBan:1449445932713377802> Added By**: [{self.author.display_name}](https://discord.com/users/{self.author.id})\n<:MekoTimer:1449451368392953998> **Expiry Time**: {expiry_text}\n<:MekoSearch:1449446045712121978> **Timestamp**: {expiry_timestamp}\n\n<:MekoRuby:1449445982931783710> **Tier**: **{self.values[0].upper()}**",
                color=0x000000
            )
            embed.set_thumbnail(url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
            await log_channel.send("<@1263792569981341819>, <@919175804829708308>",embed=embed)
            

        
        embed = discord.Embed(description=f"**Added Global No Prefix**:\n<:MekoUser:1449446018163806270> **User**: **[{self.user}](https://discord.com/users/{self.user.id})**\n<:MekoPing:1449446025206173807> **User Mention**: {self.user.mention}\n<:MekoBan:1449445932713377802> **Added By**: **[{self.author.display_name}](https://discord.com/users/{self.author.id})**\n<:MekoTimer:1449451368392953998> **Expiry Time:** {expiry_text}\n<:MekoSearch:1449446045712121978> **Timestamp:** {expiry_timestamp}", color=0x000000)
        embed.set_author(name="Added No Prefix")
        embed.set_footer(text="Cypher will DM you , when your noprefix expires!")
        await interaction.response.edit_message(embed=embed, view=None)

class TimeSelectView(View):
    def __init__(self, user, db_path, author):
        super().__init__()
        self.user = user
        self.db_path = db_path
        self.author = author
        self.add_item(TimeSelect(user, db_path, author))



class Noprefix(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.staff = set()
        self.db_path = 'database/np.db'
        
        self.db = None  # Single database connection
        self.client.loop.create_task(self.initialize_database())
        self.expiry_check.start()
        
    async def initialize_database(self):
        """Initialize the database connection and create tables"""
        self.db = await aiosqlite.connect("database/np.db")
        await self.db.execute('''
                CREATE TABLE IF NOT EXISTS np (
                    id INTEGER PRIMARY KEY
                )
            ''')
        
        async with self.db.execute("PRAGMA table_info(np);") as cursor:
                columns = [info[1] for info in await cursor.fetchall()]
                
                if "expiry_time" not in columns:
                    await self.db.execute('''
                                          ALTER TABLE np ADD COLUMN expiry_time TEXT NULL;
                                          ''')
                    
                    await self.db.execute('''
                                          UPDATE np
                                          SET expiry_time = NULL
                                          WHERE expiry_time IS NULL;
                                          ''')
                    await self.db.execute('''
                                          CREATE TABLE IF NOT EXISTS autonp (
                                              guild_id INTEGER PRIMARY KEY
                                              )
                                              ''')
                    await self.db.commit()

    async def cog_unload(self):
        """Close the database connection when cog unloads"""
        if self.db:
            await self.db.close()



    @tasks.loop(minutes=10)
    async def expiry_check(self):
        now = datetime.utcnow().isoformat()
        async with self.db.execute("SELECT id FROM np WHERE expiry_time IS NOT NULL AND expiry_time <= ?", (now,)) as cursor:
            expired_users = [row[0] for row in await cursor.fetchall()]
            
            if expired_users:
                async with self.db.execute("DELETE FROM np WHERE id IN ({})".format(",".join("?" * len(expired_users))), expired_users):
                    await self.db.commit()
                    
                    for user_id in expired_users:
                        user = self.client.get_user(user_id)
                        if user:
                            log_channel = self.client.get_channel(1336378798425247834)
                            if log_channel:
                                embed_log = discord.Embed(
                                    title="No Prefix Expired",
                                    description=(
                                        f"**<:MekoUser:1449446018163806270> User**: [{user}](https://discord.com/users/{user.id})\n"
                                        f"**<:MekoPing:1449446025206173807> User Mention**: {user.mention}\n"
                                        f"**<:MekoBan:1449445932713377802> Removed By**: **[Cypher#2733](https://discord.com/users/1191399940014997584)**\n"
                                        ),
                                    color=0x000000
                                    )
                                embed_log.set_thumbnail(url=user.display_avatar.url if user.avatar else user.default_avatar.url)
                                embed_log.set_footer(text="No Prefix Removal Log")
                                await log_channel.send(embed=embed_log)
                                bot = self.client
                                guild = bot.get_guild(1301490367945904189)
                                if guild:
                                    member = guild.get_member(user.id)
                                    if member:
                                        role = guild.get_role(1329777273557225532)
                                        if role in member.roles:
                                            await member.remove_roles(role)
                                            
                                            embed = discord.Embed(
                                                description=f"<:MekoExclamation:1449445917500510229> Your No Prefix status has been **Expired**. You will now require the prefix to use commands.\n> Example : **.help**",
                                                color=0x000000
                                                )
                                            embed.set_author(name="No Prefix Expired", icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
                                            embed.set_footer(text="Cypher - No Prefix, Join support to regain access.")
                                            support = Button(label='Support',
                                                             style=discord.ButtonStyle.link,
                                                             url=f'https://discord.gg/UtZ3rRnBnU')
                                            view = View()
                                            view.add_item(support)
                                            
                                            try:
                                                await user.send(f"{user.mention}", embed=embed, view=view)
                                            except discord.Forbidden:
                                                pass
                                            except discord.HTTPException:
                                                pass
                                            
    @expiry_check.before_loop
    async def before_expiry_check(self):
        await self.client.wait_until_ready()

    @commands.group(name="np", help="Allows you to add someone to the no-prefix list (owner-only command)")
    @commands.check(is_owner_or_staff)
    async def _np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @_np.command(name="list", help="List of no-prefix users")
    @commands.check(is_owner_or_staff)
    async def np_list(self, ctx):
        async with self.db.execute("SELECT id FROM np") as cursor:
            ids = [row[0] for row in await cursor.fetchall()]
            if not ids:
                await ctx.reply(f"No users in the no-prefix list.", mention_author=False)
                return
            entries = [
                f"`#{no+1}`  <@{mem}> (ID: {mem})"
                for no, mem in enumerate(ids, start=0)
                ]
            paginator = Paginator(source=DescriptionEmbedPaginator(
                entries=entries,
                title=f"No Prefix Users [{len(ids)}]",
                description="",
                per_page=10,
                color=0x000000),
                                  ctx=ctx)
            await paginator.paginate()

    

    @_np.command(name="add", help="Add user to no-prefix with time options")
    @commands.check(is_owner_or_staff)
    async def np_add(self, ctx, user: discord.User):
        async with self.db.execute("SELECT id FROM np WHERE id = ?", (user.id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                embed = discord.Embed(description=f"**{user}** is already in No prefix list\n\n<:MekoBan:1449445932713377802> **Requested By**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n", color=0x000000)
                await ctx.reply(embed=embed)
                return
            
            view = TimeSelectView(user, self.db_path, ctx.author)
            embed = discord.Embed(title="Select No Prefix Duration", description="**Choose the duration for how long no-prefix should be enabled for this user:**", color=0x000000)
            await ctx.reply(embed=embed, view=view)
        

    @_np.command(name="remove", help="Remove user from no-prefix")
    @commands.check(is_owner_or_staff)
    async def np_remove(self, ctx, user: discord.User):
        async with self.db.execute("SELECT id FROM np WHERE id = ?", (user.id,)) as cursor:
            result = await cursor.fetchone()
            if not result:
                embed = discord.Embed(description=f"**{user}** is not in the No Prefix list\n\n<:MekoBan:1449445932713377802> **Removed By**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n", color=0x000000)
                await ctx.reply(embed=embed)
                return
            
            await self.db.execute("DELETE FROM np WHERE id = ?", (user.id,))
            await self.db.commit()
            
            guild = ctx.bot.get_guild(1301490367945904189)
            if guild:
                member = guild.get_member(user.id)
                if member:
                    role = guild.get_role(1329777273557225532)
                    if role in member.roles:
                        await member.remove_roles(role)
                        
                        embed = discord.Embed(
                            description=(
                                f"**<:MekoUser:1449446018163806270> User**: [{user}](https://discord.com/users/{user.id})\n"
                                f"**<:MekoPing:1449446025206173807> User Mention**: {user.mention}\n"
                                f"**<:MekoBan:1449445932713377802> Removed By**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n"
                                ),
                            color=0x000000
                            )
                        embed.set_author(name="Removed No Prefix")
                        await ctx.reply(embed=embed)
                        
                        log_channel = ctx.bot.get_channel(1336378798425247834)
                        if log_channel:
                            embed_log = discord.Embed(
                                title="No Prefix Removed",
                                description=(
                                    f"**<:MekoUser:1449446018163806270> User**: [{user}](https://discord.com/users/{user.id})\n"
                                    f"**<:MekoPing:1449446025206173807> User Mention**: {user.mention}\n"
                                    f"**<:MekoBan:1449445932713377802> Removed By**: [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n"
                                    ),
                                color=0x000000
                                )
                            embed_log.set_thumbnail(url=user.display_avatar.url if user.avatar else user.default_avatar.url)
                            embed_log.set_footer(text="No Prefix Removal Log")
                            await log_channel.send(embed=embed_log)


    

    @_np.command(name="status", help="Check if a user is in the No Prefix list and show details.")
    @commands.check(is_owner_or_staff)
    async def np_status(self, ctx, user: discord.User):
        async with self.db.execute("SELECT id, expiry_time FROM np WHERE id = ?", (user.id,)) as cursor:
            result = await cursor.fetchone()
            
            if not result:
                embed = discord.Embed(
                    title="No Prefix Status",
                    description=f"**{user}** is not in the No Prefix list\n\n"
                    f"<:MekoMember:1449446061541167175> **Requested By**: "
                    f"[{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})\n",
                    color=0x000000
                    )
                await ctx.reply(embed=embed)
                return
            
            user_id, expires = result
            
            if expires and expires != "Null": 
                expire_time = datetime.fromisoformat(expires)
                expire_timestamp = f"<t:{int(expire_time.timestamp())}:F>"
            else:
                expire_time = "Lifetime"
                expire_timestamp = "Lifetime"
                
                embed = discord.Embed(
                    title="No Prefix Status",
                    description=(
                        f"**<:MekoUser:1449446018163806270> User**: [{user}](https://discord.com/users/{user.id})\n"
                        f"**<:MekoTimer:1449451368392953998> Expiry**: {expire_time} ({expire_timestamp})"
                        ),
                    color=0x000000
                    )
                embed.set_thumbnail(url=user.display_avatar.url if user.avatar else user.default_avatar.url)
                
                await ctx.reply(embed=embed)
                    
async def setup(client):
    await client.add_cog(Noprefix(client))
