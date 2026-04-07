import discord
from discord.ext import commands
from gtts import gTTS
import asyncio
import os
from io import BytesIO
from utils.Tools import *
import tempfile

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tts")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @blacklist_check()
    @ignore_check()
    async def speak(self, ctx, *, text: str):
        """Makes the bot join the VC and speak the provided text."""
        if not ctx.author.voice:
            await ctx.send("You need to join a voice channel first.")
            return

        channel = ctx.author.voice.channel

        # Check if the bot is already in a voice channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.channel != channel:
            await voice_client.move_to(channel)
        elif not voice_client:
            voice_client = await channel.connect()

        # Notify the user
        await ctx.send(f":speaking_head: Speaking: {text}", delete_after=10)

        # Create the TTS audio with male voice using gTTS
        tts = gTTS(text=text, lang='hi', tld='co.in')

        # Save the TTS audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            tts.save(temp_file.name)  # Save the audio to the file
            temp_file_path = temp_file.name

        try:
            # Stop any currently playing audio before starting new audio
            if voice_client.is_playing():
                voice_client.stop()

            # Play the TTS audio with improved settings
            options = "-af 'equalizer=f=300:t=h:width=200:g=3,bass=g=5'"
            voice_client.play(discord.FFmpegPCMAudio(temp_file_path, options=options), 
                              after=lambda e: os.remove(temp_file_path))

            # Wait until the audio finishes playing
            while voice_client.is_playing():
                await asyncio.sleep(1)

        finally:
            # Ensure the file is deleted even if an error occurs
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)


async def setup(client):
    await client.add_cog(TTS(client))