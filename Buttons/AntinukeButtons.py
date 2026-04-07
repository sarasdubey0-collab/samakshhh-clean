import discord
from discord.ui import Button, View, Modal, TextInput, Select, ChannelSelect
from rix import ParrotPaginator, PaginationView
from utils.tool import *
from utils.tool import getConfig, getanti, updateAntiChannelLogs, updateAntiGuildLogs, updateAntiModLogs, updateAntiRoleLogs




class TrashButton(discord.ui.Button):
    def __init__(self, author_id):
        super().__init__(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.gray)
        self.author_id = author_id
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFFFFFF ),ephemeral=True)
            return
        await interaction.message.delete()

class SupportButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Need Help? Join Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/UtZ3rRnBnU")


class Buttons(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=None)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="<:WhitelistUser:1449445925109108888>", label="Whitelisted Users", style=discord.ButtonStyle.grey, row=0)
    async def wl_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = getConfig(interaction.guild_id)
        if data is None:
            await interaction.response.send_message(
                "Failed to load configuration data.",
                ephemeral=True
            )
            return
        wled = data.get("whitelisted", [])
        prefix = data["prefix"]
        if len(wled) == 0:
            await interaction.response.send_message(
                f"There isn't any Whitelisted users to show. You can add them by `{prefix}antinuke wl add <user>`",
                ephemeral=True
            )
        else:
            embed = discord.Embed(
                title="Whitelisted Users:",
                description="Whitelisted users for this server:\n",
                color=0xFFFFFF
            )
            for idk in wled:
                embed.description += f"<@{idk}> | (ID: {idk})\n"
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="<:MekoBan:1449445932713377802> ", label="Antinuke Punishment", style=discord.ButtonStyle.grey, row=0)
    async def puni_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = getConfig(interaction.guild_id)

        if data is None:
            await interaction.response.send_message(
                "Failed to load configuration data.",
                ephemeral=True
            )
            return

        punish = data.get("punishment", "Not set")
        await interaction.response.send_message(
            f"Current Antinuke Punishment For Antinuke In This Server Is: **{punish.title()}**",
            ephemeral=True
        )

class PunishmentView(View):
    def __init__(self, author_id: int, guild_id: int):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.guild_id = guild_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="Kick", style=discord.ButtonStyle.gray)
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.set_punishment("Kick")
            embed = discord.Embed(
                    description=f"<:tick_icons:1449445939256229961> {interaction.user.mention}: Punishment for this server has been set to **`Kick`**.",
                    color=0xFFFFFF)
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed,view=self.replace_with_trash_button()
            )
        except Exception as e:
            print(e)
            
    @discord.ui.button(label="Ban", style=discord.ButtonStyle.gray)
    async def ban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.set_punishment("Ban")
            embed = discord.Embed(
                    description=f"<:tick_icons:1449445939256229961> {interaction.user.mention}: Punishment for this server has been set to **`Ban`**.",
                    color=0xFFFFFF)
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed,view=self.replace_with_trash_button()
            )
        except Exception as e:
            print(e)

    @discord.ui.button(label="Strip", style=discord.ButtonStyle.gray)
    async def none_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.set_punishment("Strip")
            embed = discord.Embed(
                    description=f"<:tick_icons:1449445939256229961> {interaction.user.mention}: Punishment for this server has been set to **`Strip`**.",
                    color=0xFFFFFF)
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed,view=self.replace_with_trash_button()
            )
        except Exception as e:
            print(e)

    async def set_punishment(self, punishment: str):
        try:
            config = getConfig(self.guild_id)
            config["punishment"] = punishment
            updateConfig(self.guild_id, config)
        except Exception as e:
            print(f"Failed to set punishment: {e}")

    def replace_with_trash_button(self) -> View:
        """Removes all buttons and adds only the Trash button."""
        trash_button_view = View()
        trash_button_view.add_item(TrashButton(self.author_id))
        return trash_button_view
    
class ChannelNameModal(Modal):
    def __init__(self, author_id):
        super().__init__(title="Channel Recovery", timeout=None)
        self.chan = TextInput(label="Enter the Channel Name", placeholder="e.g. general", style=discord.TextStyle.short)
        self.add_item(self.chan)
        self.author_id = author_id
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_name = self.chan.value
            channels = [channel for channel in interaction.guild.channels if channel.name == channel_name]
            if channels:
                view = ChannelConfirmationView(channels, channel_name, self.author_id)
                embed = discord.Embed(description=f"Channel(s) found by the name: **`{channel_name}`** | Channel(s) count `{len(channels)}`\n- Use the **`Proceed`** button below if you want to delete all the channel(s) by the name **`{channel_name}`** in this server, Or Use the **`Abort`** button to abort the channel recovery", color=0xFFFFFF)
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                view = View()
                view.add_item(TrashButton(self.author_id))
                embed = discord.Embed(description=f"No channels found by the name: **`{channel_name}`**\n- Use the `antinuke recover` command again and this time please submit a valid channel name", color=0xFFFFFF)
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            print(e)

class ChannelConfirmationView(View):
    def __init__(self, channels,channel_name, author_id):
        super().__init__(timeout=None)
        self.channels = channels
        self.channelname = channel_name
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.gray)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            for channel in self.channels:
                await channel.delete(reason="Cypher • Recovery | (Channels)")
            embed = discord.Embed(description=f"**__Channel recovery finished__**\nDeleted all the channel(s) by the name: **`{self.channelname}`**.\n - Total channel(s) deleted: **`{len(self.channels)}`**", color=0xFFFFFF)
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            view = View()
            view.add_item(TrashButton(self.author_id))
            await interaction.response.edit_message(embed=embed, view=view)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have the necessary permissions needed to perform this action.")
        except Exception as e:
            print(e)

    @discord.ui.button(label="Abort", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            embed = discord.Embed(description="Ok, I will not delete any channel(s)", color=0xFFFFFF)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            view = View()
            view.add_item(TrashButton(self.author_id))
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            print(e)

class RoleNameModal(Modal):
    def __init__(self, author_id):
        super().__init__(title="Role Recovery", timeout=None)
        self.role = TextInput(label="Enter the Role Name", placeholder="e.g. newrole", style=discord.TextStyle.short)
        self.add_item(self.role)
        self.author_id = author_id
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            role_name = self.role.value
            roles = [role for role in interaction.guild.roles if role.name == role_name]
            if roles:
                view = RoleConfirmationView(roles, role_name, self.author_id)
                embed = discord.Embed(
                    description=f"Role(s) found by the name: **`{role_name}`** | Role count `{len(roles)}`\n- Use the **`Proceed`** button below if you want to delete all the role(s) by the name **`{role_name}`** in this server, or use the **`Cancel`** button to abort the role recovery",
                    color=0xFFFFFF
                )
                embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                view = View()
                view.add_item(TrashButton(self.author_id))
                embed = discord.Embed(
                    description=f"No roles found by the name: **`{role_name}`**\n- Use the `antinuke recover` command again and this time please submit a valid role name",
                    color=0xFFFFFF
                )
                embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            print(f"Error in RoleNameModal on_submit: {e}")

class RoleConfirmationView(View):
    def __init__(self, roles, role_name, author_id):
        super().__init__(timeout=None)
        self.roles = roles
        self.rolename = role_name
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Proceed", style=discord.ButtonStyle.gray)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            for role in self.roles:
                await role.delete(reason="Cypher • Recovery | (Roles)")
            embed = discord.Embed(description=f"**__Role recovery finished__**\nDeleted all the role(s) by the name: **`{self.rolename}`**.\n - Total role(s) deleted: **`{len(self.roles)}`**", color=0xFFFFFF)
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url={interaction.user.display_avatar.url})
            view = View()
            view.add_item(TrashButton(self.author_id))
            await interaction.response.edit_message(embed=embed, view=view)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have the necessary permissions to perform this action.")
        except Exception as e:
            pass

    @discord.ui.button(label="Abort", style=discord.ButtonStyle.gray)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            embed = discord.Embed(
                description="Ok, I will not delete any role(s).",
                color=0xFFFFFF
            )
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url={interaction.user.display_avatar.url})
            view = View()
            view.add_item(TrashButton(self.author_id))
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            pass

class RecoverButton(View):
    def __init__(self, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Channel", style=discord.ButtonStyle.gray)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(ChannelNameModal(self.author_id))
        except Exception as e:
            pass

    @discord.ui.button(label="Role", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(RoleNameModal(self.author_id))
        except Exception as e:
            pass

class AntiEvents(Select):
    def __init__(self, guild_id, author):
        self.guild_id = guild_id
        self.author_id = author
        options = [
            discord.SelectOption(label="AntiBan", description="Configure AntiBan Event For Antinuke", value="antiban"),
            discord.SelectOption(label="Antikick", description="Configure AntiKick Event For Antinuke", value="antikick"),
            discord.SelectOption(label="AntiPrune", description="Configure AntiPrune Event For Antinuke", value="antiprune"),
            discord.SelectOption(label="AntiGuild", description="Configure AntiGuild Event For Antinuke", value="antiguild"),
            discord.SelectOption(label="AntiBot", description="Configure AntiBot Event For Antinuke", value="antibot"),
            discord.SelectOption(label="AntiMember", description="Configure AntiMember Event For Antinuke", value="antimemb"),
            discord.SelectOption(label="AntiPing", description="Configure AntiPing (@everyone or @here) Event For Antinuke", value="antiping"),
            discord.SelectOption(label="AntiChannel", description="Configure AntiChannel (Channel Create, Delete, Update) Event For Antinuke", value="antich"),
            discord.SelectOption(label="AntiRole", description="Configure AntiRole (Role Create, Delete, Update) Event For Antinuke", value="antirole"),
            discord.SelectOption(label="AntiWebhook", description="Configure AntiWebhook (Webhook Create, Delete, Update) Event For Antinuke", value="antiweb"),
            discord.SelectOption(label="AntiSticker/Emoji", description="Configure AntiSticker/Emoji (Create, Delete, Webhook) Event For Antinuke", value="antiemojisticker")
        ]
        super().__init__(placeholder="Select an event to configure", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                f"You cannot use this button. Only <@{self.author_id}> can use this button.", ephemeral=True
            )
            return
        try:
            if self.values[0] == "antiban":
                embed = discord.Embed(
                    description=f"**__Configure AntiBan Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiBan`** event for this guild\n\n**__What does AntiBan do__**?\n - **{interaction.client.user.name}** prevents unauthorized bans by banning the user and automatically unbanning the user who got banned by the user & also prevents unauthorized unbans by banning the user and banning the unbanned user again.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=0xFFFFFF
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntibanButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antikick":
                embed = discord.Embed(
                    description=f"**__Configure AntiKick Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiKick`** event for this guild\n\n**__What does AntiKick do__**?\n - **{interaction.client.user.name}** prevents unauthorized bans by banning the user and automatically unbanning the user who got banned by the user.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=0xFFFFFF
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntikickButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antiprune":
                embed = discord.Embed(
                    description=f"**__Configure AntiPrune Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiPrune`** event for this guild\n\n**__What does AntiPrune do__**?\n - **{interaction.client.user.name}** punishes the user if they prune members and is not whitelisted.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=0xFFFFFF
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiPruneButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antiguild":
                embed = discord.Embed(
                    description=f"**__Configure AntiGuild Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiGuild`** event for this guild\n\n**__What does AntiGuild do__**?\n - **{interaction.client.user.name}** punishes the user if they made changes in the server like `Name`, `Icon`, `Description`, and more & reverts the changes to before.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=0xFFFFFF
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiGuildButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antibot":
                color = 0xFFFFFF
                embed = discord.Embed(
                    description=f"**__Configure AntiBot Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiBot`** event for this guild\n\n**__What does AntiBot do__**?\n - **{interaction.client.user.name}** punishes the user if they add any bots in the server & also bans the added bot.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiBotButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antimemb":
                color = 0xFFFFFF
                embed = discord.Embed(
                    description=f"**__Configure AntiMember Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiMember`** event for this guild\n\n**__What does AntiMember do__**?\n - **{interaction.client.user.name}** punishes the user if they updates member like `Nickname`, `Timeout`, `Role Update` & also reverts the changes made to the user.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiMemberButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antiping":
                color = 0xFFFFFF
                embed = discord.Embed(
                    description=f"**__Configure AntiMember Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiMember`** event for this guild\n\n**__What does AntiMember do__**?\n - **{interaction.client.user.name}** punishes the user if they mentions `@everyone` or `@here` in the server & also deletes the mention message(s)\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiPingButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antich":
                color = 0xFFFFFF
                embed = discord.Embed(
                    description=f"**__Configure AntiChannel Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiChannel`** event for this guild\n\n**__What does AntiChannel do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update channels & also reverts the changes made by the user.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiChannelButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antirole":
                color = 0xFFFFFF
                embed = discord.Embed(
                    description=f"**__Configure AntiRole Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiRole`** event for this guild\n\n**__What does AntiRole do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update roles & also reverts the changes made by the user.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiRoleButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antiweb":
                color = 0xFFFFFF
                embed = discord.Embed(
                    description=f"**__Configure AntiWebhook Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiWebhook`** event for this guild\n\n**__What does AntiWebhook do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update webhooks & also reverts the changes made by the user.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiWebhookButtons(self.guild_id, self.author_id))
            elif self.values[0] == "antiemojisticker":
                color = 0xFFFFFF
                embed = discord.Embed(
                    description=f"**__Configure AntiEmoji/Sticker Event__**\nUse the **`Enable`** or **`Disable`** button to enable or disable **`AntiEmoji/Sticker`** event for this guild\n\n**__What does AntiEmoji/Sticker do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update emojis/stickers & also reverts the changes made by the user.\n\nNote - The **`Antinuke`** must be enabled for the guild for this event to function properly.",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                 icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                 icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed, view=AntiEmojiStickerButtons(self.guild_id, self.author_id))
        except Exception as e:
            print(f"Error in select_callback for guild {self.guild_id}: {e}")

class AntibanButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.guild_id = guild_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantiban(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled Antiban event for this guild__**\n\n**__What does Antiban do__**?\n - **{interaction.client.user.name}** prevents unauthorized bans by banning the user and automatically unbanning the user who got banned by the user & also prevents unauthorized unbans by banning the user and banning the unbanned user again.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantiban(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled Antiban event for this guild__**\n\n**__What does Antiban do__**?\n - **{interaction.client.user.name}** prevents unauthorized bans by banning the user and automatically unbanning the user who got banned by the user & also prevents unauthorized unbans by banning the user and banning the unbanned user again.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n<:info:1449445954142081278> **__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n<:info:1449445954142081278> **__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n<:info:1449445954142081278> **__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntikickButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.guild_id = guild_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantikick(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiKick event for this guild__**\n\n**__What does Antiban do__**?\n - **{interaction.client.user.name}** punishes the user if they kicked another user and is not whitelisted.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantikick(self.guild_id, "off")
            await interaction.response.send_message(f"Antikick has been disabled for this guild.", ephemeral=True)
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiKick event for this guild__**\n\n**__What does Antiban do__**?\n - **{interaction.client.user.name}** punishes the user if they kicked another user and is not whitelisted.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiPruneButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantiprune(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiPrune event for this guild__**\n\n**__What does Antiban do__**?\n - **{interaction.client.user.name}** punishes the user if they prune members and is not whitelisted.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantiprune(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiPrune event for this guild__**\n\n**__What does AntiPrune do__**?\n - **{interaction.client.user.name}** punishes the user if they prune members and is not whitelisted.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiGuildButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantiguild(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiGuild event for this guild__**\n\n**__What does AntiGuild do__**?\n - **{interaction.client.user.name}** punishes the user if they made changes in the server like `Name`, `Icon`, `Description`, and more & reverts the changes to before if they are not whitelisted.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantiguild(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiGuild event for this guild__**\n\n**__What does AntiGuild do__**?\n - **{interaction.client.user.name}** punishes the user if they made changes in the server like `Name`, `Icon`, `Description`, and more & reverts the changes to before.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiBotButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantibot(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiBot event for this guild__**\n\n**__What does AntiBot do__**?\n - **{interaction.client.user.name}** punishes the user if they add any bots in the server & also bans the added bot",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantibot(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiBot event for this guild__**\n\n**__What does AntiBot do__**?\n - **{interaction.client.user.name}** punishes the user if they add any bots in the server & also bans the added bot",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiMemberButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            antiupdatememb(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiMember event for this guild__**\n\n**__What does AntiMember do__**?\n - **{interaction.client.user.name}** punishes the user if they updates member like `Nickname`, `Timeout`, `Role Update` & also reverts the changes made to the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            antiupdatememb(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiMember event for this guild__**\n\n**__What does AntiMember do__**?\n - **{interaction.client.user.name}** punishes the user if they updates member like `Nickname`, `Timeout`, `Role Update` & also reverts the changes made to the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiPingButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:icons_info:1449445961326792896> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantiping(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiPing event for this guild__**\n\n**__What does AntiPing do__**?\n - **{interaction.client.user.name}** punishes the user if they mentions `@everyone` or `@here` in the server & also deletes the mention message(s).",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantiping(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiPing event for this guild__**\n\n**__What does AntiPing do__**?\n - **{interaction.client.user.name}** punishes the user if they mentions `@everyone` or `@here` in the server & also deletes the mention message(s).",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiChannelButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantichannel(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiPing event for this guild__**\n\n**__What does AntiPing do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update channels & also reverts the changes made by the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantichannel(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiPing event for this guild__**\n\n**__What does AntiPing do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update channels & also reverts the changes made by the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiRoleButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantirole(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiPing event for this guild__**\n\n**__What does AntiPing do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update roles & also reverts the changes made by the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantirole(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiPing event for this guild__**\n\n**__What does AntiPing do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update roles & also reverts the changes made by the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiWebhookButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantiweb(self.guild_id, "on")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiPing event for this guild__**\n\n**__What does AntiPing do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update webhooks & also reverts the changes made by the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantiweb(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiPing event for this guild__**\n\n**__What does AntiPing do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update webhooks & also reverts the changes made by the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))

class AntiEmojiStickerButtons(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {interaction.user.mention}: Oops! Sorry, but you can't interact with these buttons this is only for <@{self.author_id}>", color=0xFEE75C ),ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.gray)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try: 
            updateantiemoji(self.guild_id, "on")
            color = 0xFFFFFF 
            embed = discord.Embed(
                description=f"**__Successfully enabled AntiEmoji/Sticker event for this guild__**\n\n**__What does AntiEmoji/Sticker do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update webhooks & also reverts the changes made by the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error enabling antiban {e}")

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.gray)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            updateantiemoji(self.guild_id, "off")
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"**__Successfully disabled AntiEmoji/Sticker event for this guild__**\n\n**__What does AntiEmoji/Sticker do__**?\n - **{interaction.client.user.name}** punishes user if they create, delete, or update webhooks & also reverts the changes made by the user.",
                color=color
                )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                             icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error disabling antiban for guild {self.guild_id}: {e}")

    @discord.ui.button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.grey)
    async def trash(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.message.delete()
        except Exception as e:
            print(e)

    @discord.ui.button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n**__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n**__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n**__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n**__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                         icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                         icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=AntiEventView(self.guild_id, interaction.user.id))


class AntiEventView(discord.ui.View):
    def __init__(self, guild_id, author_id):
        super().__init__(timeout=None)
        self.add_item(SupportButton())
        self.add_item(TrashButton(author_id))
        self.add_item(AntiEvents(guild_id, author_id))



class ChannelLogDropdown(Select):
    def __init__(self, guild_id, author):
        self.guild_id = guild_id
        self.author_id = author
        options = [
            discord.SelectOption(label="Channel Log", value="chan"),
            discord.SelectOption(label="Role Log", value="role")
        ]
        super().__init__(placeholder="Select an event to configure", options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                f"You cannot use this button. Only <@{self.author_id}> can use this button.", ephemeral=True
            )
            return
        try:
            if self.values[0] == "chan":
                embed = discord.Embed(title="Channel Log Selected", description=f"Selected: {self.values[0]}")
                embed.add_field(name="Next Step", value="Select a specific channel or create a new log.")
                await interaction.response.edit_message(embed=embed)
            elif self.values[0] == "role":
                embed = discord.Embed(title="Role Log Selected", description=f"Selected: {self.values[0]}")
                embed.add_field(name="Next Step", value="Select a specific channel or create a new log.")
                await interaction.response.edit_message(embed=embed)
        except Exception as e:
            print(f"Error in select_callback for guild {self.guild_id}: {e}")


class ShowModulesButton(discord.ui.Button):
    def __init__(self, author_id: int):
        super().__init__(label="Show Modules!", style=discord.ButtonStyle.primary)
        self.author_id = author_id  

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.author_id:
            color = 0xFFFFFF
            embed1 = discord.Embed(
                title="Antinuke Modules:\nTotal Modules: 19",
                description=f"""
                > **Anti Ban:** <:enable:1449445968297853040>
                > **Anti Kick:** <:enable:1449445968297853040>
                > **Anti Prune:** <:enable:1449445968297853040>
                > **Anti Bot:** <:enable:1449445968297853040>
                > **Anti Channel Create:** <:enable:1449445968297853040>
                > **Anti Channel Delete:** <:enable:1449445968297853040>
                > **Anti Channel Update:** <:enable:1449445968297853040>
                > **Anti Role Create:** <:enable:1449445968297853040>
                > **Anti Role Delete:** <:enable:1449445968297853040>
                > **Anti Role Update:** <:enable:1449445968297853040>
                > **Anti Emoji Create:** <:enable:1449445968297853040>
                > **Anti Emoji Delete:** <:enable:1449445968297853040>
                > **Anti Emoji Update:** <:enable:1449445968297853040>
                > **Anti Sticker Create:** <:enable:1449445968297853040>
                > **Anti Sticker Delete:** <:enable:1449445968297853040>
                > **Anti Sticker Update:** <:enable:1449445968297853040>
                > **Anti Webhook Create:** <:enable:1449445968297853040>
                > **Anti Webhook Delete:** <:enable:1449445968297853040>
                > **Anti Everyone/Here Mention:** <:enable:1449445968297853040>""",
                color=color)
            embed1.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            await interaction.response.send_message(embed=embed1, ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)


class OtherSettingsButton(discord.ui.Button):
    def __init__(self, author_id: int):
        super().__init__(label="Other Settings", style=discord.ButtonStyle.primary)
        self.author_id = author_id  

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.author_id:
            color = 0xFFFFFF
            ok = getConfig(interaction.guild.id)
            wled = ok["whitelisted"]
            prefix = ok.get("prefix", ".")
            response_embed = discord.Embed(
                title="Other Settings",
                description=f"**Auto Recovery:** <:enable:1449445968297853040>\n\n**Whitelisted Users:** {len(wled)}\nUse **`{prefix}antinuke whitelist`** to check the whitelist command(s)\n\nTo change the punishment type **`>antinuke punishment set <type>`**\nAvailable Punishments are - **`Ban`**, **`Kick`** & **`Strip`**",
                color=color
            )
            await interaction.response.send_message(embed=response_embed, ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)



class ThresholdDatabase:
    def __init__(self, option):
        self.file_path = f"AntinukeDatabase/AntinukeThresholdDB/{option.lower()}.json"

    def get_threshold(self, guild_id):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
            return data.get("guilds", {}).get(str(guild_id), {}).get("threshold", 1)
        except FileNotFoundError:
            return 1

    def update_threshold(self, guild_id, threshold):
        try:
            with open(self.file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"guilds": {}}

        if "guilds" not in data:
            data["guilds"] = {}
        
        if str(guild_id) not in data["guilds"]:
            data["guilds"][str(guild_id)] = {}

        data["guilds"][str(guild_id)]["threshold"] = threshold

        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

class ThresholdModal(Modal):
    def __init__(self, guild_id, option, original_view, original_embed):
        super().__init__(title=f"Set Threshold for {option}")
        self.guild_id = guild_id
        self.option = option
        self.database = ThresholdDatabase(option)
        self.original_view = original_view
        self.original_embed = original_embed

        self.threshold_input = TextInput(
            label="Enter Threshold (Number)",
            placeholder="e.g., 3",
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.threshold_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            threshold = int(self.threshold_input.value)
            if threshold <= 0:
                raise ValueError("Threshold must be a positive integer.")

            self.database.update_threshold(self.guild_id, threshold)
            color = 0xFFFFFF
            embed = discord.Embed(
                description=f"<:tick_icons:1449445939256229961>{interaction.user.mention} Threshold has been set to **`{threshold}`** for **`{self.option}`**",
                color=color
            )
            embed.set_author(name=interaction.guild.name,
                             icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            view = View()
            view.add_item(BackButton(self.original_embed, self.original_view))
            view.add_item(DeleteButton())
            view.add_item(SupportServerButton())

            await interaction.response.edit_message(embed=embed, view=view)

        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid positive integer.", ephemeral=True
            )

class ThresholdDropdown(Select):
    def __init__(self, guild_id, original_view, original_embed):
        self.guild_id = guild_id
        self.original_view = original_view
        self.original_embed = original_embed
        options = [
            discord.SelectOption(label="Ban", description="Set threshold for ban event"),
            discord.SelectOption(label="Kick", description="Set threshold for kick event"),
            discord.SelectOption(label="Prune", description="Set threshold for prune event"),
            discord.SelectOption(label="Role", description="Set threshold for role events"),
            discord.SelectOption(label="Channel", description="Set threshold for channel events"),
            discord.SelectOption(label="Webhook", description="Set threshold for webhook events"),
            discord.SelectOption(label="Member", description="Set threshold for member update events"),
            discord.SelectOption(label="Guild", description="Set threshold for guild events"),
            discord.SelectOption(label="Emoji", description="Set threshold for emoji/sticker events"),
            discord.SelectOption(label="Bot", description="Set threshold for bot add events"),
            discord.SelectOption(label="Ping", description="Set threshold for @everyone/@here mention events")
        ]
        super().__init__(placeholder="Select an event to set threshold", options=options)

    async def callback(self, interaction: discord.Interaction):
        option = self.values[0]
        modal = ThresholdModal(self.guild_id, option, self.original_view, self.original_embed)
        await interaction.response.send_modal(modal)

class DeleteButton(Button):
    def __init__(self):
        super().__init__(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()

class SupportServerButton(Button):
    def __init__(self):
        super().__init__(label="Support Server", url="https://discord.gg/UtZ3rRnBnU", style=discord.ButtonStyle.link)


class BackButton(Button):
    def __init__(self, original_embed, original_view):
        super().__init__(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.blurple)
        self.original_embed = original_embed
        self.original_view = original_view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.original_embed, view=self.original_view)

class ShowEventsButton(discord.ui.Button):
    def __init__(self, author_id: int):
        super().__init__(label="Show Events", style=discord.ButtonStyle.primary)
        self.author_id = author_id  

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.author_id:
            ok = getConfig(interaction.guild.id)
            prefix = ok["prefix"]
            color = 0xFFFFFF
            embed1 = discord.Embed(
                title="Event: Ban:\n<:info:1449445954142081278>**__How it works?__**",
                description=f"""For example if a user who isn't **`whitelisted`** in the server **`Bans`** a user from the server {interaction.client.user.mention} will take action depending on the punishment you set & also unban the user who was bannned\n\n<:info:1449445954142081278> **__How to whitelist__**\nTo **`Whitelist`** use the command **`{prefix}antinuke whitelist`** to check all of the **`Whitelist`** commands available\n\n<:info:1449445954142081278> **__How to set punishment__**\nTo set your own custom punishment for the server use the command **`{prefix}antinuke punishment set`**""",
                color=color)
            embed1.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed2 = discord.Embed(
                title="Event: Kick:\n<:info:1449445954142081278>**__How it works?__**",
                description=f"""For example if a user who isn't **`whitelisted`** in the server **`Kicks`** a user from the server {interaction.client.user.mention} will take action depending on the punishment you set\n\n<:info:1449445954142081278> **__How to whitelist__**\nTo **`Whitelist`** use the command **`{prefix}antinuke whitelist`** to check all of the **`Whitelist`** commands available\n\n<:info:1449445954142081278> **__How to set punishment__**\nTo set your own custom punishment for the server use the command **`{prefix}antinuke punishment set`**""",
                color=color)
            embed2.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed3 = discord.Embed(
                title="Event: Channel:\n<:info:1449445954142081278>**__How it works?__**",
                description=f"""For example if a user who isn't **`whitelisted`** in the server **`Creates`**, **`Deletes`** or **`Updates`** a channel in the server {interaction.client.user.mention} will take action depending on the punishment you set\n\n<:info:1449445954142081278> **__How to whitelist__**\nTo **`Whitelist`** use the command **`{prefix}antinuke whitelist`** to check all of the **`Whitelist`** commands available\n\n<:info:1449445954142081278> **__How to set punishment__**\nTo set your own custom punishment for the server use the command **`{prefix}antinuke punishment set`**""",
                color=color)
            embed3.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed4 = discord.Embed(
                title="Event: Webhook:\n<:info:1449445954142081278>**__How it works?__**",
                description=f"""For example if a user who isn't **`whitelisted`** in the server **`Creates`**, **`Deletes`** or **`Updates`** a webhook in the server {interaction.client.user.mention} will take action depending on the punishment you set\n\n<:info:1449445954142081278> **__How to whitelist__**\nTo **`Whitelist`** use the command **`{prefix}antinuke whitelist`** to check all of the **`Whitelist`** commands available\n\n<:info:1449445954142081278> **__How to set punishment__**\nTo set your own custom punishment for the server use the command **`{prefix}antinuke punishment set`**""",
                color=color)
            embed4.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed5 = discord.Embed(
                title="Event: Role:\n<:info:1449445954142081278>**__How it works?__**",
                description=f"""For example if a user who isn't **`whitelisted`** in the server **`Creates`**, **`Deletes`** or **`Updates`** a role in the server {interaction.client.user.mention} will take action depending on the punishment you set\n\n<:info:1449445954142081278> **__How to whitelist__**\nTo **`Whitelist`** use the command **`{prefix}antinuke whitelist`** to check all of the **`Whitelist`** commands available\n\n<:info:1449445954142081278> **__How to set punishment__**\nTo set your own custom punishment for the server use the command **`{prefix}antinuke punishment set`**""",
                color=color)
            embed5.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed6 = discord.Embed(
                title="Event: Guild:\n<:info:1449445954142081278>**__How it works?__**",
                description=f"""For example if a user who isn't **`whitelisted`** in the server makes any changes in the server {interaction.client.user.mention} will take action depending on the punishment you set\n\n<:info:1449445954142081278> **__How to whitelist__**\nTo **`Whitelist`** use the command **`{prefix}antinuke whitelist`** to check all of the **`Whitelist`** commands available\n\n<:info:1449445954142081278> **__How to set punishment__**\nTo set your own custom punishment for the server use the command **`{prefix}antinuke punishment set`**""",
                color=color)
            embed6.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed7 = discord.Embed(
                title="Event: Prune:\n<:info:1449445954142081278>**__How it works?__**",
                description=f"""For example if a user who isn't **`whitelisted`** in the server **`Prunes`** server {interaction.client.user.mention} will take action depending on the punishment you set\n\n<:info:1449445954142081278> **__How to whitelist__**\nTo **`Whitelist`** use the command **`{prefix}antinuke whitelist`** to check all of the **`Whitelist`** commands available\n\n<:info:1449445954142081278> **__How to set punishment__**\nTo set your own custom punishment for the server use the command **`{prefix}antinuke punishment set`**""",
                color=color)
            embed7.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed8 = discord.Embed(
                title="Event: Bot:\n<:info:1449445954142081278>**__How it works?__**",
                description=f"""For example if a user who isn't **`whitelisted`** in the server adds a **`Bot`** {interaction.client.user.mention} will ban the **`Bot`** take action depending on the punishment you set\n\n<:info:1449445954142081278> **__How to whitelist__**\nTo **`Whitelist`** use the command **`{prefix}antinuke whitelist`** to check all of the **`Whitelist`** commands available\n\n<:info:1449445954142081278> **__How to set punishment__**\nTo set your own custom punishment for the server use the command **`{prefix}antinuke punishment set`**""",
                color=color)
            embed8.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed9 = discord.Embed(
                title="\n<:info:1449445954142081278>**__Extra Info__**",
                description=f"""There are many more events like these i pointed out the main modules of the antinuke hope you enjoy using {interaction.client.user.mention}'s antinuke\nTo check all of the remaining events use `{prefix}antinuke config` command**""",
                color=color)
            embed9.set_author(
                name=interaction.guild.name,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embeds = [embed1, embed2, embed3,embed4,embed5,embed6,embed7,embed8,embed9]
            paginator = PaginationView(embeds, author_id=interaction.user.id)
            await interaction.response.send_message(embed=embed1,view=paginator, ephemeral=True)
        else:
            await interaction.response.send_message("You are not authorized to use this button.", ephemeral=True)


class ChannelSelectorView(discord.ui.View):  
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

        self.channel_select = discord.ui.ChannelSelect(
            custom_id="channel_select",
            channel_types=[discord.ChannelType.text],
            placeholder="Select a channel for Channel Logging..."
        )
        self.channel_select.callback = self.channel_select_callback
        self.add_item(self.channel_select)

        reset_button = discord.ui.Button(label="Reset", style=discord.ButtonStyle.blurple)
        reset_button.callback = self.reset_callback
        self.add_item(reset_button)

        delete_button = discord.ui.Button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_callback
        self.add_item(delete_button)

        back_button = discord.ui.Button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.gray)
        back_button.callback = self.back_callback
        self.add_item(back_button)

    async def channel_select_callback(self, interaction: discord.Interaction):
        selected_channel = interaction.data["values"][0]
        updateAntiChannelLogs(self.ctx.guild.id, int(selected_channel))
        color = 0xFFFFFF
        embed = discord.Embed(
            description=f"<:info:1449445954142081278> Moderation loggings channel has been set to <#{selected_channel}>",
            color=color
        )
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=self.create_final_view())

    async def reset_callback(self, interaction: discord.Interaction):
        updateAntiChannelLogs(self.ctx.guild.id, None)
        color = 0xFFFFFF 
        embed = discord.Embed(
            description="<:tick_icons:1449445939256229961>Moderation loggings channel has been set to `None`",
            color=color
        )
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=self.create_final_view())

    async def delete_callback(self, interaction: discord.Interaction):
        await interaction.message.delete()

    async def back_callback(self, interaction: discord.Interaction):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Logging Configuration__**\n\n<:info:1449445954142081278> **__What is this__**?\n - Using this you can **`Enable`** `&` **`Choose`** logging channel for each designated events\n<:info:1449445954142081278> **__How to use__**?\n- Using the dropdown you can select the **`Event`** you need to setup **`Logging`** for, then after that you can choose your designated channel for the **`Event`**\n- Note - The logging will not work if the **`Antinuke`** is disabled for this guild even if you enable the event using this command\n<:info:1449445954142081278> **__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        select = discord.ui.Select(
            placeholder="Choose a logging type...",
            options=[
                discord.SelectOption(label="Channel Loggings", value="channel"),
                discord.SelectOption(label="Moderation Loggings", value="mod"),
                discord.SelectOption(label="Guild Loggings", value="guild"),
                discord.SelectOption(label="Role Loggings", value="role"),
            ]
        )
                
        async def select_callback(interaction: discord.Interaction):
            color = 0xFFFFFF

            if select.values[0] == "channel":
                embed = discord.Embed(
                    title="Channel Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Channel Logging`** tracks the following events: `create`, `delete`, `update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ChannelSelectorView(self.ctx))

            elif select.values[0] == "mod":
                embed = discord.Embed(
                    title="Moderation Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Channel Logging`** tracks the following events: `kick`, `ban`, `prune`, `ping`, `member-role-update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ModSelectorView(self.ctx))

            elif select.values[0] == "guild":
                embed = discord.Embed(
                    title="Guild Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Guild Logging`** tracks the following events: `emoji & sticker`, `webhook`, `server`, `bot`, `role`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=GuildSelectorView(self.ctx))

            elif select.values[0] == "role":
                embed = discord.Embed(
                    title="Role Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Role Logging`** tracks the following events: `create`, `delete`, `update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=RoleSelectorView(self.ctx))


        select.callback = select_callback
        b2 = discord.ui.Button(label="Need Help? Join Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/UtZ3rRnBnU")
        view = discord.ui.View()
        view.add_item(b2)
        view.add_item(TrashButton(interaction.user.id))
        view.add_item(select)
        await interaction.response.edit_message(embed=embed, view=view)

    def create_final_view(self):
        view = discord.ui.View()
        delete_button = discord.ui.Button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_callback
        view.add_item(delete_button)

        back_button = discord.ui.Button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.gray)
        back_button.callback = self.back_callback
        view.add_item(back_button)
        return view




class ModSelectorView(discord.ui.View):  
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

        self.channel_select = discord.ui.ChannelSelect(
            custom_id="mod_channel_select",
            channel_types=[discord.ChannelType.text],
            placeholder="Select a channel for Moderation Logging..."
        )
        self.channel_select.callback = self.channel_select_callback
        self.add_item(self.channel_select)

        reset_button = discord.ui.Button(label="Reset", style=discord.ButtonStyle.blurple)
        reset_button.callback = self.reset_callback
        self.add_item(reset_button)

        delete_button = discord.ui.Button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_callback
        self.add_item(delete_button)

        back_button = discord.ui.Button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.gray)
        back_button.callback = self.back_callback
        self.add_item(back_button)

    async def channel_select_callback(self, interaction: discord.Interaction):
        selected_channel = interaction.data["values"][0]
        updateAntiModLogs(self.ctx.guild.id, int(selected_channel))
        color = 0xFFFFFF 
        embed = discord.Embed(
            description=f"<:info:1449445954142081278> Moderation loggings channel has been set to <#{selected_channel}>",
            color=color
        )
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        await interaction.response.edit_message(embed=embed, view=self.create_final_view())


    async def reset_callback(self, interaction: discord.Interaction):
        updateAntiModLogs(self.ctx.guild.id, None)
        color = 0xFFFFFF
        embed = discord.Embed(
            description="<:tick_icons:1449445939256229961>Moderation loggings channel has been set to `None`",
            color=color
        )
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        await interaction.response.edit_message(embed=embed, view=self.create_final_view())


    async def delete_callback(self, interaction: discord.Interaction):
        await interaction.message.delete()

    async def back_callback(self, interaction: discord.Interaction):
        color = 0xFFFFFF  
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Logging Configuration__**\n\n<:info:1449445954142081278> **__What is this__**?\n - Using this you can **`Enable`** `&` **`Choose`** logging channel for each designated events\n<:info:1449445954142081278> **__How to use__**?\n- Using the dropdown you can select the **`Event`** you need to setup **`Logging`** for, then after that you can choose your designated channel for the **`Event`**\n- Note - The logging will not work if the **`Antinuke`** is disabled for this guild even if you enable the event using this command\n<:info:1449445954142081278> **__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        select = discord.ui.Select(
            placeholder="Choose a logging type...",
            options=[
                discord.SelectOption(label="Channel Loggings", value="channel"),
                discord.SelectOption(label="Moderation Loggings", value="mod"),
                discord.SelectOption(label="Guild Loggings", value="guild"),
                discord.SelectOption(label="Role Loggings", value="role"),
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            color = 0xFFFFFF
            if select.values[0] == "channel":
                embed = discord.Embed(
                    title="Channel Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Channel Logging`** tracks the following events: `create`, `delete`, `update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ChannelSelectorView(self.ctx))

            elif select.values[0] == "mod":
                embed = discord.Embed(
                    title="Moderation Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Moderation Logging`** tracks the following events: `kick`, `ban`, `prune`, `ping`, `member-role-update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ModSelectorView(self.ctx))

            elif select.values[0] == "guild":
                embed = discord.Embed(
                    title="Guild Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Guild Logging`** tracks the following events: `emoji & sticker`, `webhook`, `server`, `bot`, `role`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=GuildSelectorView(self.ctx))

            elif select.values[0] == "role":
                embed = discord.Embed(
                    title="Role Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Role Logging`** tracks the following events: `create`, `delete`, `update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=RoleSelectorView(self.ctx))


        select.callback = select_callback
        b2 = discord.ui.Button(label="Need Help? Join Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/UtZ3rRnBnU")
        view = discord.ui.View()
        view.add_item(b2)
        view.add_item(TrashButton(interaction.user.id))
        view.add_item(select)

        await interaction.response.edit_message(embed=embed, view=view)

    def create_final_view(self):
        view = discord.ui.View()
        delete_button = discord.ui.Button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_callback
        back_button = discord.ui.Button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.gray)
        back_button.callback = self.back_callback
        view.add_item(delete_button)
        view.add_item(back_button)
        return view
    
class GuildSelectorView(discord.ui.View):  
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

        self.channel_select = discord.ui.ChannelSelect(
            custom_id="guild_channel_select",
            channel_types=[discord.ChannelType.text],
            placeholder="Select a channel for Guild Logging..."
        )
        self.channel_select.callback = self.channel_select_callback
        self.add_item(self.channel_select)

        reset_button = discord.ui.Button(label="Reset", style=discord.ButtonStyle.blurple)
        reset_button.callback = self.reset_callback
        self.add_item(reset_button)

        delete_button = discord.ui.Button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_callback
        self.add_item(delete_button)

        back_button = discord.ui.Button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.gray)
        back_button.callback = self.back_callback
        self.add_item(back_button)

    async def channel_select_callback(self, interaction: discord.Interaction):
        selected_channel = interaction.data["values"][0]
        updateAntiGuildLogs(self.ctx.guild.id, int(selected_channel))
        color = 0xFFFFFF
        embed = discord.Embed(
            description=f"<:info:1449445954142081278> Guild loggings channel has been set to <#{selected_channel}>",
            color=color
        )
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        await interaction.response.edit_message(embed=embed, view=self.create_final_view())


    async def reset_callback(self, interaction: discord.Interaction):
        updateAntiGuildLogs(self.ctx.guild.id, None)
        color = 0xFFFFFF  
        embed = discord.Embed(
            description="<:tick_icons:1449445939256229961>Guild loggings channel has been set to `None`",
            color=color
        )
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        await interaction.response.edit_message(embed=embed, view=self.create_final_view())


    async def delete_callback(self, interaction: discord.Interaction):
        await interaction.message.delete()

    async def back_callback(self, interaction: discord.Interaction):
        color = 0xFFFFFF
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Logging Configuration__**\n\n<:info:1449445954142081278> **__What is this__**?\n - Using this you can **`Enable`** `&` **`Choose`** logging channel for each designated events\n<:info:1449445954142081278> **__How to use__**?\n- Using the dropdown you can select the **`Event`** you need to setup **`Logging`** for, then after that you can choose your designated channel for the **`Event`**\n- Note - The logging will not work if the **`Antinuke`** is disabled for this guild even if you enable the event using this command\n<:info:1449445954142081278> **__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        select = discord.ui.Select(
            placeholder="Choose a logging type...",
            options=[
                discord.SelectOption(label="Channel Loggings", value="channel"),
                discord.SelectOption(label="Moderation Loggings", value="mod"),
                discord.SelectOption(label="Guild Loggings", value="guild"),
                discord.SelectOption(label="Role Loggings", value="role"),
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            color = 0xFFFFFF
            if select.values[0] == "channel":
                embed = discord.Embed(
                    title="Channel Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Channel Logging`** tracks the following events: `create`, `delete`, `update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ChannelSelectorView(self.ctx))

            elif select.values[0] == "mod":
                embed = discord.Embed(
                    title="Moderation Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Moderation Logging`** tracks the following events: `kick`, `ban`, `prune`, `ping`, `member-role-update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ModSelectorView(self.ctx))

            elif select.values[0] == "mod":
                embed = discord.Embed(
                    title="Moderation Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Moderation Logging`** tracks the following events: `kick`, `ban`, `prune`, `ping`, `member-role-update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ModSelectorView(self.ctx))

            elif select.values[0] == "guild":
                embed = discord.Embed(
                    title="Guild Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Guild Logging`** tracks the following events: `emoji & sticker`, `webhook`, `server`, `bot`, `role`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=GuildSelectorView(self.ctx))

            elif select.values[0] == "role":
                embed = discord.Embed(
                    title="Role Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Role Logging`** tracks the following events: `create`, `delete`, `update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=RoleSelectorView(self.ctx))


        select.callback = select_callback
        b2 = discord.ui.Button(label="Need Help? Join Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/UtZ3rRnBnU")
        view = discord.ui.View()
        view.add_item(b2)
        view.add_item(TrashButton(interaction.user.id))
        view.add_item(select)

        await interaction.response.edit_message(embed=embed, view=view)

    def create_final_view(self):
        view = discord.ui.View()
        delete_button = discord.ui.Button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_callback
        back_button = discord.ui.Button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.gray)
        back_button.callback = self.back_callback
        view.add_item(delete_button)
        view.add_item(back_button)
        return view
    
class RoleSelectorView(discord.ui.View):  
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

        self.channel_select = discord.ui.ChannelSelect(
            custom_id="role_channel_select",
            channel_types=[discord.ChannelType.text],
            placeholder="Select a channel for Role Logging..."
        )
        self.channel_select.callback = self.channel_select_callback
        self.add_item(self.channel_select)

        reset_button = discord.ui.Button(label="Reset", style=discord.ButtonStyle.blurple)
        reset_button.callback = self.reset_callback
        self.add_item(reset_button)

        delete_button = discord.ui.Button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_callback
        self.add_item(delete_button)

        back_button = discord.ui.Button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.gray)
        back_button.callback = self.back_callback
        self.add_item(back_button)

    async def channel_select_callback(self, interaction: discord.Interaction):
        selected_channel = interaction.data["values"][0]
        updateAntiRoleLogs(self.ctx.guild.id, int(selected_channel))
        color = 0xFFFFFF  
        embed = discord.Embed(
            description=f"<:info:1449445954142081278> Role loggings channel has been set to <#{selected_channel}>",
            color=color
        )
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        await interaction.response.edit_message(embed=embed, view=self.create_final_view())


    async def reset_callback(self, interaction: discord.Interaction):
        updateAntiRoleLogs(self.ctx.guild.id, None)
        color = 0xFFFFFF
        embed = discord.Embed(
            description="<:tick_icons:1449445939256229961>Role loggings channel has been set to `None`",
            color=color
        )
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        await interaction.response.edit_message(embed=embed, view=self.create_final_view())


    async def delete_callback(self, interaction: discord.Interaction):
        await interaction.message.delete()

    async def back_callback(self, interaction: discord.Interaction):
        color = 0xFFFFFF  
        ok = getConfig(interaction.guild.id)
        prefix = ok["prefix"]
        embed = discord.Embed(description=f"**__Antinuke Logging Configuration__**\n\n<:info:1449445954142081278> **__What is this__**?\n - Using this you can **`Enable`** `&` **`Choose`** logging channel for each designated events\n<:info:1449445954142081278> **__How to use__**?\n- Using the dropdown you can select the **`Event`** you need to setup **`Logging`** for, then after that you can choose your designated channel for the **`Event`**\n- Note - The logging will not work if the **`Antinuke`** is disabled for this guild even if you enable the event using this command\n<:info:1449445954142081278> **__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=color)
        embed.set_author(name=interaction.guild.name,
                        icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url)

        select = discord.ui.Select(
            placeholder="Choose a logging type...",
            options=[
                discord.SelectOption(label="Channel Loggings", value="channel"),
                discord.SelectOption(label="Moderation Loggings", value="mod"),
                discord.SelectOption(label="Guild Loggings", value="guild"),
                discord.SelectOption(label="Role Loggings", value="role"),
            ]
        )
        
        async def select_callback(interaction: discord.Interaction):
            color = 0xFFFFFF
            if select.values[0] == "channel":
                embed = discord.Embed(
                    title="Channel Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Channel Logging`** tracks the following events: `create`, `delete`, `update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ChannelSelectorView(self.ctx))

            elif select.values[0] == "mod":
                embed = discord.Embed(
                    title="Moderation Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Moderation Logging`** tracks the following events: `kick`, `ban`, `prune`, `ping`, `member-role-update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ModSelectorView(self.ctx))

            elif select.values[0] == "mod":
                embed = discord.Embed(
                    title="Moderation Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Moderation Logging`** tracks the following events: `kick`, `ban`, `prune`, `ping`, `member-role-update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=ModSelectorView(self.ctx))

            elif select.values[0] == "guild":
                embed = discord.Embed(
                    title="Guild Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Guild Logging`** tracks the following events: `emoji & sticker`, `webhook`, `server`, `bot`, `role`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=GuildSelectorView(self.ctx))

            elif select.values[0] == "role":
                embed = discord.Embed(
                    title="Role Loggings",
                    description="<:info:1449445954142081278> **__What it includes__**\n- **`Role Logging`** tracks the following events: `create`, `delete`, `update`\n<:info:1449445954142081278> **__How to use__?**\n- Use the select menu below to choose a specific channel for logging these events\n",
                    color=color
                )
                embed.set_author(name=interaction.guild.name,
                                icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.set_footer(text=f"Requested By {interaction.user.display_name}",
                                icon_url=interaction.user.display_avatar.url)

                await interaction.response.edit_message(embed=embed, view=RoleSelectorView(self.ctx))


        select.callback = select_callback
        b2 = discord.ui.Button(label="Need Help? Join Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/UtZ3rRnBnU")
        view = discord.ui.View()
        view.add_item(b2)
        view.add_item(TrashButton(interaction.user.id))
        view.add_item(select)

        await interaction.response.edit_message(embed=embed, view=view)

    def create_final_view(self):
        view = discord.ui.View()
        delete_button = discord.ui.Button(emoji="<:MekoTrash:1449445909585723454>", style=discord.ButtonStyle.danger)
        delete_button.callback = self.delete_callback
        back_button = discord.ui.Button(emoji="<:green_arrow:1449445946361385100>", style=discord.ButtonStyle.gray)
        back_button.callback = self.back_callback
        view.add_item(delete_button)
        view.add_item(back_button)
        return view