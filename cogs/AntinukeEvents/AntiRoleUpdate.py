from datetime import datetime
import discord
from discord.ext import commands
from utils.tool import getAntiRoleLogs, getConfig, getanti, getantirole


class AntiRoleUpdate(commands.Cog):
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
                        await member.remove_roles(*roles_to_remove, reason="Unauthorized role update (AntiNuke)")
                    else:
                        pass
            else:
                pass
        except Exception as e:
            pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        try:
            guild = before.guild
            anti = getanti(guild.id)
            if anti != "on":
                return

            role_protection = getantirole(guild.id)
            if role_protection != "on":
                return

            data = getConfig(guild.id)
            punishment = data["punishment"]
            wled = data["whitelisted"]
            own = data["owners"]
            reason = "Cypher • Security | AntiRoleUpdate"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
                user_id = entry.user.id
                if user_id == self.client.user.id or user_id == guild.owner_id or str(user_id) in wled or str(user_id) in own:
                    return

                await self.handle_punishment(user_id, guild, punishment, reason)
                await after.edit(
                    name=before.name,
                    permissions=before.permissions,
                    color=before.color,
                    hoist=before.hoist,
                    mentionable=before.mentionable,
                    reason=reason
                )
                break

        except discord.Forbidden:
            pass
        except Exception as e:
            pass


async def setup(client: commands.Bot):
    await client.add_cog(AntiRoleUpdate(client))
