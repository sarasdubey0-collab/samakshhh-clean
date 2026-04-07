import discord
from discord.ext import commands
import aiosqlite
from utils.Tools import *
import asyncio

class ShowRules(discord.ui.View):
    def __init__(self, author, selected_events):
        super().__init__(timeout=60)
        self.author = author
        self.selected_events = selected_events

    @discord.ui.button(label="Show Rules", style=discord.ButtonStyle.secondary)
    async def show_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            embed = discord.Embed()
            embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        rules = {
            "Mass Text": "__**Mass Text**__:\n Cypher will take action if the message contains >70% caps.\n• Messages under 45 characters are bypassed.",
            "Links": "__**Links**__:\n Cypher will take action if the message contains a link.\n Some links are bypassed.",
            "Mass Invites": "__**Anti Invites**__:\n Cypher will take action if the message contains a Discord server invite.",
            "Mass Emoji": "__**Mass Emoji**__:\n Cypher will take action if a message contains more than 5 emojis.",
            "Mass Mention": "__**Mass Mention**__:\n Cypher will take action if a message contains more than 4 mentions.",
            "Fast Message": "__**Fast Message**__:\n Cypher will take action if more than 5 messages are sent rapidly in a short time.",
        }

        enabled_rules = "\n\n".join([rules[event] for event in self.selected_events])

        embed = discord.Embed(title="Enabled Automod Rules", description=enabled_rules, color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        

class ConfirmDisable(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=30)
        self.author = author
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            embed = discord.Embed()
            embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        self.value = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            embed = discord.Embed()
            embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        self.value = False
        self.stop()


        
class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_punishment = "Mute"
        self.bot.loop.create_task(self.init_db())
        

    async def get_exempt_roles_channels(self, guild_id):
        async with aiosqlite.connect("database/automod.db") as db:
            roles_cursor = await db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'role'", (guild_id,))
            channels_cursor = await db.execute("SELECT id FROM automod_ignored WHERE guild_id = ? AND type = 'channel'", (guild_id,))
            
            exempt_roles = [discord.Object(id) for (id,) in await roles_cursor.fetchall()]
            exempt_channels = [discord.Object(id) for (id,) in await channels_cursor.fetchall()]
            
            return exempt_roles, exempt_channels
            

    async def is_automod_enabled(self, guild_id):
        retries=3
        for attempt in range(retries):
            try:
                async with aiosqlite.connect("database/automod.db") as db:
                    cursor = await db.execute("SELECT enabled FROM automod WHERE guild_id = ?", (guild_id,))
                    result = await cursor.fetchone()
                    return result is not None and result[0] == 1
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    await asyncio.sleep(1)  # wait and retry
                else:
                    raise

    async def update_punishments(self, guild_id, event, punishment):
        retries=3
        for attempt in range(retries):
            try:
                async with aiosqlite.connect("database/automod.db") as db:
                    await db.execute("INSERT OR REPLACE INTO automod_punishments (guild_id, event, punishment) VALUES (?, ?, ?)", (guild_id, event, punishment))
                    await db.commit()
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    await asyncio.sleep(1)  # wait and retry
                else:
                    raise

    async def get_current_punishments(self, guild_id):
        retries=3
        for attempt in range(retries):
            try:
                async with aiosqlite.connect("database/automod.db") as db:
                    async with db.execute(
                        "SELECT event, punishment FROM automod_punishments WHERE guild_id = ? AND event != 'Anti NSFW link'", 
                        (guild_id,)
                        ) as cursor:
                        return await cursor.fetchall()
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    await asyncio.sleep(1)  # wait and retry
                else:
                    raise

    async def is_anti_nsfw_enabled(self, guild_id):
        retries=3
        for attempt in range(retries):
            try:
                async with aiosqlite.connect("database/automod.db") as db:
                    cursor = await db.execute("SELECT punishment FROM automod_punishments WHERE guild_id = ? AND event = 'Anti NSFW link'", (guild_id,))
                    result = await cursor.fetchone()
                    return result is not None
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    await asyncio.sleep(1)  # wait and retry
                else:
                    raise

                

    async def init_db(self):
        retries=3
        for attempt in range(retries):
            try:
                async with aiosqlite.connect("database/automod.db") as db:
                    await db.execute("""
                                     CREATE TABLE IF NOT EXISTS automod (
                                         guild_id INTEGER PRIMARY KEY,
                                         enabled INTEGER DEFAULT 0
                                     )
                    """)
                    
                    await db.execute("""
                                     CREATE TABLE IF NOT EXISTS automod_punishments (
                                         guild_id INTEGER,
                                         event TEXT,
                                         punishment TEXT,
                                         PRIMARY KEY (guild_id, event)
                                     )
                    """)
                    await db.execute("""
                                     CREATE TABLE IF NOT EXISTS automod_ignored (
                                         guild_id INTEGER,
                                         type TEXT,
                                         id INTEGER,
                                         PRIMARY KEY (guild_id, type, id)
                                     )
                    """)
                    await db.execute("""
                                     CREATE TABLE IF NOT EXISTS automod_logging (
                                         guild_id INTEGER,
                                         log_channel INTEGER,
                                         PRIMARY KEY (guild_id)
                                     )
                    """)
                    
                    await db.commit()
                    break
                    
            except aiosqlite.OperationalError as e:
                if "database is locked" in str(e) and attempt < retries - 1:
                    await asyncio.sleep(1)  # wait and retry
                else:
                    raise

    @commands.hybrid_group(invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def automod(self, ctx):
        try:
            embed = discord.Embed(
                title="Automod Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @automod.command(name="enable", help="Enable Automod on the server.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def enable(self, ctx):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="<a:MekoCross:1449446075948859462> Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return
            
        if await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"**<:MekoExclamation:1449445917500510229> Your Server already has Automod Enabled.**\n\nCurrent Status: True\nTo Disable use `{ctx.prefix}automod disable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        events = [
            "Anti spam",
            "Anti caps",
            "Anti link",
            "Anti invites",
            "Anti mass mention",
            "Anti emoji spam",
        ]

        embed = discord.Embed(color=0x000000)
        embed.set_author(name="Automod Setup")
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.description = "\n".join([f"**{event}** : `False`" for event in events])

        select_menu = discord.ui.Select(placeholder="Select events to enable", min_values=1, max_values=len(events), options=[
            discord.SelectOption(label=event, value=event) for event in events
        ])

        async def select_callback(interaction):
            if interaction.user != ctx.author:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            selected_events = select_menu.values
            await self.enable_automod(ctx, guild_id, selected_events, interaction)
        select_menu.callback = select_callback

        enable_all_button = discord.ui.Button(label="Enable for All Events", style=discord.ButtonStyle.primary)

        async def enable_all_callback(interaction):
            if interaction.user != ctx.author:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
                
            await self.enable_automod(ctx, guild_id, events, interaction)

        enable_all_button.callback = enable_all_callback

        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
                
            select_menu.disabled = True
            enable_all_button.disabled = True
            cancel_button.disabled = True
            await interaction.response.edit_message(content="Automod Setup Cancelled", embed=embed, view=view)

        cancel_button.callback = cancel_callback

        view = discord.ui.View()
        view.add_item(select_menu)
        view.add_item(enable_all_button)
        view.add_item(cancel_button)

        await ctx.send(embed=embed, view=view)
        

    async def enable_automod(self, ctx, guild_id, selected_events, interaction):

        async with aiosqlite.connect("database/automod.db") as db:
            await db.execute("INSERT OR REPLACE INTO automod (guild_id, enabled) VALUES (?, 1)", (guild_id,))
            for event in selected_events:
                await db.execute("INSERT OR REPLACE INTO automod_punishments (guild_id, event, punishment) VALUES (?, ?, ?)", (guild_id, event, self.default_punishment))
            await db.commit()


        embed = discord.Embed(color=0x000000)
        embed.set_author(name="Automod Enabled", icon_url=ctx.guild.icon.url)
        embed.description = "\n".join([f"**{event}** : `True`" for event in selected_events] +
                                       [f"**{event}** : `False`" for event in ["Anti spam", "Anti caps", "Anti link", "Anti invites", "Anti mass mention", "Anti emoji spam"] if event not in selected_events])

        enable_logging_button = discord.ui.Button(label="Enable Automod Logging", style=discord.ButtonStyle.success)

        async def enable_logging_callback(interaction):
            if interaction.user != ctx.author:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if not interaction.guild.me.guild_permissions.manage_channels:
                await interaction.response.send_message("I do not have permission to create channels.", ephemeral=True)
                return

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.guild.me: discord.PermissionOverwrite(view_channel=True)
            }

            try:
                for channel in interaction.guild.channels:
                    if channel.name == "cypher-logs":
                        await interaction.response.send_message(f"A logging channel with the name \"cypher-logs\" already exists.", ephemeral=True)
                        return
                log_channel = await interaction.guild.create_text_channel("cypher-logs", overwrites=overwrites)
                guild_id = interaction.guild.id

                async with aiosqlite.connect("database/automod.db") as db:
                    await db.execute("INSERT OR REPLACE INTO automod_logging (guild_id, log_channel) VALUES (?, ?)", (guild_id, log_channel.id))
                    await db.commit()

                await interaction.response.send_message(f"Logging channel {log_channel.mention} created and set successfully.", ephemeral=True)

            except discord.HTTPException as e:
                await interaction.response.send_message(f"Failed to create logging channel: {e}", ephemeral=True)

        enable_logging_button.callback = enable_logging_callback


        view = ShowRules(ctx.author, selected_events)
        view.add_item(enable_logging_button)

        
        await interaction.response.edit_message(content="Setup Completed.", embed=embed, view=view)


    

    @automod.command(name="punishment", aliases=["punish"], help="Set the punishment for automod events.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def punishment(self, ctx):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return
            
        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        current_punishments = await self.get_current_punishments(guild_id)
        embed = discord.Embed(title=f"Current Automod Punishments for {ctx.guild.name}", color=0x000000)
        punishment_map = {}
        for event, punishment in current_punishments:
            punishment_map[event] = punishment or "None"
            embed.add_field(name=event, value=punishment or "None", inline=False)
            embed.set_footer(text="Keep the default punishment (Mute) to prevent server raids without kicking or banning raiders", icon_url=self.bot.user.avatar.url)
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        events = [event for event, _ in current_punishments]
        select = discord.ui.Select(placeholder="Select events to update punishment", options=[
            discord.SelectOption(label=event) for event in events
        ], min_values=1, max_values=len(events))

        async def select_callback(interaction):
            if interaction.user != ctx.author:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this menu.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this menu"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            selected_events = select.values
            await interaction.response.send_message("You selected: " + ", ".join(selected_events))

            punishment_buttons = discord.ui.View()
            for punishment in ["Mute", "Kick", "Ban"]:
                button = discord.ui.Button(label=punishment, style=discord.ButtonStyle.danger)

                async def punishment_callback(button_interaction, selected_events=selected_events, punishment=punishment):
                    if button_interaction.user != ctx.author:
                        embed = discord.Embed()
                        embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        return

                    
                    for event in selected_events:
                        await self.update_punishments(guild_id, event, punishment)

                    updated_punishments = await self.get_current_punishments(guild_id)
                    updated_embed = discord.Embed(title=f"Updated Automod Punishments for {ctx.guild.name}", color=0x000000)
                    for event, punishment in updated_punishments:
                        updated_embed.add_field(name=event, value=punishment or "None", inline=False)
                        updated_embed.set_footer(text="You can modify the punishments by running the command again.", icon_url=self.bot.user.avatar.url)
                        updated_embed.set_thumbnail(url=self.bot.user.avatar.url)

                    
                    await button_interaction.response.edit_message(embed=updated_embed, view=None)

                button.callback = punishment_callback
                punishment_buttons.add_item(button)

            await interaction.edit_original_response(view=punishment_buttons)

        select.callback = select_callback
        view = discord.ui.View()
        view.add_item(select)

        await ctx.send(embed=embed, view=view)




    @automod.group(name="ignore", aliases=["exempt", "whitelist", "wl"], help="Manage whitelisted roles and channels for Automod.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def ignore(self, ctx):
        if ctx.subcommand_passed is None:
            rix = discord.Embed()
            rix.description = "`automod ignore channel`, `automod ignore role`, `automod ignore show`, `automod ignore reset`"
            await ctx.send(embed=rix)
            ctx.command.reset_cooldown(ctx)
            

    @ignore.command(name="channel", help="Add a channel to the whitelist.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def ignore_channel(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        async with aiosqlite.connect("database/automod.db") as db:
            cursor = await db.execute("SELECT 1 FROM automod_ignored WHERE guild_id = ? AND type = 'channel' AND id = ?", (guild_id, channel.id))
            if await cursor.fetchone() is not None:
                embed = discord.Embed(description=f"<a:MekoCross:1449446075948859462> The channel {channel.mention} is already in the ignore list.\n\n<:MekoArrowRight:1449445989436887090> Use **{ctx.prefix}automod unignore channel {channel.mention}** to remove it.", color=0x000000)
                
                embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=embed)
                return
                
            count_cursor = await db.execute("SELECT COUNT(*) FROM automod_ignored WHERE guild_id = ? AND type = 'channel'", (guild_id,))
            count = await count_cursor.fetchone()

            if count[0] >= 10:
                await ctx.send("You can only ignore up to 10 channels.")
                return

            await db.execute("INSERT OR REPLACE INTO automod_ignored (guild_id, type, id) VALUES (?, 'channel', ?)", (guild_id, channel.id))
            await db.commit()

                    
            success = discord.Embed( description=f"The channel {channel.mention} has been added to the ignore list \n\n<:MekoArrowRight:1449445989436887090> Use `{ctx.prefix}automod ignore show` to view the ignore list.", color=0x000000)
            success.set_thumbnail(url=self.bot.user.avatar.url)
            success.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

        await ctx.send(embed=success)

    @ignore.command(name="role", help="Add a role to the whitelist.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def ignore_role(self, ctx, role: discord.Role):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(title="<a:MekoCross:1449446075948859462> Access Denied", description="Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(title=f"Automod Settings for {ctx.guild.name}", description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        async with aiosqlite.connect("database/automod.db") as db:
            cursor = await db.execute("SELECT 1 FROM automod_ignored WHERE guild_id = ? AND type = 'role' AND id = ?", (guild_id, role.id))
            
            if await cursor.fetchone() is not None:
                embed = discord.Embed(description=f"<a:MekoCross:1449446075948859462> The role {role.mention} is already in the ignore list.\n\n<:MekoArrowRight:1449445989436887090> Use **{ctx.prefix}automod unignore role {role.mention}** to remove it.", color=0x000000)
                embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                await ctx.send(embed=embed)
                return
                
            count_cursor = await db.execute("SELECT COUNT(*) FROM automod_ignored WHERE guild_id = ? AND type = 'role'", (guild_id,))
            count = await count_cursor.fetchone()


            if count[0] >= 5:
                await ctx.send("You can only ignore up to 5 roles.")
                return

            await db.execute("INSERT OR REPLACE INTO automod_ignored (guild_id, type, id) VALUES (?, 'role', ?)", (guild_id, role.id))
            await db.commit()

            if await self.is_anti_nsfw_enabled(guild_id):
                try:
                    rules = await ctx.guild.fetch_automod_rules()
                    for rule in rules:
                        if rule.name == "Anti NSFW Links":
                            exempt_roles = list(rule.exempt_roles)  
                            exempt_roles.append(role) 
                            await rule.edit(
                                exempt_roles=exempt_roles,
                                reason="Role exempted from Anti NSFW Links via automod ignore command"
                            )
                            break
                except discord.HTTPException:
                    pass
                    
                    
            success = discord.Embed(description=f"<a:H_TICK:1449446011490537603> The role {role.mention} has been added to the ignore list \n\n<:MekoArrowRight:1449445989436887090> Use `{ctx.prefix}automod ignore show` to view the ignore list.", color=0x000000)
            success.set_thumbnail(url=self.bot.user.avatar.url)
            success.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)

        await ctx.send(embed=success)

    @ignore.command(name="show", aliases=["view", "list", "config"], help="Show the whitelisted roles and channels.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def ignore_show(self, ctx):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="<a:MekoCross:1449446075948859462> Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return
            

        async with aiosqlite.connect("database/automod.db") as db:
            cursor = await db.execute("SELECT type, id FROM automod_ignored WHERE guild_id = ?", (guild_id,))
            ignored_items = await cursor.fetchall()

        if not ignored_items:
            await ctx.reply("No ignored channels or roles found.")
            return

        ignored_channels = []
        ignored_roles = []

        for item_type, item_id in ignored_items:
            if item_type == "channel":
                channel = ctx.guild.get_channel(item_id)
                if channel:
                    ignored_channels.append(f"{channel.mention} (ID: {channel.id})")
                else:
                    ignored_channels.append(f"Deleted Channel (ID: {item_id})")
            elif item_type == "role":
                role = ctx.guild.get_role(item_id)
                if role:
                    ignored_roles.append(f"{role.mention} (ID: {role.id})")
                else:
                    ignored_roles.append(f"Deleted Role (ID: {item_id})")

        embed = discord.Embed(color=0x000000)

        if ignored_channels:
            embed.add_field(name="__Ignored Channels:__", value="\n".join(ignored_channels), inline=False)
        else:
            embed.add_field(name="__Ignored Channels:__", value="None", inline=False)

        if ignored_roles:
            embed.add_field(name="__Ignored Roles:__", value="\n".join(ignored_roles), inline=False)
        else:
            embed.add_field(name="__Ignored Roles:__", value="None", inline=False)

        await ctx.send(embed=embed)


    @ignore.command(name="reset", help="Reset the whitelist.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def ignore_reset(self, ctx):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="<a:MekoCross:1449446075948859462> Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        async with aiosqlite.connect("database/automod.db") as db:
            await db.execute("DELETE FROM automod_ignored WHERE guild_id = ?", (guild_id,))
            await db.commit()
        embed=discord.Embed(description=f"** <a:H_TICK:1449446011490537603> All ignored channels and roles have been reset!**\n\nTo view current Automod settings use `{ctx.prefix}automod config`", color=0x000000)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=embed)
        

    @automod.group(name="unignore", aliases=["unwhitelist", "unwl"], invoke_without_command=True, help="Remove channels and roles from the whitelist.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unignore(self, ctx):
        try:
            embed = discord.Embed(
                title="Automod UnIgnore Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @unignore.command(name="channel", help="Remove a channel from the whitelist.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def unignore_channel(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        
        async with aiosqlite.connect("database/automod.db") as db:
            result = await db.execute("DELETE FROM automod_ignored WHERE guild_id = ? AND type = 'channel' AND id = ?", (guild_id, channel.id))
            await db.commit()

        if result.rowcount > 0:
            embed = discord.Embed(description=f"{channel.mention} has been removed from the automod ignore list.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"{channel.mention} is not in the automod ignore list.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            

    @unignore.command(name="role", help="Remove a role from the whitelist.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def unignore_role(self, ctx, role: discord.Role):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="<a:MekoCross:1449446075948859462> Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return


        
        async with aiosqlite.connect("database/automod.db") as db:
            result = await db.execute("DELETE FROM automod_ignored WHERE guild_id = ? AND type = 'role' AND id = ?", (guild_id, role.id))
            await db.commit()

        if result.rowcount > 0:
            embed = discord.Embed(description=f"<a:H_TICK:1449446011490537603> {role.mention} has been removed from the automod ignore list.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"<a:MekoCross:1449446075948859462> {role.mention} is not in the automod ignore list.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
    

    @automod.command(name="disable", help="Disable Automod in the server.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="<a:MekoCross:1449446075948859462> Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return
            
        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return
            
        embed = discord.Embed(
            description="**Are you sure you want to disable Automod?**\n\nThis will delete all custom event settings, punishments, ignored roles/channels, & logging channel data.",
            color=0x0000000
        )
        embed.set_footer(text="Click 'Yes' to disable Automod or 'No' to cancel.")
        embed.set_thumbnail(url=self.bot.user.avatar.url)

        view = ConfirmDisable(ctx.author)
        message = await ctx.send(embed=embed, view=view)

        await view.wait()

        if view.value is None:
            embed.description = "You took too long to respond. Automod disable process has been canceled."
            embed.color = 0x000000
            
            await message.edit(embed=embed, view=None)

        elif view.value:
            
            async with aiosqlite.connect("database/automod.db") as db:
                await db.execute("DELETE FROM automod WHERE guild_id = ?", (guild_id,))
                await db.execute("DELETE FROM automod_punishments WHERE guild_id = ?", (guild_id,))
                await db.execute("DELETE FROM automod_ignored WHERE guild_id = ?", (guild_id,))
                await db.execute("DELETE FROM automod_logging WHERE guild_id = ?", (guild_id,))
                await db.commit()



            embed.description = f"Automod has been successfully disabled for **{ctx.guild.name}.** \nAll settings, punishments, and logs have been removed.\n\nCurrent Status: False\n<:MekoArrowRight:1449445989436887090> To Re-enable use `{ctx.prefix}automod enable`."
            embed.color = 0x000000
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await message.edit(embed=embed, view=None)
            

        else:
            embed.description = "Automod disable process has been canceled."
            embed.color = 0x00000
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await message.edit(embed=embed, view=None)

        

    @automod.command(name="config", aliases=["settings", "show", "view"], help="View Automod settings.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="<a:MekoCross:1449446075948859462> Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return
            
        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return

        current_punishments = await self.get_current_punishments(guild_id)
        embed = discord.Embed(title=f"Enabled Automod Events & their punishment type for {ctx.guild.name}", color=0x000000)
        embed.set_footer(text="Manage punishment type for events by executing “automod punishment” command.", icon_url=self.bot.user.avatar.url)

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        else:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        for event, punishment in current_punishments:
            embed.add_field(name=event, value=punishment or "None", inline=False)

        async with aiosqlite.connect("database/automod.db") as db:
            cursor = await db.execute("SELECT log_channel FROM automod_logging WHERE guild_id = ?", (guild_id,))
            log_channel_id = await cursor.fetchone()

        if log_channel_id and log_channel_id[0]:
            log_channel = ctx.guild.get_channel(log_channel_id[0])
            if log_channel:
                embed.add_field(name="Logging Channel", value=f"{log_channel.mention}", inline=False)
            else:
                embed.add_field(name="Logging Channel", value="Deleted Channel", inline=False)
        else:
            embed.add_field(name="Logging Channel", value="No logging channel", inline=False)

        await ctx.send(embed=embed)


    @automod.command(name="logging", help="Set the logging channel for Automod events.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def logging(self, ctx, channel: discord.TextChannel):
        guild_id = ctx.guild.id
        if ctx.author != ctx.guild.owner and ctx.author.top_role.position < ctx.guild.me.top_role.position:
            embed = discord.Embed(description="<a:MekoCross:1449446075948859462> Your top role must be at the **same** position or **higher** than my top role.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return
        if not await self.is_automod_enabled(guild_id):
            embed=discord.Embed(description=f"Umm, looks like your server has not enabled Automod.\n\nCurrent Status: False\nTo Enable use `{ctx.prefix}automod enable`", color=0x000000)
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.send(embed=embed)
            return
            
        async with aiosqlite.connect("database/automod.db") as db:
            await db.execute("INSERT OR REPLACE INTO automod_logging (guild_id, log_channel) VALUES (?, ?)", (guild_id, channel.id))
            await db.commit()
            embed=discord.Embed(description=f"**<a:H_TICK:1449446011490537603> Automod Logging channel set to {channel.mention}.**\n\n<:MekoArrowRight:1449445989436887090> Use `{ctx.prefix}automod config` to view current Automod settings.", color=0x000000)
            embed.set_footer(text=f"“{ctx.command.qualified_name}” Command executed by {ctx.author}",
                   icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        guild_id = guild.id

        async with aiosqlite.connect("database/automod.db") as db:
            await db.execute("DELETE FROM automod WHERE guild_id = ?", (guild_id,))
            await db.execute("DELETE FROM automod_punishments WHERE guild_id = ?", (guild_id,))
            await db.execute("DELETE FROM automod_ignored WHERE guild_id = ?", (guild_id,))
            await db.execute("DELETE FROM automod_logging WHERE guild_id = ?", (guild_id,))
            await db.commit()
            
async def setup(client):
    await client.add_cog(Automod(client))