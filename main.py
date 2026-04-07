from keep_alive import keep_alive
import os
from core.Cypher import Cypher
from utils.config import whCL, TOKEN
from discord.ext.commands import Context
from discord.ext import commands
import discord
import jishaku, cogs
from discord import app_commands
from lavalink import Client
import lavalink
from utils.database import init_db
import time
import aiohttp
import aiosqlite
import asyncio
try:
    import traceback
    from utils.Tools import *
    from discord import Webhook
except ModuleNotFoundError:
    os.system("pip install git+https://github.com/darknight156/jishaku")
    os.system("pip install git+https://github.com/Rapptz/discord-ext-menus")


os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

token = TOKEN


        
client = Cypher()

tree = client.tree

    

            
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
        
@client.event
async def on_ready():   
    print("Loaded & Online!")
    print(f"Logged in as: {client.user}")
    print(f"Connected to: {len(client.guilds)} guilds")
    print(f"Connected to: {len(client.users)} users")
        
async def load():
    for root, _, files in os.walk("cogs"):
        for filename in files:
            if filename.endswith(".py") and filename != "__init__.py":
                module_path = os.path.join(root, filename[:-3]).replace(os.sep, ".")
                await client.load_extension(module_path)    
        
    
        

async def main():
    os.makedirs("database", exist_ok=True)
    init_db()
    async with client:
        os.system("cls" if os.name == "nt" else "clear")
        await client.load_extension("jishaku")
        await load()
        await client.start(token)


if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
