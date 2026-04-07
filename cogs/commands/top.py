import discord
from discord.ext import commands
import aiosqlite
from utils.Tools import *

class TopStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def ensure_db(self):
        """Creates the database table if not exists."""
        async with aiosqlite.connect("database/top.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS command_usage (
                    guild_id INTEGER,
                    user_id INTEGER,
                    commands_used INTEGER,
                    PRIMARY KEY (guild_id, user_id)
                )
            """)
            await db.commit()

    async def update_usage(self, ctx, retries=3):
        """Updates command usage count for a guild and user."""
        for attempt in range(retries):
            try:
                async with aiosqlite.connect("database/top.db") as db:
                    await db.execute("""
                        INSERT INTO command_usage (guild_id, user_id, commands_used)
                        VALUES (?, ?, 1)
                        ON CONFLICT(guild_id, user_id) DO UPDATE SET
                        commands_used = commands_used + 1
                    """, (ctx.guild.id, ctx.author.id))
                    await db.commit()
                    return
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    await asyncio.sleep(1)  # wait and retry
                else:
                    raise

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Listener to track command usage."""
        await self.update_usage(ctx)

    async def fetch_top_guilds(self):
        """Fetches the top 10 guilds by command usage."""
        async with aiosqlite.connect("database/top.db") as db:
            cursor = await db.execute("""
                SELECT guild_id, SUM(commands_used) AS total_commands 
                FROM command_usage 
                GROUP BY guild_id 
                ORDER BY total_commands DESC 
                LIMIT 10
            """)
            return await cursor.fetchall()

    async def fetch_top_users(self):
        """Fetches the top 10 users by command usage."""
        async with aiosqlite.connect("database/top.db") as db:
            cursor = await db.execute("""
                SELECT user_id, SUM(commands_used) AS total_commands 
                FROM command_usage 
                GROUP BY user_id 
                ORDER BY total_commands DESC 
                LIMIT 10
            """)
            return await cursor.fetchall()
        
    @commands.hybrid_group(name="top")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @ignore_check()
    @blacklist_check()
    async def top(self, ctx):
        try:
            embed = discord.Embed(
                title="Top Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")  

    @top.command(name="guild", aliases=["guilds"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @ignore_check()
    @blacklist_check()
    async def top_guild(self, ctx):
        """Displays the top 10 guilds by command usage."""
        data = await self.fetch_top_guilds()
        if not data:
            return await ctx.send("No guilds found.")

        embed = discord.Embed(title="Commands Used In Guild", color=discord.Color.blue())
        description = ""

        for i, (guild_id, commands_used) in enumerate(data, start=1):
            guild = self.bot.get_guild(guild_id)
            guild_name = guild.name if guild else f"Unknown Guild ({guild_id})"
            description += f"`{i}.` {guild_name} **- `{commands_used}`**\n"
            
        embed.description = description

        await ctx.send(embed=embed)

    @top.command(name="user", aliases=["users"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def top_user(self, ctx):
        """Displays the top 10 users by command usage."""
        data = await self.fetch_top_users()
        if not data:
            return await ctx.send("No users found.")

        embed = discord.Embed(title="Commands Used By Users", color=discord.Color.green())
        description = ""

        for i, (user_id, commands_used) in enumerate(data, start=1):
            user = self.bot.get_user(user_id)
            user_name = f"[{user.display_name}](https://discord.com/users/{user.id})" if user else f"Unknown User ({user_id})"
            description += f"`{i}.` {user_name} **- `{commands_used}`**\n"
            
        embed.description = description

        await ctx.send(embed=embed)

 
async def setup(bot):
    cog = TopStats(bot)
    await cog.ensure_db()
    await bot.add_cog(cog)