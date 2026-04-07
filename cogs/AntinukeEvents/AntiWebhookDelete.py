import discord
from discord.ext import commands
from datetime import datetime
from utils.tool import *

class AntiWebhookDelete(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel: discord.abc.GuildChannel):
        try:
            guild = channel.guild
            anti = getanti(guild.id)
            if anti != "on":
                return

            data = getConfig(guild.id)
            punishment = data.get("punishment", "Strip")
            wled = data.get("whitelisted", [])
            owner = data.get("owners", [])
            reason = "Cypher • Security | AntiWebhookDelete"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.webhook_delete):
                user = entry.user

                if user.id == self.client.user.id or user.id == guild.owner_id or str(user.id) in owner or str(user.id) in wled:
                    return

                if entry.target and isinstance(entry.target, discord.Webhook):
                    try:
                        if punishment == "Ban":
                            await guild.ban(user, reason=reason)
                        elif punishment == "Kick":
                            await guild.kick(user, reason=reason)
                        elif punishment == "Strip":
                            member = guild.get_member(user.id)
                            if member:
                                await member.edit(roles=[role for role in member.roles if not role.permissions.administrator], reason=reason)

                    except Exception as e:
                        print(e)

        except Exception as error:
            print(error)


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiWebhookDelete(bot))
