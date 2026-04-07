import discord
from discord.ext import commands
import aiosqlite
from utils.Tools import ignore_check, blacklist_check
from utils import Paginator, DescriptionEmbedPaginator

class ReactBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None  # Single database connection
        self.bot.loop.create_task(self.initialize_database())
        
    async def initialize_database(self):
        """Initialize the database connection and create tables"""
        self.db = await aiosqlite.connect("database/reactban.db")
        await self.db.execute("""CREATE TABLE IF NOT EXISTS reactbanned (
                guild_id INTEGER,
                target_id INTEGER,
                is_role INTEGER,
                channel_id INTEGER,
                PRIMARY KEY(guild_id, target_id, is_role, channel_id))""")
        await self.db.execute("""CREATE TABLE IF NOT EXISTS reactbanlog (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER)""")
        await self.db.commit()

    async def cog_unload(self):
        """Close the database connection when cog unloads"""
        if self.db:
            await self.db.close()

    @commands.group(invoke_without_command=True)
    async def reactban(self, ctx):
        embed = discord.Embed(
            title="Reactban Subcommands",
            description=(
                "`reactban add <user|role> [channel]`\n"
                "`reactban remove <user|role> [channel]`\n"
                "`reactban config`\n"
                "`reactban logchannel set <channel>`\n"
                "`reactban logchannel remove`"
            ),
            color=0x2f3136)
        await ctx.send(embed=embed)

    @reactban.command(name="add")
    @commands.has_permissions(administrator=True)
    @ignore_check()
    @blacklist_check()
    async def reactban_add(self, ctx, target: discord.Role | discord.Member, channel: discord.TextChannel = None):
        is_role = isinstance(target, discord.Role)
        if not is_role:
            if target == ctx.guild.owner:
                return await ctx.send(embed=discord.Embed(description="I can't reactban the Server Owner!", color=discord.Color.red()))
            if target.top_role >= ctx.guild.me.top_role:
                return await ctx.send(embed=discord.Embed(description="I can't reactban a user with a higher or equal role!", color=discord.Color.red()))
            if ctx.author != ctx.guild.owner and target.top_role >= ctx.author.top_role:
                return await ctx.send(embed=discord.Embed(description="You can't reactban a user with a higher or equal role!", color=discord.Color.red()))
            await self.db.execute("INSERT OR IGNORE INTO reactbanned (guild_id, target_id, is_role, channel_id) VALUES (?, ?, ?, ?)",
                                  (ctx.guild.id, target.id, int(is_role), channel.id if channel else 0))
            await self.db.commit()
            
            await ctx.send(embed=discord.Embed(description=f"{target.mention} is now react banned {'in ' + channel.mention if channel else 'in all channels'}!", color=discord.Color.red()))
            embed=discord.Embed(
                title="Reactban Issued",
                description=f"<:MekoMod:1449446053345628297> Moderator : {ctx.author.mention}\n"
                f"<:MekoMember:1449446061541167175> Target : {target.mention} ({'Role' if is_role else 'User'})\n"
                f"<:MekoRuby:1449445982931783710> Scope : {'All Channels' if channel is None else channel.mention}",
                color=discord.Color.green()
                )
            await self.log_action(ctx.guild.id, embed=embed)

    @reactban.command(name="remove")
    @commands.has_permissions(administrator=True)
    @ignore_check()
    @blacklist_check()
    async def reactban_remove(self, ctx, target: discord.Role | discord.Member, channel: discord.TextChannel = None):
        is_role = isinstance(target, discord.Role)
        await self.db.execute("DELETE FROM reactbanned WHERE guild_id=? AND target_id=? AND is_role=? AND channel_id=?",
                              (ctx.guild.id, target.id, int(is_role), channel.id if channel else 0))
        await self.db.commit()
        await ctx.send(embed=discord.Embed(description=f"{target.mention} can now react {'in ' + channel.mention if channel else 'in all channels'} again!", color=discord.Color.green()))
        embed=discord.Embed(
          title="Reactban Removed",
          description=f"<:MekoMod:1449446053345628297> Moderator : {ctx.author.mention}\n"
          f"<:MekoMember:1449446061541167175> Target : {target.mention} ({'Role' if is_role else 'User'})\n"
          f"<:MekoRuby:1449445982931783710> Scope : {'All Channels' if channel is None else channel.mention}",
          color=discord.Color.red()
          )
        await self.log_action(ctx.guild.id, embed=embed)

    @reactban.command(name="config")
    @commands.has_permissions(administrator=True)
    @ignore_check()
    @blacklist_check()
    async def reactbans(self, ctx):
        async with self.db.execute("SELECT target_id,is_role,channel_id FROM reactbanned WHERE guild_id=?", (ctx.guild.id,)) as cursor:
            banned = await cursor.fetchall()
            if not banned:
                return await ctx.send(embed=discord.Embed(description="There are no react-banned users or roles in this server.", color=discord.Color.green()))
            entries = []
            for index, (target_id, is_role, channel_id) in enumerate(banned, start=1):
                if is_role:
                    target = ctx.guild.get_role(target_id)
                    label = f"{target.mention if target else f'Unknown Role (`{target_id}`)'} (Role)"
                else:
                    target = ctx.guild.get_member(target_id)
                    label = f"{target.mention if target else f'Unknown User (`{target_id}`)'} (User)"
                    location = f"in {self.bot.get_channel(channel_id).mention}" if channel_id else "(all channels)"
                    entries.append(f"`{index:02}` {label} {location}")
                    paginator = Paginator(
                        source=DescriptionEmbedPaginator(entries=entries, description="", author=f"List of Reactbanned Targets - {len(entries)}",
                                                         author_icon=ctx.guild.icon.url if ctx.guild.icon else None, per_page=10),
                        ctx=ctx)
                    
                    await paginator.paginate()

    @reactban.group(name="log", invoke_without_command=True)
    async def reactban_logchannel(self, ctx):
        await ctx.send("")

    @reactban_logchannel.command(name="set")
    @commands.has_permissions(administrator=True)
    async def set_logchannel(self, ctx, channel: discord.TextChannel):
        await self.db.execute("INSERT OR REPLACE INTO reactbanlog (guild_id, channel_id) VALUES (?, ?)", (ctx.guild.id, channel.id))
        await self.db.commit()
        await ctx.send(f"Logging channel set to {channel.mention}.")

    @reactban_logchannel.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def remove_logchannel(self, ctx):
        await self.db.execute("DELETE FROM reactbanlog WHERE guild_id=?", (ctx.guild.id,))
        await self.db.commit()
        await ctx.send("Logging channel has been removed.")

    async def log_action(self, guild_id: int, embed: discord.Embed = None, message: str = None):
        async with self.db.execute("SELECT channel_id FROM reactbanlog WHERE guild_id=?", (guild_id,)) as cursor:
            result = await cursor.fetchone()
            if result:
                channel = self.bot.get_channel(result[0])
                if channel:
                    try:
                        if embed:
                            await channel.send(embed=embed)
                        elif message:
                            await channel.send(embed=discord.Embed(description=message, color=discord.Color.blurple()))
                    except discord.Forbidden:
                        pass

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        message = reaction.message
        async with self.db.execute("SELECT target_id,is_role,channel_id FROM reactbanned WHERE guild_id=?", (message.guild.id,)) as cursor:
            banned = await cursor.fetchall()
            for target_id, is_role, channel_id in banned:
                if is_role:
                    if any(role.id == target_id for role in user.roles):
                        if channel_id == 0 or message.channel.id == channel_id:
                            await reaction.remove(user)
                            await self.log_action(message.guild.id, f"❌ {user.mention} was prevented from reacting in {message.channel.mention} (Role restriction)")
                            return
                else:
                    if user.id == target_id:
                        if channel_id == 0 or message.channel.id == channel_id:
                            await reaction.remove(user)
                            await self.log_action(message.guild.id, f"❌ {user.mention} was prevented from reacting in {message.channel.mention} (User restriction)")
                            return

async def setup(bot):
    await bot.add_cog(ReactBan(bot))
