from utils import getConfig  
import discord
from discord.ext import commands
from utils.Tools import get_ignore_data
import aiosqlite
import wavelink
import datetime
import platform
import sys
import logging
from core import Cypher
import psutil
import asyncio

start_time = datetime.datetime.now()

def get_uptime():
    now = datetime.datetime.now()
    uptime = now - start_time
    days, seconds = uptime.days, uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days} day, {hours}:{minutes}:{seconds}"

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;197m[\x1b[0m%(asctime)s\x1b[38;5;197m]\x1b[0m -> \x1b[38;5;197m%(message)s\x1b[0m",
    datefmt="%H:%M:%S",
)

block_db = None

async def initialize_block_db():
    """Initialize the block.db connection."""
    global block_db
    if block_db is None:
        block_db = await aiosqlite.connect('database/block.db')
        await block_db.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
        await block_db.commit()

async def close_block_db():
    """Close the block.db connection."""
    global block_db
    if block_db:
        await block_db.close()
        block_db = None

class MenuView(discord.ui.View):
    def __init__(self, author, bot):
        super().__init__(timeout=30)
        self.author = author
        self.client = bot
        self.value = None
        
    @discord.ui.button(label="System Info", style=discord.ButtonStyle.success)
    async def system_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        try:
            if interaction.user.id != self.author.id:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please ping the bot first then you can access this button"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            ram_info = psutil.virtual_memory()
            total_ram_gb = ram_info.total / (1024 ** 3)  # Convert total RAM from bytes to GB without decimals
            used_ram_mb = ram_info.used / (170 **3)
            disk_info = psutil.disk_usage('/')
            uptime = get_uptime()
            total_users = sum(guild.member_count for guild in self.client.guilds)
            total_guilds = len(self.client.guilds)
            cpu_percent = psutil.cpu_percent(interval=1)
            python_version = sys.version.split()[0]
            cpu_total_cores = psutil.cpu_count(logical=True)
            ram_used = ram_info.used / (1024 ** 3)
            latency = self.client.latency * 1000
            using_storage_mb = disk_info.used / (450 ** 3)
            os_name = platform.system()
            disk_usage = psutil.disk_usage('/')
            
            
            embed = discord.Embed(colour=0x2b2d31, description=f"**<:1181899559853621419:1449446128733913331> Uptime: {uptime}**\n**<:ExoticUser:1449446145146486845> Users: {total_users}**\n**<:ExoticGuild:1449446159490748426> Guilds: {total_guilds}**\n**<:MekoApplication:1449446166269001882> Shards: {interaction.guild.shard_id+1}/{len(self.client.shards.items())}**\n**<:ExoticPing:1449446173659234415> Latency: {latency:.3f}ms**\n**<:ExoticCPU:1449446180688756787> Total Load: {cpu_percent}%**\n**<:MekoUtility:1449446187362160650> Storage: {using_storage_mb:.2f} MB / 2.00 GB ({disk_usage.percent}%)**\n<:ExoticRam:1449446194500599858> **Ram Info: {used_ram_mb:.2f} MB / 9.98 GB**\n**<:ExoticPython:1449446201362481354> Python: {python_version}**\n**<:ExoticCores:1449446209348571208> Cores: {cpu_total_cores}**\n**<:wl_dark:1449446216781009006> Music Wrapper: Lavalink.Py 5.9.0**\n**<:ExoticOS:1449446225001578710> Os: {os_name}**")
            embed.set_author(name="Some Informations About Me", icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text="Thanks for choosing Samaksh Core", icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    @discord.ui.button(label="Developer Info", style=discord.ButtonStyle.success)
    async def developer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.author.id:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please ping the bot first then you can access this button"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            dev1 = interaction.guild.get_member(1263792569981341819)
            dev2 = interaction.guild.get_member(1264585642780790814)
            dev3 = interaction.guild.get_member(1162455661041434787)
            
            status_emojis = {
                discord.Status.online: "<:online:1449451100691496991>",
                discord.Status.idle: "<:idle:1449451113660284969>",
                discord.Status.dnd: "<:dnd:1449451120987734228>",
                discord.Status.offline: "<:offline:1449451107049799784>",
            }
            
            if dev1:
                dev1_activity = dev1.activities[0].name if dev1.activities else "Offline"
                dev1_status = f"{status_emojis.get(dev1.status, '⚪')} {dev1.status}" if dev1 else "Unknown"
            else:
                dev1_activity = "No activity."
                dev1_status = "<:offline:1449451107049799784> Offline"
                
            if dev2:
                dev2_activity = dev2.activities[0].name if dev2.activities else "No activity"
                dev2_status = f"{status_emojis.get(dev2.status, '⚪')} {dev2.status}" if dev2 else "Unknown"
            
            else:
                dev2_activity = "No activity."
                dev2_status = "<:offline:1449451107049799784> Offline"
                
            if dev3:
                dev3_activity = dev3.activities[0].name if dev3.activities else "No activity"
                dev3_status = f"{status_emojis.get(dev3.status, '⚪')} {dev3.status}" if dev3 else "Unknown"
            
            else:
                dev3_activity = "No activity."
                dev3_status = "<:offline:1449451107049799784> Offline"
            
            embed = discord.Embed(colour=0x2b2d31, description=f"<:MekoArrowRight:1449445989436887090> Below Is The Information Regarding The Bot's Owner, Developer, And Team Members.\n\n<:MekoDeveloper:1449451029358710896> **Owner & Developers**\n`1.` [`DarkNighT`](https://discordapp.com/users/919147106684510249)\n**<:icon_status:1449451424709611712> Status :** {dev1_status}\n**<:MekoActivity:1449451431751979058> Activity :** {dev1_activity}\n\n`2.` [`Hecronn`](https://discordapp.com/users/919175804829708308)\n**<:icon_status:1449451424709611712> Status :** {dev2_status}\n**<:MekoActivity:1449451431751979058> Activity :** {dev2_activity}\n\n`3.` [`fugitive`](https://discordapp.com/users/1295700461663289419)\n**<:icon_status:1449451424709611712> Status :** {dev3_status}\n**<:MekoActivity:1449451431751979058> Activity :** {dev3_activity}\n\n\n**<a:MekoLove:1449446084131819601>Credits**\n`1.` [`iyad`](https://discordapp.com/users/1041381818273906799) & [`Console`](https://discordapp.com/users/687482572703662108) **[** Emoji Credits **]**\n`2.` [`Glaxin`](https://discordapp.com/users/620569922870837253) **[** Web Developer **]**\n`3.` [`None`](https://discordapp.com/users/) **[** Contributors **]**")
            embed.set_author(name="Some Informations About My Devs", icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text="Thanks for choosing Samaksh Core", icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    @discord.ui.button(label="Useful Links", style=discord.ButtonStyle.success)
    async def links_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.author.id:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please ping the bot first then you can access this button"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(colour=0x2b2d31)
            embed.description="<:Team:1449451439100399878> [**Support Server**](https://discord.gg/UtZ3rRnBnU)\nFeel free to click on the `Support Server` link and join our community for any assistance you may need.\n\n<:MekoInvite:1449451444754190380> [**Bot Invite**](https://discordapp.com/oauth2/authorize?client_id=1417399852031148085&scope=bot+applications.commands&permissions=8)\nClick on the `Bot Invite` button to invite the Cypher bot to any of your servers.\n\n<:MekoTopgg:1449446097071116440> [**Vote on top.gg**](https://top.gg/bot/1191399940014997584/vote)\nClick on the `Vote On Top.gg` option and kindly cast your valuable vote for the incredible Cypher."
            embed.set_author(name="Some Useful Links", icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text="Cypher Information", icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
           
    @discord.ui.button(emoji="<:MekoHome:1449451451771523284>", style=discord.ButtonStyle.danger)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            
            if interaction.user.id != self.author.id:
                embed = discord.Embed()
                embed.description = f"<:MekoExclamation:1449445917500510229> I'm sorry, **{interaction.user.name}**, you cannot access this button.\n<:MekoArrowRight:1449445989436887090> Please ping the bot first then you can access this button"
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            guild_id = interaction.guild.id
            data = await getConfig(guild_id) 
            prefix = data["prefix"]
            embed = discord.Embed(colour=0x2b2d31)
            embed.description=f"<a:MekoLove:1449446084131819601> Hey {interaction.user.mention},\n<:MekoPrefix:1449451039441944717> Prefix For This Server is `{prefix}`\n\nType `{prefix}help` for more information."
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed.set_thumbnail(url=interaction.user.avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

class antipinginv(commands.Cog):
    def __init__(self, client: Cypher):
        self.bot = client
        self.spam_control = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)

    async def is_blacklisted(self, message):
        try:
            await initialize_block_db()  # Ensure the database connection is initialized
            async with block_db.execute("SELECT 1 FROM guild_blacklist WHERE guild_id = ?", (message.guild.id,)) as cursor:
                if await cursor.fetchone():
                    return True
                    
            async with block_db.execute("SELECT 1 FROM user_blacklist WHERE user_id = ?", (message.author.id,)) as cursor:
                if await cursor.fetchone():
                    return True

            return False
        except aiosqlite.OperationalError as e:
            if "database is locked" in str(e):
                await asyncio.sleep(1)
                return await self.is_blacklisted(message)  # Retry after a delay
            else:
                raise

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        if await self.is_blacklisted(message):
            return

        ignore_data = await get_ignore_data(message.guild.id)
        if str(message.author.id) in ignore_data["user"] or str(message.channel.id) in ignore_data["channel"]:
            return

        if message.reference and message.reference.resolved:
            if isinstance(message.reference.resolved, discord.Message):
                if message.reference.resolved.author.id == self.bot.user.id:
                    return

        guild_id = message.guild.id
        data = await getConfig(guild_id) 
        prefix = data["prefix"]

        if self.bot.user in message.mentions:
            if len(message.content.strip().split()) == 1:
                view = MenuView(message.author, self.bot)
                embed = discord.Embed(
                        description=(
                            f"<a:MekoLove:1449446084131819601> Hey {message.author.mention},\n"
                            f"<:MekoPrefix:1449451039441944717> Prefix For This Server is `{prefix}`\n\n"
                            f"Type `{prefix}help` for more information."
                        )
                    )
                embed.set_author(name=message.guild.name, icon_url=message.guild.icon.url if message.guild.icon else None)
                embed.set_thumbnail(url=message.author.avatar.url)
                await message.reply(embed=embed, view=view, mention_author=False)
                
async def setup(client):
    await client.add_cog(antipinginv(client))