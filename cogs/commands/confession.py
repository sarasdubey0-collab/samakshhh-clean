import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from utils.Tools import *
from rix import ParrotPaginator, PaginationView




class ConfessionModal(discord.ui.Modal, title="Anonymous Confession"):
    message = discord.ui.TextInput(label="Your confession", style=discord.TextStyle.paragraph, required=True)
    attachment_url = discord.ui.TextInput(label="Image URL (optional)", required=False)

    def __init__(self, bot, channel_id):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        confession_channel = self.bot.get_channel(self.channel_id)
        if confession_channel is None:
            return await interaction.response.send_message("Confession channel not found.", ephemeral=True)

        embed = discord.Embed(
            description=f"```{self.message.value}```",
            color=0xFFFFFF
        )
        embed.set_author(name="Anonymous Reply", icon_url="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/discord-round-color-icon.png")
        if self.attachment_url.value:
            embed.set_image(url=self.attachment_url.value)

        sent_message = await confession_channel.send(embed=embed)
        conn = sqlite3.connect("database/confessions.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO confession_posts (message_id, channel_id, guild_id, author_id)
            VALUES (?, ?, ?, ?)
        """, (sent_message.id, confession_channel.id, interaction.guild.id, interaction.user.id))
        conn.commit()
        conn.close()

        view = ConfessionView(self.bot, message=sent_message)
        await sent_message.edit(view=view)

        await interaction.response.send_message("Your anonymous confession has been submitted!", ephemeral=True)


class ConfessionReplyModal(discord.ui.Modal, title="Anonymous Reply"):
    message = discord.ui.TextInput(label="Your reply", style=discord.TextStyle.paragraph, required=True)

    def __init__(self, bot, original_message):
        super().__init__()
        self.bot = bot
        self.original_message = original_message

    async def on_submit(self, interaction: discord.Interaction):
        try:
            if not self.original_message.thread:
                thread = await self.original_message.create_thread(name="Confession Replies")
            else:
                thread = self.original_message.thread

            await thread.send(embed=discord.Embed(
                description=f"```{self.message.value}```",
                color=0xFFFFFF
            ).set_author(name="Anonymous Reply", icon_url="https://uxwing.com/wp-content/themes/uxwing/download/brands-and-social-media/discord-round-color-icon.png"))
            conn = sqlite3.connect("database/confessions.db")
            cursor = conn.cursor()
            cursor.execute("SELECT author_id FROM confession_posts WHERE message_id = ?", (self.original_message.id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                confessor_id = result[0]
                user = self.bot.get_user(confessor_id)
                if user:
                    try:
                        guild_jump = f"https://discord.com/channels/{interaction.guild.id}/{self.original_message.channel.id}/{self.original_message.id}"
                        embed = discord.Embed(
                            description=f"Someone replied to your confession in {guild_jump}",
                            color=0xFFFFFF
                        )
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass

            await interaction.response.send_message("Your anonymous reply has been sent.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error sending reply: {e}", ephemeral=True)


class ConfessionView(discord.ui.View):
    def __init__(self, bot, channel_id=None, message=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id
        self.message = message

    @discord.ui.button(label="Submit a confession!", style=discord.ButtonStyle.primary, custom_id="submit_confession")
    async def submit_confession(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect("database/confessions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM muted_confessors WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
        if cursor.fetchone():
            await interaction.response.send_message("You are muted from submitting confessions in this server.", ephemeral=True)
            return
        cursor.execute("SELECT channel_id FROM confessions WHERE guild_id = ? AND status = 'enabled'", (interaction.guild.id,))
        result = cursor.fetchone()
        conn.close()
        if not result:
            return await interaction.response.send_message("Confession channel is not set.", ephemeral=True)
        await interaction.response.send_modal(ConfessionModal(self.bot, result[0]))

    @discord.ui.button(label="Reply", style=discord.ButtonStyle.secondary, custom_id="reply_confession")
    async def reply_confession(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect("database/confessions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM muted_confessors WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
        if cursor.fetchone():
            await interaction.response.send_message("You are muted from replying to confessions in this server.", ephemeral=True)
            conn.close()
            return
        conn.close()
        original_message = interaction.message  
        if not original_message:
            return await interaction.response.send_message("Cannot find the original message for the reply.", ephemeral=True)
        await interaction.response.send_modal(ConfessionReplyModal(self.bot, original_message))

class Confessions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect("database/confessions.db")
        self.cursor = self.db.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS confessions (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                status TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS confession_posts (
                message_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                guild_id INTEGER,
                author_id INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS muted_confessors (
                guild_id INTEGER,
                user_id INTEGER,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        self.db.commit()
        self.bot.add_view(ConfessionView(bot)) 


    def is_user_muted(self, guild_id, user_id):
        self.cursor.execute("SELECT 1 FROM muted_confessors WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        return self.cursor.fetchone() is not None
    
    @commands.group(invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    async def confessions(self, ctx):
        try:
            embed = discord.Embed(
                title="Confession Commands",
                description=""
            )
            commands_list = []
            if hasattr(ctx.command, 'commands'):
                commands_list = [f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands]
                commands_list.insert(0, "`/confess`")
                command_text = ", ".join(commands_list)
                embed.add_field(name="", value=f"> {command_text}" if command_text else "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @confessions.command()
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        user_id = str(ctx.author.id)

        self.cursor.execute("""
            INSERT INTO confessions (guild_id, channel_id, status)
            VALUES (?, ?, 'enabled')
            ON CONFLICT(guild_id) DO UPDATE SET
                channel_id = excluded.channel_id,
                status = 'enabled'
        """, (guild_id, channel.id))
        self.db.commit()

        await ctx.send(embed=discord.Embed(description=f"<a:H_TICK:1449446011490537603> {ctx.author.mention}: Confession channel set to {channel.mention}."))



    @confessions.command()
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        guild_id = ctx.guild.id
        user_id = str(ctx.author.id)

        self.cursor.execute("""
            UPDATE confessions
            SET channel_id = NULL,
                status = 'disabled'
            WHERE guild_id = ?
        """, (guild_id,))
        self.db.commit()

        await ctx.send(embed=discord.Embed(description=f"<a:H_TICK:1449446011490537603> {ctx.author.mention}: Confessions have been disabled for this server."))

    @app_commands.command(name="confess", description="Submit an anonymous confession.")
    async def confess(self, interaction: discord.Interaction):
        if self.is_user_muted(interaction.guild.id, interaction.user.id):
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: You are muted from submitting confessions in this server.",color=0xFEE75C), ephemeral=True)
            return

        self.cursor.execute("SELECT channel_id FROM confessions WHERE guild_id = ? AND status = 'enabled'", (interaction.guild_id,))
        result = self.cursor.fetchone()

        if not result or not result[0]:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Confessions are disabled in this server.",color=0xFEE75C), ephemeral=True)
            return

        channel_id = result[0]
        await interaction.response.send_modal(ConfessionModal(self.bot, channel_id))


    @confessions.command()
    @commands.has_permissions(manage_guild=True)
    async def mute(self, ctx, user: discord.User):
        user_id = str(ctx.author.id)
        self.cursor.execute("INSERT OR IGNORE INTO muted_confessors (guild_id, user_id) VALUES (?, ?)", (ctx.guild.id, user.id))
        self.db.commit()
        await ctx.send(embed=discord.Embed(description=f"<a:H_TICK:1449446011490537603> {ctx.author.mention}: {user.mention} has been muted from using confessions."))



    @confessions.command()
    @commands.has_permissions(manage_guild=True)
    async def unmute(self, ctx, user: discord.User):
        user_id = str(ctx.author.id)
        self.cursor.execute("DELETE FROM muted_confessors WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, user.id))
        self.db.commit()
        await ctx.send(embed=discord.Embed(description=f"<a:H_TICK:1449446011490537603> {ctx.author.mention}: {user.mention} has been unmuted and can now use confessions again."))


async def setup(bot):
    await bot.add_cog(Confessions(bot))