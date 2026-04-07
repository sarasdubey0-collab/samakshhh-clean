import discord
from discord.ext import commands, tasks
import aiohttp
import requests

from core.Cypher import Cypher
from utils.tool import getConfig, getanti, getantiguild
from utils.config import TOKEN  # ✅ secure token


class AntiGuild(commands.Cog):
    def __init__(self, client: Cypher):
        self.client = client

        # ✅ secure headers
        self.headers = {"Authorization": f"Bot {TOKEN}"}

        self.session = aiohttp.ClientSession(headers=self.headers)
        self.processing = []

    async def cog_unload(self):
        await self.session.close()

    @tasks.loop(seconds=15)
    async def clean_processing(self):
        self.processing.clear()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.clean_processing.is_running():
            self.clean_processing.start()

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        try:
            anti = getanti(before.id)
            antiguild = getantiguild(before.id)

            if anti != "on" or antiguild != "on":
                return

            data = getConfig(before.id)
            punishment = data.get("punishment", "Strip")
            wled = data.get("whitelisted", [])

            reason = "Cypher • Security | AntiGuildUpdate"

            async for entry in after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
                user_id = entry.user.id

                # ✅ bypass checks
                if (
                    user_id == self.client.user.id
                    or user_id == after.owner_id
                    or str(user_id) in wled
                    or str(user_id) in data.get("owners", [])
                ):
                    return

                # ✅ punishment
                if punishment == "Ban":
                    await self.session.put(
                        f"https://discord.com/api/v10/guilds/{after.id}/bans/{user_id}",
                        json={"reason": reason}
                    )

                elif punishment == "Kick":
                    await self.session.delete(
                        f"https://discord.com/api/v10/guilds/{after.id}/members/{user_id}",
                        json={"reason": reason}
                    )

                elif punishment == "Strip":
                    member = after.get_member(user_id)
                    if member:
                        await member.edit(
                            roles=[r for r in member.roles if not r.permissions.administrator],
                            reason=reason
                        )

                # ✅ revert guild changes
                try:
                    icon_bytes = None
                    if before.icon:
                        resp = requests.get(before.icon.url)
                        icon_bytes = resp.content

                    await after.edit(
                        name=before.name,
                        description=before.description,
                        verification_level=before.verification_level,
                        icon=icon_bytes,
                        rules_channel=before.rules_channel,
                        afk_channel=before.afk_channel,
                        afk_timeout=before.afk_timeout,
                        default_notifications=before.default_notifications,
                        explicit_content_filter=before.explicit_content_filter,
                        system_channel=before.system_channel,
                        system_channel_flags=before.system_channel_flags,
                        public_updates_channel=before.public_updates_channel,
                        premium_progress_bar_enabled=before.premium_progress_bar_enabled,
                        reason=reason
                    )

                except Exception:
                    pass

        except Exception:
            pass


async def setup(bot):
    await bot.add_cog(AntiGuild(bot))