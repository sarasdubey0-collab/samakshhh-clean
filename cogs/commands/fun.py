import discord
import requests
import aiohttp
import datetime
import random
from discord.ext import commands
from random import randint
from utils.Tools import *
from core import Cog, Cypher, Context
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from pathlib import Path
import json

PICKUP_LINES = json.loads(Path("database/pikup.json").read_text("utf8"))

        
def RandomColor():
    randcolor = discord.Color(random.randint(0x0d0d13, 0xFFFFFF))
    return randcolor


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def add_role(self, *, role: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=int(role))
            await member.add_roles(role, reason="Cypher Role Added ")

    async def remove_role(self, *, role: int, member: discord.Member):
        if member.guild.me.guild_permissions.manage_roles:
            role = discord.Object(id=int(role))
            await member.remove_roles(role, reason="Cypher Role Removed")

    @blacklist_check()
    @ignore_check()
    @commands.command(name="tickle",
                      help="Tickle mentioned user .",
                      usage="Tickle <member>")
    async def tickle(self, ctx, user: discord.Member = None):
         if user is None:
            embed = discord.Embed()
            embed.description = "<:MekoExclamation:1449445917500510229> Mention a user to use this command."
            await ctx.send (embed=embed)
         else:
            r = requests.get("https://nekos.life/api/v2/img/tickle")
            res = r.json()
            embed = discord.Embed(
                timestamp=datetime.datetime.utcnow(),
                description=f"{ctx.author.mention} tickle {user.mention}",
                color=0x00FFCA)
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)
            
    @commands.hybrid_command(name="wanted")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def wanted(self, ctx, user: discord.Member = None):
        user_id = str(ctx.author.id)
        if user is None:
            user = ctx.author

        wanted = Image.open("download.jpg")
        asset = user.display_avatar.replace(size=128)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((100, 100))
        wanted.paste(pfp, (45, 75))
        
        wanted_fp = BytesIO()
        wanted.save(wanted_fp, format='JPEG')
        wanted_fp.seek(0)

        embed = discord.Embed(color=0xFFFFFF)
        embed.set_author(name=f"{str(user)} Wanted", icon_url=user.avatar.url)
        embed.set_image(url="attachment://profile.jpg")

        await ctx.send(embed=embed, file=discord.File(fp=wanted_fp, filename='profile.jpg'))
            
    @commands.hybrid_command()
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def jailed(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_id = str(ctx.author.id)
        avatar_url = member.display_avatar.url
        response = requests.get(avatar_url)
        avatar_img = Image.open(BytesIO(response.content)).convert("RGBA")

        jail_bars = Image.open('jail_bars.png').convert("RGBA")
        jail_bars = jail_bars.resize(avatar_img.size, Image.LANCZOS)

        jailed_avatar = Image.alpha_composite(avatar_img, jail_bars)

        jail_av = BytesIO()
        jailed_avatar.save(jail_av, format='PNG')
        jail_av.seek(0)

        embed = discord.Embed(color=0xFFFFFF)
        embed.set_author(name=f"{str(member)} Jailed", icon_url=member.avatar.url)
        embed.set_image(url="attachment://jailed_avatar.png")

        await ctx.send(embed=embed, file=discord.File(fp=jail_av, filename='jailed_avatar.png'))
        
    @commands.command()
    @ignore_check()
    @blacklist_check()
    async def wasted(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.display_avatar.url
        response = requests.get(avatar_url)
        avatar = Image.open(BytesIO(response.content)).convert("RGB")
        avatar = ImageOps.grayscale(avatar).convert("RGBA").resize((500, 500))
        final_img = Image.new("RGBA", (500, 500))
        final_img.paste(avatar, (0, 0))
        try:
            font = ImageFont.truetype("Pricedown.otf", 90)
        except IOError:
            return
        draw = ImageDraw.Draw(final_img)
        text = "WASTED"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        text_x, text_y = (500 - text_width) // 2, (500 - text_height) // 2
        draw.text((text_x, text_y), text, font=font, fill=(255, 0, 0, 255))
        img_bytes = BytesIO()
        final_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        file = discord.File(img_bytes, filename="wasted.png")
        embed = discord.Embed(title=f"{member.display_name} got wasted!", color=discord.Color.red())
        embed.set_image(url="attachment://wasted.png")
        await ctx.send(embed=embed, file=file)

    @blacklist_check()
    @ignore_check()
    @commands.command(name="kiss",
                      help="Kiss mentioned user .",
                      usage="Kiss <member>")
    async def kiss(self, ctx, user: discord.Member = None):
         if user is None:
            embed = discord.Embed()
            embed.description = "<:MekoExclamation:1449445917500510229> Mention a user to use this command."
            await ctx.send (embed=embed)
         else:
            r = requests.get("https://nekos.life/api/v2/img/kiss")
            res = r.json()
            embed = discord.Embed(
                timestamp=datetime.datetime.utcnow(),
                description=f"{ctx.author.mention} kisses {user.mention}",
                color=0x00FFCA)
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)
            
    @commands.hybrid_command(
        name="8ball",
        description="Ask any question to the bot.",
    )
    async def eight_ball(self, context: Context, *, question: str) -> None:
        """
        Ask any question to the bot.

        :param context: The hybrid command context.
        :param question: The question that should be asked by the user.
        """
        answers = [
            "It is certain.",
            "It is decidedly so.",
            "You may rely on it.",
            "Without a doubt.",
            "Yes - definitely.",
            "As I see, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again later.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        
        await context.send(f"{random.choice(answers)}")
        
    @commands.command(name="slap",
                      help="Slap mentioned user .",
                      usage="Slap <member>")
    @blacklist_check()
    @ignore_check()
    async def slap(self, ctx, user: discord.Member = None):
         if user is None:
            embed = discord.Embed()
            embed.description = "<:MekoExclamation:1449445917500510229> Mention a user to use this command."
            await ctx.send (embed=embed)
         else:
            r = requests.get("https://nekos.life/api/v2/img/slap")
            res = r.json()
            embed = discord.Embed(
                timestamp=datetime.datetime.utcnow(),
                color=0x00FFCA,
                description=f"{ctx.author.mention} slapped {user.mention}",
            )
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)

    @commands.command(name="feed",
                      help="Feed mentioned user .",
                      usage="Feed <member>")
    @blacklist_check()
    @ignore_check()
    async def feed(self, ctx, user: discord.Member = None):
         if user is None:
            embed = discord.Embed()
            embed.description = "<:MekoExclamation:1449445917500510229> Mention a user to use this command."
            await ctx.send (embed=embed)
         else:
            r = requests.get("https://nekos.life/api/v2/img/feed")
            res = r.json()
            embed = discord.Embed(
                timestamp=datetime.datetime.utcnow(),
                description=f"{ctx.author.mention} feeds {user.mention}",
                color=0x00FFCA)
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)

    @commands.command(name="pet", usage="Pet <member>")
    @blacklist_check()
    @ignore_check()
    async def pet(self, ctx, user: discord.Member = None):
         if user is None:
            embed = discord.Embed()
            embed.description = "<:MekoExclamation:1449445917500510229> Mention a user to use this command."
            await ctx.send (embed=embed)
         else:
            r = requests.get("https://nekos.life/api/v2/img/pat")
            res = r.json()
            embed = discord.Embed(
                timestamp=datetime.datetime.utcnow(),
                description=f"{ctx.author.mention} pets {user.mention}",
                color=0x0d0d13)
            embed.set_image(url=res['url'])
            embed.set_footer(text=f"{ctx.guild.name}")
            await ctx.send(embed=embed)

    @commands.command(name="howcute",
             aliases=['howsexy', 'howhot', 'cute', 'sexy', 'hot'],
             help="check someone cute percentage",
             usage="Howcute <person>")
    @blacklist_check()
    @ignore_check()
    async def howcute(self, ctx, *, person):
             embed = discord.Embed(color=0x0d0d13)
             responses = [
  '50', '75', '25', '1', '3', '5', '15', '10', '65', '60', '85', '30',
  '40', '45', '80', '100', '150', '1000', '5000', '10000', '999999',
  ]
             embed.description = f'**{person} is {random.choice(responses)}% Cute** :hot_face:'
             embed.set_footer(text=f'How cute are you? - {ctx.author.name}')
             await ctx.send(embed=embed)

        

    @commands.command(name="howgay",

             aliases=['gay'],

             help="check someone cute percentage",

             usage="Howgay <person>")

    @blacklist_check()

    @ignore_check()

    async def howgay(self, ctx, *, person):

             embed = discord.Embed(color=0x0d0d13)

             responses = [

  '50', '75', '25', '1', '3', '5', '15', '10', '65', '60', '85', '30',

  '40', '45', '80', '100', '150', '1000', '5000', '10000', '999999',

  ]

             embed.description = f'**{person} is {random.choice(responses)}% Gay** :rainbow:'

             embed.set_footer(text=f'How gay are you? - {ctx.author.name}')

             await ctx.send(embed=embed)

    @commands.command(name="slots")
    @blacklist_check()
    @ignore_check()
    async def slots(self, ctx):
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)
        slotmachine = f"[ {a} {b} {c} ]\n{ctx.author.mention}"
        if (a == b == c):
            await ctx.send(embed=discord.Embed(
                title="Slot machine",
                description=f"{slotmachine} All Matching! You Won!",
                color=0x0d0d13))
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(embed=discord.Embed(
                title="Slot machine",
                description=f"{slotmachine} 2 Matching! You Won!",
                color=0x0d0d13))
        else:
            await ctx.send(embed=discord.Embed(
                title="Slot machine",
                description=f"{slotmachine} No Matches! You Lost!",
                color=0x0d0d13))

    @commands.command(name="penis",
                      aliases=['dick'],
                      help="Check someone`s dick`s size .",
                      usage="Dick [member]")
    @blacklist_check()
    @ignore_check()
    async def penis(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        size = random.randint(1, 15)
        dong = ""
        for _i in range(0, size):
            dong += "="
        em = discord.Embed(title=f"**{user}'s** Dick size",
                           description=f"8{dong}D",
                           color=0x00FFCA)
        em.set_footer(text=f'whats {user} dick size?')
        await ctx.send(embed=em)
        
    @commands.command(name="sigma",
            help="check someone Sigma percentage",
            usage="Sigma <person>")
    @blacklist_check()
    @ignore_check()
    async def Sigma(self, ctx, *, person):
        embed = discord.Embed(color=0x0d0d13)
        responses = [
          '50', '75', '25', '1', '3', '5', '15', '10', '65', '60', '85', '30',
          '40', '45', '80', '100', '150', '1000', '5000', '10000', '999999',
          ]
        embed.description = f'**{person} is {random.choice(responses)}% Sigma** <a:sigma:1449451080634204417> '
        embed.set_footer(text=f'How Sigma are you? - {ctx.author.name}')
        await ctx.send(embed=embed)
        

    
    @commands.command()
    async def pickupline(self, ctx: Context) -> None:
        """
        Gives you a random pickup line.
        Note that most of them are very cheesy.
        """
        random_line = random.choice(PICKUP_LINES["lines"])
        embed = discord.Embed(
            title="<:rizz:1449451087437238345> Your pickup line <:rizz:1449451087437238345>",
            description=random_line["line"],
            color=ctx.author.color,
        )
        embed.set_thumbnail(
            url=random_line.get("image", PICKUP_LINES["placeholder"]))
        await ctx.send(embed=embed)

    @commands.command(name="iplookup",
                             aliases=['ip', 'ipl'],
                             help="shows info about an ip",
                             usage="Iplookup [ip]")
    @blacklist_check()
    @ignore_check()
    async def iplookup(self, ctx, *, ip):
        async with aiohttp.ClientSession() as a:
            async with a.get(f"http://ipwhois.app/json/{ip}") as b:
                c = await b.json()
                try:
                    coordj = ''.join(f"{c['latitude']}" + ", " +
                                     f"{c['longitude']}")
                    embed = discord.Embed(
                        title="IP: {}".format(ip),
                        description=
                        f"```txt\n\nLocation Info:\nIP: {ip}\nIP Type: {c['type']}\nCountry, Country code: {c['country']} ({c['country_code']})\nPhone Number Prefix: {c['country_phone']}\nRegion: {c['region']}\nCity: {c['city']}\nCapital: {c['country_capital']}\nLatitude: {c['latitude']}\nLongitude: {c['longitude']}\nLat/Long: {coordj} \n\nTimezone Info:\nTimezone: {c['timezone']}\nTimezone Name: {c['timezone_name']}\nTimezone (GMT): {c['timezone_gmt']}\nTimezone (GMT) offset: {c['timezone_gmtOffset']}\n\nContractor/Hosting Info:\nASN: {c['asn']}\nISP: {c['isp']}\nORG: {c['org']}\n\nCurrency:\nCurrency type: {c['currency']}\nCurrency Code: {c['currency_code']}\nCurrency Symbol: {c['currency_symbol']}\nCurrency rates: {c['currency_rates']}\nCurrency type (plural): {c['currency_plural']}```",
                        color=0x00FFCA)
                    embed.set_footer(
                        text='Thanks For Using Cypher',
                        icon_url=
                        "https://media.discordapp.net/attachments/1138517714646876252/1138847074499170344/LaurieManGif_5.gif"
                    )
                    await ctx.send(embed=embed)
                except KeyError:
                    embed = discord.Embed(
                        description=
                        "KeyError has occured, perhaps this is a bogon IP address, or invalid IP address?",
                        color=0x00FFCA)
                    await ctx.send(embed=embed)
                    
async def setup(client):
    await client.add_cog(Fun(client))