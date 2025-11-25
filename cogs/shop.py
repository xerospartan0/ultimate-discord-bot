import discord
from discord.ext import commands

SHOP = {
    'vip-role': {'price': 1000, 'type': 'role', 'role_name': 'VIP'},
}

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='shop')
    async def view_shop(self, ctx):
        embed = discord.Embed(title='Shop')
        for key, item in SHOP.items():
            embed.add_field(name=key, value=f"Price: {item['price']}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='buy')
    async def buy(self, ctx, item_key: str):
        item = SHOP.get(item_key)
        if not item:
            return await ctx.send('Item not found.')
        # integrate with economy cog: this is a template
        await ctx.send(f'You bought {item_key} for {item["price"]} (template - integrate economy).')

def setup(bot):
    bot.add_cog(Shop(bot))
