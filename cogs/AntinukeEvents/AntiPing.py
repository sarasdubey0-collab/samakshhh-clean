import discord
from discord.ext import commands
from utils.tool import  getConfig, getanti, getantiping

class AntipingInv(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.spam_control = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)

    async def handle_punishment(self, user_id: int, guild: discord.Guild, punishment: str, reason: str):
        try:
            if punishment == "Ban":
                await guild.ban(discord.Object(id=user_id), delete_message_days=1, reason=reason)
            elif punishment == "Kick":
                await guild.kick(discord.Object(id=user_id), reason=reason)
            elif punishment == "Strip":
                member = guild.get_member(user_id)
                if member:
                    await member.edit(roles=[], reason=reason)
        except discord.Forbidden:
            pass
        except Exception as e:
            pass


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.client.user or not message.guild:
            return

        try:
            anti = getanti(message.guild.id)
            if anti != "on":
                return

            data = getConfig(message.guild.id)
            antiping = getantiping(message.guild.id)
            wled = data.get("whitelisted", [])
            punishment = data.get("punishment", "Strip")
            reason = "Cypher • Security | AntiPing"

            if message.mention_everyone:
                if (str(message.author.id) in wled or
                        str(message.author.id) in data.get("owners", []) or
                        message.author.id == message.guild.owner_id or
                        anti == "off" or antiping == "off"):
                    return

                await self.handle_punishment(message.author.id, message.guild, punishment, reason)
                async for msg in message.channel.history(limit=20):
                    if msg.author == message.author and ('@everyone' in msg.content or '@here' in msg.content):
                        try:
                            await msg.delete()
                        except discord.Forbidden:
                            pass
                        except Exception as e:
                            pass
        except Exception as e:
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AntipingInv(bot))
