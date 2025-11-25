import discord, os, sqlite3
from discord.ext import commands

DB = os.path.join(os.getcwd(), 'data', 'suggestions.db')

class Suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='suggest')
    async def suggest(self, ctx, *, suggestion: str):
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS suggestions(id INTEGER PRIMARY KEY, user_id INTEGER, suggestion TEXT, approved INTEGER DEFAULT 0)')
        cur.execute('INSERT INTO suggestions(user_id, suggestion) VALUES(?,?)', (ctx.author.id, suggestion))
        conn.commit(); conn.close()
        await ctx.send('✅ Suggestion recorded.')

    @commands.command(name='suggestions_list')
    @commands.has_permissions(manage_guild=True)
    async def suggestions_list(self, ctx):
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute('SELECT id, user_id, suggestion, approved FROM suggestions ORDER BY id DESC LIMIT 50')
        rows = cur.fetchall(); conn.close()
        embed = discord.Embed(title='Suggestions')
        for id_, user_id, suggestion, approved in rows:
            embed.add_field(name=f'#{id_} ({"approved" if approved else "pending"})', value=suggestion, inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Suggestions(bot))
