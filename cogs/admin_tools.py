import os, sqlite3, discord
from discord.ext import commands

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='migration_preview')
    @commands.has_permissions(administrator=True)
    async def migration_preview(self, ctx):
        """Shows counts of records in local sqlite DBs without modifying anything."""
        data_dir = os.path.join(os.getcwd(), 'data')
        dbs = ['economy.db', 'levels.db', 'reminders.db', 'suggestions.db']
        embed = discord.Embed(title='Migration Preview', description='Counts from local sqlite DBs')
        for db in dbs:
            path = os.path.join(data_dir, db)
            if not os.path.exists(path):
                embed.add_field(name=db, value='Not found', inline=False)
                continue
            try:
                conn = sqlite3.connect(path); cur = conn.cursor()
                # try common tables
                counts = []
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cur.fetchall()]
                for t in tables:
                    try:
                        cur.execute(f'SELECT COUNT(*) FROM {t}')
                        c = cur.fetchone()[0]
                        counts.append(f"{t}: {c}")
                    except Exception:
                        pass
                conn.close()
                embed.add_field(name=db, value='\n'.join(counts) or 'No tables found', inline=False)
            except Exception as e:
                embed.add_field(name=db, value='Error: '+str(e), inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(AdminTools(bot))
