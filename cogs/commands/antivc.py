import discord
from discord.ext import commands
import aiosqlite
import math
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator

class AntiVC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.bot.loop.create_task(self.initialize_database())
        
    async def initialize_database(self):
        """Initialize the database connection and create tables"""
        self.db = await aiosqlite.connect("database/antivc.db")
        await self.db.execute("""CREATE TABLE IF NOT EXISTS vc_bans (
                guild_id INTEGER,
                target_id INTEGER,
                is_role BOOLEAN,
                channel_id INTEGER
            )""")
        await self.db.execute("PRAGMA journal_mode=WAL") 
        await self.db.commit()

    async def cog_unload(self):
        """Close the database connection when cog unloads"""
        if self.db:
            await self.db.close()


    async def is_banned(self, guild_id, member, channel_id):
        async with self.db.execute("SELECT channel_id FROM vc_bans WHERE guild_id = ? AND target_id = ? AND is_role = 0",
                                (guild_id, member.id)) as cursor:
            rows = await cursor.fetchall()
            if any(row[0] == channel_id or row[0] is None for row in rows):
                return True
        for role in member.roles:
            async with self.db.execute("SELECT channel_id FROM vc_bans WHERE guild_id = ? AND target_id = ? AND is_role = 1",
                                    (guild_id, role.id)) as cursor:
                rows = await cursor.fetchall()
                if any(row[0] == channel_id or row[0] is None for row in rows):
                    return True

        return False 

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and await self.is_banned(member.guild.id, member, after.channel.id):
            await member.move_to(None)
            await member.send(f"<:MekoExclamation:1449445917500510229> {member.mention} you are not allowed to join voice channels in **{member.guild.name}**.")

    @commands.group(name="vcban", invoke_without_command=True)
    async def antivc(self, ctx):
        await ctx.send(embed=discord.Embed(
            title="VCban Subcommands",
            description="`vcban add <user|role> [channel]`\n`vcban remove <user|role> [channel]`\n`vcban config`",
            color=0x2f3136
        ))

    @antivc.command(name="add")
    @commands.has_permissions(administrator=True)
    async def antivc_add(self, ctx, target: discord.Member | discord.Role, channel: discord.VoiceChannel = None):
        is_role = isinstance(target, discord.Role)
        await self.db.execute(
            "INSERT INTO vc_bans (guild_id, target_id, is_role, channel_id) VALUES (?, ?, ?, ?)",
            (ctx.guild.id, target.id, int(is_role), channel.id if channel else None)
            )
        await self.db.commit()
        
        await ctx.send(embed=discord.Embed(
            description=f"<a:H_TICK:1449446011490537603> {ctx.author.mention}: added {'role' if is_role else 'user'} {target.mention} to anti-vc ban list {'for ' + channel.mention if channel else 'for all VCs'}.",
            color=0x2f3136
        ))

    @antivc.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def antivc_remove(self, ctx, target: discord.Member | discord.Role, channel: discord.VoiceChannel = None):
        is_role = isinstance(target, discord.Role)
        cursor = await self.db.execute(
            "DELETE FROM vc_bans WHERE guild_id = ? AND target_id = ? AND is_role = ? AND (channel_id IS ? OR channel_id = ?)",
            (ctx.guild.id, target.id, int(is_role), None if channel is None else channel.id, channel.id if channel else None)
            )
        await self.db.commit()
        if cursor.rowcount == 0:
            await ctx.send(embed=discord.Embed(
                description=f"<:MekoExclamation:1449445917500510229> {ctx.author.mention}: no ban found for {target.mention}.",
                color=0x2f3136
                ))
            return
        
        await ctx.send(embed=discord.Embed(
            description=f"<a:H_TICK:1449446011490537603> {ctx.author.mention}: removed {'role' if is_role else 'user'} {target.mention} from anti-vc ban list {'for ' + channel.mention if channel else 'for all VCs'}.",
            color=0x2f3136
            ))

    @antivc.command(name="config")
    @commands.has_permissions(administrator=True)
    async def antivc_config(self, ctx):
        cursor = await self.db.execute(
            "SELECT target_id, is_role, channel_id FROM vc_bans WHERE guild_id = ?",
            (ctx.guild.id,)
            )
        results = await cursor.fetchall()

        if not results:
            return await ctx.send(embed=discord.Embed(
                description=f"<:MekoExclamation:1449445917500510229> {ctx.author.mention}: no entries found.",
                color=0x2f3136
            ))

        entries = []
        for idx, (target_id, is_role, channel_id) in enumerate(results, 1):
            target = ctx.guild.get_role(target_id) if is_role else ctx.guild.get_member(target_id)
            if not target:
                continue
            name = target.name
            mention = "Role" if is_role else "User"
            link = f"https://discord.com/users/{target_id}" if not is_role else "https://discord.com"
            channel = f"<#{channel_id}>" if channel_id else "All Channels"
            entries.append(f"`{idx:02}.` [{name}]({link}) ({mention}) → {channel}")

        guild = ctx.guild
        paginator = Paginator(source=DescriptionEmbedPaginator(
            entries=entries,
            description="",
            author=f"List Of Vcban Users in {guild.name}",
            author_icon=guild.icon.url if guild.icon else None,
            color=0x2f3136),
            ctx=ctx
        )
        await paginator.paginate()

async def setup(bot):
    await bot.add_cog(AntiVC(bot))