import discord
from discord.ext import commands
import lavalink
from lavalink.filters import (
    LowPass, Karaoke, Timescale, Tremolo, Vibrato, Rotation, Distortion, ChannelMix
)


class Filters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x2F3136  


    @commands.hybrid_group(invoke_without_command=True)
    async def filter(self, ctx):
        try:
            embed = discord.Embed(
                title="Filter Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")
            
    @filter.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lowpass(self, ctx, action: str):
        """Enable/disable lowpass filter."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(LowPass(smoothing=20.0))
            embed = discord.Embed(description=f"`LowPass` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("lowPass")
            embed = discord.Embed(description=f"`LowPass` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")

    @filter.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def karaoke(self, ctx, action: str):
        """Enable/disable karaoke filter."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Karaoke(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0))
            embed = discord.Embed(description=f"`Karaoke` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("karaoke")
            embed = discord.Embed(description=f"`Karaoke` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")

    @filter.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def timescale(self, ctx, action: str):
        """Enable/disable timescale filter."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Timescale(speed=1.1, pitch=1.0, rate=1.0))
            embed = discord.Embed(description=f"`Timescale` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("timescale")
            embed = discord.Embed(description=f"`Timescale` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")

    @filter.command()
    async def tremolo(self, ctx, action: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Tremolo(frequency=2.0, depth=0.5))
            embed = discord.Embed(description=f"`Tremolo` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("tremolo")
            embed = discord.Embed(description=f"`Tremolo` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")

    @filter.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vibrato(self, ctx, action: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Vibrato(frequency=2.0, depth=0.5))
            embed = discord.Embed(description=f"`Vibrato` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("vibrato")
            embed = discord.Embed(description=f"`Vibrato` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")

    @filter.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rotation(self, ctx, action: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Rotation(rotation_hz=5.0))
            embed = discord.Embed(description=f"`Rotation` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("rotation")
            embed = discord.Embed(description=f"`Rotation` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")

    @filter.command()
    async def distortion(self, ctx, action: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Distortion(
                sin_offset=0.0, sin_scale=1.0,
                cos_offset=0.0, cos_scale=1.0,
                tan_offset=0.0, tan_scale=1.0,
                offset=0.0, scale=1.0
            ))
            embed = discord.Embed(description=f"`Distortion` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("distortion")
            embed = discord.Embed(description=f"`Distortion` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")

    @filter.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def channelmix(self, ctx, action: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(ChannelMix(
                left_to_left=1.0, left_to_right=0.0,
                right_to_left=0.0, right_to_right=1.0
            ))
            embed = discord.Embed(description=f"`ChannelMix` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("channelMix")
            embed = discord.Embed(description=f"`ChannelMix` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed , delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")
            
    @filter.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bassboost(self, ctx, action: str):
        """Enable/disable bassboost filter."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            # Emulate bass boost by modifying channel mix and low pass
            await player.set_filter(
                ChannelMix(left_to_left=1.25, left_to_right=0.0,
                           right_to_left=0.0, right_to_right=1.25)
            )
            await player.set_filter(LowPass(smoothing=10.0))
            embed = discord.Embed(description=f"`BassBoost` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("channelMix")
            await player.remove_filter("lowPass")
            embed = discord.Embed(description=f"`BassBoost` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed , delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")
            
    @filter.command(name="8d")
    async def _8d(self, ctx, action: str):
        """Enable/disable 8D filter."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Rotation(rotation_hz=0.2))
            embed = discord.Embed(description=f"`8d` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("rotation")
            embed = discord.Embed(description=f"`8d` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")
            
    @filter.command()
    async def lofi(self, ctx, action: str):
        """Enable/disable lofi filter."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(LowPass(smoothing=25.0))
            await player.set_filter(Timescale(speed=0.9, pitch=0.8, rate=1.0))
            embed = discord.Embed(description=f"`Lofi` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("lowPass")
            await player.remove_filter("timescale")
            embed = discord.Embed(description=f"`Lofi` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")
            
    @filter.command()
    async def slowmo(self, ctx, action: str):
        """Enable/disable slow motion filter."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Timescale(speed=0.5, pitch=0.8, rate=0.8))
            embed = discord.Embed(description=f"`SlowMo` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("timescale")
            embed = discord.Embed(description=f"`SlowMo` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")
            
    @filter.command()
    async def nightcore(self, ctx, action: str):
        """Enable/disable nightcore filter."""
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if action.lower() == "enable":
            await player.set_filter(Timescale(speed=1.2, pitch=1.2, rate=1.0))
            embed = discord.Embed(description=f"`NightCore` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
            await ctx.send(embed=embed, delete_after=5)
        elif action.lower() == "disable":
            await player.remove_filter("timescale")
            embed = discord.Embed(description=f"`NightCore` **filter has been removed!**\n**( It takes 5 second to disable filter.)**", color=self.color)
            await ctx.send(embed=embed ,delete_after=5)
        else:
            await ctx.send("Invalid action. Use `enable` or `disable`.")


async def setup(bot):
    await bot.add_cog(Filters(bot))