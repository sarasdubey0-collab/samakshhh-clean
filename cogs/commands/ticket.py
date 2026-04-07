import asyncio
import discord
from discord.ext import commands
import sqlite3
import datetime
from checks.colorcheck import get_embed_color
from utils.Tools import *



class CloseTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Close Ticket", custom_id="close_ticket", row=1)

    async def callback(self, interaction: discord.Interaction):
        conn = sqlite3.connect("tickets.db")
        cursor = conn.cursor()
        cursor.execute("SELECT creator_id FROM tickets WHERE channel_id = ?", (str(interaction.channel_id),))
        ticket_data = cursor.fetchone()

        if not ticket_data:
            conn.close()
            return

        creator_id = ticket_data[0]
        topic_name = None
        for topic in cursor.execute("SELECT topic_name FROM topics WHERE guild_id = ?", (str(interaction.guild_id),)):
            if topic[0].lower() in interaction.channel.name.lower():
                topic_name = topic[0]
                break

        support_role_id = None
        if topic_name:
            cursor.execute("SELECT support FROM topics WHERE topic_name = ? AND guild_id = ?", (topic_name, str(interaction.guild_id)))
            result = cursor.fetchone()
            if result:
                support_role_id = result[0]

        conn.close()

        is_creator = str(interaction.user.id) == creator_id
        has_support_role = support_role_id and discord.utils.get(interaction.user.roles, id=int(support_role_id))
        is_admin = interaction.user.guild_permissions.administrator

        if not (is_creator or has_support_role or is_admin):
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="Only the ticket creator, a support team member, or an administrator can close this ticket.",
                    color=0x71368a
                ),
                ephemeral=True
            )
            return

        creator = interaction.guild.get_member(int(creator_id))
        if creator:
            await interaction.channel.set_permissions(creator, view_channel=False)

        embed = discord.Embed(
            description="🔒 This ticket has been closed.\nUse the button below to delete this ticket.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=DeleteTicketView())
        
class SimpleUserSelect(discord.ui.UserSelect):
    def __init__(self, remove=False):
        super().__init__(placeholder="Select a user", min_values=1, max_values=1)
        self.remove = remove

    async def callback(self, interaction: discord.Interaction):
        selected_user = self.values[0]
        member = interaction.guild.get_member(selected_user.id)

        if not member:
            await interaction.response.send_message("Could not find the selected user.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("I don't have permission to manage channels.", ephemeral=True)
            return

        conn = sqlite3.connect("tickets.db")
        cursor = conn.cursor()

        cursor.execute("SELECT creator_id FROM tickets WHERE channel_id = ?", (str(interaction.channel_id),))
        result = cursor.fetchone()
        conn.close()

        if not result:
            await interaction.response.send_message("Could not verify ticket ownership.", ephemeral=True)
            return

        creator_id = result[0]
        is_admin = interaction.user.guild_permissions.administrator
        is_creator = str(interaction.user.id) == creator_id

        if not (is_admin or is_creator):
            await interaction.response.send_message("Only the ticket creator or an admin can manage users.", ephemeral=True)
            return

        if self.remove:
            await interaction.channel.set_permissions(member, overwrite=None)
            await interaction.response.send_message(content=f"{member.mention} has been removed from this ticket.")
        else:
            await interaction.channel.set_permissions(
                member,
                read_messages=True,
                send_messages=True,
                view_channel=True
            )
            await interaction.response.send_message(content=f"{member.mention} has been added to this ticket")

class SimpleUserSelectView(discord.ui.View):
    def __init__(self, remove=False):
        super().__init__(timeout=None)
        self.add_item(SimpleUserSelect(remove=remove))

class SimpleAddUserButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Add User", custom_id="simple_add_user", row=2)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Select a user to **add** to this ticket:",
            ephemeral=True,
            view=SimpleUserSelectView(remove=False)
        )

class SimpleRemoveUserButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Remove User", custom_id="simple_remove_user", row=2)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Select a user to **remove** from this ticket:",
            ephemeral=True,
            view=SimpleUserSelectView(remove=True)
        )


class TicketView2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())
        self.add_item(SimpleAddUserButton())
        self.add_item(SimpleRemoveUserButton())

class UserSelect(discord.ui.UserSelect):
    def __init__(self, remove=False):
        super().__init__(placeholder="Select a user", min_values=1, max_values=1)
        self.remove = remove

    async def callback(self, interaction: discord.Interaction):
        try:
            selected_user = self.values[0]
            member = interaction.guild.get_member(selected_user.id)

            if not member:
                await interaction.response.send_message("Could not find the selected user.", ephemeral=True)
                return

            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.response.send_message("I don't have permission to manage channels.", ephemeral=True)
                return

            conn = sqlite3.connect("tickets.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT topic_name FROM topics WHERE guild_id = ? LIMIT 1",
                (str(interaction.guild.id),)
            )
            result = cursor.fetchone()

            if result:
                topic_name = result[0]
            else:
                await interaction.response.send_message("Could not find the topic for this ticket.", ephemeral=True)
                conn.close()
                return

            cursor.execute(
                "SELECT support FROM topics WHERE topic_name = ? AND guild_id = ? LIMIT 1",
                (topic_name, str(interaction.guild.id))
            )
            result = cursor.fetchone()
            conn.close()

            support_role_id = result[0] if result and result[0] else None
            support_role = interaction.guild.get_role(int(support_role_id)) if support_role_id else None
            is_admin = interaction.user.guild_permissions.administrator
            is_support = support_role and support_role in interaction.user.roles

            if not (is_support or is_admin):
                await interaction.response.send_message("Only support staff or admins can manage ticket users.", ephemeral=True)
                return

            if self.remove:
                await interaction.channel.set_permissions(member, overwrite=None)
                await interaction.response.send_message(content=f"{member.mention} has been removed from this ticket.")
            else:
                await interaction.channel.set_permissions(member,
                    read_messages=True,
                    send_messages=True,
                    view_channel=True)
                await interaction.response.send_message(content=f"{member.mention} has been added to this ticket")

        except Exception as e:
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

class UserSelectView(discord.ui.View):
    def __init__(self, remove=False):
        super().__init__(timeout=None)
        self.add_item(UserSelect(remove=remove))

class AddUserButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Add User", custom_id="add_user", row=2)
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Select a user to add to this ticket:", ephemeral=True, view=UserSelectView(remove=False))
        except Exception as e:
            pass

class RemoveUserButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, label="Remove User", custom_id="remove_user", row=2)
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("Select a user to remove from this ticket:", ephemeral=True, view=UserSelectView(remove=True))
        except Exception as e:
            pass

class DeleteTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, label="Delete Ticket", custom_id="delete_ticket")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Deleting this ticket in 3 seconds...", ephemeral=True)
        await asyncio.sleep(3)

        conn = sqlite3.connect("tickets.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tickets WHERE channel_id = ?", (str(interaction.channel_id),))
        conn.commit()
        conn.close()

        await interaction.channel.delete()


class DeleteTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(DeleteTicketButton())

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())
        self.add_item(AddUserButton())
        self.add_item(RemoveUserButton())

class TopicDropdown(discord.ui.Select):
    def __init__(self, topics):
        options = []
        for topic in topics:
            label = topic[0]
            emoji = topic[1]
            if emoji:
                options.append(discord.SelectOption(label=label, emoji=emoji))
            else:
                options.append(discord.SelectOption(label=label))

        super().__init__(placeholder="Select a topic", options=options, custom_id="topic_dropdown")

    async def callback(self, interaction: discord.Interaction):
        try:
            conn = sqlite3.connect("tickets.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT category, support FROM topics WHERE topic_name = ? AND guild_id = ?",
                (self.values[0], str(interaction.guild_id))
            )
            topic_data = cursor.fetchone()

            if not topic_data:
                await interaction.response.send_message("Topic not found.", ephemeral=True)
                conn.close()
                return

            category = None
            if topic_data[0]:
                category = interaction.guild.get_channel(int(topic_data[0]))
                if not isinstance(category, discord.CategoryChannel):
                    category = None

            support_role = interaction.guild.get_role(int(topic_data[1])) if topic_data[1] else None
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
            }

            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True)

            ticket_channel = await interaction.guild.create_text_channel(
                f"ticket-{interaction.user.name}",
                category=category,
                overwrites=overwrites
            )

            cursor.execute("""
                INSERT INTO tickets (channel_id, creator_id, guild_id, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (str(ticket_channel.id), str(interaction.user.id), str(interaction.guild.id)))
            conn.commit()
            conn.close()

            embed = discord.Embed(
                title="Ticket Created",
                description=f"Hello {interaction.user.mention}, a support member will assist you shortly.",
                color=discord.Color.green()
            )
            embed.set_footer(
                text="Cypher - Ticketing without clutter",
                icon_url=interaction.client.user.avatar.url if interaction.client.user.avatar else None
            )

            await ticket_channel.send(
                content=f"{interaction.user.mention}" + (f" | {support_role.mention}" if support_role else ""),
                embed=embed,
                view=TicketView()
            )

            await interaction.response.send_message(
                f"<:ded:1449451410025353226> | {interaction.user.mention}: Your ticket has been created - {ticket_channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            print(f"[ERROR] Exception occurred: {e}")
            try:
                await interaction.response.send_message("An error occurred, please contact our support team.", ephemeral=True)
            except discord.InteractionResponded:
                pass

class TicketDropdownView(discord.ui.View):
    def __init__(self, topics):
        super().__init__(timeout=None)
        self.add_item(TopicDropdown(topics))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True
    
class NoTopicTicketModal(discord.ui.Modal, title="Create Ticket"):
    purpose = discord.ui.TextInput(
        label="Purpose of the ticket",
        style=discord.TextStyle.paragraph,
        placeholder="Describe why you're creating this ticket...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    attach_files=True,
                    read_message_history=True
                )
            }

            ticket_channel = await interaction.guild.create_text_channel(
                f"ticket-{interaction.user.name}",
                overwrites=overwrites
            )
            conn = sqlite3.connect("tickets.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tickets (channel_id, creator_id, guild_id, created_at)
                VALUES (?, ?, ?, datetime('now'))
            """, (str(ticket_channel.id), str(interaction.user.id), str(interaction.guild.id)))
            conn.commit()
            conn.close()
            embed = discord.Embed(
                title="Ticket Created",
                description=f"Hello {interaction.user.mention}, a support member will assist you shortly.\n\n**Purpose:**\n```{self.purpose.value}```",
                color=discord.Color.green()
            )
            embed.set_footer(
                text="Cypher - Ticketing without clutter",
                icon_url=interaction.client.user.avatar.url if interaction.client.user.avatar else None
            )

            await ticket_channel.send(
                content=interaction.user.mention,
                embed=embed,
                view=TicketView2()
            )

            await interaction.response.send_message(
                f"<:ded:1449451410025353226> | {interaction.user.mention}: Your ticket has been created - {ticket_channel.mention}",
                ephemeral=True
            )
        except Exception as e:
            print(f"[ERROR] Modal submit failed: {e}")
            try:
                await interaction.response.send_message("Something went wrong while creating your ticket.", ephemeral=True)
            except discord.InteractionResponded:
                pass


class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.gray, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect("tickets.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM tickets WHERE creator_id = ? AND guild_id = ?",
            (str(interaction.user.id), str(interaction.guild_id))
        )
        open_tickets_count = cursor.fetchone()[0]
        if open_tickets_count >= 1:
            await interaction.response.send_message(
                "You already have an open ticket in this server.",
                ephemeral=True
            )
            return

        cursor.execute("SELECT topic_name, emoji FROM topics WHERE guild_id = ?", (str(interaction.guild_id),))
        topics = cursor.fetchall()
        conn.close()

        if not topics:
            await interaction.response.send_modal(NoTopicTicketModal())
            return

        embed = discord.Embed(
            description="Choose a topic from the dropdown below to create a ticket.",
            color=0x71368a
        )
        view = TicketDropdownView(topics)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class Ticket(commands.GroupCog, name="ticket"):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("tickets.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                channel_id TEXT PRIMARY KEY,
                creator_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(creator_id, guild_id)
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name TEXT,
                category TEXT,
                support TEXT,
                emoji TEXT,
                guild_id TEXT,
                UNIQUE(topic_name, guild_id)
            );
        """)

        self.conn.commit()
        self.load_persistent_views()
        
    def load_persistent_views(self):
        self.bot.add_view(TicketButton())
        self.bot.add_view(TicketView())
        self.bot.add_view(TicketView2())
        self.bot.add_view(DeleteTicketView())

    async def replace_placeholders(self, text, ctx):
        if not text:
            return text

        IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(IST)

        replacements = {
            '{user.mention}': ctx.author.mention,
            '{user.name}': ctx.author.name,
            '{user.id}': str(ctx.author.id),
            '{user.nick}': ctx.author.nick if hasattr(ctx.author, 'nick') else ctx.author.name,
            '{user.display_name}': ctx.author.display_name,
            '{user.avatar}': str(ctx.author.display_avatar.url),
            '{user.status}': str(ctx.author.status) if hasattr(ctx.author, 'status') else 'unknown',
            '{user.created_at}': f"<t:{int(ctx.author.created_at.timestamp())}:R>",
            '{user.joined_at}': f"<t:{int(ctx.author.joined_at.timestamp())}:R>" if hasattr(ctx.author, 'joined_at') else '',
            '{user.color}': str(ctx.author.color) if hasattr(ctx.author, 'color') else '',
            '{server.name}': ctx.guild.name if ctx.guild else 'Direct Message',
            '{server.id}': str(ctx.guild.id) if ctx.guild else '',
            '{server.membercount}': str(ctx.guild.member_count) if ctx.guild else '0',
            '{server.created_at}': f"<t:{int(ctx.guild.created_at.timestamp())}:R>" if ctx.guild else '',
            '{server.icon}': str(ctx.guild.icon.url) if ctx.guild and ctx.guild.icon else '',
            '{server.banner}': str(ctx.guild.banner.url) if ctx.guild and ctx.guild.banner else '',
            '{server.owner.name}': ctx.guild.owner.name if ctx.guild else '',
            '{server.owner.id}': str(ctx.guild.owner.id) if ctx.guild else '',
            '{server.owner.mention}': ctx.guild.owner.mention if ctx.guild else '',
            '{present.time}': now.strftime('%H:%M:%S'),
            '{present.date}': now.strftime('%Y-%m-%d'),
            '{present.day}': now.strftime('%A')
        }

        result = text
        for placeholder, value in replacements.items():
            if value is not None:
                result = result.replace(placeholder, value)
        return result

    @commands.group(name="ticket", invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ticket(self, ctx):
        try:
            embed = discord.Embed(
                title="Ticket Topic Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @ticket.group(name="topic", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def topic(self, ctx):
        try:
            embed = discord.Embed(
                title="Ticket Topic Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @topic.command(name="create")
    @commands.has_permissions(manage_guild=True)
    async def topic_create(self, ctx, topic_name: str, emoji: discord.Emoji = None):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM topics WHERE guild_id = ?", (str(ctx.guild.id),))
            topic_count = self.cursor.fetchone()[0]
            if topic_count >= 5:
                await ctx.send(embed=discord.Embed(description=f"<:ded:1449451410025353226> {ctx.author.mention}: You cannot create more than 5 topics per server.",color=0xFEE75C))
                return

            emoji_str = str(emoji) if emoji else None

            self.cursor.execute(
                "INSERT INTO topics (topic_name, emoji, guild_id) VALUES (?, ?, ?)",
                (topic_name, emoji_str, str(ctx.guild.id))
            )
            self.conn.commit()
            await ctx.send(embed=discord.Embed(
                description=f"<:ded:1449451410025353226> {ctx.author.mention}: Topic `{topic_name}` has been created.",
                color=0xFEE75C
            ))

        except sqlite3.IntegrityError:
            await ctx.send(embed=discord.Embed(
                description=f"<:danger:1449451416513941705> | Topic by the name `{topic_name}` already exists in this server.",
                color=0xFEE75C
            ))

    @topic.command(name="name")
    @commands.has_permissions(manage_guild=True)
    async def topic_rename(self, ctx, topic_name: str, new_name: str):
        try:
            self.cursor.execute(
                "SELECT * FROM topics WHERE topic_name = ? AND guild_id = ?",
                (topic_name, str(ctx.guild.id))
            )
            topic = self.cursor.fetchone()

            if not topic:
                await ctx.send(embed=discord.Embed(
                    description=f"<:icons_info:1449445961326792896> {ctx.author.mention}: Topic `{topic_name}` does not exist.",
                    color=0xFEE75C
                ))
                return
            self.cursor.execute(
                "UPDATE topics SET topic_name = ? WHERE topic_name = ? AND guild_id = ?",
                (new_name, topic_name, str(ctx.guild.id))
            )
            self.conn.commit()

            await ctx.send(embed=discord.Embed(
                description=f"<:ded:1449451410025353226> {ctx.author.mention}: Topic `{topic_name}` has been renamed to `{new_name}`.",
                color=0x71368a
            ))

        except sqlite3.IntegrityError:
            await ctx.send(embed=discord.Embed(
                description=f"<:icons_info:1449445961326792896> {ctx.author.mention}: A topic named `{new_name}` already exists.",
                color=0xFEE75C
            ))

    @topic.command(name="emoji")
    @commands.has_permissions(manage_guild=True)
    async def topic_emoji_update(self, ctx, topic_name: str, new_emoji: discord.Emoji):
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        try:
            self.cursor.execute(
                "SELECT * FROM topics WHERE topic_name = ? AND guild_id = ?",
                (topic_name, str(ctx.guild.id))
            )
            topic = self.cursor.fetchone()

            if not topic:
                await ctx.send(embed=discord.Embed(
                    description=f"<:icons_info:1449445961326792896> {ctx.author.mention}: Topic `{topic_name}` does not exist.",
                    color=0xFEE75C
                ))
                return
            self.cursor.execute(
                "UPDATE topics SET emoji = ? WHERE topic_name = ? AND guild_id = ?",
                (str(new_emoji), topic_name, str(ctx.guild.id))
            )
            self.conn.commit()

            await ctx.send(embed=discord.Embed(
                description=f"<:ded:1449451410025353226> {ctx.author.mention}: Emoji for topic `{topic_name}` has been updated to {str(new_emoji)}.",
                color=embed_color
            ))

        except Exception as e:
            await ctx.send(embed=discord.Embed(
                description=f"<:icons_info:1449445961326792896> {ctx.author.mention}: An error occurred: Please contact my staff team`",
                color=0xFEE75C
            ))

    @topic.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def topic_remove(self, ctx, *, topic_name: str):
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        self.cursor.execute("DELETE FROM topics WHERE topic_name = ? AND guild_id = ?", 
                          (topic_name, str(ctx.guild.id)))
        if self.cursor.rowcount:
            self.conn.commit()
            await ctx.send(embed=discord.Embed(description=f"<:ded:1449451410025353226> {ctx.author.mention}: Topic `{topic_name}` has been removed from the database.", color=embed_color))
        else:
            await ctx.send(embed=discord.Embed(description=f"<:icons_info:1449445961326792896> {ctx.author.mention}: Topic by the name `{topic_name}` does not exist in this server.", color=0xFEE75C))


    @ticket.command(name="category")
    @commands.has_permissions(manage_guild=True)
    async def set_category(self, ctx, topic: str, category_id: str):
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        self.cursor.execute("UPDATE topics SET category = ? WHERE topic_name = ? AND guild_id = ?", 
                          (category_id, topic, str(ctx.guild.id)))
        if self.cursor.rowcount:
            self.conn.commit()
            await ctx.send(embed=discord.Embed(description=f"<:ded:1449451410025353226> {ctx.author.mention}: Category for topic `{topic}` has been set to `{category_id}`.", color=embed_color))
        else:
            await ctx.send(embed=discord.Embed(description=f"<:icons_info:1449445961326792896> {ctx.author.mention}: Topic by the name `{topic}` does not exist in this server.", color=0xFEE75C))

    @ticket.command(name="support")
    @commands.has_permissions(manage_guild=True)
    async def set_support(self, ctx, topic: str, support_role: discord.Role):
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        self.cursor.execute("UPDATE topics SET support = ? WHERE topic_name = ? AND guild_id = ?", 
                          (support_role.id, topic, str(ctx.guild.id)))
        if self.cursor.rowcount:
            self.conn.commit()
            await ctx.send(embed=discord.Embed(description=f"<:ded:1449451410025353226> {ctx.author.mention}: Support for topic `{topic}` has been set to {support_role.mention}.", color=embed_color))
        else:
            await ctx.send(embed=discord.Embed(description=f"<:icons_info:1449445961326792896> {ctx.author.mention}: Topic by the name `{topic}` does not exist in this server.", color=0xFEE75C))
    

    @ticket.command(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def setup_ticket(self, ctx, *, code: str = None):
        view = TicketButton()
        embed = discord.Embed(description="> If you require assistance, please select the appropriate support category by clicking the corresponding button below.", color=0x71368a)
        embed.set_footer(text=f"{self.bot.user.name} Ticket", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        await ctx.send(embed=embed, view=view)
            
async def setup(bot):
    await bot.add_cog(Ticket(bot))