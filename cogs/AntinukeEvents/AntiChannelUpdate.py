import discord
from discord.ext import commands
from utils.tool import getAntiChannelLogs, getConfig, getanti, getantichannel
from datetime import datetime, timedelta

class AntiChannelUpdate(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def handle_punishment(self, user_id: int, guild: discord.Guild, punishment: str, reason: str):
        try:
            member = guild.get_member(user_id) or await guild.fetch_member(user_id)
            if not member:
                return

            if punishment == "Ban":
                await guild.ban(member, delete_message_days=1, reason=reason)
            elif punishment == "Kick":
                await member.kick(reason=reason)
            elif punishment == "Strip":
                roles_to_remove = [role for role in member.roles if role != guild.default_role and role.position < guild.me.top_role.position]
                if roles_to_remove:
                    await member.remove_roles(*roles_to_remove, reason="Unauthorized channel update (AntiNuke)")
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        try:
            guild = before.guild
            anti = getanti(guild.id)
            if anti != "on":
                return

            data = getConfig(guild.id)
            antichannel = getantichannel(guild.id)
            punishment = data["punishment"]
            wled = data["whitelisted"]
            reason = "Cypher • Security | AntiChannelUpdate"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
                if entry.user.id == self.client.user.id:
                    return

                if (
                    entry.user.id == guild.owner_id or
                    str(entry.user.id) in wled or
                    str(entry.user.id) in data.get("owners", []) or
                    antichannel == "off"
                ):
                    return

                await self.handle_punishment(entry.user.id, guild, punishment, reason)

                await after.edit(
                    name=before.name,
                    topic=getattr(before, 'topic', None),
                    nsfw=getattr(before, 'nsfw', None),
                    category=before.category,
                    slowmode_delay=getattr(before, 'slowmode_delay', 0),
                    type=before.type,
                    overwrites=before.overwrites,
                    reason=reason
                )
                break

        except discord.Forbidden:
            pass
        except Exception as e:
            print(e)

async def setup(client: commands.Bot):
    await client.add_cog(AntiChannelUpdate(client))
