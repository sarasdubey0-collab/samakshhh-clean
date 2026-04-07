import discord
from discord.ext import commands
import aiosqlite
import asyncio
from datetime import datetime
from utils.Tools import *

class AFKView(discord.ui.View):
    def __init__(self, author, reason):
        super().__init__(timeout=60)
        self.author = author
        self.reason = reason

    @discord.ui.button(label="Server AFK", style=discord.ButtonStyle.gray)
    async def server_afk(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the command author can use this button.", ephemeral=True)
            return
        
        timestamp = datetime.now().isoformat()
        guild_id = interaction.guild.id if interaction.guild else None

        async with aiosqlite.connect('database/afk.db') as db:
            await db.execute("DELETE FROM afk_mentions WHERE user_id = ? AND guild_id = ?", (self.author.id, guild_id))
            await db.execute(
                "INSERT OR REPLACE INTO server_afk (user_id, guild_id, timestamp, reason) VALUES (?, ?, ?, ?)",
                (self.author.id, guild_id, timestamp, self.reason)
            )
            await db.commit()

        embed = discord.Embed(
            description=f"<:MekoArrowRight:1449445989436887090> **Reason:** {self.reason}",
            color=0x00ff00
        )
        embed.set_author(name=f"{interaction.user.display_name}, You are now AFK only in this server", icon_url=self.author.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Global AFK", style=discord.ButtonStyle.gray)
    async def global_afk(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the command author can use this button.", ephemeral=True)
            return
        
        timestamp = datetime.now().isoformat()

        async with aiosqlite.connect('database/afk.db') as db:
            await db.execute("DELETE FROM afk_mentions WHERE user_id = ?", (self.author.id,))
            await db.execute(
                "INSERT OR REPLACE INTO global_afk (user_id, timestamp, reason) VALUES (?, ?, ?)",
                (self.author.id, timestamp, self.reason)
            )
            await db.commit()

        embed = discord.Embed(
            description=f"<:MekoArrowRight:1449445989436887090> **Reason:** {self.reason}",
            color=0xff9900
        )
        embed.set_author(name=f"{interaction.user.display_name}, You are now AFK globally across all servers", icon_url=self.author.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=None)


class AFKCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.init_db())

    async def time_formatter(self, seconds: float):
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        tmp = ((str(days) + " days, ") if days else "") + \
            ((str(hours) + " hours, ") if hours else "") + \
            ((str(minutes) + " minutes, ") if minutes else "") + \
            ((str(seconds) + " seconds, ") if seconds else "")
        return tmp.rstrip(', ')

    async def init_db(self):
        async with aiosqlite.connect('database/afk.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS server_afk (
                    user_id INTEGER,
                    guild_id INTEGER,
                    timestamp TEXT,
                    reason TEXT,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS global_afk (
                    user_id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    reason TEXT
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS afk_mentions (
                    user_id INTEGER,
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_link TEXT
                )
            ''')
            await db.commit()

    @commands.command(name='afk')
    @ignore_check()
    @blacklist_check()
    @commands.cooldown(1,5, commands.BucketType.user)
    async def afk(self, ctx, *, reason: str = "I am afk :)"):
        if any(word in reason.lower() for word in ['discord.gg', '.gg/', 'https', 'http', 'www', 'guns.lol']):
            emd = discord.Embed(description=f"<:icons_info:1449445961326792896> {ctx.author.mention}: You can't advertise in your AFK reason.", color=0x00FFCA)
            return await ctx.send(embed=emd)

        embed = discord.Embed(color=0x5865f2)
        embed.set_author(name=f"{ctx.author.display_name}, Choose your AFK status", icon_url=ctx.author.display_avatar.url)
        view = AFKView(ctx.author, reason)
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        await self.check_remove_afk(message)

        if message.mentions:
            await self.check_afk_mentions(message)

    async def check_remove_afk(self, message):
        async with aiosqlite.connect('database/afk.db') as db:
            guild_id = message.guild.id if message.guild else None
            user_id = message.author.id

            cursor = await db.execute("SELECT reason, timestamp FROM server_afk WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
            server_afk = await cursor.fetchone()

            cursor = await db.execute("SELECT reason, timestamp FROM global_afk WHERE user_id = ?", (user_id,))
            global_afk = await cursor.fetchone()

            if server_afk or global_afk:
                await db.execute("DELETE FROM server_afk WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
                await db.execute("DELETE FROM global_afk WHERE user_id = ?", (user_id,))
                
                if server_afk:
                    cursor = await db.execute("SELECT channel_id, message_link FROM afk_mentions WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
                else:
                    cursor = await db.execute("SELECT channel_id, message_link FROM afk_mentions WHERE user_id = ?", (user_id,))
                
                rows = await cursor.fetchall()
                await db.execute("DELETE FROM afk_mentions WHERE user_id = ?", (user_id,))
                await db.commit()

                afk_data = server_afk if server_afk else global_afk
                afk_time_str = afk_data[1]
                afk_time = datetime.fromisoformat(afk_time_str)
                time_away = (datetime.now() - afk_time).total_seconds()
                formatted_time = await self.time_formatter(time_away)

                embed = discord.Embed(color=0x00ff00)
                embed.set_author(
                    name=f"{message.author.display_name}, Your {'server' if server_afk else 'global'} AFK has been removed after {formatted_time}",
                    icon_url=message.author.display_avatar.url
                )
                if rows:
                    desc = ""
                    for channel_id, link in rows[:10]: 
                        desc += f"[Jump to message]({link})\n"

                    if len(rows) > 10:
                        desc += f"...and {len(rows) - 10} more mentions."

                    embed.title = "Mentions"
                    embed.description = desc
                else:
                    embed.title = "Mentions"
                    embed.description = "You had no mentions while AFK."

                try:
                    await message.channel.send(embed=embed)
                except discord.HTTPException as e:
                    print(f"Failed to send AFK removal embed: {e}")

    async def check_afk_mentions(self, message):
        async with aiosqlite.connect('database/afk.db') as db:
            for user in message.mentions:
                mention_recorded = False

                cursor = await db.execute("SELECT reason FROM server_afk WHERE user_id = ? AND guild_id = ?", (user.id, message.guild.id))
                row = await cursor.fetchone()
                afk_type = 'server'

                if not row:
                    cursor = await db.execute("SELECT reason FROM global_afk WHERE user_id = ?", (user.id,))
                    row = await cursor.fetchone()
                    afk_type = 'global'

                if row:
                    reason = row[0]
                    msg_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"

                    await db.execute(
                        "INSERT INTO afk_mentions (user_id, guild_id, channel_id, message_link) VALUES (?, ?, ?, ?)",
                        (user.id, message.guild.id, message.channel.id, msg_link)
                    )
                    await db.commit()

                    embed = discord.Embed(
                        description=f"<:MekoArrowRight:1449445989436887090> **Reason Was:** {reason}",
                        color=0xffff00
                    )
                    embed.set_author(name=f"{user.display_name} went AFK", icon_url=user.display_avatar.url)

                    await message.channel.send(embed=embed, delete_after=10)

async def setup(bot):
    await bot.add_cog(AFKCog(bot))
