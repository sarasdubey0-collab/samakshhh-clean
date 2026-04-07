import discord
from discord.ext import commands
import aiosqlite
import random
import string
from datetime import datetime, timedelta
import asyncio

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_expired_premium())

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS premium_codes (
                    code TEXT,
                    expires_at TEXT,
                    guild_count INTEGER
                )
            ''')
            await db.execute('''
                CREATE TABLE IF NOT EXISTS premium_users (
                    user_id INTEGER,
                    guild_id INTEGER,
                    activated_at TEXT,
                    expires_at TEXT,
                    code TEXT,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            await db.commit()
        async with aiosqlite.connect('database/np.db') as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS np (
                    id INTEGER PRIMARY KEY,
                    expiry_time TEXT
                )
            ''')
            await db.commit()

    @commands.group(name="premium", invoke_without_command=True)
    async def premium(self, ctx):
        pass

    @premium.command(name="generate")
    @commands.is_owner()
    async def generate(self, ctx, duration: str, guild_count: int):
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        expires_at = self.parse_duration(duration)
        if not expires_at:
            await ctx.send('Invalid duration format. Use `1m` for 1 minute, `1h` for 1 hour, `1d` for 1 day, `1w` for 1 week, `1y` for 1 year.')
            return
        async with aiosqlite.connect('database/premium_codes.db') as db:
            await db.execute('INSERT INTO premium_codes (code, expires_at, guild_count) VALUES (?, ?, ?)', (code, expires_at.isoformat(), guild_count))
            await db.commit()
        embed = discord.Embed()
        embed.set_author(name="Premium Code", icon_url=ctx.author.display_avatar.url)
        embed.description =f"Hey, {ctx.author.display_name} I've Generated a code for you.\n\n<:MekoTimer:1449451368392953998> **Expires at :** {duration}\n<:MekoRuby:1449445982931783710> **Valid for :** {guild_count} guild(s)\n<:MekoArrowRight:1449445989436887090> **Redeem Code :**\n```\n{code}```"
        embed.set_footer(text="Use premium activate <code> to get premium.")
        await ctx.send(embed=embed)
        
        
    @premium.command(name="activate")
    async def activate(self, ctx, code: str):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            async with db.execute('SELECT expires_at FROM premium_users WHERE guild_id = ?', (ctx.guild.id,)) as cursor:
                existing_premium = await cursor.fetchone()
                if existing_premium:
                    existing_expires_at = datetime.fromisoformat(existing_premium[0])
                    if existing_expires_at > discord.utils.utcnow():
                        expires_timestamp = int(existing_expires_at.timestamp())
                        embed = discord.Embed()
                        embed.description = (
                            f"Hey, this guild already has premium activated!\n\n"
                            f"<:MekoTimer:1449451368392953998> **Expires at :** <t:{expires_timestamp}:F>"
                        )
                        await ctx.send(embed=embed)
                        return
            async with db.execute('SELECT expires_at, guild_count FROM premium_codes WHERE code = ?', (code,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await ctx.send('Invalid premium code.')
                    return
                expires_at = datetime.fromisoformat(row[0])
                guild_count = row[1]
                if expires_at < discord.utils.utcnow():
                    await ctx.send('This premium code has expired.')
                    return
                async with db.execute('SELECT COUNT(*) FROM premium_users WHERE code = ?', (code,)) as cursor:
                    count_row = await cursor.fetchone()
                    if count_row[0] >= guild_count:
                        await ctx.send('This premium code has reached its maximum number of activations.')
                        return
                activated_at = discord.utils.utcnow().isoformat()
                user_expires_at = (discord.utils.utcnow() + (expires_at - discord.utils.utcnow())).isoformat()
                await db.execute('''
                    INSERT INTO premium_users (user_id, guild_id, activated_at, expires_at, code) 
                    VALUES (?, ?, ?, ?, ?) 
                    ON CONFLICT(user_id, guild_id) 
                    DO UPDATE SET expires_at = excluded.expires_at, activated_at = excluded.activated_at
                ''', (ctx.author.id, ctx.guild.id, activated_at, user_expires_at, code))
                await db.commit()
                
        new_bot_name = f"Cypher Prime"
        avatar_url = 'https://media.discordapp.net/attachments/1245007104721420441/1252983899588526132/1718805023427.png?ex=67ceee30&is=67cd9cb0&hm=d8d6796d9190002f6ebde7681d8c7740eb6a4753d78a14c0d0a15916b1f227f3&=&format=webp&quality=lossless&width=600&height=600'
        
        try:
            await ctx.guild.me.edit(nick=new_bot_name)               
        except discord.Forbidden:
            pass    
        
        activated_at = discord.utils.utcnow().isoformat()
        expires_at = datetime.fromisoformat(row[0])
        activated_timestamp = int(discord.utils.utcnow().timestamp())
        expires_timestamp = int(expires_at.timestamp())
        embed = discord.Embed()
        embed.set_author(name="Premium Activated", icon_url=ctx.author.display_avatar.url)
        embed.description = (
            f"Hey, {ctx.author.display_name} You have successfully activated premium for this guild.\n\n"
            f"<:MekoRuby:1449445982931783710> **Activated at :** <t:{activated_timestamp}:F>\n"
            f"<:MekoTimer:1449451368392953998> **Ends at :** <t:{expires_timestamp}:F>"
        )
        embed.set_footer(text="Premium is activated for this guild.")
        await ctx.send(embed=embed)

    @premium.command(name="deactivate")
    async def deactivate(self, ctx):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            await db.execute('DELETE FROM premium_users WHERE guild_id = ?', (ctx.guild.id,))
            await db.commit()
        async with aiosqlite.connect('database/np.db') as db:
            await db.execute('DELETE FROM np WHERE id = ?', (ctx.author.id,))
            await db.commit()
        embed = discord.Embed()
        embed.set_author(name="Successfully revoked premium of this user.")
        await ctx.send(embed=embed)

    @premium.command(name="stats", aliases=["status"])
    async def stats(self, ctx):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            async with db.execute('SELECT activated_at, expires_at FROM premium_users WHERE user_id = ? AND guild_id = ?', (ctx.author.id, ctx.guild.id)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    embed = discord.Embed()
                    embed.set_author(name="You just discovered a premium feature", icon_url="https://media.discordapp.net/attachments/1245007104721420441/1252983899588526132/1718805023427.png?ex=67ceee30&is=67cd9cb0&hm=d8d6796d9190002f6ebde7681d8c7740eb6a4753d78a14c0d0a15916b1f227f3&=&format=webp&quality=lossless&width=2110&height=2110")
                    embed.description="- Do you want to use my commands without prefix ? You need to purchase premium.\n  - Join our [**Support Server**](https://discord.gg/cypherbot) and create a ticket to purchase premium."
                    
                    button = discord.ui.Button(label="Support Server", style=discord.ButtonStyle.link, url="https://discord.gg/cypherbot")
                    view = discord.ui.View()
                    view.add_item(button)
                    await ctx.send(embed=embed, view=view)
                    return
                activated_at = datetime.fromisoformat(row[0])
                expires_at = datetime.fromisoformat(row[1])
                activated_timestamp = int(activated_at.timestamp())
                expires_timestamp = int(expires_at.timestamp())

            async with db.execute('SELECT guild_id FROM premium_users WHERE user_id = ?', (ctx.author.id,)) as cursor:
                rows = await cursor.fetchall()
                guild_count = len(rows)
                guild_names = [self.bot.get_guild(row[0]).name for row in rows if self.bot.get_guild(row[0])]
                
        embed = discord.Embed()
        embed.set_author(name="Premium Status", icon_url=ctx.author.display_avatar.url)
        embed.description = (
            f"Hey, {ctx.author.display_name} here is your premium status :\n\n"
            f"<:MekoRuby:1449445982931783710> **Premium activated :** <t:{activated_timestamp}:F>\n"
            f"<:MekoTimer:1449451368392953998> **Premium ends :** <t:{expires_timestamp}:F>\n\n"
            f"<:MekoArrowRight:1449445989436887090> **You have added premium to {guild_count} guild(s):** \n"
            f"{', '.join(guild_names)}"
        )
        embed.set_footer(text="Happy to say that you are already purchased our Premium plan!")
        await ctx.send(embed=embed)
    
    @premium.command(name="revoke")
    @commands.is_owner()
    async def revoke(self, ctx, user: discord.User):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            async with db.execute('SELECT 1 FROM premium_users WHERE user_id = ?', (user.id,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    embed = discord.Embed(
                        title="<:MekoExclamation:1449445917500510229> No Premium",
                        description=f"{user.mention} does not have an active premium subscription.",
                        color=0xFF0000
                    )
                    await ctx.send(embed=embed)
                    return
            await db.execute('DELETE FROM premium_users WHERE user_id = ?', (user.id,))
            await db.commit()
        async with aiosqlite.connect('database/np.db') as db:
            await db.execute('DELETE FROM np WHERE id = ?', (user.id,))
            await db.commit()
        await ctx.send(f'Revoked premium and removed No Prefix for {user.mention}.')

    @premium.command(name="guilds")
    @commands.is_owner()
    async def premium_guilds(self, ctx):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            async with db.execute('SELECT DISTINCT guild_id FROM premium_users') as cursor:
                rows = await cursor.fetchall()
                guild_count = len(rows)
                guild_names = [self.bot.get_guild(row[0]).name for row in rows if self.bot.get_guild(row[0])]
        await ctx.send(f'Total premium guilds: {guild_count}\nGuilds: {", ".join(guild_names)}')

    @premium.command(name="users")
    @commands.is_owner()
    async def premium_users(self, ctx):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            async with db.execute('SELECT DISTINCT user_id FROM premium_users') as cursor:
                rows = await cursor.fetchall()
                user_count = len(rows)
                user_names = [str(self.bot.get_user(row[0])) for row in rows if self.bot.get_user(row[0])]
        await ctx.send(f'Total premium users: {user_count}\nUsers: {", ".join(user_names)}')

    def parse_duration(self, duration: str):
        unit = duration[-1]
        amount = int(duration[:-1])
        if unit == 'm':
            return discord.utils.utcnow() + timedelta(minutes=amount)
        elif unit == 'h':
            return discord.utils.utcnow() + timedelta(hours=amount)
        elif unit == 'd':
            return discord.utils.utcnow() + timedelta(days=amount)
        elif unit == 'w':
            return discord.utils.utcnow() + timedelta(weeks=amount)
        elif unit == 'y':
            return discord.utils.utcnow() + timedelta(days=amount*365)
        return None

    async def check_expired_premium(self):
        while True:
            async with aiosqlite.connect('database/premium_codes.db') as db:
                await db.execute('DELETE FROM premium_users WHERE expires_at < ?', (discord.utils.utcnow().isoformat(),))
                await db.commit()
            await asyncio.sleep(60)

    async def is_user_in_np(self, user_id):
        async with aiosqlite.connect('database/np.db') as db:
            async with db.execute('SELECT 1 FROM np WHERE id = ?', (user_id,)) as cursor:
                return await cursor.fetchone() is not None

    async def add_np(self, user, duration):
        expiry_time = datetime.utcnow() + duration
        async with aiosqlite.connect('database/np.db') as db:
            await db.execute('INSERT INTO np (id, expiry_time) VALUES (?, ?)', (user.id, expiry_time.isoformat()))
            await db.commit()

        embed = discord.Embed(
            title="<:MekoGift:1449451126901440647> You got No Prefix!",
            description=f"You've been credited No Prefix for your premium subscription. You can now use commands without prefix.",
            color=0x000000
        )
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

    async def remove_np(self, user):
        async with aiosqlite.connect('database/np.db') as db:
            await db.execute('DELETE FROM np WHERE id = ?', (user.id,))
            await db.commit()

        embed = discord.Embed(
            title="<:MekoExclamation:1449445917500510229> No Prefix Expired",
            description=f"Your No Prefix status has expired.",
            color=0x000000
        )
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

    @premium.command(name="noprefix")
    async def premium_noprefix(self, ctx):
        class NoPrefixView(discord.ui.View):
            def __init__(self, user, cog, guild_id, row):
                super().__init__()
                self.user = user
                self.cog = cog
                self.guild_id = guild_id
                self.row = row

                # Add buttons to the view
                self.add_item(self.AddNoPrefixButton())
                self.add_item(self.RemoveNoPrefixButton())

            class AddNoPrefixButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(label="Add No Prefix", style=discord.ButtonStyle.green)

                async def callback(self, interaction: discord.Interaction):
                    if await self.view.cog.is_user_in_np(self.view.user.id):
                        await interaction.response.send_message("User already has No Prefix.", ephemeral=True)
                    else:
                        expires_at = datetime.fromisoformat(self.view.row[1])
                        duration = expires_at - discord.utils.utcnow()
                        await self.view.cog.add_np(self.view.user, duration)
                        await interaction.response.send_message("No Prefix added successfully.")

            class RemoveNoPrefixButton(discord.ui.Button):
                def __init__(self):
                    super().__init__(label="Remove No Prefix", style=discord.ButtonStyle.red)

                async def callback(self, interaction: discord.Interaction):
                    if not await self.view.cog.is_user_in_np(self.view.user.id):
                        await interaction.response.send_message("User does not have No Prefix.", ephemeral=True)
                    else:
                        await self.view.cog.remove_np(self.view.user)
                        await interaction.response.send_message("No Prefix removed successfully.", ephemeral=True)

        async with aiosqlite.connect('database/premium_codes.db') as db:
            async with db.execute('SELECT activated_at, expires_at FROM premium_users WHERE user_id = ? AND guild_id = ?', (ctx.author.id, ctx.guild.id)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    embed = discord.Embed()
                    embed.set_author(name="You just discovered a premium feature", icon_url="https://media.discordapp.net/attachments/1245007104721420441/1252983899588526132/1718805023427.png?ex=67ceee30&is=67cd9cb0&hm=d8d6796d9190002f6ebde7681d8c7740eb6a4753d78a14c0d0a15916b1f227f3&=&format=webp&quality=lossless&width=2110&height=2110")
                    embed.description="- Do you want to use my commands without prefix ? You need to purchase premium.\n  - Join our [**Support Server**](https://discord.gg/cypherbot) and create a ticket to purchase premium."
                    
                    button = discord.ui.Button(label="Support Server", style=discord.ButtonStyle.link, url="https://discord.gg/cypherbot")
                    view = discord.ui.View()
                    view.add_item(button)
                    await ctx.send(embed=embed, view=view)
                    return

        view = NoPrefixView(ctx.author, self, ctx.guild.id, row)
        await ctx.send("Manage No Prefix for your premium subscription:", view=view)

def premium_check():
    async def predicate(ctx):
        async with aiosqlite.connect('database/premium_codes.db') as db:
            async with db.execute('SELECT expires_at FROM premium_users WHERE user_id = ? AND guild_id = ?', (ctx.author.id, ctx.guild.id)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    await ctx.send('You do not have an active premium subscription in this server.')
                    return False
                expires_at = datetime.fromisoformat(row[0])
                if expires_at < discord.utils.utcnow():
                    await ctx.send('Your premium subscription has expired.')
                    return False
        return True
    return commands.check(predicate)

async def setup(bot):
    await bot.add_cog(Premium(bot))