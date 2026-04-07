import discord
from discord.ext import commands
from utils.Tools import *
from discord import ui

class UnmuteAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="unmuteall",
        help="Removes timeout (mute) from everyone in the server!",
        aliases=['masstimeoutremove', 'massunmute'],
        usage="Unmuteall",
        with_app_command=True
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @ignore_check()
    @blacklist_check()
    async def unmuteall(self, ctx):
        user_id = str(ctx.author.id)
        embed = discord.Embed(color=0x2f3135)

        button = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label="Yes",
            emoji="<a:H_TICK:1449446011490537603>"
        )
        button1 = discord.ui.Button(
            style=discord.ButtonStyle.red,
            label="No",
            emoji="<a:MekoCross:1449446075948859462>"
        )

        async def button_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                if interaction.guild.me.guild_permissions.moderate_members:
                    await interaction.response.edit_message(
                        content="Removing timeout from all muted users...",
                        embed=None,
                        view=None
                    )

                    a = 0
                    for member in interaction.guild.members:
                        if member.timed_out_until is not None:
                            try:
                                await member.timeout(None, reason=f"Requested by {ctx.author}")
                                a += 1
                            except Exception:
                                pass

                    await interaction.channel.send(f"Successfully removed timeout from {a} member(s)!")
                else:
                    await interaction.response.send_message(
                        "I am missing Moderate Members permission, try giving me permissions and use the command again.",
                        ephemeral=True
                    )

        async def button1_callback(interaction: discord.Interaction):
            if interaction.user == ctx.author:
                await interaction.response.edit_message(
                    content="Okay, I will not unmute anyone.",
                    embed=None,
                    view=None
                )

        embed = discord.Embed(
            color=0x2f3135,
            description="**Are you sure you want to remove timeout (mute) from everyone in this server?**"
        )

        view = discord.ui.View()
        button.callback = button_callback
        button1.callback = button1_callback
        view.add_item(button)
        view.add_item(button1)

        await ctx.reply(embed=embed, view=view, mention_author=False)

async def setup(bot):
    await bot.add_cog(UnmuteAll(bot))
