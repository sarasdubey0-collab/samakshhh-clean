from datetime import datetime
import discord
from discord.ext import commands, tasks
from utils.tool import getAntiModLogs, getConfig, getanti, getantiban

class AntiBan(commands.Cog):
    def __init__(self, client):
        self.client = client      
    

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User) -> None:
        try:
            anti = getanti(guild.id)
            antiban = getantiban(guild.id)
            if anti != "on" or antiban != "on":
                return

            data = getConfig(guild.id)
            owners = data.get("owners", [])
            wled = data.get("whitelisted", [])
            punishment = data.get("punishment", "none")
            reason = "Cypher • Security | AntiBan"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                banner_id = entry.user.id

                if (
                    banner_id == self.client.user.id or
                    banner_id == guild.owner_id or
                    str(banner_id) in owners or
                    str(banner_id) in wled
                ):
                    return 

                if punishment == "Ban":
                    await guild.ban(discord.Object(id=banner_id), reason=reason)
                    await guild.unban(user, reason=reason)
                elif punishment == "Kick":
                    await guild.kick(discord.Object(id=banner_id), reason=reason)
                    await guild.unban(user, reason=reason)
                elif punishment == "Strip":
                    member_to_update = guild.get_member(banner_id)
                    if member_to_update:
                        new_roles = [role for role in member_to_update.roles if not role.permissions.administrator]
                        await member_to_update.edit(roles=new_roles, reason=reason)
                    await guild.unban(user, reason=reason)
                return 

        except discord.errors.NotFound:
            pass
        except Exception as error:
            print(f"An error occurred in on_member_ban: {error}")

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User) -> None:
        try:
            anti = getanti(guild.id)
            if anti != "on":
                return

            data = getConfig(guild.id)
            owners = data.get("owners", [])
            wled = data.get("whitelisted", [])
            punishment = data.get("punishment", "none")
            reason = "Cypher • Security | AntiUnban"

            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                unbanner_id = entry.user.id

                if (
                    unbanner_id == self.client.user.id or
                    unbanner_id == guild.owner_id or
                    str(unbanner_id) in owners or
                    str(unbanner_id) in wled
                ):
                    return  

                if punishment == "Ban":
                    await guild.ban(discord.Object(id=unbanner_id), reason=reason)
                    await guild.ban(user, reason=reason)
                elif punishment == "Kick":
                    await guild.kick(discord.Object(id=unbanner_id), reason=reason)
                    await guild.ban(user, reason=reason)
                elif punishment == "Strip":
                    member_to_update = guild.get_member(unbanner_id)
                    if member_to_update:
                        new_roles = [role for role in member_to_update.roles if not role.permissions.administrator]
                        await member_to_update.edit(roles=new_roles, reason=reason)
                    await guild.ban(user, reason=reason)
                return 

        except discord.errors.NotFound:
            pass
        except Exception as error:
            print(f"An error occurred in on_member_unban: {error}")


async def setup(bot):
    await bot.add_cog(AntiBan(bot))
