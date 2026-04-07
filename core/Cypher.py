from __future__ import annotations

from discord.ext import commands
import discord
import asyncio
import typing
from typing import List
import aiosqlite
from lavalink import Client

from utils.config import OWNER_IDS
from utils import getConfig
from .Context import Context

import colorama
from colorama import Fore, Style, init

init(autoreset=True)

# ❌ REMOVED: import jishaku

np_db = None


# ================= DATABASE ================= #

async def initialize_np_db():
    global np_db
    if np_db is None:
        np_db = await aiosqlite.connect('database/np.db')
        await np_db.execute("PRAGMA journal_mode=WAL")
        await np_db.commit()


async def close_np_db():
    global np_db
    if np_db:
        await np_db.close()
        np_db = None


# ================= BOT CLASS ================= #

class Cypher(commands.AutoShardedBot):

    def __init__(self, *arg, **kwargs):
        intents = discord.Intents.all()
        intents.presences = True
        intents.members = True

        super().__init__(
            command_prefix=self.get_prefix,
            case_insensitive=True,
            intents=intents,
            status=discord.Status.do_not_disturb,
            strip_after_prefix=True,
            owner_ids=OWNER_IDS,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, replied_user=False, roles=False
            ),
            shard_count=2
        )

        self.lavalink: Client = None

    # ================= SETUP ================= #

    async def setup_hook(self):
        # Lavalink setup
        self.lavalink = Client(self.user.id)
        self.lavalink.add_node(
            host="lava-v4.ajieblogs.eu.org",
            port=80,
            password="https://dsc.gg/ajidevserver",
            region="in",
            name="default-node",
            ssl=False
        )

        self.lavalink.add_event_hooks(self)
        self.lavalink.add_event_hooks(self.lavalink_event_handler)

        # Slash sync
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"❌ Sync error: {e}")

    async def lavalink_event_handler(self, event):
        print(f"🎵 Lavalink Event: {event}")

    # ================= PRESENCE ================= #

    async def on_connect(self):
        await self.change_presence(
            status=discord.Status.do_not_disturb,
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=".help | Security"
            )
        )

    # ================= UTIL ================= #

    async def send_raw(self, channel_id: int, content: str, **kwargs):
        await self.http.send_message(channel_id, content, **kwargs)

    async def invoke_help_command(self, ctx: Context):
        return await ctx.send_help(ctx.command)

    async def fetch_message_by_channel(
        self, channel: discord.TextChannel, messageID: int
    ):
        async for msg in channel.history(
            limit=1,
            before=discord.Object(messageID + 1),
            after=discord.Object(messageID - 1),
        ):
            return msg

    # ================= PREFIX ================= #

    async def get_prefix(self, message: discord.Message):
        try:
            await initialize_np_db()

            if message.guild:
                guild_id = message.guild.id

                async with np_db.execute(
                    "SELECT id FROM np WHERE id = ?",
                    (message.author.id,)
                ) as cursor:
                    row = await cursor.fetchone()

                data = await getConfig(guild_id)
                prefix = data["prefix"]

                if row:
                    return commands.when_mentioned_or(prefix, '')(self, message)
                else:
                    return commands.when_mentioned_or(prefix)(self, message)

            else:
                async with np_db.execute(
                    "SELECT id FROM np WHERE id = ?",
                    (message.author.id,)
                ) as cursor:
                    row = await cursor.fetchone()

                if row:
                    return commands.when_mentioned_or('.', '')(self, message)
                else:
                    return commands.when_mentioned_or('')(self, message)

        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                await asyncio.sleep(1)
                return await self.get_prefix(message)
            else:
                raise

    # ================= EVENTS ================= #

    async def on_message_edit(self, before, after):
        ctx: Context = await self.get_context(after, cls=Context)

        if before.content != after.content:
            if after.guild is None or after.author.bot:
                return
            if ctx.command is None:
                return
            await self.invoke(ctx)


# ================= SETUP ================= #

def setup_bot():
    intents = discord.Intents.all()
    return Cypher(intents=intents)
