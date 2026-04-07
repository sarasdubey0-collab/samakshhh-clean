from discord.ext import commands, tasks
import datetime, pytz, time as t
from discord.ui import Button, Select, View
import aiosqlite, random, typing
import discord, logging
from discord.utils import get
from utils.Tools import *
import os
import aiohttp
import asyncio

db_folder = 'database'
db_file = 'giveaways.db'
db_path = os.path.join(db_folder, db_file)

def parse_isoformat(date_string):
    """
    Parses an ISO format string into a datetime object.
    Works for Python versions earlier than 3.7.
    """
    try:
        from datetime import datetime
        # Try using the built-in fromisoformat if available (Python 3.7+)
        return datetime.fromisoformat(date_string)
    except AttributeError:
        # Fallback for older Python versions
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f")

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self) -> None:
        self.connection = await aiosqlite.connect(db_path)
        self.cursor = await self.connection.cursor()
        await self.cursor.execute('''CREATE TABLE IF NOT EXISTS Giveaway (
                    guild_id INTEGER,
                    host_id INTEGER,
                    start_time TIMESTAMP,
                    ends_at TIMESTAMP,
                    prize TEXT,
                    winners INTEGER,
                    message_id INTEGER,
                    channel_id INTEGER,
                    PRIMARY KEY (guild_id, message_id)
                )''')
        await self.connection.commit()
        await self.check_for_ended_giveaways() 
        self.GiveawayEnd.start()

    async def cog_unload(self) -> None:
        await self.connection.close()

    async def check_for_ended_giveaways(self):
        await self.cursor.execute("SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE ends_at <= ?", (datetime.datetime.now().timestamp(),))
        ended_giveaways = await self.cursor.fetchall()
        for giveaway in ended_giveaways:
            await self.end_giveaway(giveaway)

    async def end_giveaway(self, giveaway):
        try:
            current_time = datetime.datetime.now().timestamp()
            guild = self.bot.get_guild(int(giveaway[1]))
            if guild is None:
                await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (giveaway[2], giveaway[1]))
                await self.connection.commit()
                return

            channel = self.bot.get_channel(int(giveaway[6]))
            if channel is None:
                await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (giveaway[2], giveaway[1]))
                await self.connection.commit()
                return

            try:
                message = await channel.fetch_message(int(giveaway[2]))
            except discord.NotFound:
                await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (giveaway[2], giveaway[1]))
                await self.connection.commit()
                return

            users = []
            for reaction in message.reactions:
                if str(reaction.emoji) == "<:MekoGift:1449451126901440647>":
                    async for user in reaction.users():
                        if user.id != self.bot.user.id and not user.bot:
                            users.append(user.id)
                    break

            if len(users) < 1:
                await message.reply(f"No one won the **{giveaway[5]}** giveaway, due to not enough participants.")
                await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                await self.connection.commit()
                return

            winners_count = min(len(users), int(giveaway[4]))
            winners = random.sample(users, k=winners_count)
            winner_mentions = ', '.join(f'<@!{winner}>' for winner in winners)

            embed = discord.Embed(
                description=f"Ended <t:{int(current_time)}:R>\nHosted by <@{int(giveaway[3])}>\nWinner(s): {winner_mentions}",
                color=0x2f3136)
            embed.set_author(name=giveaway[5],
                             icon_url=guild.icon.url if guild.icon else None)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Ended at")

            await message.edit(content="<:MekoGift:1449451126901440647> **Giveaway Ended** <:MekoGift:1449451126901440647>", embed=embed)
            await message.reply(f"<a:MekoLove:1449446084131819601> Congratulations {winner_mentions}! You've won the giveaway!")
            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
            await self.connection.commit()

        except Exception as e:
            logging.error(f"Error ending giveaway: {e}")
            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (giveaway[2], giveaway[1]))
            await self.connection.commit()

    @tasks.loop(seconds=5)
    async def GiveawayEnd(self):
        await self.cursor.execute("SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE ends_at <= ?", (datetime.datetime.now().timestamp(),))
        ends_raw = await self.cursor.fetchall()
        for giveaway in ends_raw:
            await self.end_giveaway(giveaway)

    def convert_time(self, time):
        pos = ["s", "m", "h", "d"]
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        
        if not time[-1] in pos:
            return -1
        
        try:
            val = int(time[:-1])
        except ValueError:
            return -2
            
        return val * time_dict[time[-1]]

    @commands.hybrid_command(description="Starts a new giveaway.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def gstart(self, ctx, time, winners: int, *, prize: str):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            async with db.execute('SELECT expires_at FROM premium_users WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                premium_row = await cursor.fetchone()
                if premium_row:
                    expires_at = parse_isoformat(premium_row[0])
                    if expires_at > discord.utils.utcnow():
                        max_giveaways = 5
                    else:
                        max_giveaways = 1
                else:
                    max_giveaways = 1

        await self.cursor.execute("SELECT message_id FROM Giveaway WHERE guild_id = ?", (ctx.guild.id,))
        re = await self.cursor.fetchall()

        if winners > 15:
            embed = discord.Embed(description="Cannot have more than 15 winners.", color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return

        if len(re) >= max_giveaways:
            embed = discord.Embed(
                description=f"You can only host up to {max_giveaways} giveaways in this Guild.", 
                color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return

        converted = self.convert_time(time)
        if converted == -1:
            embed = discord.Embed(description="Invalid time format", color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return
        if converted == -2:
            embed = discord.Embed(
                description="Invalid time format. Please provide the time in numbers.",
                color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return
        if converted / 60 >= 50400:  # 31 days in minutes
            embed = discord.Embed(description="Time cannot exceed 31 days!", color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return

        ends = (datetime.datetime.now().timestamp() + converted)

        embed = discord.Embed(
            description=f"**Ends:** <t:{round(ends)}:R> (<t:{round(ends)}:f>)\n"
                       f"**React with <:MekoGift:1449451126901440647> to participate.**\n"
                       f"**Hosted By:** {ctx.author.mention}\n"
                       f"**Winners:** {winners}", 
            color=0x2f3136)
        embed.set_author(name=prize, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        ends_utc = datetime.datetime.utcnow() + datetime.timedelta(seconds=converted)
        embed.timestamp = ends_utc
        embed.set_footer(text="Ends at", icon_url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else None)

        message = await ctx.send("<:MekoGift:1449451126901440647> **Giveaway Started** <:MekoGift:1449451126901440647>", embed=embed)
        try:
            await ctx.message.delete()
        except:
            pass

        await self.cursor.execute(
            "INSERT INTO Giveaway(guild_id, host_id, start_time, ends_at, prize, winners, message_id, channel_id) "
            "VALUES(?, ?, ?, ?, ?, ?, ?, ?)", 
            (ctx.guild.id, ctx.author.id, datetime.datetime.now().timestamp(), ends, prize, winners, message.id, ctx.channel.id))
        await self.connection.commit()
        await message.add_reaction("<:MekoGift:1449451126901440647>")

    @commands.Cog.listener("on_message_delete")
    async def GiveawayMessageDelete(self, message):
        if message.author.id != self.bot.user.id:
            return

        await self.cursor.execute("SELECT 1 FROM Giveaway WHERE message_id = ?", (message.id,))
        if await self.cursor.fetchone():
            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ?", (message.id,))
            await self.connection.commit()
            print(f"Giveaway message deleted in {message.guild.name} - {message.guild.id}")

    @commands.hybrid_command(name="gend", description="Ends a giveaway before its ending time.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def gend(self, ctx, message_id: typing.Optional[int] = None):
        if message_id is None and not ctx.message.reference:
            await ctx.send("Please reply to the giveaway message or provide the giveaway ID.")
            return

        if message_id is None:
            message_id = ctx.message.reference.message_id

        try:
            message_id = int(message_id)
        except ValueError:
            embed = discord.Embed(description="Invalid message ID provided.", color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return

        await self.cursor.execute(
            'SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id '
            'FROM Giveaway WHERE message_id = ?', 
            (message_id,))
        giveaway = await self.cursor.fetchone()

        if giveaway is None:
            embed = discord.Embed(description="The giveaway was not found.", color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return

        channel = self.bot.get_channel(int(giveaway[6]))
        if channel is None:
            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ?", (message_id,))
            await self.connection.commit()
            return

        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ?", (message_id,))
            await self.connection.commit()
            return

        users = []
        for reaction in message.reactions:
            if str(reaction.emoji) == "<:MekoGift:1449451126901440647>":
                async for user in reaction.users():
                    if user.id != self.bot.user.id and not user.bot:
                        users.append(user.id)
                break

        current_time = datetime.datetime.now().timestamp()

        if len(users) < 1:
            await message.reply(f"No one won the **{giveaway[5]}** giveaway, due to not enough participants.")
        else:
            winners_count = min(len(users), int(giveaway[4]))
            winners = random.sample(users, k=winners_count)
            winner_mentions = ', '.join(f'<@!{winner}>' for winner in winners)

            embed = discord.Embed(
                description=f"Ended <t:{int(current_time)}:R>\nHosted by <@{int(giveaway[3])}>\nWinner(s): {winner_mentions}",
                color=0x2f3136)
            embed.set_author(name=giveaway[5], icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text="Ended at")

            await message.edit(content="<:MekoGift:1449451126901440647> **Giveaway Ended** <:MekoGift:1449451126901440647>", embed=embed)
            await message.reply(f"<a:MekoLove:1449446084131819601> Congratulations {winner_mentions}! You've won the giveaway!")

        await self.cursor.execute("DELETE FROM Giveaway WHERE message_id = ?", (message_id,))
        await self.connection.commit()

        if ctx.channel.id != channel.id:
            await ctx.send(f"✅ Successfully ended the giveaway in <#{channel.id}>")

    @commands.hybrid_command(description="Rerolls a giveaway.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(manage_guild=True)
    async def greroll(self, ctx, message_id: typing.Optional[int] = None):
        if message_id is None and not ctx.message.reference:
            message = await ctx.send("Please reply to the giveaway ended message or provide the message ID.")
            await asyncio.sleep(5)
            await message.delete()
            return

        if message_id is None:
            message_id = ctx.message.reference.message_id

        try:
            message = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            embed = discord.Embed(description="Message not found.", color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return

        # Check if it's a giveaway ended message
        if not message.content.startswith("<:MekoGift:1449451126901440647> **Giveaway Ended**"):
            embed = discord.Embed(description="This is not a giveaway ended message.", color=0x000000)
            message = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await message.delete()
            return

        users = []
        for reaction in message.reactions:
            if str(reaction.emoji) == "<:MekoGift:1449451126901440647>":
                async for user in reaction.users():
                    if user.id != self.bot.user.id and not user.bot:
                        users.append(user.id)
                break

        if len(users) < 1:
            await ctx.send("No participants found to reroll.")
            return

        winner = random.choice(users)
        await ctx.send(f"<a:MekoLove:1449446084131819601> Congratulations <@{winner}>! You've won the rerolled giveaway!")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))