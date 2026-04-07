from keep_alive import keep_alive
import os
import asyncio

from core.Cypher import Cypher
from utils.config import TOKEN, whCL
from utils.database import init_db

from discord.ext import commands
import discord
import cogs


# ✅ TOKEN
token = TOKEN

# ✅ CLIENT
client = Cypher()
tree = client.tree


# ================= COMMANDS ================= #

@client.command()
async def guildinfo(ctx, guild_id: int):
    guild = client.get_guild(guild_id)
    if not guild:
        await ctx.send("Guild not found!")
        return

    invite_links = await guild.invites()
    if invite_links:
        invite = invite_links[0]
        await ctx.send(f"Guild Invite Link: {invite.url}")
    else:
        await ctx.send("No active invite links found for this guild!")


@client.command()
async def find_guild(ctx, channel_id: int):
    channel = client.get_channel(channel_id)
    if channel:
        guild = channel.guild
        await ctx.send(f"Channel belongs to guild: {guild.name} (ID: {guild.id})")
    else:
        await ctx.send("Channel not found or not in cache!")


# ================= EVENTS ================= #

@client.event
async def on_ready():
    print("🔥 Bot Loaded & Online!")
    print(f"👤 Logged in as: {client.user}")
    print(f"🌍 Servers: {len(client.guilds)}")
    print(f"👥 Users: {len(client.users)}")


# ================= LOAD COGS ================= #

async def load():
    for root, _, files in os.walk("cogs"):
        for filename in files:
            if filename.endswith(".py") and filename != "__init__.py":
                module_path = os.path.join(root, filename[:-3]).replace(os.sep, ".")
                try:
                    await client.load_extension(module_path)
                    print(f"✅ Loaded: {module_path}")
                except Exception as e:
                    print(f"❌ Failed: {module_path} → {e}")


# ================= MAIN ================= #

async def main():
    os.makedirs("database", exist_ok=True)
    init_db()

    async with client:
        os.system("cls" if os.name == "nt" else "clear")
        await load()
        await client.start(token)


# ================= START ================= #

if __name__ == "__main__":
    keep_alive()  # ✅ Render uptime
    asyncio.run(main())
