import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

PREMIUM_ROLE = os.getenv("PREMIUM_ROLE_NAME", "Premium")
LICENSE_KEYS = set(k.strip() for k in os.getenv("LICENSE_KEYS", "").split(",") if k.strip())

class Premium(commands.Cog):
    """Premium and licensing helpers."""
    def __init__(self, bot):
        self.bot = bot
        self.licensed = set()  # runtime activated licenses

    def is_premium_member(self, member: discord.Member):
        # Check if member has premium role
        role = discord.utils.get(member.guild.roles, name=PREMIUM_ROLE)
        if role and role in member.roles:
            return True
        return False

    def has_license(self, key: str):
        return key in LICENSE_KEYS or key in self.licensed

    @commands.command(name='redeem')
    async def redeem(self, ctx, key: str):
        """Redeem a license key for premium access (server-level - adds role)."""
        if self.has_license(key):
            guild = ctx.guild
            role = discord.utils.get(guild.roles, name=PREMIUM_ROLE)
            if not role:
                role = await guild.create_role(name=PREMIUM_ROLE, reason='Premium role created')
            await ctx.author.add_roles(role, reason='Redeemed premium key')
            self.licensed.add(key)
            await ctx.send(f'✅ License accepted — {ctx.author.mention} granted **{role.name}**.')
        else:
            await ctx.send('❌ Invalid license key.')

    @commands.command(name='premium_check')
    async def premium_check(self, ctx, member: discord.Member = None):
        """Check premium status of a member."""
        member = member or ctx.author
        if self.is_premium_member(member):
            await ctx.send(f'✅ {member.mention} is a **premium** member.')
        else:
            await ctx.send(f'ℹ️ {member.mention} is **not** premium.')

def setup(bot):
    bot.add_cog(Premium(bot))
