import discord
from discord.ext import commands
from discord import ui
from utils.Tools import *

class BanView(ui.View):
    def __init__(self, user, author):
        super().__init__(timeout=120)
        self.user = user
        self.author = author
        self.message = None  
        self.color = discord.Color.from_rgb(0, 0, 0)

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

    @ui.button(label="Unban", style=discord.ButtonStyle.success)
    async def unban(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReasonModal(user=self.user, author=self.author, view=self)
        await interaction.response.send_modal(modal)

    @ui.button(style=discord.ButtonStyle.gray, emoji="<:MekoTrash:1449445909585723454>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class AlreadyBannedView(ui.View):
    def __init__(self, user, author):
        super().__init__(timeout=120)
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
            await self.message.edit(view=self)

    @ui.button(label="Unban", style=discord.ButtonStyle.success)
    async def unban(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReasonModal(user=self.user, author=self.author, view=self)
        await interaction.response.send_modal(modal)

    @ui.button(style=discord.ButtonStyle.gray, emoji="<:MekoTrash:1449445909585723454>")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

class ReasonModal(ui.Modal):
    def __init__(self, user, author, view):
        super().__init__(title="Unban Reason")
        self.user = user
        self.author = author
        self.view = view
        self.reason_input = ui.TextInput(label="Why do you want to unban?", placeholder="Provide a reason to unban or leave it blank for no reason.", required = False, max_length=2000, style=discord.TextStyle.paragraph)
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason_input.value or "No reason provided"
        try:
            await self.user.send(f"<a:H_TICK:1449446011490537603> You have been Unbanned from **{self.author.guild.name}** by **{self.author}**. Reason: {reason or 'Not Provided'}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"
            
        embed = discord.Embed(description=f"**<:MekoUser:1449446018163806270> Target User:** [{self.user}](https://discord.com/users/{self.user.id})\n<:MekoPing:1449446025206173807> **User Mention:** {self.user.mention}\n**<:Mail:1449446038934126754> DM Sent:** {dm_status}\n**<:MekoSearch:1449446045712121978> Reason:** {reason}", color=0x000000)
        embed.set_author(name=f"Successfully Unbanned {self.user.name}", icon_url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
        embed.set_footer(text=f"Requested by {self.author}", icon_url=self.author.avatar.url if self.author.avatar else self.author.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        try:
            await interaction.guild.unban(self.user, reason=f"Unban requested by {self.author}")
            
        except discord.NotFound:
            pass
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

        try:
            await interaction.response.edit_message(embed=embed, view=self.view)
            for item in self.view.children:
                item.disabled = True
                await interaction.message.edit(view=self.view)
        except discord.NotFound:
            pass
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass
        
        

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(0, 0, 0)

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    @commands.hybrid_command(
        name="ban",
        help="Bans a user from the Server",
        usage="ban <member>",
        aliases=["fuckban", "hackban"])
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):
        
        member = ctx.guild.get_member(user.id)
        if not member:
            embed = discord.Embed(description=f"**{user} is not a member of this server.**", color=self.color)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            return await ctx.send(embed=embed)

        bans = [entry async for entry in ctx.guild.bans()]
        if any(ban_entry.user.id == user.id for ban_entry in bans):
            embed = discord.Embed(description=f"**Requested User is already banned in this server.**", color=self.color)
            embed.add_field(name="__Unban__:", value="Click on the `Unban` button to unban the mentioned user.")
            embed.set_author(name=f"User is Already Banned!", icon_url=self.get_user_avatar(user))
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            view = AlreadyBannedView(user=user, author=ctx.author)
            message = await ctx.send(embed=embed, view=view)
            view.message = message 
            return

        if member == ctx.guild.owner:
            error = discord.Embed(color=self.color, description="I can't ban the Server Owner!")
            error.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            return await ctx.send(embed=error)

        if isinstance(member, discord.Member) and member.top_role >= ctx.guild.me.top_role:
            error = discord.Embed(color=self.color, description="I can't ban a user with a higher or equal role!")
            error.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
            return await ctx.send(embed=error)

        if isinstance(member, discord.Member):
            if ctx.author != ctx.guild.owner:
                if member.top_role >= ctx.author.top_role:
                    error = discord.Embed(color=self.color, description="You can't ban a user with a higher or equal role!")
                    error.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
                    return await ctx.send(embed=error)

        try:
            await user.send(f"<:MekoExclamation:1449445917500510229> You have been banned from **{ctx.guild.name}** by **{ctx.author}**. Reason: {reason or 'No reason provided'}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        await ctx.guild.ban(user, reason=f"Ban requested by {ctx.author} for reason: {reason or 'No reason provided'}")

        reasonn = reason or "No reason provided"
        embed = discord.Embed(description=f"<:MekoMod:1449446053345628297> Moderator : [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id}) ({ctx.author.mention})\n<:MekoMember:1449446061541167175> Target : [{user.display_name}](https://discord.com/users/{user.id}) ({user.mention})\n<:icon_mail:1449446068940050624> Dm : {dm_status}\n<:MekoRuby:1449445982931783710> Reason : {reasonn}", color=self.color)
        embed.set_author(name=f"User Banned", icon_url=self.get_user_avatar(user))
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=self.get_user_avatar(ctx.author))
        embed.timestamp = discord.utils.utcnow()

        view = BanView(user=user, author=ctx.author)
        message = await ctx.send(embed=embed, view=view)
        view.message = message
        
async def setup(client):
    await client.add_cog(Ban(client))