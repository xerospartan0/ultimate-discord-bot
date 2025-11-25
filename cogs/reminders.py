import asyncio, time, sqlite3, os
import discord
from discord.ext import commands, tasks

DB = os.path.join(os.getcwd(), 'data', 'reminders.db')

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task = self.loop_check.start()

    def cog_unload(self):
        self.loop_check.cancel()

    @tasks.loop(seconds=30)
    async def loop_check(self):
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY, user_id INTEGER, channel_id INTEGER, message TEXT, ts INTEGER)')
        now = int(time.time())
        cur.execute('SELECT id, user_id, channel_id, message FROM reminders WHERE ts<=?', (now,))
        rows = cur.fetchall()
        for id_, user_id, channel_id, message in rows:
            try:
                ch = self.bot.get_channel(channel_id)
                user = self.bot.get_user(user_id)
                if ch:
                    await ch.send(f'{user.mention} Reminder: {message}')
                cur.execute('DELETE FROM reminders WHERE id=?', (id_,))
            except Exception:
                pass
        conn.commit(); conn.close()

    @commands.command(name='remindme')
    async def remindme(self, ctx, seconds: int, *, message: str):
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS reminders(id INTEGER PRIMARY KEY, user_id INTEGER, channel_id INTEGER, message TEXT, ts INTEGER)')
        ts = int(time.time()) + seconds
        cur.execute('INSERT INTO reminders(user_id, channel_id, message, ts) VALUES(?,?,?,?)', (ctx.author.id, ctx.channel.id, message, ts))
        conn.commit(); conn.close()
        await ctx.send(f'✅ Reminder set for {seconds} seconds from now.')

def setup(bot):
    bot.add_cog(Reminders(bot))
