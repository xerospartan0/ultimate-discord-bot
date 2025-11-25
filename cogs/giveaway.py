import discord
import asyncio
from discord.ext import commands, tasks
import random
import datetime

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='giveaway')
    @commands.has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx, duration: int, winners: int, *, prize: str):
        """Create a giveaway: duration in seconds."""
        embed = discord.Embed(title='🎉 Giveaway', description=f'Prize: {prize}\nHosted by: {ctx.author.mention}')
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('🎉')
        await asyncio.sleep(duration)
        msg = await ctx.channel.fetch_message(msg.id)
        users = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == '🎉':
                users = await reaction.users().flatten()
                break
        users = [u for u in users if not u.bot]
        if len(users) == 0:
            return await ctx.send('No participants.')
        winners_chosen = random.sample(users, min(winners, len(users)))
        await ctx.send('🎊 Winners: ' + ', '.join(w.mention for w in winners_chosen))

def setup(bot):
    bot.add_cog(Giveaway(bot))
