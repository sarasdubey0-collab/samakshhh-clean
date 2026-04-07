import discord
from discord.ext import commands
from datetime import datetime
from utils.tool import getAntiModLogs, getConfig, getanti, getantibot


class antibot(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def handle_punishment(self, user_id: int, guild: discord.Guild, punishment: str, reason: str):
        try:
            if punishment == "Ban":
                await guild.ban(discord.Object(id=user_id), delete_message_days=1, reason=reason)
            elif punishment == "Kick":
                await guild.kick(discord.Object(id=user_id), reason=reason)
            elif punishment == "Strip":
                member = guild.get_member(user_id) or await guild.fetch_member(user_id)
                if member:
                    roles_to_remove = [role for role in member.roles if role != guild.default_role and role.position < guild.me.top_role.position]
                    if roles_to_remove:
                        await member.remove_roles(*roles_to_remove, reason="Unauthorized behaviour (AntiNuke)")
                    else:
                        pass
            else:
                pass
        except Exception as e:
            pass




    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        try:
            guild = member.guild
            anti = getanti(guild.id)
            if anti != "on":
                return 

            data = getConfig(guild.id)
            antibot = getantibot(guild.id)
            punishment = data.get("punishment", "none")
            wled = data.get("whitelisted", [])
            reason = "Cypher • Securty | AntiBot"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                user_id = entry.user.id
                if entry.user.id == guild.owner_id:
                    return
                if entry.user.id == self.client.user.id:
                    return

                if str(entry.user.id) in wled or str(entry.user.id) in data.get("owners", []):
                    return

                if anti == "off" or antibot == "off":
                    return

                if member.bot:
                    await self.handle_punishment(user_id, guild, punishment, reason)
                    await guild.ban(member, reason=reason)
        except Exception as error:
            print(f"Unexpected error while handling member join: {error}")

async def setup(bot: commands.Bot):
    await bot.add_cog(antibot(bot))