import discord
from discord.ext import commands
import aiosqlite
import asyncio
from datetime import timedelta

class AntiCaps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.caps_threshold = 70
        self.mute_duration = 2 * 60
        self.db = None  # Database connection will be initialized in cog_load

    async def cog_load(self):
        """Initialize database connection when cog is loaded."""
        self.db = await aiosqlite.connect("database/automod.db")

    async def cog_unload(self):
        """Close database connection when cog is unloaded."""
        if self.db:
            await self.db.close()

    async def is_automod_enabled(self, guild_id):
        """Check if automod is enabled for the guild."""
        async with self.db.execute("SELECT enabled FROM automod WHERE guild_id = ?", (guild_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None and result[0] == 1

    async def is_anti_caps_enabled(self, guild_id):
        """Check if anti-link is enabled for the guild."""
        async with self.db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti link'", (guild_id,)) as cursor:
            result = await cursor.fetchone()
            return result is not None

    async def get_ignored_channels(self, guild_id):
        """Get ignored channels for the guild."""
        async with self.db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'channel'", (guild_id,)) as cursor:
            return [row[0] for row in await cursor.fetchall()]

    async def get_ignored_roles(self, guild_id):
        """Get ignored roles for the guild."""
        async with self.db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'role'", (guild_id,)) as cursor:
            return [row[0] for row in await cursor.fetchall()]

    async def get_punishment(self, guild_id):
        """Get punishment for anti-link violations."""
        async with self.db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti link'", (guild_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

    async def log_action(self, guild, user, channel, action, reason):
        """Log automod actions to the logging channel."""
        async with self.db.execute("SELECT log_channel FROM automod_logging WHERE guild_id = ?", (guild.id,)) as cursor:
            log_channel_id = await cursor.fetchone()

        if log_channel_id and log_channel_id[0]:
            log_channel = guild.get_channel(log_channel_id[0])
            if log_channel:
                embed = discord.Embed(title="Automod Log: Anti-Caps", color=0xff0000)
                embed.add_field(name="User", value=user.mention, inline=False)
                embed.add_field(name="Action", value=action, inline=False)
                embed.add_field(name="Channel", value=channel.mention, inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.set_footer(text=f"User ID: {user.id}")
                avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
                embed.set_thumbnail(url=avatar_url)
                embed.timestamp=discord.utils.utcnow()
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.content) < 45:
            return
            
        if message.author.bot:
            return

        guild = message.guild
        user = message.author
        channel = message.channel
        guild_id = guild.id

        if not await self.is_automod_enabled(guild_id) or not await self.is_anti_caps_enabled(guild_id):
            return

        if user == guild.owner or user == self.bot.user:
            return

        ignored_channels = await self.get_ignored_channels(guild_id)
        if channel.id in ignored_channels:
            return

        ignored_roles = await self.get_ignored_roles(guild_id)
        if any(role.id in ignored_roles for role in user.roles):
            return

        if len(message.content) > 0:
            caps_count = sum(1 for c in message.content if c.isupper())
            caps_percentage = (caps_count / len(message.content)) * 100

            if caps_percentage > self.caps_threshold:
                punishment = await self.get_punishment(guild_id)
                action_taken = None
                reason = "Excessive Caps"

                try:
                    if punishment == "Mute":
                        timeout_duration = discord.utils.utcnow() + timedelta(minutes=2)
                        await user.edit(timed_out_until=timeout_duration, reason="Excessive Caps")
                        action_taken = "`2` minutes ."
                    elif punishment == "Kick":
                        await user.kick(reason="Excessive Caps")
                        action_taken = "Kicked"
                    elif punishment == "Ban":
                        await user.ban(reason="Excessive Caps")
                        action_taken = "Banned"
                    await message.delete()

                    simple_embed = discord.Embed(color=0xff0000)
                    simple_embed.description = f"<:MekoAutomod:1449445976157720760> You've been timed out by **Cypher Automod** for {action_taken}\n<:MekoRuby:1449445982931783710> **Reason :** Excessive caps."

                    await channel.send(content=f"{user.mention}", embed=simple_embed, delete_after=30)

                    await self.log_action(guild, user, channel, action_taken, reason)

                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_rate_limit(self, message):
        await asyncio.sleep(10)
        
async def setup(client):
    await client.add_cog(AntiCaps(client))