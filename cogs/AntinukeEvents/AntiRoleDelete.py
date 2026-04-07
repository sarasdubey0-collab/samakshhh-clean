import discord
from discord.ext import commands
from utils.tool import getAntiRoleLogs, getConfig, getanti, getantichannel
from datetime import datetime

class AntiRoleDelete(commands.Cog):
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
                        await member.remove_roles(*roles_to_remove, reason="Unauthorized role deletation (AntiNuke)")
                    else:
                        pass
            else:
                pass
        except Exception as e:
            pass


    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        try:
            guild = role.guild
            anti = getanti(guild.id)
            if anti != "on":
                return

            ch = getantichannel(guild.id)
            if ch != "on":
                return

            data = getConfig(guild.id)
            punishment = data["punishment"]
            wled = data["whitelisted"]
            own = data["owners"]
            reason = "Cypher • Security | AntiRoleDelete"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
                if entry.user.id == self.client.user.id or entry.user.id == guild.owner_id or str(entry.user.id) in wled or str(entry.user.id) in own:
                    return

                await self.handle_punishment(entry.user.id, guild, punishment, reason)
                break

        except Exception as e:
            print(f"Unexpected error in on_guild_role_delete: {e}")

async def setup(client: commands.Bot):
    await client.add_cog(AntiRoleDelete(client))