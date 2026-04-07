import sqlite3
import discord
from discord.ext import commands
from Buttons.AntinukeButtons import AntiEvents, Buttons, PunishmentView, RecoverButton,TrashButton
from checks.colorcheck import get_embed_color
from utils.tool import *
from discord.ui import View, Button
import aiosqlite
from datetime import datetime


async def is_premium_guild(guild_id: int) -> bool:
    try:
        async with aiosqlite.connect("database/premium_codes.db") as db:
            async with db.execute(
                "SELECT expires_at FROM premium_users WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    expires_at = datetime.fromisoformat(row[0])
                    return expires_at > discord.utils.utcnow()
        return False
    except Exception as e:
        print(f"[Premium Check Error] {e}")
        return False

class AntinukeGroups(commands.Cog):
    """Shows a list of commands regarding antinuke"""
    def __init__(self, client):
        self.client = client

    @commands.hybrid_group(name="antinuke", aliases=["anti", "security", "protection"], help="Enables/Disables antinuke in your server!", invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    
    async def _antinuke(self, ctx):
        try:
            embed = discord.Embed(
                title="AntiNuke Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @_antinuke.command(name="enable",
                       help="Server owner should enable antinuke for the server!",
                       aliases=["on"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def antinuke_enable(self, ctx: commands.Context):
        data = getanti(ctx.guild.id)
        ok = getConfig(ctx.guild.id)
        punish = ok["punishment"]
        if ctx.author.id == ctx.guild.owner_id:
           if data == "on":
            embed = discord.Embed(
                description="**Antinuke** is already enabled for this guild.\n> Disable the **Antinuke** using `antinuke disable`",
                color=0xFFFFFF
                )
            embed.set_footer(text=f"Current punishment type: {punish}")
            await ctx.send(embed=embed)
           else:
            data = "on"
            updateanti(ctx.guild.id, data)
            embed = discord.Embed(
                description="Enabled **Antinuke** for this guild\n> Disable the **Antinuke** using `antinuke disable`",
                color=0xFFFFFF
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {ctx.author.mention}: You must be the guild owner to use this command", color=0xFFFFFF)
            await ctx.send(embed=embed)

    @_antinuke.command(name="disable",
                       help="You can disable antinuke for your server using this command",
                       aliases=["off"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def antinuke_disable(self, ctx: commands.Context):
      data = getanti(ctx.guild.id)
      ok = getConfig(ctx.guild.id)
      prefix = ok.get("prefix", ".")
      user_id = str(ctx.author.id)
      embed_color = get_embed_color(user_id, ctx)
      if ctx.author.id == ctx.guild.owner_id: 
        if data == "off":
          embed = discord.Embed(
              description="**Antinuke** is already disabled for this guild.\n> Enable the **Antinuke** using `antinuke enable`",
              color=0xFFFFFF
              )
          await ctx.send(embed=embed)
        else:
          data = "off"
          updateanti(ctx.guild.id, data)
          embed = discord.Embed(
              description="Disabled **Antinuke** for this guild\n> Enable the **Antinuke** using `antinuke enable`",
              color=0xFFFFFF
              )
          await ctx.send(embed=embed)
      else:
        embed = discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {ctx.author.mention}: You must be the guild owner to use this command", color=0xFFFFFF)
        await ctx.send(embed=embed)

    @_antinuke.command(name="show",
                       help="Shows currently antinuke config settings of your server",
                       aliases=["config"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    
    async def antinuke_show(self, ctx: commands.Context):
        data = getanti(ctx.guild.id)
        antiban = getantiban(ctx.guild.id)
        antibot = getantibot(ctx.guild.id)
        antikick = getantikick(ctx.guild.id)
        antiprune = getantiprune(ctx.guild.id)
        antichannel = getantichannel(ctx.guild.id)
        antirole = getantirole(ctx.guild.id)
        antiweb = getantiweb(ctx.guild.id)
        antiemoji = getantiemoji(ctx.guild.id)
        antiguild = getantiguild(ctx.guild.id)
        antiping = getantiping(ctx.guild.id)
        antimember = getantimember(ctx.guild.id)

        ok = getConfig(ctx.guild.id)
        wled = ok["whitelisted"]
        punish = ok["punishment"]
        prefix = ok["prefix"]
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        if user_id != str(ctx.guild.owner_id):
                embed = discord.Embed(description=f"<:MekoExclamation:1449445917500510229> {ctx.author.mention}: You must be the guild owner to use this command", color=0xFEE75C)
                await ctx.send(embed=embed)
                return

        if data == "off":
            description = (f"**{ctx.guild.name} Antinuke Configurations**\n\n"
                          "Antinuke has been disabled on this server. This means that the bot will no longer monitor and prevent any actions that could potentially harm the server or its members.\n\n"
                          "Current Status: <:disabled:1449445995883790358>\n\n"
                          f"> To enable use **`{prefix}antinuke enable`**")
            color = embed_color
            embed_fields = []
            view = None 
        else:
            modules = {
                "Anti Bot": antibot,
                "Anti Ban": antiban,
                "Anti Kick": antikick,
                "Anti Prune": antiprune,
                "Anti Webhook Create": antiweb,
                "Anti Member Role Add/Remove": antimember,
                "Anti Channel Create/Delete/Update": antichannel,
                "Anti Role Create/Delete/Update": antirole,
                "Anti Emoji Create/Delete/Update": antiemoji,
                "Anti Guild Update": antiguild,
                "Anti Everyone/Here Mention": antiping,
                "Anti Integration": antiweb,
            }

            module_status = "\n".join(f"**{name}:** {'<:enable:1449445968297853040>' if status == 'on' else '<:disabled:1449445995883790358>'}" for name, status in modules.items())
            
            description = (f"**{ctx.guild.name} Antinuke Configurations**\n\n"
                          "Move my role to top of roles for me to work properly, This will ensure that I have the necessary permissions to perform my functions and prevent any potential security breaches.\n\n"
                          f"**__Antinuke Modules__**:\n\n{module_status}\n\n"
                          f"**Whitelisted Users:** {len(wled)}\nUse **`{prefix}antinuke whitelist show`** to check the whitelisted users list.\n\n"
                          f"**Auto Recovery:** <:enable:1449445968297853040>\n"
                          f"**Antinuke Logging:** Use `{ctx.prefix}antinuke logging show` to check")
            color = embed_color
            embed_fields = [
                {
                    "name": "Other settings",
                    "value": f"To change the punishment type **`{prefix}punishment set <type>`**\nAvailable Punishments types are: **`Ban`**, **`Kick`** & **`strip`**",
                }
            ]
            view = Buttons(author_id=ctx.author.id) 

        embed = discord.Embed(description=description, color=color)
        for field in embed_fields:
            embed.add_field(name=field["name"], value=field["value"])
        embed.set_footer(text=f"Current punishment type is {punish}",
                         icon_url=ctx.message.author.avatar)
        embed.set_author(name=f"{self.client.user.name} • Security",
                         icon_url=self.client.user.avatar.url)

        await ctx.send(embed=embed, view=view, mention_author=False)

        
    @_antinuke.command(name="recover", aliases=['clear'], help="Delete all the channels or roles by the same name")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    
    async def recover(self, ctx: commands.Context):
        data = getConfig(ctx.guild.id)
        ded = getanti(ctx.guild.id)
        owner = data["owners"]
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        if ctx.author.id != ctx.guild.owner_id and str(ctx.author.id) not in owner:
            em1 = discord.Embed(description="<:Icon_No:1449446003550715906> | This command can only be used by the guild owner or extra owners.", color=embed_color)
            return await ctx.send(embed=em1, delete_after=120)
        if ded == "off":
            em4 = discord.Embed(description="<:Icon_No:1449446003550715906> | Antinuke is not enabled for this guild.", color=embed_color)
            return await ctx.send(embed=em4, delete_after=120) 
        else: 
            embed = discord.Embed(title="Cypher • Recovery", description="Select one of the button below: **`Channel`** or **`Role`**\n**__How to use?__**\n- Use one of the button and a modal will pop up in the modal submit the name of the channel/role that exists in the server", color=embed_color)
            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_footer(text=f"Requested By {ctx.author.display_name}", 
                            icon_url=ctx.author.display_avatar.url)
            view = (RecoverButton(ctx.author.id))
            await ctx.send(embed=embed, view=view)

    @_antinuke.command(name="events", aliases=['module'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def module(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        ok = getConfig(ctx.guild.id)
        ded = getanti(ctx.guild.id)
        owner = ok["owners"]
        prefix = ok["prefix"]
        if ctx.author.id != ctx.guild.owner_id and str(ctx.author.id) not in owner:
            em1 = discord.Embed(description="<:Icon_No:1449446003550715906> | This command can only be used by the guild owner or extra owners.", color=embed_color)
            return await ctx.send(embed=em1, delete_after=120)
        if ded == "off":
            em4 = discord.Embed(description="<:Icon_No:1449446003550715906> | Antinuke is not enabled for this guild.", color=embed_color)
            return await ctx.send(embed=em4, delete_after=120)
        else: 
            embed = discord.Embed(description=f"**__Antinuke Events Configuration__**\n\n<:info:1449445954142081278> **__What is this__**?\n - Using this you can **`Enable/Disable`** events for **`Antinuke`**, The whitelisted users will not be affected by the events\n<:info:1449445954142081278> **__How to Whitelist__**?\n- Use `{prefix}antinuke whitelist add <@user>`\n<:info:1449445954142081278> **__How to use__**?\n- Using the dropdown you can select the event you need to **`Enable/Disable`** after that you can use the **`Enable`** button to enable the event or the **`Disable`** button to disable the event\n- Note - The event will not work if the **`Antinuke`** is disable for this guild even if you enable the event using this command\n<:info:1449445954142081278> **__How to enable Antinuke__**?\n- Use `{prefix}antinuke enable`", color=embed_color)
            embed.set_author(name=ctx.guild.name,
                            icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_footer(text=f"Requested By {ctx.author.display_name}",
                            icon_url=ctx.author.display_avatar.url)
            b2 = Button(label="Need Help? Join Support Server", style=discord.ButtonStyle.url, url="https://discord.gg/UtZ3rRnBnU")
            view = View()
            view.add_item(b2)
            view.add_item(TrashButton(ctx.author.id))
            view.add_item(AntiEvents(guild_id=ctx.guild.id, author=ctx.author.id))
            await ctx.send(embed=embed, view=view)

    @commands.hybrid_group(name="extraowner", aliases=["own"], help="Add extra owners for the server", invoke_without_command=True)
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    
    @commands.has_permissions(administrator=True)
    async def _owner(self, ctx):
        try:
            embed = discord.Embed(
                title="AntiNuke Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @_owner.command(name="add", help="Add a user to extra server owner")
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def owner_add(self, ctx, user: discord.User):
        data = getConfig(ctx.guild.id)
        own = data["owners"]
        owner = ctx.guild.owner
        clr = get_embed_color(ctx.author.id, ctx)
        max_owners = 5 if is_premium_guild(ctx.guild.id) else 3
        
        if ctx.author.id == ctx.guild.owner_id:
            if len(own) >= max_owners:
                embed = discord.Embed(
                    description=f"<:Icon_No:1449446003550715906> | This server has reached the maximum number of extra owners ({max_owners}).\n- Remove one to add another.\n- Add up-to 5 extraowners by having premium",
                    color=clr
                )
                await ctx.send(embed=embed)
            else:
                if str(user.id) in own:
                    embed = discord.Embed(
                        description=f"<:Icon_No:1449446003550715906> | {user.mention} is already an extra owner for this server.",
                        color=clr
                    )
                    await ctx.send(embed=embed)
                else:
                    own.append(str(user.id))
                    updateConfig(ctx.guild.id, data)
                    embed = discord.Embed(
                        description=f"<:tick_icons:1449445939256229961> | Successfully added **{user.mention}** to extra owner.",
                        color=clr
                    )
                    await ctx.send(embed=embed)
        else:
            await ctx.send("<:Icon_No:1449446003550715906> | You must be the guild owner to add someone as an extra owner.")


    @_owner.command(name="remove", help="Remove a user from extra owners")
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def owner_remove(self, ctx, user: discord.User):
      data = getConfig(ctx.guild.id)
      own = data["owners"]
      clr = get_embed_color(ctx.author.id, ctx)
      if ctx.author.id == ctx.guild.owner_id:
        if str(user.id) in own:
          own.remove(str(user.id))
          updateConfig(ctx.guild.id, data)
          embed = discord.Embed(description=f"<:tick_icons:1449445939256229961> | Successfully removed **{user.mention}** from extraowner.", color=clr)
          await ctx.send(embed=embed)
        else:
          embed = discord.Embed(description=f"<:Icon_No:1449446003550715906> | {user.mention} Is not an extraowner for this server .",
                                  color=clr
            )
          await ctx.send(embed=embed)
      else:
        await ctx.send("<:Icon_No:1449446003550715906> | You must be the guild owner to remove someone from extra owners.")


    @_owner.command(name="show", help="Shows the list of Extra Owners")
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def owner_show(self, ctx):
        data = getConfig(ctx.guild.id)
        own = data["owners"]
        prefix = data["prefix"]
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        if ctx.author.id == ctx.guild.owner_id :
            if not own:
                await ctx.send(f"<:Icon_No:1449446003550715906> | There aren't any extraowner(s) to show. You can add them by `{prefix}extraowner add <user>`")
            else:
                owner_list = "\n".join([f"`[{str(index+1).zfill(2)}]` | <@{owner_id}>" for index, owner_id in enumerate(own)])
                embed = discord.Embed(title=f"Extraowners list for {ctx.guild.name}:", description=f"\n{owner_list}", color=embed_color)
                embed.set_footer(text=f"Requested By {ctx.author.name}", icon_url=ctx.author.display_avatar)
                embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                view = discord.ui.View(timeout=None)
                view.add_item(TrashButton(ctx.author.id))
                await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("<:Icon_No:1449446003550715906> | You must be the guild owner to view the extra owners.")

    @_antinuke.group(name="whitelist", aliases=["wl"], help="Whitelist your TRUSTED users for anti-nuke", invoke_without_command=True)
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    @commands.has_permissions(administrator=True)
    async def _whitelist(self, ctx):
        try:
            embed = discord.Embed(
                title="AntiNuke Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @_whitelist.command(name="add", help="Add a user to whitelisted users")
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def whitelist_add(self, ctx, user: discord.User):
        data = getConfig(ctx.guild.id)
        ded = getanti(ctx.guild.id)
        ownerr = data["owners"]
        wled = data["whitelisted"]
        clr = get_embed_color(ctx.author.id, ctx)
        max_whitelisted = 15 if is_premium_guild(ctx.guild.id) else 10
        if ctx.author == ctx.guild.owner or str(ctx.author.id) in ownerr: 
            if len(wled) >= max_whitelisted:
                embed = discord.Embed(
                    description=f"<:Icon_No:1449446003550715906> | This server has reached the maximum number of extra owners ({max_whitelisted}).\n- Remove one to add another.\n- Add up-to 5 extraowners by having premium",
                    color=clr
                )
                await ctx.send(embed=embed)
            elif ded == "off":
                em4 = discord.Embed(
                    description="<:Icon_No:1449446003550715906> | Antinuke is not enabled for this guild.", 
                    color=clr
                )
                await ctx.send(embed=em4, delete_after=120)
            else:
                if str(user.id) in wled:
                    embed = discord.Embed(
                        description=f"<:Icon_No:1449446003550715906> | {user.mention} is already whitelisted.", 
                        color=clr
                    )
                    await ctx.send(embed=embed)
                else:
                    wled.append(str(user.id))
                    data["whitelisted"] = wled
                    updateConfig(ctx.guild.id, data)
                    embed = discord.Embed(
                        description=f"<:tick_icons:1449445939256229961> | Successfully whitelisted **{user.mention}**.", 
                        color=clr
                    )
                    await ctx.send(embed=embed)
        else:
            await ctx.send("<:Icon_No:1449446003550715906> | You must be the guild owner or an extra owner to whitelist someone.")


    @_whitelist.command(name="remove", aliases=["rmv"], help="Remove a user from whitelisted users")
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def whitelist_remove(self, ctx, user: discord.User):
      d3 = getConfig(ctx.guild.id)
      data = getConfig(ctx.guild.id)
      ded = getanti(ctx.guild.id)
      ownerr = d3["owners"]
      wled = data["whitelisted"]
      owner = ctx.guild.owner
      clr = get_embed_color(ctx.author.id, ctx)
      if ctx.author == owner or str(ctx.author.id) in ownerr: 
        if ded == "off":
            em4 = discord.Embed(description="<:Icon_No:1449446003550715906> | Antinuke is not enabled for this guild.", color=clr)
            return await ctx.send(embed=em4, delete_after=120) 
        if str(user.id) in wled:
          wled.remove(str(user.id))
          updateConfig(ctx.guild.id, data)
          embed = discord.Embed(description=f"<:tick_icons:1449445939256229961> | Successfully unwhitelisted **{user.mention}**.", color=clr)
          await ctx.send(embed=embed)
        else:
          embed = discord.Embed(description=f"<:Icon_No:1449446003550715906> | {user.mention} Is not whitelisted.", color=clr)
          await ctx.send(embed=embed)
      else:
        await ctx.send("<:Icon_No:1449446003550715906> | You must be the guild owner to remove someone from whitelist.", mention_author=False)


    @_whitelist.command(name="show", help="Check who are in whitelist database")
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def whitelist_show(self, ctx):
        data = getConfig(ctx.guild.id)
        ownerr = data["owners"]
        prefix = data["prefix"]
        wled = data["whitelisted"]
        ded = getanti(ctx.guild.id)
        user_id = str(ctx.author.id)
        owner = ctx.guild.owner
        embed_color = get_embed_color(user_id, ctx)
        if ctx.author == owner or str(ctx.author.id) in ownerr: 
            if ded == "off":
                em4 = discord.Embed(description="<:Icon_No:1449446003550715906> | Antinuke is not enabled for this guild.", color=embed_color)
                return await ctx.send(embed=em4, delete_after=120) 
            if len(wled) == 0:
                await ctx.send(f"<:Icon_No:1449446003550715906> | There aren't any whitelisted user(s). You can add them by `{prefix}antinuke wl add <user>`")
            else:
                embed = discord.Embed(title=f"Whitelisted Users for {ctx.guild.name}:", description="", color=embed_color)
                for index, idk in enumerate(wled):
                    embed.description += f"`[{str(index+1).zfill(2)}]` <@{idk}> | `(ID: {idk})`\n"
                embed.set_footer(text=f"Requested By {ctx.author.name}", icon_url=ctx.author.display_avatar)
                embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                view = discord.ui.View(timeout=None)
                view.add_item(TrashButton(ctx.author.id))
                await ctx.send(embed=embed, view=view)
        else:
           await ctx.send("<:Icon_No:1449446003550715906> | You must be the guild owner to view the whitelisted users.", mention_author=False)



    @_whitelist.command(name="reset", help="Removes every user from the whitelist database", aliases=["clear"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def wl_reset(self, ctx):
        d3 = getConfig(ctx.guild.id)
        owner = d3["owners"]
        embed_color = get_embed_color(ctx.author.id, ctx)
        ded = getanti(ctx.guild.id)
        ownerr = ctx.guild.owner
        if ded == "off":
            em4 = discord.Embed(description="<:Icon_No:1449446003550715906> | Antinuke is not enabled for this guild.", color=embed_color)
            return await ctx.send(embed=em4, delete_after=120)
        if ctx.author == ownerr or str(ctx.author.id) in owner:
            if not d3["whitelisted"]:
                em5 = discord.Embed(description="<:Icon_No:1449446003550715906> | The whitelist is already empty. There is nothing to reset.", color=embed_color)
                return await ctx.send(embed=em5, delete_after=120)
            d3["whitelisted"] = []
            updateConfig(ctx.guild.id, d3)
            em = discord.Embed(description="<:tick_icons:1449445939256229961> | Successfully reset the whitelist for this server.", color=embed_color)
            await ctx.send(embed=em)
        else:
            await ctx.send("<:Icon_No:1449446003550715906> | You must be the guild owner or an extra owner to use this command.")



    @_antinuke.group(name="punishment", help="Changes Punishment of antinuke and antiraid for this server.", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def _punishment(self, ctx):
        try:
            embed = discord.Embed(
                title="AntiNuke Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

    @_punishment.command(name='set')
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    async def set(self, ctx):
        ded = getanti(ctx.guild.id)
        data = getConfig(ctx.guild.id) 
        owner = data["owners"]
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        if ctx.author.id != ctx.guild.owner_id and str(ctx.author.id) not in owner:
            em1 = discord.Embed(description="<:Icon_No:1449446003550715906> | This command can only be used by the guild owner or extra owners.", color=embed_color)
            return await ctx.send(embed=em1, delete_after=120)
        if ded == "off":
            em4 = discord.Embed(description="<:Icon_No:1449446003550715906> | Antinuke is not enabled for this guild.", color=embed_color)
            return await ctx.send(embed=em4, delete_after=120) 
        else:
           embed = discord.Embed(
              title="Choose the Punishment for Antinuke Events",
              description=f"Please choose the appropriate punishment for antinuke events by clicking one of the buttons below.\n\n- Available punishments are `Kick`, `Ban`, `Strip`\n> Note: - If the punishment is set to `None` {self.client.user.mention} will not punish the user(s) but it will revert the changes made by the user(s) ",
              color=embed_color
              )
           embed.set_footer(text=f"Requested By {ctx.author.name}",
                            icon_url=ctx.author.display_avatar.url)
           embed.set_author(name=ctx.guild.name,
                            icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
           view = PunishmentView(ctx.author.id, ctx.guild.id)
           view.add_item(TrashButton(ctx.author.id))
           await ctx.send(embed=embed, view=view)


    @_punishment.command(name="show", help="Shows the antinuke punishment type for this server")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    
    async def punishment_show(self, ctx: commands.Context):
        user_id = str(ctx.author.id)
        embed_color = get_embed_color(user_id, ctx)
        data = getConfig(ctx.guild.id)
        punish = data["punishment"]
        ded = getanti(ctx.guild.id)
        owner = data["owners"]
        if ctx.author.id != ctx.guild.owner_id and str(ctx.author.id) not in owner:
            em1 = discord.Embed(description="<:Icon_No:1449446003550715906> | This command can only be used by the guild owner or extra owners.", color=embed_color)
            return await ctx.send(embed=em1, delete_after=120)
        if ded == "off":
            em4 = discord.Embed(description="<:Icon_No:1449446003550715906> | Antinuke is not enabled for this guild.", color=embed_color)
            return await ctx.send(embed=em4, delete_after=120) 
        else:
            embed = discord.Embed(
              description=f"Current punishment type for antinuke events: **{punish.title()}**",
              color=embed_color
              )
            embed.set_author(name=ctx.guild.name,
                                icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_footer(text=f"Requested by {ctx.author}",
                                icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(AntinukeGroups(bot))