import discord
from discord.ext import commands
import datetime
import random

from utils.tool import *

class AntiPrune(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def handle_punishment(self, user_id: int, guild: discord.Guild, punishment: str, reason: str):
        try:
            if punishment == "Ban":
                await guild.ban(discord.Object(id=user_id), delete_message_days=1, reason=reason)
            elif punishment == "Kick":
                await guild.kick(discord.Object(id=user_id), reason=reason)
            elif punishment == "Strip":
                member = guild.get_member(id=user_id)
                if member:
                    await member.edit(roles=[], reason=reason)
            else:
                pass
        except Exception as e:
            pass



    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        try:
            guild = member.guild
            anti = getanti(guild.id)
            if anti != "on":
                return 
            
            data = getConfig(guild.id)
            antiprune = getantiprune(guild.id)
            punishment = data.get("punishment", "none")
            wled = data.get("whitelisted", [])
            owner = data.get("owners", [])
            reason = "Cypher • Security | AntiPrune"
            
            async for entry in guild.audit_logs(limit=1,after=datetime.datetime.utcnow() - datetime.timedelta(seconds=30),action=discord.AuditLogAction.member_prune):
                user_id = entry.user
                if (user_id.id == self.client.user.id or user_id.id == guild.owner_id or str(user_id.id) in wled or str(user_id.id) in owner or antiprune == "off"):
                    return
                
                await self.handle_punishment(user_id, guild, punishment, reason)
        except Exception as error:
            print(f"Error in AntiPrune: {error}")

async def setup(bot):
    await bot.add_cog(AntiPrune(bot))
