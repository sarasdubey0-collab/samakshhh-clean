import discord
from discord.ext import commands
import aiohttp

from utils.tool import getConfig, getanti, getantiemoji
from utils.config import TOKEN  # ✅ secure import


class AntiEmojiCreate(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        
        # ✅ TOKEN from env (NO HARDCODE)
        self.headers = {"Authorization": f"Bot {TOKEN}"}
        
        # ✅ session create
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
            
            if len(after) > len(before):
                created_emojis = [emoji for emoji in after if emoji not in before]
                
                data = getConfig(guild.id)
                antiemoji = getantiemoji(guild.id)

                punishment = data.get("punishment", "Strip")
                wled = data.get("whitelisted", [])
                reason = "Cypher • Security | AntiEmojiCreate"

                async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.emoji_create):
                    user_id = entry.user.id

                    if (
                        user_id == self.client.user.id
                        or user_id == guild.owner_id
                        or str(user_id) in wled
                        or str(user_id) in data.get("owners", [])
                        or anti == "off"
                        or antiemoji == "off"
                    ):
                        return

                    # ✅ API actions
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

                    # ✅ delete emojis
                    for emoji in created_emojis:
                        try:
                            await emoji.delete(reason=reason)
                        except (discord.Forbidden, discord.HTTPException):
                            pass

        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(AntiEmojiCreate(bot))