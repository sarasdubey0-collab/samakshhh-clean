import discord
from discord.ext import commands
import json
from discord.ui import View, Button, Select
from typing import Dict, List, Tuple, Any
from collections import defaultdict
from functools import wraps
import asyncio
import uuid

class RoleLimit(Exception):
    pass

def role_limit_decorator(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except RoleLimit as e:
            interaction = next((arg for arg in args if isinstance(arg, discord.Interaction)), None)
            if interaction:
                await interaction.response.send_message(str(e), ephemeral=True)
    return wrapper

class AutoRoleManager:
    def __init__(self):
        self.data: Dict[str, Dict[str, List[int]]] = defaultdict(lambda: {"humans": [], "bots": []})


    def load_data(self):
        try:
            with open('database/autorole.json', 'r') as f:
                self.data = defaultdict(lambda: {"humans": [], "bots": []}, json.load(f))
        except FileNotFoundError:
            pass

    def save_data(self):
        with open('database/autorole.json', 'w') as f:
            json.dump(dict(self.data), f, indent=4)

    def check_role_limit(self, guild_id: str, role_type: str) -> Tuple[bool, int]:
        current_roles = self.data[guild_id][role_type]
        max_roles = 5 if role_type == "humans" else 2
        return len(current_roles) >= max_roles, max_roles

    def add_role(self, guild_id: str, role_type: str, role_id: int) -> None:
        at_limit, max_roles = self.check_role_limit(guild_id, role_type)
        if at_limit:
            raise RoleLimit(f"<:MekoExclamation:1449445917500510229> Maximum limit of {max_roles} roles for {role_type} has been reached.")
        if role_id not in self.data[guild_id][role_type]:
            self.data[guild_id][role_type].append(role_id)
            self.save_data()

    def remove_role(self, guild_id: str, role_type: str, role_id: int) -> None:
        if role_id in self.data[guild_id][role_type]:
            self.data[guild_id][role_type].remove(role_id)
            self.save_data()

    def get_roles(self, guild_id: str, role_type: str) -> List[int]:
        return self.data[guild_id][role_type]

    def reset_guild(self, guild_id: str) -> None:
        if guild_id in self.data:
            del self.data[guild_id]
            self.save_data()

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = AutoRoleManager()
        self.manager.load_data()

    @commands.command(name="Autorole", invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx):
        embed = discord.Embed(description="<:MekoArrowRight:1449445989436887090> Please choose an option from the provided buttons below.\n\n**Autorole Add**\nClick on the `Autorole Add` button to setup autoroles for bots or human.\n\n**Autorole Remove**\nTo remove autoroles for bots or humans, click on the `Autorole Remove` button.\n\n**Autorole Config**\nClick on the `Autorole Config` button to list the current configuration of the autorole setup.", color=discord.Color.red())
        embed.set_author(name=f"Autorole Menu", icon_url=self.bot.user.avatar)
        view = AutoroleView(self.bot, self.manager, ctx.author.id, ctx.guild.id)
        message = await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            error_embed = discord.Embed(description="<:MekoWarn:1449451374113984532> **Autorole Setup Menu** has been timed out.", color=discord.Color.red())
            await message.edit(embed=error_embed, view=None)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        role_type = "bots" if member.bot else "humans"
        roles = self.manager.get_roles(guild_id, role_type)
        for role_id in roles:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason=f"{self.bot.user.name} @ {role_type} autorole")
                except discord.HTTPException:
                    pass

class AutoroleView(discord.ui.View):
    def __init__(self, bot, manager: AutoRoleManager, user_id: int, guild_id: int):
        super().__init__(timeout=300)
        self.bot = bot
        self.manager = manager
        self.user_id = user_id
        self.guild_id = guild_id
        self.value = None

    @discord.ui.button(label="Autorole Add", style=discord.ButtonStyle.success)
    async def autorole_add(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                description=(
                    f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n"
                    f"<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button."
                )
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create a new view for the second embed with Human, Bot, and Back buttons
        view = AutoroleSubmenuView(self.bot, self.manager, self.user_id, self.guild_id)
        embed = discord.Embed(
            description="<:MekoArrowRight:1449445989436887090> Please choose an option from the provided buttons below to setup an autorole for `Humans` or `Bots`."
        )
        embed.set_author(name=f"Autorole Menu", icon_url=self.bot.user.avatar)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Autorole Config", style=discord.ButtonStyle.success)
    async def config(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            embed = discord.Embed()
            embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = str(self.guild_id)
        human_roles = self.manager.get_roles(guild_id, "humans")
        bot_roles = self.manager.get_roles(guild_id, "bots")
        
        human_role_mentions = ", ".join([f"<@&{role_id}>" for role_id in human_roles]) or "Not Configured Yet"
        bot_role_mentions = ", ".join([f"<@&{role_id}>" for role_id in bot_roles]) or "Not Configured Yet"
        
        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(name=f"Autorole Setup Config", icon_url=interaction.user.avatar.url)
        embed.set_footer(icon_url=interaction.user.avatar.url, text=f"Requested by {interaction.user.name}")
        embed.add_field(name="Human Autoroles", value=human_role_mentions, inline=False)
        embed.add_field(name="Bot Autoroles", value=bot_role_mentions, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Autorole Reset", style=discord.ButtonStyle.danger)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            embed = discord.Embed()
            embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        self.manager.reset_guild(str(self.guild_id))
        embed = discord.Embed(description=f"All the roles and setup data for autoroles including **Humans** and **Bots** have been cleared and no roles will be assigned to the users upon joining!", color=discord.Color.red())
        embed.set_author(name="Autorole Setup Cleared", icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"Action performed by {interaction.user.name}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)


class AutoroleSubmenuView(discord.ui.View):
    def __init__(self, bot, manager, user_id, guild_id):
        super().__init__()
        self.bot = bot
        self.manager = manager
        self.user_id = user_id
        self.guild_id = guild_id

    async def setup_roles(self, interaction: discord.Interaction, role_type: str):
        guild = interaction.guild
        roles = [role for role in guild.roles if role < guild.me.top_role and not role.managed and role != guild.default_role]
        
        at_limit, max_roles = self.manager.check_role_limit(str(self.guild_id), role_type)
        if at_limit:
            raise RoleLimit(f"Maximum limit of {max_roles} roles for {role_type} has been reached.")
        
        view = RoleSelectView(self.manager, self.user_id, roles, role_type, str(self.guild_id))
        embed = discord.Embed(
            description="<:MekoArrowRight:1449445989436887090> Please select one or more roles from the selection menu to assign as human autoroles.\n\n<:MekoRuby:1449445982931783710> **Note :** If your server roles have custom font names you may not be able to find them in the selection menu, so in that case use the `Add Roles` button."
        )
        embed.set_author(name=f"Autorole Menu", icon_url=self.bot.user.avatar)
        await interaction.response.edit_message(content=None, embed=embed, view=view)
        
        await view.wait()
        if not view.roles:
            await interaction.followup.send(f"oops! this **Autorole** setup menu has timed out due to inactivity!")
            return

        role_mentions = ", ".join([role.mention for role in view.roles])
        embed = discord.Embed(description=f"Alright! **{role_type}** autorole has been setup and roles will be assigned to users upon joining from now onwards!", color=discord.Color.blurple())
        embed.add_field(name=f"**__Roles__**", value=role_mentions)
        embed.set_footer(icon_url=interaction.user.avatar.url, text=f"Action performed by {interaction.user.name}")
        embed.set_author(name=f"Autorole Setup", icon_url=interaction.user.avatar.url)
        await interaction.followup.send(embed=embed)

    @discord.ui.button(label="Humans", style=discord.ButtonStyle.success)
    async def humans(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                description=(
                    f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n"
                    f"<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button."
                )
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await self.setup_roles(interaction, "humans")

    @discord.ui.button(label="Bots", style=discord.ButtonStyle.success)
    async def bots(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                description=(
                    f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n"
                    f"<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button."
                )
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await self.setup_roles(interaction, "bots")

    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                description=(
                    f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button."
                )
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Return to the main autorole embed
        view = AutoroleView(self.bot, self.manager, self.user_id, self.guild_id)
        embed = discord.Embed(description="<:MekoArrowRight:1449445989436887090> Please choose an option from the provided buttons below.\n\n**Autorole Add**\nClick on the `Autorole Add` button to setup autoroles for bots or human.\n\n**Autorole Remove**\nTo remove autoroles for bots or humans, click on the `Autorole Remove` button.\n\n**Autorole Config**\nClick on the `Autorole Config` button to list the current configuration of the autorole setup.", color=discord.Color.red())
        embed.set_author(name=f"Autorole Menu", icon_url=self.bot.user.avatar)
        await interaction.response.edit_message(embed=embed, view=view)


class RoleSelectView(discord.ui.View):
    def __init__(self, manager: AutoRoleManager, user_id: int, roles: List[discord.Role], role_type: str, guild_id: str):
        super().__init__(timeout=300)
        self.manager = manager
        self.user_id = user_id
        self.roles: List[discord.Role] = []
        self.role_type = role_type
        self.guild_id = guild_id
        self.add_item(RoleSelect(roles, role_type, manager.check_role_limit(guild_id, role_type)[1]))
        self.add_item(UseMentionButton(manager, user_id, guild_id, role_type))
        self.add_item(Button(label="Back", style=discord.ButtonStyle.primary, custom_id="back_button"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
class RoleSelect(discord.ui.Select):
    def __init__(self, roles: List[discord.Role], role_type: str, max_roles: int):
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in roles[:25]]
        super().__init__(placeholder=f"Select roles", options=options, max_values=max_roles)

    async def callback(self, interaction: discord.Interaction):
        view: RoleSelectView = self.view
        selected_roles = [interaction.guild.get_role(int(value)) for value in self.values]
        
        for role in selected_roles:
            try:
                view.manager.add_role(view.guild_id, view.role_type, role.id)
                view.roles.append(role)
            except RoleLimit as e:
                await interaction.response.send_message(str(e), ephemeral=True)
                return
        await interaction.response.defer()
        view.stop()

    
class UseMentionButton(discord.ui.Button):
    def __init__(self, manager: AutoRoleManager, user_id: int, guild_id: str, role_type: str):
        super().__init__(label="Use Mention/ID", style=discord.ButtonStyle.success)
        self.manager = manager
        self.user_id = user_id
        self.guild_id = guild_id
        self.role_type = role_type

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                description=(
                    f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n"
                    f"<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button."
                )
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed= discord.Embed()
        embed.description="<:MekoArrowRight:1449445989436887090> Please send upto 5 role Mentions or IDs in this channel."
        
        await interaction.response.send_message(
            embed=embed, 
            ephemeral=True
        )

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for("message", check=check, timeout=60)
            content = msg.content.strip()

            if content.isdigit():
                # If the input is a number, treat it as a role ID
                role_id = int(content)
                role = interaction.guild.get_role(role_id)
                if role:
                    try:
                        self.manager.add_role(self.guild_id, self.role_type, role.id)
                        await interaction.followup.send(f"Role {role.name} added successfully!")
                    except RoleLimit as e:
                        await interaction.followup.send(str(e), ephemeral=True)
                else:
                    await interaction.followup.send(f"Role with ID `{role_id}` not found. Please check the role ID.", ephemeral=True)
            else:
                # If it's not a number, check if it's a mention
                if len(content) > 2 and content[0] == '<' and content[1] == '@':
                    role_id = int(content.split('>')[0][3:])
                    role = interaction.guild.get_role(role_id)
                    if role:
                        try:
                            self.manager.add_role(self.guild_id, self.role_type, role.id)
                            await interaction.followup.send(f"Role {role.name} added successfully!")
                        except RoleLimit as e:
                            await interaction.followup.send(str(e), ephemeral=True)
                    else:
                        await interaction.followup.send(f"Role mention `{content}` not found. Please check the role mention.", ephemeral=True)
                else:
                    await interaction.followup.send("Invalid input. Please provide a valid role ID or mention a role.", ephemeral=True)

        except asyncio.TimeoutError:
            await interaction.followup.send("You took too long to respond. The action has been cancelled.", ephemeral=True)
            
    @discord.ui.button(label="Back", style=discord.ButtonStyle.primary, custom_id="back_button")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                description=(
                    f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button."
                )
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Return to the previous menu (Main or Submenu based on your logic)
        view = AutoroleView(self.bot, self.manager, self.user_id, self.guild_id)
        embed = discord.Embed(
            description=(
                "<:MekoArrowRight:1449445989436887090> Please choose an option from the provided buttons below.\n\n"
                "**Autorole Add**\nClick on the `Autorole Add` button to setup autoroles for bots or humans.\n\n"
                "**Autorole Remove**\nTo remove autoroles for bots or humans, click on the `Autorole Remove` button.\n\n"
                "**Autorole Config**\nClick on the `Autorole Config` button to list the current configuration of the autorole setup."
            ),
            color=discord.Color.red()
        )
        embed.set_author(name="Autorole Menu", icon_url=self.bot.user.avatar)
        await interaction.response.edit_original_message(embed=embed, view=view)
    

async def setup(client):
    await client.add_cog(AutoRole(client))