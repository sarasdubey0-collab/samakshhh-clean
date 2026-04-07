import discord
from discord.ext import commands
import aiohttp

from utils.tool import getConfig, getanti, getantiemoji
from utils.config import TOKEN  # ✅ secure token import


class AntiEmojiDelete(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
        # ✅ NO HARDCODE TOKEN
        self.headers = {"Authorization": f"Bot {TOKEN}"}
        
        # ✅ session
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def cog_unload(self):
        await self.session.close()

    @commands.Cog.listener()
    async def on_guild_emojis_update(
        self,
        guild: discord.Guild,
        before: list[discord.Emoji],
        after: list[discord.Emoji]
    ) -> None:
        try:
            anti = getanti(guild.id)
            if anti != "on":
                return

            data = getConfig(guild.id)
            antiemoji = getantiemoji(guild.id)

            if antiemoji != "on":
                return

            punishment = data.get("punishment", "Strip")
            wled = data.get("whitelisted", [])
            reason = "Cypher • Security | AntiEmojiDelete"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.emoji_delete):
                user_id = entry.user.id

                if (
                    user_id == self.client.user.id
                    or user_id == guild.owner_id
                    or str(user_id) in wled
                    or str(user_id) in data.get("owners", [])
                    or anti == "off"
                ):
                    return

                # ✅ punishment actions
                if punishment == "Ban":
                    await self.session.put(
                        f"https://discord.com/api/v10/guilds/{guild.id}/bans/{user_id}",
                        json={"reason": reason}
                    )

                elif punishment == "Kick":
                    await self.session.delete(
                        f"https://discord.com/api/v10/guilds/{guild.id}/members/{user_id}",
                        json={"reason": reason}
                    )

                elif punishment == "Strip":
                    member = guild.get_member(user_id)
                    if member:
                        await member.edit(
                            roles=[r for r in member.roles if not r.permissions.administrator],
                            reason=reason
                        )

                # ✅ restore deleted emojis
                if before:
                    for emoji in before:
                        try:
                            image_bytes = await emoji.read()

                            await self.session.post(
                                f"https://discord.com/api/v10/guilds/{guild.id}/emojis",
                                json={
                                    "name": emoji.name,
                                    "image": f"data:image/png;base64,{image_bytes.decode('latin1')}"
                                }
                            )
                        except Exception:
                            pass

        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiEmojiDelete(bot))