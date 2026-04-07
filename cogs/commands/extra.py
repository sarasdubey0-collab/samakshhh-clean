import os 
import discord
from discord.ext import commands
import datetime
import sys
from discord.ui import Button, View
import psutil
import time
import wavelink
from discord.ext import commands, tasks
from utils.Tools import *
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown
import requests
from typing import *
import platform
import random
from utils import *
from utils.config import BotName, serverLink
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from core import Cog, Cypher, Context
from io import BytesIO
from typing import Optional

async def increment_command_usage(guild_id: int, user_id: int):
    async with aiosqlite.connect("database/top.db") as db:
        await db.execute("""
            INSERT INTO command_usage (guild_id, user_id, commands_used)
            VALUES (?, ?, 1)
            ON CONFLICT(guild_id, user_id)
            DO UPDATE SET commands_used = commands_used + 1
        """, (guild_id, user_id))
        await db.commit()
        
async def get_command_usage(user_id: int):
    async with aiosqlite.connect("database/top.db") as db:
        async with db.execute("SELECT SUM(commands_used) FROM command_usage WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row and row[0] else 0
  # Default to 0 if no data exists
        
class VoteView(discord.ui.View):
    def __init__(self, support_url):
        super().__init__()
        self.add_item(discord.ui.Button(
            emoji=f"<:dbl:1449446090712551474>",
            label="Vote on DBL",
            url="https://discord.ly/cypher-2733",
            style=discord.ButtonStyle.link
        ))
        self.add_item(discord.ui.Button(
            emoji=f"<:MekoTopgg:1449446097071116440>",
            label="Vote on Top.GG",
            url="https://top.gg/bot/1191399940014997584/vote",
            style=discord.ButtonStyle.link
        ))

        
class InviteView(discord.ui.View):
    def __init__(self, bot_id):
        super().__init__()
        # Invite button
        self.add_item(discord.ui.Button(
            emoji=f"<:MekoAdd:1449446103945580584>",
            label=f"Invite Me!",
            url=f"https://discord.com/oauth2/authorize?client_id={bot_id}&permissions=8&scope=bot%20applications.commands",
            style=discord.ButtonStyle.link
        ))
        
class SupportView(discord.ui.View):
    def __init__(self, support_url):
        super().__init__()
        self.add_item(discord.ui.Button(
            emoji=f"<:Support:1449446111696654388>",
            label="Support Me!",
            url=support_url,
            style=discord.ButtonStyle.link
        ))
        
        
start_time = time.time()
rix_time = datetime.datetime.now()
dark_time = datetime.datetime.now()

def get_uptime():
    now = datetime.datetime.now()
    uptime = now - dark_time
    days, seconds = uptime.days, uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days} days, {hours} hour, {minutes} minutes and {seconds} seconds"

def get_rix():
    now = datetime.datetime.now()
    uptime = now - rix_time
    days, seconds = uptime.days, uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days} day, {hours}:{minutes}:{seconds}"


def datetime_to_seconds(thing: datetime.datetime):
  current_time = datetime.datetime.fromtimestamp(time.time())
  return round(
    round(time.time()) +
    (current_time - thing.replace(tzinfo=None)).total_seconds())

tick = "<a:H_TICK:1449446011490537603>"
cross = "<a:MekoCross:1449446075948859462>"

class Extra(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.color = 0x2f3136
    self.support_url = "https://discord.gg/UtZ3rRnBnU"
 
  @commands.group(name="banner")
  async def banner(self, ctx):
    if ctx.invoked_subcommand is None:
      embed = discord.Embed()
      embed.title = "Banner Subcommands:"
      embed.description = "`banner user`, `banner server`"
      await ctx.send(embed=embed)

  @banner.command(name="server")
  async def server(self, ctx):
    if not ctx.guild.banner:
      await ctx.reply(f"{cross} This server does not have a banner.")
    else:
      webp = ctx.guild.banner.replace(format='webp')
      jpg = ctx.guild.banner.replace(format='jpg')
      png = ctx.guild.banner.replace(format='png')
      embed = discord.Embed(
        color=self.color,
        description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
        if not ctx.guild.banner.is_animated() else
        f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
      )
      embed.set_image(url=ctx.guild.banner)
      embed.set_author(name=ctx.guild.name,
                       icon_url=ctx.guild.icon.url
                       if ctx.guild.icon else ctx.guild.default_icon.url)
      embed.set_footer(text=f"Requested By {ctx.author}",
                       icon_url=ctx.author.avatar.url
                       if ctx.author.avatar else ctx.author.default_avatar.url)
      await ctx.reply(embed=embed)

  @blacklist_check()
  @ignore_check()
  @banner.command(name="user")
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  async def _user(self,
                  ctx,
                  member: Optional[Union[discord.Member,
                                         discord.User]] = None):
    if member == None or member == "":
      member = ctx.author
    bannerUser = await self.bot.fetch_user(member.id)
    if not bannerUser.banner:
      await ctx.reply("{}  {} doesn't have any banner.".format(cross, member))
    else:
      webp = bannerUser.banner.replace(format='webp')
      jpg = bannerUser.banner.replace(format='jpg')
      png = bannerUser.banner.replace(format='png')
      embed = discord.Embed(
        color=self.color,
        description=f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
        if not bannerUser.banner.is_animated() else
        f"[`PNG`]({png}) | [`JPG`]({jpg}) | [`WEBP`]({webp})"
      )
      embed.set_author(name=f"{member}",
                       icon_url=member.avatar.url
                       if member.avatar else member.default_avatar.url)
      embed.set_image(url=bannerUser.banner)
      embed.set_footer(text=f"Requested By {ctx.author}",
                       icon_url=ctx.author.avatar.url
                       if ctx.author.avatar else ctx.author.default_avatar.url)

      await ctx.send(embed=embed)

  @commands.command(name="invite", aliases=['inv'])
  @blacklist_check()
  @ignore_check()
  async def invite(self, ctx: commands.Context):
    embed = discord.Embed(
      description=
      f"Heads Up! You Can Invite Me To Your Server By Clicking The Button Below.\nWe hope you enjoy using our bot.",
      color=discord.Color.red())
    embed.title = "Invite Me To Your Server"
    embed.set_thumbnail(url=self.bot.user.avatar.url)
    embed.set_footer(text=f"Have A Nice Day.", icon_url=self.bot.user.avatar.url)
    view = InviteView(self.bot.user.id)
    await ctx.send(embed=embed, view=view)
    
  @commands.command(name="support", aliases=['supp'])
  @blacklist_check()
  @ignore_check()
  async def support(self, ctx: commands.Context):
    embed = discord.Embed(color=discord.Color.red())
    embed.set_author(name=f"Here is Some Useful Links of Cypher!",
                     icon_url=self.bot.user.avatar.url)
    view = SupportView(self.support_url)
    await ctx.send(embed=embed, view=view)
    
    
  @commands.command(name="vote")
  @blacklist_check()
  @ignore_check()
  async def vote(self, ctx: commands.Context):
    embed = discord.Embed(color=discord.Color.red())
    embed.set_author(name=f"Consider Voting me",
                     icon_url=self.bot.user.avatar.url)
    embed.description = f"<:upvote:1449446119733198921> {ctx.author.mention}: [DBL](https://discord.ly/https://discord.ly/cypher-2733)/[Top.gg](https://top.gg/bot/1191399940014997584/vote) vote from the button below!"
    view = VoteView(self.support_url)
    await ctx.send(embed=embed, view=view)
    

  

    

  @blacklist_check()
  @ignore_check()
  @commands.command(name="botinfo",
                           aliases=['bi', 'stats'],
                           help="Get info about me!",
                           with_app_command=True)
  async def botinfo(self, ctx: commands.Context):
        ram_info = psutil.virtual_memory()
        total_ram_gb = ram_info.total / (1024 ** 3)  # Convert total RAM from bytes to GB without decimals
        used_ram_mb = ram_info.used / (170 **3)
        disk_info = psutil.disk_usage('/')
        uptime = get_rix()
        channel = len(set(self.bot.get_all_channels()))
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_guilds = len(self.bot.guilds)
        cpu_percent = psutil.cpu_percent()
        python_version = sys.version.split()[0]
        cpu_total_cores = psutil.cpu_count(logical=True)
        latency = self.bot.latency * 1000
        using_storage_mb = disk_info.used / (450 ** 3)
        os_name = platform.system()
        disk_usage = psutil.disk_usage('/')
        
        embed = discord.Embed(colour=0x2b2d31, description=f"**<:1181899559853621419:1449446128733913331> Uptime: {uptime}**\n**<:ExoticUser:1449446145146486845> Users: {total_users}**\n**<:MekoChannel:1449446152108904509> Channels: {channel}**\n**<:ExoticGuild:1449446159490748426> Guilds: {total_guilds}**\n**<:MekoApplication:1449446166269001882> Shards: {ctx.guild.shard_id+1}/{len(self.bot.shards.items())}**\n**<:ExoticPing:1449446173659234415> Latency: {latency:.3f}ms**\n**<:ExoticCPU:1449446180688756787> Total Load: {cpu_percent}%**\n**<:MekoUtility:1449446187362160650> Storage: {using_storage_mb:.2f} MB / 2.00 GB ({disk_usage.percent}%)**\n<:ExoticRam:1449446194500599858> **Ram Info: {used_ram_mb:.2f} MB / 9.98 GB**\n**<:ExoticPython:1449446201362481354> Python: {python_version}**\n**<:ExoticCores:1449446209348571208> Cores: {cpu_total_cores}**\n**<:wl_dark:1449446216781009006> Music Wrapper: Lavalink.Py 5.9.0**\n**<:ExoticOS:1449446225001578710> Os: {os_name}**")
        embed.set_author(name="Some Informations About Me", icon_url=ctx.author.avatar.url)
        embed.set_footer(text="Thanks for choosing Samaksh Core", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

  @commands.command(name="uptime",
                    description="Shows you Cypher Uptime.")
  @blacklist_check()
  @ignore_check()
  async def uptime(self, ctx):
        pfp = ctx.author.display_avatar.url
        
        #uptime = str(uptime).split('.')[0]
        embed = discord.Embed(title=f"{BotName}'s Uptime", description=f"```{str(datetime.timedelta(seconds=int(round(time.time()-start_time))))}```",
                              color=self.color)
        embed.set_footer(text=f"Requested by {ctx.author}" ,  icon_url=pfp)
        await ctx.send(embed=embed)
    
    
  @commands.command(name="serverinfo",
                           aliases=["sinfo", "si"],
                           with_app_command=True)
  @blacklist_check() 
  @ignore_check()
  async def serverinfo(self, ctx: commands.Context):
    c_at = int(ctx.guild.created_at.timestamp())
    nsfw_level = ''
    if ctx.guild.nsfw_level.name == 'default':
      nsfw_level = 'Default'
    if ctx.guild.nsfw_level.name == 'explicit':
      nsfw_level = 'Explicit'
    if ctx.guild.nsfw_level.name == 'safe':
      nsfw_level = 'Safe'
    if ctx.guild.nsfw_level.name == 'age_restricted':
      nsfw_level = 'Age Restricted'

    guild: discord.Guild = ctx.guild
    t_emojis = len(guild.emojis)
    t_stickers = len(guild.stickers)
    total_emojis = t_emojis + t_stickers

    embed = discord.Embed(color=self.color).set_author(
      name=f"{guild.name}'s Information",
      icon_url=guild.me.display_avatar.url
      if guild.icon is None else guild.icon.url).set_footer(
        text=f"Requested By {ctx.author}",
        icon_url=ctx.author.avatar.url
        if ctx.author.avatar else ctx.author.default_avatar.url)
    if guild.icon is not None:
      embed.set_thumbnail(url=guild.icon.url)
      embed.timestamp = discord.utils.utcnow()

    for r in ctx.guild.roles:
      if len(ctx.guild.roles) < 1:
        roless = "None"
      else:
        if len(ctx.guild.roles) < 50:
          roless = " • ".join(
            [role.mention for role in ctx.guild.roles[1:][::-1]])
        else:
          if len(ctx.guild.roles) > 50:
            roless = "Too many roles to show here."
    embed.add_field(
      name="<:MekoServer:1449446233935450244> **__About Server__**",
      value=
      f"> Server Name :  {guild.name}\n> Server ID : {guild.id}\n> Server Owner : {guild.owner} (<@{guild.owner_id}>)\n> Created :  <t:{c_at}:F>\n> Members Count : {len(guild.members)}",
      inline=False)

    embed.add_field(
      name="<:MekoUtility:1449446187362160650> **__Server Settings__**",
      value=
      f"""> Verification Level : {str(guild.verification_level).title()}\n> Inactive Channel : {ctx.guild.afk_channel}\n> Inactive Timeout : {str(ctx.guild.afk_timeout / 60)}\n> System Channel : {"None" if guild.system_channel is None else guild.system_channel.mention}\n> NSFW level : {nsfw_level}\n> Explicit Content Filter : {guild.explicit_content_filter.name}\n> Max Talk Bitrate : {int(guild.bitrate_limit)} kbps""",
      inline=False)

    embed.add_field(name="<:MekoNewLines:1449446241535656052> **__Description__**",
                    value=f"""> {guild.description}""",
                    inline=False)
    if guild.features:
      ftrs = ("\n").join([f" {'> <a:H_TICK:1449446011490537603>'+' : '+feature.replace('_',' ').title()}" for feature in guild.features])

      embed.add_field(

        name="<:MekoRuby:1449445982931783710> **__Server Features__**",

        value=ftrs[:1024]
      )
      

    embed.add_field(name="<:MekoMember:1449446061541167175> **__Total Members__**",
                    value=f"""
> Members : {len(guild.members)}
> Humans : {len(list(filter(lambda m: not m.bot, guild.members)))}
> Bots : {len(list(filter(lambda m: m.bot, guild.members)))}
            """,
                    inline=False)
    tchl = 0
    tchh = 0
    tvcl = 0
    tvch = 0
    #hhh
    for channel1 in ctx.guild.channels:
    
        if channel1 in ctx.guild.text_channels:
            overwrite = channel1.overwrites_for(ctx.guild.default_role)
            if overwrite.send_messages == False:
                tchl += 1
            if overwrite.view_channel == False:
                tchh += 1
        if channel1 in ctx.guild.voice_channels:
            overwrite = channel1.overwrites_for(ctx.guild.default_role)
            if overwrite.connect == False:
                tvcl += 1
            if overwrite.view_channel:
                tvch += 1
    #tchl1 = tchl
            
    #for vc1 in
    embed.add_field(name="<:MekoCategory:1449446249341259850> **__Channels__**",
                    value=f"""
> Categories : {len(guild.categories)}
> Text Channels : {len(guild.text_channels)} (Locked: {tchl}, Hidden: {tchh})
> Voice Channels : {len(guild.voice_channels)} (Locked: {tvcl}, Hidden: {tvch})
> Threads : {len(guild.threads)}
            """,
                    inline=False)

    embed.add_field(name="<:Sticker:1449446257218289734> **__Emojis & Stickers Info__**",
                    value=f"""
> Static Emojis : {t_emojis}
> Stickers : {t_stickers}
> Total Emoji/Stickers : {total_emojis}
             """,
                    inline=False)

    embed.add_field(
      name="<:MekoBoost:1449446264734355476> **__Boost Status__**",
      value=
      f"> Level : {guild.premium_tier}  [ {guild.premium_subscription_count} Boosts ]\n> Booster Role : {guild.premium_subscriber_role.mention if guild.premium_subscriber_role else 'None'}",
      inline=False)
    
    total_roles = len(ctx.guild.roles)
    normal_roles = [role for role in ctx.guild.roles if role.name != '@everyone' and not any(member.bot for member in role.members)]
    integrated_roles = [role for role in ctx.guild.roles if any(member.bot for member in role.members)]
    
    embed.add_field(name=f"<:Meko_Role:1449446272544280616>**__Server Roles__**",
                    value=f"> Total Roles : {total_roles}\n"
                          f"> Normal Roles : {len(normal_roles)}\n"
                          f"> Integrated Roles : {len(integrated_roles)}", 
                    inline=False)

    if guild.banner is not None:
        embed.set_image(url=guild.banner.url)
    return await ctx.reply(embed=embed)

  @blacklist_check()
  @ignore_check()
  @commands.command(name="userinfo",
                           aliases=["whois", "ui"],
                           usage="Userinfo [user]",
                           with_app_command=True)
  @commands.cooldown(1, 2, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  async def _userinfo(self,
                      ctx,
                      member: Optional[Union[discord.Member,
                                             discord.User]] = None):
    if member == None or member == "":
      member = ctx.author
    elif member not in ctx.guild.members:
      member = await self.bot.fetch_user(member.id)

    badges = ""
    if member.public_flags.hypesquad:
      badges += "HypeSquad Events "
    if member.public_flags.hypesquad_balance:
      badges += "HypeSquad Balance "
    if member.public_flags.hypesquad_bravery:
      badges += "HypeSquad Bravery "
    if member.public_flags.hypesquad_brilliance:
      badges += "HypeSquad Brilliance "
    if member.public_flags.early_supporter:
      badges += "Early Supporter "
    if member.public_flags.active_developer:
      badges += "Active Developer "
    if member.public_flags.verified_bot_developer:
      badges += "Early Verified Bot Developer "
    if member.public_flags.discord_certified_moderator:
      badges += "Moderators Program Alumni "
    if member.public_flags.staff:
      badges += "Discord Staff "
    if member.public_flags.partner:
      badges += "Partnered Server Owner "
    if badges == None or badges == "":
      badges += f"{cross}"

    if member in ctx.guild.members:
        nickk = f"{member.nick if member.nick else 'None'}"
        joinedat = f"<t:{round(member.joined_at.timestamp())}:R>"
    else:
        nickk = "None"
        joinedat = "`Not Joined`"

    kp = ""
    if member in ctx.guild.members:
      if member.guild_permissions.create_instant_invite:
        kp += "`Create Instant Invite`"
      if member.guild_permissions.kick_members:
        kp += ", `Kick Members`"
      if member.guild_permissions.ban_members:
        kp += ", `Ban Members`"
      if member.guild_permissions.administrator:
        kp += ", `Administrator`"
      if member.guild_permissions.manage_channels:
        kp += ", `Manage Channels`"
      if member.guild_permissions.manage_guild:
        kp += ", `Manage Guild`"
      if member.guild_permissions.add_reactions:
        kp += ", `Add Reactions`"
      if member.guild_permissions.view_audit_log:
        kp += ", `View Audit Log`"
      if member.guild_permissions.priority_speaker:
        kp += ", `Priority Speaker`"
      if member.guild_permissions.stream:
        kp += ", `Stream`"
      if member.guild_permissions.view_channel:
        kp += ", `View Channel`"
      if member.guild_permissions.send_messages:
        kp += ", `Send Messages`"
      if member.guild_permissions.send_tts_messages:
        kp += ", `Send TTS Messages`"
      if member.guild_permissions.manage_messages:
        kp += ", `Manage Messages`"
      if member.guild_permissions.embed_links:
        kp += ", `Embed Links`"
      if member.guild_permissions.attach_files:
        kp += ", `Attach Files`"
      if member.guild_permissions.read_message_history:
        kp += ", `Read Message History`"
      if member.guild_permissions.mention_everyone:
        kp += ", `Mention Everyone`"
      if member.guild_permissions.use_external_emojis:
        kp += ", `Use External Emojis`"
      if member.guild_permissions.view_guild_insights:
        kp += ", `View Guild Insights`"
      if member.guild_permissions.connect:
        kp += ", `Connect`"
      if member.guild_permissions.speak:
        kp += ", `Speak`"
      if member.guild_permissions.mute_members:
        kp += ", `Mute Members`"
      if member.guild_permissions.deafen_members:
        kp += ", `Deafen Members`"
      if member.guild_permissions.move_members:
        kp += ", `Move Members`"
      if member.guild_permissions.use_voice_activation:
        kp += ", `Use Voice Activity`"
      if member.guild_permissions.change_nickname:
        kp += ", `Change Nickname`"
      if member.guild_permissions.manage_nicknames:
        kp += ", `Manage Nicknames`"
      if member.guild_permissions.manage_roles:
        kp += ", `Manage Roles`"
      if member.guild_permissions.manage_webhooks:
        kp += ", `Manage Webhooks`"
      if member.guild_permissions.manage_emojis:
        kp += ", `Manage Emojis`"
      if member.guild_permissions.use_application_commands:
        kp += ", `Use Slash Commands`"
      if member.guild_permissions.request_to_speak:
        kp += ", `Request to Speak`"
      if member.guild_permissions.manage_events:
        kp += ", `Manage Events`"
      if member.guild_permissions.manage_threads:
        kp += ", `Manage Threads`"
      if member.guild_permissions.create_public_threads:
        kp += ", `Create Public Threads`"
      if member.guild_permissions.create_private_threads:
        kp += ", `Create Private Threads`"
      if member.guild_permissions.use_external_stickers:
        kp += ", `Use External Stickers`"
      if member.guild_permissions.send_messages_in_threads:
        kp += ", `Send Messages in Threads`"
      if member.guild_permissions.use_embedded_activities:
        kp += ", `Use Embedded Activities`"
      if member.guild_permissions.moderate_members:
        kp += ", `Moderate Members`"

      if kp is None or kp == "":
        kp = "None"

    if member in ctx.guild.members:
      if member == ctx.guild.owner:
        aklm = "<:MekoOwner:1449446280303743176> Server Owner"
      elif member.guild_permissions.administrator:
        aklm = "<:MekoAdmin:1449446287740239966> Server Admin"
      elif member.guild_permissions.ban_members or member.guild_permissions.kick_members:
        aklm = "<:icon_moderator:1449446295012905101> Server Moderator"
      else:
        aklm = "<:MekoUser:1449446018163806270> Server Member"

    bannerUser = await self.bot.fetch_user(member.id)
    embed = discord.Embed(color=self.color)
    embed.timestamp = discord.utils.utcnow()
    if not bannerUser.banner:
      pass
    else:
      embed.set_image(url=bannerUser.banner)
    embed.set_author(name=f"{member.name}'s Information",
                     icon_url=member.avatar.url
                     if member.avatar else member.default_avatar.url)
    embed.set_thumbnail(
      url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="<:MekoMember:1449446061541167175> __About__",
                    value=f"""
> Default Name : {member}
> ID : {member.id}
> Global Name : {member.global_name}
> Bot? : {'<a:H_TICK:1449446011490537603>' if member.bot else '<a:MekoCross:1449446075948859462>'}
> Badges : {badges}
> Account Created : <t:{round(member.created_at.timestamp())}:R>
> Server Joined : {joinedat}
            """,
                    inline=False)
    if member in ctx.guild.members:
      r = (', '.join(role.mention for role in member.roles[1:][::-1])
           if len(member.roles) > 1 else 'None.')
      embed.add_field(name="<:Meko_Role:1449446272544280616> __User Roles Info__",
                      value=f"""
> Highest Role : {member.top_role.mention if len(member.roles) > 1 else 'None'}
> All Roles [{f'{len(member.roles) - 1}' if member.roles else '0'}] : {r if len(r) <= 1024 else r[0:1006] + ' and more...'}
> Hex Colour : {member.color if member.color else '000000'}
                """,
                      inline=False)
    if member in ctx.guild.members:
      embed.add_field(
        name="<:MekoRuby:1449445982931783710> __Extra__",
        value=
        f"> Boosting : {f'<t:{round(member.premium_since.timestamp())}:R>' if member in ctx.guild.premium_subscribers else 'None'}\n> Voice : {'None' if not member.voice else member.voice.channel.mention}",
        inline=False)
    if member in ctx.guild.members:
      embed.add_field(name="<:MekoKey:1449446302977884221> __Key Permissions__",
                      value=", ".join([kp]),
                      inline=False)
    if member in ctx.guild.members:
      embed.add_field(name="<:MekoSearch:1449446045712121978> __Acknowledgement__",
                      value=f"{aklm}",
                      inline=False)
    if member in ctx.guild.members:
      embed.set_footer(text=f"Requested by {ctx.author}",
                       icon_url=ctx.author.avatar.url
                       if ctx.author.avatar else ctx.author.default_avatar.url)
    else:
      if member not in ctx.guild.members:
        embed.set_footer(text=f"{member.name} not in this this server.",
                         icon_url=ctx.author.avatar.url if ctx.author.avatar
                         else ctx.author.default_avatar.url)
    await ctx.send(embed=embed)

  @commands.command(name="roleinfo",
                           help="Shows you all information about a role.",
                           usage="Roleinfo <role>",
                           with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def roleinfo(self, ctx: commands.Context, *, role: discord.Role):
    """Get information about a role"""
    content = discord.Embed()
    content.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
  
    content.colour = role.color
    
    if role.icon:
        content.set_thumbnail(url=role.icon.url)
    
    description = ""
  
    description += (
        f"<:MekoRoleYellow:1449446314038394882>**Name :** {role.name}\n"
        f"<:MekoPing:1449446025206173807>**Mention :** {role.mention}\n"
        f"<:id:1449446321223110797>**ID :** {role.id}\n"
        f"<:MekoTimer:1449451368392953998>**Created at :** {role.created_at.strftime('%d/%m/%Y %H:%M')}\n"
        f"<:MekoEmoji:1449446336129929390>**Hex Color :** {str(role.color).upper()}\n"
        f"<:MekoType:1449446344216281118>**Mentionable :** {role.mentionable}\n"
        f"<:MekoRuby:1449445982931783710>**Hoisted :** {str(role.hoist)}\n"
        f"<:MekoMember:1449446061541167175>**Members :** {len(role.members)}"
    )

    if role.managed:
      if role.tags.is_bot_managed():
        manager = ctx.guild.get_member(role.tags.bot_id)
      elif role.tags.is_integration():
        manager = ctx.guild.get_member(role.tags.integration_id)
      elif role.tags.is_premium_subscriber():
        manager = "Server boosting"
      else:
        manager = "UNKNOWN"
        
        description += f"\n**Managed by :** {manager}"


    perms = []
    for perm, allow in iter(role.permissions):
      if allow:
        perms.append(f"`{perm.upper()}`")

    if perms:
      description += f"\n\n<:MekoKey:1449446302977884221>**Allowed permissions :** {' '.join(perms)}"
    
    content.description = description

    await ctx.send(embed=content)




  @commands.command(name="boostcount",
                    help="Shows boosts count",
                    usage="boosts",
                    aliases=["bc", "boosts"],
                    with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def boosts(self, ctx):
        boost_count = ctx.guild.premium_subscription_count
        boost_tier = ctx.guild.premium_tier
        
        embed=discord.Embed(color=self.color)
        
        if boost_tier > 0:
            embed.set_author(
                name=f"The Server Boost Level Is {ctx.guild.premium_tier} with {ctx.guild.premium_subscription_count} Boosts",
                icon_url=ctx.guild.icon.url if ctx.guild.icon else None
            )
        else:
            embed.set_author(
                name=f"The Server Has {ctx.guild.premium_subscription_count} Boosts",
                icon_url=ctx.guild.icon.url if ctx.guild.icon else None
            )
        await ctx.send(embed=embed)

  @commands.group(name="list",
                         invoke_without_command=True,
                         with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def __list_(self, ctx: commands.Context):
        try:
            embed = discord.Embed(
                title="List Commands",
                description=""
            )
            if hasattr(ctx.command,'commands'):
                commands_list = ", ".join([f"`{ctx.prefix}{ctx.command.name} {command.name}`" for command in ctx.command.commands])
                embed.add_field(name="", value=f"> {commands_list}" or "No subcommands available.", inline=False)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{e}")

  @__list_.command(name="boosters",
                   aliases=["boost", "booster"],
                   usage="List boosters",
                   help="Get a list of all boosters of the server.",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def list_boost(self, ctx):
    guild = ctx.guild
    entries = [
      f"`{index:02}` [{mem.display_name}](https://discord.com/users/{mem.id}) ({mem.mention})\n> **Boosted :** <t:{round(mem.premium_since.timestamp())}:R>"
      for index, mem in enumerate(guild.premium_subscribers, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      description="",
      author=f"List Of Boosters - {len(guild.premium_subscribers)}",
      author_icon=guild.icon.url if guild.icon else None,
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="bans", aliases=["ban"],
help="Get a list of all banned users from the server.",                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def list_ban(self, ctx):
    bans = [ban_entry async for ban_entry in ctx.guild.bans()]
    if not bans:
      return await ctx.reply("There are no banned users here.", mention_author=False)
    else:
      hackers = ([
      member async for member in ctx.guild.bans()
    ])
      guild = ctx.guild
      entries = [
      f"`{index:02}.` [{ban_entry.user.display_name}](https://discord.com/users/{ban_entry.user.id}) ({ban_entry.user.mention})"
      for index, ban_entry in enumerate(bans, start=1)
    ]
      paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      description="",
      author=f"List of Banned Users - {len(bans)}",
      author_icon=guild.icon.url if guild.icon else None,
      per_page=10),
                          ctx=ctx)
      await paginator.paginate()
    
  @__list_.command(
    name="inrole",
    aliases=["inside-role"],
    help="Get a list of members in a specific role.",
    with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def list_inrole(self, ctx, role: discord.Role):
    guild = ctx.guild
    entries = [
      f"`{index:02}.` [{mem.display_name}](https://discord.com/users/{mem.id}) ({mem.mention})"
      for index, mem in enumerate(role.members, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      description="",
      author=f"List of Users With {role}",
      author_icon=guild.icon.url if guild.icon else None,
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="emojis",
                   aliases=["emoji"],
                   help="Get a list of all the emojis of the server",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def list_emojis(self, ctx):
    guild = ctx.guild
    entries = [
      f"`{index:02}.` {e} - `{e}`"
      for index, e in enumerate(ctx.guild.emojis, start=1)
    ]
    
    total_emojis = len(ctx.guild.emojis)
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      description="",
      author=f"List Of Emojis - {total_emojis}",
      author_icon=guild.icon.url if guild.icon else None,
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="roles",
                   aliases=["role"],
                   help="Get a list of all the roles of the server.",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def list_roles(self, ctx):
    guild = ctx.guild
    entries = [
      f"`{index:02}.` {e.mention} - `[{e.id}]`"
      for index, e in enumerate(ctx.guild.roles, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      author=f"List Of Roles - {len(ctx.guild.roles)}",
      author_icon=guild.icon.url if guild.icon else None,
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="bots",
                   aliases=["bot"],
                   help="Get a list of all bots of the server.",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def list_bots(self, ctx):
    guild = ctx.guild
    people = filter(lambda member: member.bot, ctx.guild.members)
    people = sorted(people, key=lambda member: member.joined_at)
    entries = [
      f"`{index:02}.` [{mem.display_name}](https://discord.com/users/{mem.id}) ({mem.mention})"
      for index, mem in enumerate(people, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      author=f"List Of Server Bots - {len(people)}",
      author_icon=guild.icon.url if guild.icon else None,
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="admins",
                   aliases=["admin"],
                   help="Get a list of all admins of the server.",
                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def list_admin(self, ctx):
    hackers = ([
      hacker for hacker in ctx.guild.members
      if hacker.guild_permissions.administrator
    ])
    #hackers = filter(lambda hacker: not hacker.bot)
    hackers = sorted(hackers, key=lambda hacker: not hacker.bot)
    admins = len([
      hacker for hacker in ctx.guild.members
      if hacker.guild_permissions.administrator
    ])
    guild = ctx.guild
    entries = [
      f"`{index:02}.` [{mem.display_name}](https://discord.com/users/{mem.id}) ({mem.mention})"
      for index, mem in enumerate(hackers, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      author=f"List Of Admins - {admins}",
      author_icon=guild.icon.url if guild.icon else None,
      description="",
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="invoice", aliases=["invc"],
help="Get a list of all members who are connected to any voice channel in your server.",                   with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def listusers(self, ctx):
    if not ctx.author.voice:
      return await ctx.send("You are not connected to a voice channel")
    members = ctx.author.voice.channel.members
    entries = [
      f"`{index:02}.` [{member.display_name}](https://discord.com/users/{member.id}) ({member.mention})"
      for index, member in enumerate(members, start=1)
    ]
    guild = ctx.guild
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      description="",
      author=f"List Of Users in {ctx.author.voice.channel.name}",
      author_icon=guild.icon.url if guild.icon else None,
      color=self.color),
                          ctx=ctx)
    await paginator.paginate()

  @__list_.command(name="moderators", aliases=["mods"],
help="Get a list of all the moderators of the server.",                  with_app_command=True)
  @blacklist_check()
  @ignore_check()
  async def list_mod(self, ctx):
    hackers = ([
      hacker for hacker in ctx.guild.members
      if hacker.guild_permissions.ban_members
      or hacker.guild_permissions.kick_members
    ])
    hackers = filter(lambda member: member.bot, ctx.guild.members)
    hackers = sorted(hackers, key=lambda hacker: hacker.joined_at)
    admins = len([
      hacker for hacker in ctx.guild.members
      if hacker.guild_permissions.ban_members
      or hacker.guild_permissions.kick_members
    ])
    guild = ctx.guild
    entries = [
      f"`{no:02}.` [{mem.display_name}](https://discord.com/users/{mem.id}) ({mem.mention})"
      for no, mem in enumerate(hackers, start=1)
    ]
    paginator = Paginator(source=DescriptionEmbedPaginator(
      entries=entries,
      title=f"Mods in {guild.name} - {admins}",
      description="",
      author=f"List Of Mods - {admins}",
      author_icon=guild.icon.url if guild.icon else None,
      per_page=10),
                          ctx=ctx)
    await paginator.paginate()

  @commands.command(name="unbanall",
                           help="Unbans Everyone In The Guild!",
                           aliases=['massunban'],
                           usage="Unbanall",
                           with_app_command=True)
  @blacklist_check()
  @ignore_check()
  @commands.cooldown(1, 30, commands.BucketType.user)
  @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
  @commands.guild_only()
  @commands.has_permissions(ban_members=True)
  async def unbanall(self, ctx):
    button = Button(label="Yes",
                    style=discord.ButtonStyle.green,
                    emoji="<a:H_TICK:1449446011490537603>")
    button1 = Button(label="No",
                     style=discord.ButtonStyle.red,
                     emoji="<a:MekoCross:1449446075948859462>")

    async def button_callback(interaction: discord.Interaction):
      a = 0
      if interaction.user == ctx.author:
        if interaction.guild.me.guild_permissions.ban_members:
          await interaction.response.edit_message(
            content="Unbanning All Banned Member(s)", embed=None, view=None)
          async for idk in interaction.guild.bans(limit=None):
            await interaction.guild.unban(
              user=idk.user,
              reason="Unbanall Command Executed By: {}".format(ctx.author))
            a += 1
          await interaction.channel.send(
            content=f"Successfully Unbanned {a} Member(s)")
        else:
          await interaction.response.edit_message(
            content=
            "I am missing ban members permission.\nTry giving me permissions and retry",
            embed=None,
            view=None)
      else:
        embed = discord.Embed()
        embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
        await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

    async def button1_callback(interaction: discord.Interaction):
      if interaction.user == ctx.author:
        await interaction.response.edit_message(
          content="Okay, i am not unbanning anyone.", embed=None, view=None)
      else:
        embed = discord.Embed()
        embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please use the bot command first then you can access this button"
        await interaction.response.send_message(embed=embed, view=None, ephemeral=True)

    embed = discord.Embed(
      color=self.color,
      description='**Are you sure you want to unban everyone in this guild?**')

    view = View()
    button.callback = button_callback
    button1.callback = button1_callback
    view.add_item(button)
    view.add_item(button1)
    await ctx.reply(embed=embed, view=view, mention_author=False)








  @commands.command(name="ping",
                           aliases=["latency"],
                           usage="Checks the bot latency .",
                           with_app_command=True)
  @commands.cooldown(1, 2, commands.BucketType.user)
  @ignore_check()
  @blacklist_check()
  async def ping(self, ctx):
    s_id = ctx.guild.shard_id
    sh = self.bot.get_shard(s_id)
    start_time = time.perf_counter()
    end_time = time.perf_counter()
    response_time = round((end_time - start_time) * 10000000, 3)
    latency = self.bot.latency * 1000
    shard_id = ctx.guild.shard_id if ctx.guild else 0
    shard_latency = round(self.bot.latencies[shard_id][1] * 1000, 3)
    uptime = get_uptime()
    users = sum(g.member_count for g in self.bot.guilds
                if g.member_count != None)
    db_latency = None
    try:
      async with aiosqlite.connect("afk_data.db") as db:
        start_time = time.perf_counter()
        await db.execute("SELECT 1")
        end_time = time.perf_counter()
        db_latency = (end_time - start_time) * 1000
        db_latency = round(db_latency, 2)
    except Exception as e:
      print(f"Error measuring database latency: {e}")
      db_latency = "N/A"
        
    embed = discord.Embed(
      color=self.color)
    embed.set_author(
        name=f"Bot Latency",
        icon_url=ctx.author.display_avatar.url)
    embed.description = f"**Latency Details**\n> API Latency : `{latency:.3f}ms`\n> Database Latency : `{db_latency}ms`\n> Response Time : `{response_time:.3f}`\n\n**Shard Details**\n> Latency : `{shard_latency:.3f}ms`\n> Status : `Online`\n> Ratelimited : `No`\n> Uptime : `{uptime}`\n> Servers : `{len(self.bot.guilds)}`\n> Members : `{users}`"
 
    await ctx.reply(embed=embed)
        
        
  @commands.hybrid_command(name="badges",
                           help="Check what premium badges a user have.",
                           aliases=["badge", "profile", "pr"],
                           usage="Badges [user]",
                           with_app_command=True)
  @commands.cooldown(1, 10, commands.BucketType.user)
  @blacklist_check()
  @ignore_check()
  async def _badges(self, ctx, user: Optional[discord.User] = None):
    mem = user or ctx.author
    sup = self.bot.get_guild(1301490367945904189)
    hacker = discord.utils.get(sup.members, id=mem.id)
    ##########
    dev = discord.utils.get(sup.roles, id=1301494729212559382)
    #law = discord.utils.get(sup.roles, id=1100263159006240788)
    chief = discord.utils.get(sup.roles, id=1301494725559451741)
    visor = discord.utils.get(sup.roles, id=1301494723982397500)    
    sdent = discord.utils.get(sup.roles, id=1301494718236065862)
    #mod = discord.utils.get(sup.roles, id=1100263155977957446)
    sup1 = discord.utils.get(sup.roles, id=1301494706454401096)
    premium = discord.utils.get(sup.roles, id=1329777273557225532)
    comp = discord.utils.get(sup.roles, id=1122157596036583564)
    promo = discord.utils.get(sup.roles, id=1122157597500395604)
    pillar = discord.utils.get(sup.roles, id=1122157598519599155)
    blesser = discord.utils.get(sup.roles, id=1301494701907771413)
    loved = discord.utils.get(sup.roles, id=1301494704084619324)
    bugo = discord.utils.get(sup.roles, id=1122157623123398696)
    pals = discord.utils.get(sup.roles, id=1122157615045165126)
    member = discord.utils.get(sup.roles, id=1301494698581561395)
###################
    badges = ""
    if mem.public_flags.hypesquad:
      badges += "Hypesquad\n"
    elif mem.public_flags.hypesquad_balance:
      badges += "<:balance:1449446350931366040> *HypeSquad Balance*\n"

    elif mem.public_flags.hypesquad_bravery:
      badges += "<:HYPERSQUADBRAVERY:1449451004306128946> *HypeSquad Bravery*\n"
    elif mem.public_flags.hypesquad_brilliance:
      badges += "<:Brilance:1449451010069102732> *Hypesquad Brilliance*\n"
    if mem.public_flags.early_supporter:
      badges += "<:earlysupporter:1449451015492337674> *Early Supporter*\n"
    elif mem.public_flags.verified_bot_developer:
      badges += "<:developer:1449451019711938871> *Verified Bot Developer*\n"
    elif mem.public_flags.active_developer:
      badges += "<:active_dev:1449451024288055578> *Active Developer*\n"
    if badges == "":
      badges = "None"
   #####################
       
##########
    bdg = ""
    if hacker in sup.members: 
      if dev in hacker.roles:
        bdg += "\n<:MekoDeveloper:1449451029358710896> Developer"
      if chief in hacker.roles:
        bdg += "\n<:MekoOwner:1449446280303743176> Owner"
      if visor in hacker.roles:
        bdg += "\n<:MekoEmoji:1449446336129929390> Founder"
        
      if sdent in hacker.roles:
        bdg += "\n<:MekoRoleYellow:1449446314038394882> Manager"
      if sup1 in hacker.roles:
        bdg += "\n<:MekoAdmin:1449446287740239966> Admin"

      if pillar in hacker.roles:
        bdg += "\n<:oxytech_pillar:1449451034908037202> Mod"   
      if premium in hacker.roles:
        bdg += "\n<:MekoPrefix:1449451039441944717> No Prefix"
      if comp in hacker.roles:
        bdg += "\n<:OxyTech_partner:1449451044273786934> *Companion*"
      if promo in hacker.roles:
        bdg += "\n<:OxyTech_verified:1449451049889824901> *Promoter*"

      if bugo in hacker.roles:
        bdg += "\n<:OxyTech_bug:1449451054553894913> *Bugo Logist*"
        
      if blesser in hacker.roles:
        bdg += "\n<:NexusStarboard:1449451060459475067> Friend"
        
      if loved in hacker.roles:
        bdg += "\n<a:MekoLove:1449446084131819601> Cypher's Special"

      if pals in hacker.roles:
        bdg += "\n<:OxyTech_developers:1449451066641875148> *Pals*"
      if member in hacker.roles:
        bdg += "\n<:MekoUser:1449446018163806270> Bot User"      
        
        
      command_count = await get_command_usage(mem.id)

    
      embed2 = discord.Embed(color=self.color)
      #embed2.add_field(name="User Badges",
                     #  value=f"{badges}",
                     #  inline=False)
      embed2.add_field(name="<:MekoReddot:1449451072803573910> List Of Badges", value=f"\u200b{bdg}", inline=False)
      embed2.add_field(name="\u200b\n<:MekoType:1449446344216281118> Commands Used", value=f"```{command_count}```", inline=False)
      embed2.add_field(
        name="",
        value=(
          f"\u200b\nIn Order To Receive Your Badges, You Must Be Present In Our Support Server. "
          f"To Join The Support Server Click [**Here**](https://discord.gg/UtZ3rRnBnU)."
          ),
        inline=False)
      embed2.set_author(
        name=f"Profile For {mem.display_name}",
        icon_url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
      embed2.set_thumbnail(
        url=mem.avatar.url if mem.avatar else mem.default_avatar.url)
      await ctx.reply(embed=embed2, mention_author=False)
    
    else:
      if bdg == "":

        embed = discord.Embed(color=self.color)
        
        embed.add_field(
          name="",
          value="```diff\n- This User Doesn't Have Any Badges Yet!\n```",
          inline=False
          )
        embed.add_field(
          name="",
          value=(
            f"In Order To Receive Your Badges, You Must Be Present In Our Support Server. "
            f"To Join The Support Server Click [Here](https://discord.gg/UtZ3rRnBnU)."
            ),
          inline=False
          )
        
        embed.set_author(
          name=f"Profile For {mem.display_name}",
          icon_url=mem.avatar.url if mem.avatar else mem.default_avatar.url)
        embed.set_thumbnail(
          url=mem.avatar.url if mem.avatar else mem.default_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)
        
async def setup(client):
    await client.add_cog(Extra(client))