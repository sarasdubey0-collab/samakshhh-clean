import discord
from discord.ext import commands
import aiosqlite
from utils.Tools import *
from utils import Paginator, DescriptionEmbedPaginator

class ChatBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None  # Single database connection
        self.bot.loop.create_task(self.initialize_database())

    async def initialize_database(self):
        """Initialize the database connection and create tables"""
        self.db = await aiosqlite.connect("database/chatban.db")
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS chatbanned (
                guild_id INTEGER,
                target_id INTEGER,
                is_role INTEGER,
                channel_id INTEGER,
                PRIMARY KEY (guild_id, target_id, is_role, channel_id)
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS chatban_config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER
            )
        """)
        await self.db.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
        await self.db.commit()

    async def cog_unload(self):
        """Close the database connection when cog unloads"""
        if self.db:
            await self.db.close()

    @commands.group(name="chatban", invoke_without_command=True)
    async def chatban(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="Chatban Subcommands",
            description="`chatban add <user|role> [channel]`\n`chatban remove <user|role> [channel]`\n`chatban config`",
            color=0x2f3136
        ))

    @chatban.command(name="add")
    @commands.has_permissions(administrator=True)
    @ignore_check()
    @blacklist_check()
    async def chatban_add(self, ctx, target: discord.Role | discord.Member, channel: discord.TextChannel = None):
        is_role = isinstance(target, discord.Role)
        
        async with self.db.execute("SELECT 1 FROM chatbanned WHERE guild_id = ? AND target_id = ?", (ctx.guild.id, target.id)) as cursor:
            exists = await cursor.fetchone()

        if exists:
            return await ctx.send(embed=discord.Embed(
                description=f"{target.mention} is already chatbanned.",
                color=discord.Color.orange()
            ))

        if not is_role and target == ctx.guild.owner:
            return await ctx.send(embed=discord.Embed(description="I can't chatban the Server Owner!"))

        if not is_role and target.top_role >= ctx.guild.me.top_role:
            return await ctx.send(embed=discord.Embed(description="I can't chatban a user with a higher or equal role!"))

        if not is_role and ctx.author != ctx.guild.owner and target.top_role >= ctx.author.top_role:
            return await ctx.send(embed=discord.Embed(description="You can't chatban a user with a higher or equal role!"))

        try:
            await self.db.execute(
                "INSERT OR IGNORE INTO chatbanned (guild_id, target_id, is_role, channel_id) VALUES (?, ?, ?, ?)",
                (ctx.guild.id, target.id, int(is_role), channel.id if channel else 0)
            )
            await self.db.commit()
        except Exception as e:
            return await ctx.send(f"Error: {e}")

        await ctx.send(embed=discord.Embed(
            description=f"{target.mention} is now chat banned {'in ' + channel.mention if channel else 'in all channels'}!",
            color=discord.Color.red()
        ))

        # Fetch log channel
        async with self.db.execute("SELECT log_channel_id FROM chatban_config WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
            result = await cursor.fetchone()

        if result:
            log_channel_id = result[0]
            log_channel = ctx.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=discord.Embed(
                    title="Chatban Issued",
                    description=f"<:MekoMod:1449446053345628297> Moderator : {ctx.author.mention}\n"
                                f"<:MekoMember:1449446061541167175> Target : {target.mention} ({'Role' if is_role else 'User'})\n"
                                f"<:MekoRuby:1449445982931783710> Scope : {'All Channels' if channel is None else channel.mention}",
                    color=discord.Color.red()
                ))

    @chatban.command(name="remove")
    @commands.has_permissions(manage_messages=True)
    @ignore_check()
    @blacklist_check()
    async def chatban_remove(self, ctx, target: discord.Role | discord.Member, channel: discord.TextChannel = None):
        is_role = isinstance(target, discord.Role)

        try:
            await self.db.execute(
                "DELETE FROM chatbanned WHERE guild_id = ? AND target_id = ? AND is_role = ? AND channel_id = ?",
                (ctx.guild.id, target.id, int(is_role), channel.id if channel else 0)
            )
            await self.db.commit()
        except Exception as e:
            return await ctx.send(f"Error: {e}")

        await ctx.send(embed=discord.Embed(
            description=f"{target.mention} can now chat {'in ' + channel.mention if channel else 'in all channels'} again!",
            color=discord.Color.green()
        ))

        # Fetch log channel
        async with self.db.execute("SELECT log_channel_id FROM chatban_config WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
            result = await cursor.fetchone()

        if result:
            log_channel_id = result[0]
            log_channel = ctx.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=discord.Embed(
                    title="Chatban Removed",
                    description=f"<:MekoMod:1449446053345628297> Moderator : {ctx.author.mention}\n"
                                f"<:MekoMember:1449446061541167175> Target : {target.mention} ({'Role' if is_role else 'User'})\n"
                                f"<:MekoRuby:1449445982931783710> Scope : {'All Channels' if channel is None else channel.mention}",
                    color=discord.Color.green()
                ))

    @chatban.group(name="log", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    @ignore_check()
    @blacklist_check()
    async def chatban_log(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="Chatban Log Subcommands",
            description="`chatban log set <channel>` - Set the log channel\n"
                        "`chatban log remove` - Remove the log channel\n"
                        "`chatban log show` - Show current log channel",
            color=discord.Color.blurple()
        ))

    @chatban_log.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def chatban_log_set(self, ctx, channel: discord.TextChannel):
        try:
            await self.db.execute("""
                INSERT INTO chatban_config (guild_id, log_channel_id)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET log_channel_id=excluded.log_channel_id
            """, (ctx.guild.id, channel.id))
            await self.db.commit()
        except Exception as e:
            return await ctx.send(f"Error: {e}")

        await ctx.send(embed=discord.Embed(
            description=f"Chatban logs will now be sent to {channel.mention}.",
            color=discord.Color.green()
        ))

    @chatban_log.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def chatban_log_remove(self, ctx):
        await self.db.execute("DELETE FROM chatban_config WHERE guild_id = ?", (ctx.guild.id,))
        await self.db.commit()

        await ctx.send(embed=discord.Embed(
            description="Chatban log channel has been removed.",
            color=discord.Color.orange()
        ))

    @chatban_log.command(name="show")
    @commands.has_permissions(manage_guild=True)
    async def chatban_log_show(self, ctx):
        async with self.db.execute("SELECT log_channel_id FROM chatban_config WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
            result = await cursor.fetchone()

        if result and (channel := ctx.guild.get_channel(result[0])):
            await ctx.send(embed=discord.Embed(
                description=f"The current log channel is {channel.mention}.",
                color=discord.Color.blurple()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                description="No log channel is currently set.",
                color=discord.Color.red()
            ))

    @chatban.command(name="config")
    @commands.has_permissions(manage_messages=True)
    @ignore_check()
    @blacklist_check()
    async def chatbans(self, ctx):
        try:
            async with self.db.execute("SELECT target_id, is_role, channel_id FROM chatbanned WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                records = await cursor.fetchall()
        except Exception as e:
            return await ctx.send(f"Error: {e}")

        if not records:
            return await ctx.send(embed=discord.Embed(
                description="There are no chat-banned users or roles in this server.",
                color=discord.Color.green()
            ))

        entries = []
        for index, (target_id, is_role, channel_id) in enumerate(records, start=1):
            if is_role:
                role = ctx.guild.get_role(target_id)
                label = f"{role.mention if role else f'Unknown Role (`{target_id}`)'} (role)"
            else:
                user = ctx.guild.get_member(target_id)
                label = f"{user.mention if user else f'Unknown User (`{target_id}`)'} (user)"
            location = f" in <#{channel_id}>" if channel_id else " (all channel)"
            entries.append(f"`{index:02}` {label}{location}")

        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            author=f"List Of Chatban Users - {len(records)}",
            author_icon=ctx.guild.icon.url if ctx.guild.icon else None,
            per_page=10
        ), ctx=ctx)

        await paginator.paginate()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        try:
            async with self.db.execute("SELECT target_id, is_role, channel_id FROM chatbanned WHERE guild_id = ?", (message.guild.id,)) as cursor:
                async for target_id, is_role, channel_id in cursor:
                    if is_role:
                        if any(role.id == target_id for role in message.author.roles):
                            if channel_id == 0 or channel_id == message.channel.id:
                                return await message.delete()
                    else:
                        if message.author.id == target_id:
                            if channel_id == 0 or channel_id == message.channel.id:
                                return await message.delete()
        except Exception:
            pass  # Silently fail to avoid spamming errors

async def setup(bot):
    await bot.add_cog(ChatBan(bot))
