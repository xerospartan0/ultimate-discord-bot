import discord
from discord.ext import commands
import sqlite3
import os

DB = os.path.join(os.getcwd(), 'data', 'economy.db')

SHOP = {
    'vip-role': {'price': 1000, 'type': 'role', 'role_name': 'VIP'},
    'nickname-change': {'price': 250, 'type': 'service'}
}

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_balance(self, user_id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS balances(user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)')
        cur.execute('SELECT balance FROM balances WHERE user_id=?', (user_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0

    def set_balance(self, user_id, new_bal):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute('INSERT OR REPLACE INTO balances(user_id, balance) VALUES(?,?)', (user_id, new_bal))
        conn.commit(); conn.close()

    @commands.command(name='shop')
    async def view_shop(self, ctx):
        embed = discord.Embed(title='Shop — Items', description='Buy using !buy <item_key>')
        for key, item in SHOP.items():
            embed.add_field(name=key, value=f"Price: {item['price']}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='buy')
    async def buy(self, ctx, item_key: str):
        item = SHOP.get(item_key)
        if not item:
            return await ctx.send('Item not found.')
        bal = self.get_balance(ctx.author.id)
        if bal < item['price']:
            return await ctx.send(f'You need {item["price"]} coins but have {bal}.')
        # deduct
        self.set_balance(ctx.author.id, bal - item['price'])
        # deliver
        if item['type'] == 'role':
            role = discord.utils.get(ctx.guild.roles, name=item['role_name'])
            if not role:
                role = await ctx.guild.create_role(name=item['role_name'])
            await ctx.author.add_roles(role, reason='Purchased from shop')
            await ctx.send(f'✅ You bought {item_key} and received role {role.name}.')
        else:
            await ctx.send(f'✅ You bought {item_key}. (deliver manually)')

def setup(bot):
    bot.add_cog(Shop(bot))
