from datetime import datetime
import discord
from discord.ext import commands
from utils.tool import getAntiModLogs, getConfig, getanti, getantikick



class AntiKick(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def handle_punishment(self, user_id: int, guild: discord.Guild, punishment: str, reason: str):
        if punishment == "Ban":
            await guild.ban(discord.Object(id=user_id), delete_message_days=1, reason=reason)
        elif punishment == "Kick":
            await guild.kick(discord.Object(id=user_id), reason=reason)
        elif punishment == "Strip":
            member = guild.get_member(user_id)
            if member:
                await member.edit(roles=[], reason=reason)


    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        try:
            guild = member.guild
            if guild.unavailable:
                return  

            anti = getanti(guild.id)
            if anti != "on":
                return

            data = getConfig(guild.id)
            antikick = getantikick(guild.id)
            punishment = data.get("punishment", "Strip")
            wled = data.get("whitelisted", [])
            owners = data.get("owners", [])
            reason = "Cypher • Security | AntiKick"

            async for entry in guild.audit_logs(limit=2):
                if entry.action == discord.AuditLogAction.kick and entry.target == member:
                    user_id = entry.user.id
                    if entry.user.id in [self.client.user.id, guild.owner_id] or str(user_id) in owners or str(user_id) in wled or antikick == "off":
                        return

                    await self.handle_punishment(user_id, guild, punishment, reason)
                    break  

        except discord.HTTPException as e:
            pass
        except Exception as e:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiKick(bot))