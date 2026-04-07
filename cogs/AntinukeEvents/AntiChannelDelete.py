import discord
from discord.ext import commands
from utils.tool import getConfig, getanti, getantichannel
from datetime import datetime, timedelta

class AntiChannelDelete(commands.Cog):
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
                    await member.remove_roles(*roles_to_remove, reason="Unauthorized channel deletion (AntiNuke)")
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        try:
            guild = channel.guild
            if getanti(guild.id) != "on" or getantichannel(guild.id) != "on":
                return

            data = getConfig(guild.id)
            punishment = data["punishment"]
            wled = data["whitelisted"]
            own = data["owners"]
            reason = "Cypher • Security | AntiChannelDelete"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                if not entry.user:
                    return

                user_id = entry.user.id
                if user_id == self.client.user.id or user_id == guild.owner_id or str(user_id) in wled or str(user_id) in own:
                    return

                await self.handle_punishment(user_id, guild, punishment, reason)

                # Restore the channel
                cloned = await channel.clone(name=channel.name, category=channel.category, reason=reason)
                await cloned.edit(position=channel.position)
                break

        except discord.Forbidden:
            pass
        except Exception as e:
            print(e)

async def setup(client: commands.Bot):
    await client.add_cog(AntiChannelDelete(client))
