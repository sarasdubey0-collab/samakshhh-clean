import discord
from discord.ext import commands
from discord import ui
import aiosqlite
import asyncio
from utils.Tools import *
from datetime import datetime, timedelta

class WarnView(ui.View):
    def __init__(self, user, author):
        super().__init__(timeout=60)
        self.user = user
        self.author = author
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            embed = discord.Embed()
            embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    @ui.button(style=discord.ButtonStyle.gray, emoji="<:MekoTrash:1449445909585723454>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(0, 0, 0)
        self.db_path = "database/warn.db"
        asyncio.create_task(self.setup())

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    async def add_warn(self, guild_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO warns (guild_id, user_id, warns) VALUES (?, ?, 0)", (guild_id, user_id))
            await db.execute("UPDATE warns SET warns = warns + 1 WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            await db.commit()

    async def get_total_warns(self, guild_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT warns FROM warns WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
                return 0
            
    async def warn_user(self, user: discord.Member, total_warns: int):
        # Determine timeout duration based on total warns
        timeout_duration = None
        if total_warns == 3:
            timeout_duration = 300  # 1 minute
        elif total_warns == 5:
            timeout_duration = 600  # 5 minutes
        elif total_warns >= 10:
            timeout_duration = 3600  # 1 hour

        if timeout_duration:
            try:
                until_time = discord.utils.utcnow() + timedelta(seconds=timeout_duration)
                await user.edit(timed_out_until=until_time, reason="Exceeded warning threshold")
                return f"\n<:MekoTimer:1449451368392953998> Timed Out : `{timeout_duration // 60}m.`"
            except discord.Forbidden:
                return "\n<:icons_Wrong:1449445703448264895> I do not have permission to timeout this user."
            except discord.HTTPException:
                return "\n<:icons_Wrong:1449445703448264895> Failed to timeout the user due to an error."
        return ""

    async def reset_warns(self, guild_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE warns SET warns = 0 WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            await db.commit()

    async def setup(self):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                CREATE TABLE IF NOT EXISTS warns (
                    guild_id INTEGER,
                    user_id INTEGER,
                    warns INTEGER,
                    PRIMARY KEY (guild_id, user_id)
                )
                """)
                await db.commit()
        except Exception as e:
            print(f"Error during database setup: {e}")

    @commands.hybrid_command(
        name="warn",
        help="Warn a user in the server",
        usage="warn <user> [reason]",
        aliases=["warnuser"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, user: discord.Member, *, reason=None):
        if user == ctx.author:
            return await ctx.reply("You cannot warn yourself.")

        if user == ctx.bot.user:
            return await ctx.reply("You cannot warn me.")

        if not ctx.author == ctx.guild.owner:
            if user == ctx.guild.owner:
                return await ctx.reply("I cannot warn the server owner.")

            if ctx.author.top_role <= user.top_role:
                return await ctx.reply("You cannot Warn a member with a higher or equal role.")

        if ctx.guild.me.top_role <= user.top_role:
            return await ctx.reply("I cannot Warn a member with a higher or equal role.")

        if user not in ctx.guild.members:
            return await ctx.reply("The user is not a member of this server.")

        try:
            await self.add_warn(ctx.guild.id, user.id)
            total_warns = await self.get_total_warns(ctx.guild.id, user.id)

            reason_to_send = reason or "Not Provided"
            try:
                await user.send(f"You have been warned in **{ctx.guild.name}** by **{ctx.author}**. Reason: {reason_to_send}")
                dm_status = "Yes"
            except discord.Forbidden:
                dm_status = "No"
            except discord.HTTPException:
                dm_status = "No"

            # Punishment system based on warn count
            punishment_msg = await self.warn_user(user, total_warns)

            embed = discord.Embed(description=f"<:MekoMod:1449446053345628297> Moderator : [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id}) ({ctx.author.mention})\n"
                                              f"<:MekoMember:1449446061541167175> Target : [{user.display_name}](https://discord.com/users/{user.id}) ({user.mention})\n"
                                              f"<:icon_mail:1449446068940050624> Dm : {dm_status}\n"
                                              f"<:MekoExclamation:1449445917500510229> Warns : {total_warns}{punishment_msg}\n"
                                              f"<:MekoRuby:1449445982931783710> Reason : `{reason_to_send}`",
                                              color=self.color)
            embed.set_author(name=f"User Warned", icon_url=self.get_user_avatar(user))
            embed.timestamp = discord.utils.utcnow()

            view = WarnView(user=user, author=ctx.author)
            message = await ctx.send(embed=embed, view=view)
            view.message = message
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            print(f"Error during warn command: {e}")
            
    @commands.hybrid_command(
        name="clearwarns",
        help="Clear all warnings for a user",
        aliases=["clearwarn" , "clearwarnings"],
        usage="clearwarns <user>")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    async def clearwarns(self, ctx, user: discord.Member):
        try:
            await self.reset_warns(ctx.guild.id, user.id)
            embed = discord.Embed(description=f"<a:H_TICK:1449446011490537603> All warnings have been cleared for **{user}** in this guild.", color=self.color)
            embed.set_author(name=f"Cleared Warn", icon_url=self.get_user_avatar(user))
            embed.timestamp = discord.utils.utcnow()

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            print(f"Error during clearwarns command: {e}")

async def setup(client):
    await client.add_cog(Warn(client))