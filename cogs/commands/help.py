import discord
from discord.ext import commands
import discord
from discord.ext import commands

from typing import Optional
from discord.ui import *
from utils.Tools import *
from discord.ui import Button, View, Select

Invite = "<:flame_invite:1449451134220632074>"
Antinuke = "<:icon_security:1449451140918808576>"
Utility = "<:MekoSetting:1449451149043302663>"
Moderation = "<:MekoModeration:1449451155397673071>"
Raidmode = "<:MekoMod:1449446053345628297>"
Giveaway = "<:MekoGift:1449451126901440647>"
Welcomer = "<:MekoGreet:1449451161118572597>"
Logging = "<:MekoVoice:1449451168114938099>"
Voice = "<:MekoUnmute:1449451173802414101>"
Confess = "<:MekoHidden:1449451180894716005>"
Extra = "<:MekoSearch:1449446045712121978>"
Customroles = "<:MekoLogs:1449451187068862535>"
Music = "<:MekoStatusRole:1449451193083625474>"
Ignore = "<:MekoFastMessage:1449451205276340315>"
Fun = "<:MekoFun:1449451213312626901>"
Ai = "<:MekoTicket:1449451219151224853>"

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context,bot):
        super().__init__()
        self.ctx = ctx
        self.bot = bot
    async def interaction_check(self, interaction: discord.Interaction):

        if interaction.user.id != self.ctx.author.id:

            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)

            return False

        return True

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        
        options = [
            discord.SelectOption(emoji='<:icon_security:1449451140918808576>', label="AntiNuke"),
            discord.SelectOption(emoji='<:MekoSetting:1449451149043302663>', label="Utility"),
            discord.SelectOption(emoji='<:MekoFun:1449451213312626901>', label="Fun"),
            discord.SelectOption(emoji='<:icon_moderator:1449446295012905101>', label="Moderation"),
            discord.SelectOption(emoji='<:MekoMod:1449446053345628297>', label="Automod"),
            discord.SelectOption(emoji='<:MekoGreet:1449451161118572597>', label="Welcomer"),
            discord.SelectOption(emoji='<:MekoLogs:1449451187068862535>', label="Customroles"),
            discord.SelectOption(emoji='<:MekoHidden:1449451180894716005>', label="Confessions"),
            discord.SelectOption(emoji='<:MekoGift:1449451126901440647>', label="Giveaway"),
            discord.SelectOption(emoji='<:MekoStatusRole:1449451193083625474>', label="Music"),
            discord.SelectOption(emoji='<:MekoUnmute:1449451173802414101>', label="Voice"),
            discord.SelectOption(emoji='<:MekoFastMessage:1449451205276340315>', label="Ignore"),
            discord.SelectOption(emoji='<:MekoSearch:1449446045712121978>', label="Extra"),
            discord.SelectOption(emoji='<:MekoTicket:1449451219151224853>', label="Ticket"),
        ]
        super().__init__(placeholder="Choose wisely, shape your destiny.", min_values=1, max_values=1, options=options)
        
    async def callback(self, interaction: discord.Interaction):
        commands_list = {
            "AntiNuke": ["`antinuke enable`, `antinuke disable`, `antinuke show`, `antinuke events`, `antinuke recover`, `antinuke whitelist add <user>`, `antinuke whitelist remove <user>`, `antinuke whitelist reset`, `antinuke whitelist show`, `antinuke punishment set`, `antinuke punishment show`, `extraowner`, `extraowner add`, `extraowner remove`, `extraonwer show`"],
            "Utility": ["`afk` , `avatar` , `firstmessage`, `servericon` , `membercount`, `snipe` , `invite` , `serverinfo` , `userinfo` , `roleinfo` , `botinfo` ,  `boosts` , `ping`, `list boosters` , `list inrole` , `list emojis` , `list bots` , `list admins` , `list invoice` , `list mods` , `list roles` , `banner user` , `banner server`"],
            "Fun": ["`jailed`, `wanted`, `wasted`, `chess`, `connect4`, `ttt`, `rps`, `wordle`, `2048`, `ship`, `tickle` , `kiss` , `slap` , `feed` , `pet` , `howcute` , `howgay` , `slots` , `penis` , `sigma` , `pickupline`, `iplookup`"],
            "Moderation": ["`mute` , `unmute` , `unmuteall` , `kick` , `warn` , `ban` , `unban` , `nick` , `setprefix` , `clear` , `clear all` , `clear bots` , `clear embeds` , `clear files` , `clear mentions` , `clear images` , `clear contains` , `clear reactions` , `clear user` , `clear emoji` , `role`, `role humans`, `role bots`, `nuke` , `lock` , `unlock` , `hide` , `unhide` , `unbanall`, `hideall` , `unhideall`, `rolecolor` ,  `roleicon`, `steal` , `addsticker`"],
            "Automod": ["`automod` , `automod enable` , `automod disable` , `automod punishment` , `automod config` , `automod logging` , `automod ignore` , `automod ignore channel` , `automod ignore role` , `automod ignore show` , `automod ignore reset` , `automod unignore` , `automod unignore channel` , `automod unignore role`"],
            "Welcomer": ["`autorole`, `greet setup` , `greet reset`, `greet channel` , `greet edit` , `greet test` , `greet config` , `greet autodelete` , `greet`"],
            "Customroles": ["`setup` , `setup create <name>` , `setup delete <name>`  , `setup list` , `setup staff` , `setup girl` , `setup friend` , `setup vip` , `setup guest` , `setup reqrole`, `setup config` , `setup reset` , `staff` , `girl` , `friend` , `vip` , `guest`"],
            "Confessions": ["`/confess` , `confessions enable <#channel>` , `confessions disable` , `confessions mute <@user>` , `confessions unmute <@user>`"],
            "Giveaway": ["`gstart`, `gend`, `greroll`"],
            "Music": ["`play`, `pause`, `resume`, `stop`, `queue`, `volume`, `skip`, `join`, `leave`, `loop`, `nowplaying`, `seek`, `enchance`, `forcefix`, `toggle`, `toggle source`, `toggle volume`,\n\n**Filters**\n`filter`, `filter tremolo enable/disable`, `filter rotation enable/disable`, `filter nightcore enable/disable`, `filter channelmix enable/disable`, `filter lofi enable/disable`, `filter slowmo enable/disable`, `filter 8d enable/disable`, `filter vibrato enable/disable`, `filter bassboost enable/disable`, `filter lowpass enable/disable`, `filter distortion enable/disable`, `filter timescale enable/disable`, `filter karaoke enable/disable`"],
            "Voice": ["`tts`, `vcinvite`, `vcrequest`, `voice` , `voice kick` , `voice kickall` , `voice mute` , `voice muteall` , `voice unmute` , `voice unmuteall` , `voice deafen` , `voice deafenall` , `voice undeafen` , `voice undeafenall` , `voice moveall` , `vc pull` , `vcrole add` , `vcrole remove` , `vcrole config`"],
            "Ignore": ["`ignore` , `ignore channel add` , `ignore channel remove` , `ignore channel show` , `ignore user add` , `ignore user remove` , `ignore user show` , `ignore bypass add` , `ignore bypass show` , `ignore bypass remove`"],
            "Extra": ["`autoreact`, `setchatbot`, `resetchatbot`, `vcban` , `vcban add <user|role>` , `vcban remove <user|role>` , `vcban clear` , `vcban config`, `chatban`, `chatban add <user|role>`, `chatban remove <user|role>`, `chatban config`, `reactban`, `reactban add <user|role>`, `reactban remove <user|role>`, `reactban config`, `top guild`, `top users`, `profile`\n\n**__Logging__**\n`chatban log set <#channel>`, `chatban log remove <#channel>`, `reactban log set <#channel>`, `reactban log remove <#channel>`"
                     ],
            "Ticket": ["`ticket` , `ticket setup`, `ticket reset`, `ticket info`, `ticket reopen`, `ticket rename`"],
        }
        
        cog_name = self.values[0]
        selected_option = next((opt for opt in self.options if opt.label == cog_name), None)
        emoji = selected_option.emoji if selected_option else ""
        c = [f"{cmd}" for cmd in commands_list.get(cog_name, [])]
        embed = discord.Embed(description=", ".join(c) if c else "No commands found.", color=0x2f3136)
        embed.title=f"{emoji} {cog_name} Menu"
        await interaction.response.edit_message(embed=embed, view=BackView(self.ctx, self.bot, original_embed=self.view.original_embed))

class BackButton(discord.ui.Button):
    def __init__(self, original_embed):
        super().__init__(label="Back", style=discord.ButtonStyle.primary)
        self.original_embed = original_embed

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.original_embed, view=HelpView(self.view.ctx, self.view.bot, original_embed=self.original_embed))

class BackView(BasicView):
    def __init__(self, ctx, bot, original_embed):
        super().__init__(ctx, bot)
        self.bot = bot
        self.ctx = ctx
        self.original_embed = original_embed
        self.add_item(BackButton(original_embed))

class HelpView(BasicView):
    def __init__(self, ctx, bot, original_embed=None):
        super().__init__(ctx, bot)
        self.bot = bot
        self.ctx = ctx
        self.original_embed = original_embed
        self.add_item(HelpDropdown(bot, ctx))
        self.add_item(discord.ui.Button(label="Invite me", url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&&permissions=8&scope=bot"))
        self.add_item(discord.ui.Button(label="Support Server", url=f"https://discord.gg/UtZ3rRnBnU"))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Get Help with the bot's commands or modules")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @ignore_check()
    @blacklist_check()
    async def help(self, ctx: commands.Context, command: Optional[str]):
            data = await getConfig(ctx.guild.id)
            prefix = data["prefix"]
        
            em = discord.Embed(description=f"<:20_pink_heart:1449451227128660070> Prefix For This Server `{prefix}`\n<:MekoBlueRightArrow:1449451233239765196> Total Commands `{len(set(ctx.bot.walk_commands()))}`\n<:MekoLeveling:1449451239724027964> Choose A Specific Module Of Your Own Desire")
            em.add_field(
                name="<:MekoCategory:1449446249341259850> __Modules__",
                value=f"""{Antinuke} `:` AntiNuke\n{Utility} `:` Utility\n{Fun} `:` Fun\n{Moderation} `:` Moderation\n{Raidmode} `:` Automod\n{Welcomer} `:` Welcomer\n{Customroles} `:` Customroles\n{Confess} `:` Confessions\n{Giveaway} `:` Giveaway\n{Music} `:` Music\n{Voice} `:` Voice\n{Ignore} `:` Ignore\n{Extra} `:` Extra\n{Ai} `:` Ticket\n\n<:MekoInvite:1449451444754190380> __**Links**__\n[Invite](https://discordapp.com/oauth2/authorize?client_id=1417399852031148085&scope=bot+applications.commands&permissions=8) | [Support Server](https://discord.gg/UtZ3rRnBnU)""",
                inline=False)
            em.set_author(name="Help Menu", icon_url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else ctx.bot.user.default_avatar.url)
            em.set_thumbnail(url=self.bot.user.avatar)
            page = HelpView(ctx,self.bot, original_embed=em)
            await ctx.send(embed=em,view=page)
          
async def setup(client):
    client.remove_command("help")
    await client.add_cog(Help(client))