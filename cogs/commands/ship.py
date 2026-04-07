import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import discord
from discord.ext import commands
import requests
from utils.Tools import *


class ShipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ship")
    @blacklist_check()
    @ignore_check()
    async def ship(self, ctx, user1: discord.Member = None, user2: discord.Member = None):
        

        if user1 is None:  
            user1 = ctx.author
            guild = ctx.guild
            members = guild.members
            user2 = random.choice(members)
        elif user2 is None:  
            user2 = user1
            user1 = ctx.author

        author_id = float(user1.id)
        user_id = float(user2.id)

        # Fetch avatars
        avatar1 = user1.avatar.url
        avatar2 = user2.avatar.url

        # Load the background image
        background = Image.open("background.png").convert("RGBA")

        # Download avatars
        response1 = requests.get(avatar1)
        response2 = requests.get(avatar2)

        img1 = Image.open(BytesIO(response1.content)).resize((200, 200)).convert("RGBA")
        img2 = Image.open(BytesIO(response2.content)).resize((200, 200)).convert("RGBA")

        # Add avatars to background
        background.paste(img1, (100, 100), img1)
        background.paste(img2, (500, 100), img2)

        # Draw larger heart in the middle
        heart_size = 200  # Increased heart size
        heart = Image.open("heart.png").resize((heart_size, heart_size)).convert("RGBA")
        heart_x, heart_y = 300, 100  # Adjusted position for larger heart
        background.paste(heart, (heart_x, heart_y), heart)

        # Draw percentage inside the heart
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("utils/arial.ttf", 50)  # Larger font for better visibility
        percentage = random.randint(0, 100)
        text = f"{percentage}%"

        # Calculate text size for centering
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Center the text within the heart
        heart_center_x = heart_x + heart_size // 2
        heart_center_y = heart_y + heart_size // 2
        text_x = heart_center_x - text_width // 2
        text_y = heart_center_y - text_height // 2

        draw.text((text_x, text_y), text, font=font, fill="white")

        # Convert to BytesIO for Discord
        buffer = BytesIO()
        background.save(buffer, "PNG")
        buffer.seek(0)

        # Send the image
        file = discord.File(fp=buffer, filename="ship.png")
        embed = discord.Embed(
            description=f"{user1.mention} ❤️ {user2.mention}",
            color=discord.Color.pink(),
        )
        embed.set_author(
            name="Relationship Percentage",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )
        embed.set_image(url="attachment://ship.png")
        await ctx.send(embed=embed, file=file)

# Add cog to bot
async def setup(bot):
    await bot.add_cog(ShipCommand(bot))
