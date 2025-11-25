import os, discord, json, aiohttp, asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
import psycopg2

load_dotenv()

PREMIUM_ROLE = os.getenv('PREMIUM_ROLE_NAME', 'Premium')
STRIPE_CHECKOUT_ENDPOINT = os.getenv('STRIPE_CHECKOUT_ENDPOINT', 'http://localhost:5001/create_checkout')
PG_DSN = os.getenv('PG_DSN', 'dbname=botdb user=bot password=botpass host=postgres')

def get_pg_conn():
    return psycopg2.connect(PG_DSN)

class PremiumV2(commands.Cog):
    """Premium features and Stripe integration placeholders."""
    def __init__(self, bot):
        self.bot = bot
        self.sync_task = self.sync_premium.start()

    def cog_unload(self):
        self.sync_task.cancel()

    @commands.command(name='premium_info')
    async def premium_info(self, ctx):
        await ctx.send('Premium grants access to special commands and higher limits. Use !buy_premium to purchase.')

    @commands.command(name='grant_premium')
    @commands.has_permissions(administrator=True)
    async def grant_premium(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name=PREMIUM_ROLE)
        if not role:
            role = await ctx.guild.create_role(name=PREMIUM_ROLE)
        await member.add_roles(role)
        await ctx.send(f'Granted {member.mention} the premium role.')

    @commands.command(name='buy_premium')
    async def buy_premium(self, ctx):
        """Creates a Stripe Checkout link (via configured webhook service) and DMs the user."""
        payload = {'user_id': ctx.author.id, 'guild_id': ctx.guild.id}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(STRIPE_CHECKOUT_ENDPOINT, json=payload, timeout=10) as resp:
                    if resp.status != 200:
                        data = await resp.text()
                        return await ctx.send('Could not create checkout: ' + data)
                    data = await resp.json()
                    url = data.get('url')
                    if not url:
                        return await ctx.send('Checkout did not return a URL.')
                    try:
                        await ctx.author.send(f'Complete your purchase here: {url}')
                        await ctx.send('✅ I sent you a DM with the checkout link.')
                    except discord.Forbidden:
                        await ctx.send(f'Please enable DMs so I can send the checkout link: {url}')
        except Exception as e:
            await ctx.send('Error creating checkout: ' + str(e))

    @tasks.loop(seconds=60)
    async def sync_premium(self):
        """Periodically sync premium_members from Postgres and ensure the role exists and is assigned."""
        await self.bot.wait_until_ready()
        try:
            conn = get_pg_conn(); cur = conn.cursor()
            cur.execute('SELECT user_id, guild_id FROM premium_members')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            # DB may not be ready
            # print('Premium sync DB error', e)
            return
        for user_id, guild_id in rows:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            member = guild.get_member(user_id)
            if not member:
                try:
                    member = await guild.fetch_member(user_id)
                except Exception:
                    continue
            role = discord.utils.get(guild.roles, name=PREMIUM_ROLE)
            if not role:
                try:
                    role = await guild.create_role(name=PREMIUM_ROLE)
                except Exception:
                    continue
            if role not in member.roles:
                try:
                    await member.add_roles(role, reason='Premium sync from Stripe')
                except Exception:
                    pass

def setup(bot):
    bot.add_cog(PremiumV2(bot))
