import discord, json
from discord.ext import commands
from utils.config import serverLink
from core import Cypher, Cog, Context
from utils.Tools import *
from utils.Tools import get_ignore_data


class Errors(Cog):
  def __init__(self, client:Cypher):
    self.client = client


  @commands.Cog.listener()
  async def on_command_error(self, ctx: Context, error):
    if ctx.command is None:
      return
    
    if isinstance(error, commands.MissingRequiredArgument):
      embed = discord.Embed()
      embed.set_author(name=f"{ctx.command.qualified_name.title()} Command",
                       icon_url=ctx.bot.user.display_avatar.url)
      embed.add_field(name="Command Usage:", value=f"<:MekoArrowRight:1449445989436887090> `{ctx.prefix}{ctx.command.signature}`")
      await ctx.send(embed=embed)
            
    if isinstance(error, commands.CommandNotFound):
      return

    if isinstance(error, commands.CheckFailure):
      data = await get_ignore_data(ctx.guild.id)
      ch = data["channel"]
      iuser = data["user"]
      cmd = data["command"]
      buser = data["bypassuser"]

      if str(ctx.author.id) in buser:
        return

      if str(ctx.channel.id) in ch:
            embed = discord.Embed()
            embed.description=f"<:MekoExclamation:1449445917500510229> Hey, {ctx.author.mention} This **channel** is on the **ignored** list. Please try my commands in another channel."
            await ctx.reply(embed=embed, delete_after=8)
            return

      if str(ctx.author.id) in iuser:
        embed = discord.Embed()
        embed.description=f"<:MekoExclamation:1449445917500510229> You are set as a ignored users for {ctx.guild.name} .\nTry my commands or modules in another guild ."
        await ctx.reply(embed=embed, delete_after=8)
        return

      if ctx.command.name in cmd or any(alias in cmd for alias in ctx.command.aliases):
            embed = discord.Embed()
            embed.description=f"<:MekoExclamation:1449445917500510229> You are set as a ignored users for {ctx.guild.name} .\nTry my commands or modules in another guild ."
            await ctx.reply(embed=embed, delete_after=8)
            return
      
            
    if isinstance(error, commands.NoPrivateMessage):
      hacker = discord.Embed(color=0x2f3136,description=f"You can't use my commands in Dms.")
      hacker.set_author(name=ctx.author,
                                       icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      hacker.set_thumbnail(url =ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=hacker,delete_after=20)
      return  
    if isinstance(error, commands.TooManyArguments):
      await ctx.send_help(ctx.command)
      ctx.command.reset_cooldown(ctx)
      return  
        
            
    if isinstance(error, commands.CommandOnCooldown):
      hacker = discord.Embed(color=0x2f3136,description=f"<:MekoExclamation:1449445917500510229> This command is on a cooldown. Please try again in `{error.retry_after:.2f}` seconds.")
      await ctx.reply(embed=hacker,delete_after=10)
      return  

    if isinstance(error, commands.MaxConcurrencyReached):
      hacker = discord.Embed(color=0x2f3136,description=f"<:MekoExclamation:1449445917500510229> Please use commands slowly, you are on cooldown.")
      await ctx.reply(embed=hacker,delete_after=10)
      ctx.command.reset_cooldown(ctx)
      return  

    if isinstance(error, commands.MissingPermissions):
      missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in error.missing_permissions
            ]
      if len(missing) > 2:
                fmt = "{}, and {}".format(", ".join(missing[:-1]), missing[-1])
      else:
                fmt = " and ".join(missing)
      hacker = discord.Embed(color=0x2f3136,description=f"<:MekoExclamation:1449445917500510229> You are lack of `{fmt}` permissions to run `{ctx.command.name}` command.")

      await ctx.reply(embed=hacker,delete_after=6)
      ctx.command.reset_cooldown(ctx)
      return  

    if isinstance(error, commands.BadArgument):
        embed = discord.Embed()
        embed.set_author(name=f"{ctx.command.qualified_name.title()} Command",
                       icon_url=ctx.bot.user.display_avatar.url)
        embed.add_field(name="Command Usage:", value=f"<:MekoArrowRight:1449445989436887090> `{ctx.prefix}{ctx.command} {ctx.command.signature}`")
        await ctx.reply(embed=embed,delete_after=5)
        
    if isinstance(error, commands.BotMissingPermissions):
        missing = ", ".join(error.missing_permissions)
        await ctx.reply(f'<:MekoExclamation:1449445917500510229> I need **{missing}** Permission to run the **{ctx.command.qualified_name}** command!', delete_after=7)
        return
      
    if isinstance(error, discord.HTTPException):
      print(f"HTTPException in {ctx.command}: {error}")
      return  
    elif isinstance(error, commands.CommandInvokeError):
      print(f"CommandInvokeError in {ctx.command}: {error.original}")
      import traceback
      traceback.print_exception(type(error.original), error.original, error.original.__traceback__)
      return  
    
async def setup(client):
    await client.add_cog(Errors(client))