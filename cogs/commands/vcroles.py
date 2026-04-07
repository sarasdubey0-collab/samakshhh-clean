import discord
from discord.ext import commands
from gtts import gTTS
from discord.utils import get
import os
from utils.Tools import *
from typing import Optional, Union
from discord.ext.commands import Context
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from utils import *
import tempfile

class VCButtons(discord.ui.View):
    def __init__(self, inviter: discord.Member, target: discord.Member, action: str):
        super().__init__(timeout=60)
        self.inviter = inviter
        self.target = target
        self.action = action  # 'invite' or 'request'
        self.message = None
        
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("You're not allowed to respond to this request.", ephemeral=True)

        if self.action == "invite":
            if not self.inviter.voice:
                return await interaction.response.send_message("The inviter is no longer in a voice channel.", ephemeral=True)

            try:
                await self.target.move_to(self.inviter.voice.channel)
                await interaction.response.edit_message(
                    content=f"{self.target.mention} has joined {self.inviter.voice.channel.mention}!", view=None)
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to move you to the VC.", ephemeral=True)

        elif self.action == "request":
            if not self.target.voice:
                return await interaction.response.send_message("The user you requested is not in a voice channel.", ephemeral=True)

            try:
                await self.inviter.move_to(self.target.voice.channel)
                await interaction.response.edit_message(
                    content=f"{self.inviter.mention} has joined {self.target.voice.channel.mention}!", view=None)
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to move you to the VC.", ephemeral=True)
                
                try:
                    await self.message.delete()
                except discord.NotFound:
                    pass

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("You're not allowed to respond to this request.", ephemeral=True)
        try:
            await self.message.delete()
        except discord.NotFound:
            pass
        await interaction.response.send_message("Request declined.", ephemeral=True)


class Voice(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.color = 0x2f3136

    @commands.hybrid_command(name="vcinvite", description="Invite a user to join your voice channel.", aliases=["vcinv"])
    async def vcinvite(self, ctx: commands.Context, user: discord.Member):
        if ctx.author.voice is None:
            return await ctx.reply("You must be in a voice channel to invite someone.", ephemeral=True)
        
        if user.voice is None:
            return await ctx.reply(f"{user.mention} is not in a voice channel to receive the invite.", ephemeral=True)
        view = VCButtons(inviter=ctx.author, target=user, action="invite")
        embed=discord.Embed(color=0xFFFFFF)
        embed.description=f"{user.mention}, do you want to join {ctx.author.mention}'s VC?"
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg
        
    @commands.hybrid_command(name="vcrequest", description="Request to join a user's voice channel." , aliases= ["vcreq"])
    async def vcrequest(self, ctx: commands.Context, user: discord.Member):
        if user.voice is None:
            return await ctx.reply(f"{user.mention} is not in a voice channel.", ephemeral=True)
        if ctx.author.voice is None:
            return await ctx.reply("You must be in a voice channel to request to join someone.", ephemeral=True)
        view = VCButtons(inviter=ctx.author, target=user, action="request")
        embed = discord.Embed(color=0xFFFFFF)
        embed.description = f"{user.mention}, do you allow {ctx.author.mention} to join your VC?"
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg
        
    @commands.group(name="voice", invoke_without_command=True, aliases=['vc'])
    @blacklist_check()
    @ignore_check()
    async def vc(self, ctx: commands.Context):
        if ctx.subcommand_passed is None:
            manaskabhosda = discord.Embed()
            manaskabhosda.title = "Voice Subcommands:"
            manaskabhosda.description = "> `voice mute`, `voice unmute`, `voice defean`, `voice undefean`, `voice muteall`, `voice unmuteall`, `voice defeanall`, `voice undefeanall`, `voice kick`, `voice kickall`, `voice moveall`, `vcinvite`, `vcrequest`, `voice pull`"
            await ctx.send(embed=manaskabhosda)
            ctx.command.reset_cooldown(ctx)

    @vc.command(name="kick",
                help="Dissconnect a member from a voice channel .",
                usage="voice kick <member>")
    @commands.has_guild_permissions(move_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _kick(self, ctx, *, member: discord.Member):
        if member.voice is None:
            hacker5 = discord.Embed(
                
                description=
                f"{str(member)} is not connected in any of the voice channel",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            hacker5.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=hacker5)
        ch = member.voice.channel.mention
        await member.edit(voice_channel=None,
                          reason=f"Disconnected by {str(ctx.author)}")
        hacker = discord.Embed(
            
            description=f"{str(member)} has been disconnected from {ch}",
            color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.reply(embed=hacker)

    @vc.command(name="kickall",
                help="Dissconnect all member from a voice channel .",
                usage="voice kick all")
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _kickall(self, ctx):
        if ctx.author.voice is None:
            hacker5 = discord.Embed(
                
                description=
                f"You are not connected in any of the voice channel",
                color=self.color)
            hacker5.set_author(name=f"{ctx.author.name}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            hacker5.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=hacker5)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            await member.edit(
                voice_channel=None,
                reason=f"Disconnected Command Executed By {str(ctx.author)}")
            count += 1
        hacker = discord.Embed(
            
            description=f"Disconnected {count} members from {ch}",
            color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.reply(embed=hacker)

    @vc.command(name="mute",
                help="mute a member in voice channel .",
                usage="voice mute <member>")
    @commands.has_guild_permissions(mute_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def vcmute(self, ctx, *, member: discord.Member):
        if member.voice is None:
            error = discord.Embed(
                
                description=
                f"{str(member)} is not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        if member.voice.mute == True:
            hacker5 = discord.Embed(
                
                description=
                f"{str(member)} is already muted in the voice channel",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            hacker5.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=hacker5)
        ch = member.voice.channel.mention
        hacker = discord.Embed(
            
            description=f"{str(member)} has been muted in {ch}",
            color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await member.edit(mute=True, reason=f"Muted by {str(ctx.author)}")
        return await ctx.reply(embed=hacker)

    @vc.command(name="unmute",
                help="unmute a member in voice channel .",
                usage="voice unmute <member>")
    @commands.has_guild_permissions(mute_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def vcunmute(self, ctx, *, member: discord.Member):
        if member.voice is None:
            error = discord.Embed(
                
                description=
                f"{str(member)} is not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        if member.voice.mute == False:
            hacker5 = discord.Embed(
                
                description=
                f"{str(member)} is already unmuted in the voice channel",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            hacker5.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=hacker5)
        ch = member.voice.channel.mention
        hacker = discord.Embed(
            
            description=f"{str(member)} has been unmuted in {ch}",
            color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await member.edit(mute=False, reason=f"Unmuted by {str(ctx.author)}")
        return await ctx.reply(embed=hacker)

    @vc.command(name="muteall",
                help="mute all member in a voice channel .",
                usage="voice muteall")
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _muteall(self, ctx):
        if ctx.author.voice is None:
            error = discord.Embed(
                
                description=
                f"You are not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.mute == False:
                await member.edit(
                    mute=True,
                    reason=
                    f"voice muteall Command Executed by {str(ctx.author)}")
                count += 1
        hacker = discord.Embed(
                               description=f"Muted {count} members in {ch}",
                               color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.reply(embed=hacker)

    @vc.command(name="unmuteall",
                help="unmute all member in a voice channel .",
                usage="voice unmuteall")
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _unmuteall(self, ctx):
        if ctx.author.voice is None:
            error = discord.Embed(
                
                description=
                f"You are not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.mute == True:
                await member.edit(
                    mute=False,
                    reason=
                    f"voice unmuteall Command Executed by {str(ctx.author)}")
                count += 1
        hacker = discord.Embed(
                               description=f"Unmuted {count} members in {ch}",
                               color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.reply(embed=hacker)

    @vc.command(name="deafen",
                help="deafen a member in a voice channel .",
                usage="voice deafen <member>")
    @commands.has_guild_permissions(deafen_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _deafen(self, ctx, *, member: discord.Member):
        if member.voice is None:
            error = discord.Embed(
                
                description=
                f"{str(member)} is not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        if member.voice.deaf == True:
            hacker5 = discord.Embed(
                
                description=
                f"{str(member)} is already deafen in the voice channel",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            hacker5.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=hacker5)
        ch = member.voice.channel.mention
        hacker = discord.Embed(
            
            description=f"{str(member)} has been Deafen in {ch}",
            color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await member.edit(deafen=True, reason=f"Deafen by {str(ctx.author)}")
        return await ctx.reply(embed=hacker)

    @vc.command(name="undeafen",
                help="undeafen a member in a voice channel .",
                usage="voice undeafen <member>")
    @commands.has_guild_permissions(deafen_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _undeafen(self, ctx, *, member: discord.Member):
        if member.voice is None:
            error = discord.Embed(
                
                description=
                f"{str(member)} is not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        if member.voice.deaf == False:
            hacker5 = discord.Embed(
                
                description=
                f"{str(member)} is already undeafen in the voice channel",
                color=self.color)
            hacker5.set_author(name=ctx.author,
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            hacker5.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=hacker5)
        ch = member.voice.channel.mention
        hacker = discord.Embed(
            
            description=f"{str(member)} has been undeafen in {ch}",
            color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        await member.edit(deafen=False,
                          reason=f"Undeafen by {str(ctx.author)}")
        return await ctx.reply(embed=hacker)

    @vc.command(name="deafenalll",
                help="deafen all member in a voice channel .",
                usage="voice deafenall")
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _deafenall(self, ctx):
        if ctx.author.voice is None:
            error = discord.Embed(
                
                description=
                "You are not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.deaf == False:
                await member.edit(
                    deafen=True,
                    reason=
                    f"voice deafenall Command Executed by {str(ctx.author)}")
                count += 1
        hacker = discord.Embed(
                               description=f"Deafened {count} members in {ch}",
                               color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.reply(embed=hacker)

    @vc.command(name="undeafenalll",
                help="undeafen all member in a voice channel .",
                usage="voice undeafenall")
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _undeafall(self, ctx):
        if ctx.author.voice is None:
            error = discord.Embed(
                
                description=
                "You are not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        count = 0
        ch = ctx.author.voice.channel.mention
        for member in ctx.author.voice.channel.members:
            if member.voice.deaf == True:
                await member.edit(
                    deafen=False,
                    reason=
                    f"voice undeafenall Command Executed by {str(ctx.author)}")
                count += 1
        hacker = discord.Embed(
            
            description=f"Undeafened {count} members in {ch}",
            color=self.color)
        hacker.set_author(name=ctx.author,
                          icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.reply(embed=hacker)

    @vc.command(name="moveall",
                help="Moves all the members from the voice channel .",
                usage="voice moveall <voice channel>")
    @commands.has_guild_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _moveall(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.author.voice is None:
            error = discord.Embed(
                
                description=
                "You are not connected in any of the voice channel",
                color=self.color)
            error.set_author(name=ctx.author,
                             icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            error.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=error)
        try:
            ch = ctx.author.voice.channel.mention
            nch = channel.mention
            count = 0
            for member in ctx.author.voice.channel.members:
                await member.edit(
                    voice_channel=channel,
                    reason=
                    f"voice moveall Command Executed by {str(ctx.author)}")
                count += 1
            hacker = discord.Embed(
                
                description=f"{count} members moved from {ch} to {nch}",
                color=self.color)
            hacker.set_author(name=ctx.author,
                              icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            hacker.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=hacker)
        except:
            hacker1 = discord.Embed(
                
                description=f"Invalid voice channel provided",
                color=self.color)
            hacker1.set_author(name=ctx.author,
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            hacker1.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            await ctx.reply(embed=hacker1)
            
    @vc.command(name="pull",
                help="Pull a member from one voice channel to yours.",
                usage="voice pull <member>")
    @blacklist_check()
    @ignore_check()
    @commands.has_guild_permissions(move_members=True)
    #@commands.bot_has_permissions(move_members=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def _pull(self, ctx, member: discord.Member):
        if ctx.author.voice is None:
            embed = discord.Embed(

                description=
                "You are not connected to any voice channel.",
                color=self.color)
            embed.set_footer(text=f"Requested by: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=embed)
        if member.voice is None:
            embed = discord.Embed(

                description=
                f"{str(member)} is not connected to any voice channel.",
                color=self.color)
            embed.set_footer(text=f"Requested by: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=embed)
        if member.voice.channel == ctx.author.voice.channel:
            embed = discord.Embed(

                description=
                f"{str(member)} is already in your voice channel.",
                color=self.color)
            embed.set_footer(text=f"Requested by: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            return await ctx.reply(embed=embed)
        await member.edit(voice_channel=ctx.author.voice.channel,
                          reason=f"Pulled by {str(ctx.author)}")
        embed2 = discord.Embed(

            description=f"{str(member)} has been pulled to your voice channel.",
            color=self.color)
        embed2.set_footer(text=f"Requested by: {ctx.author}",
                               icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        return await ctx.reply(embed=embed2)
    
async def setup(client):
    await client.add_cog(Voice(client))