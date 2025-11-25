# Redis-backed reminders using Redis sorted sets (template)
import aioredis, os, json, time, asyncio
import discord
from discord.ext import commands, tasks

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

class RemindersRedis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = None
        bot.loop.create_task(self.init_redis())
        self.check_loop.start()

    async def init_redis(self):
        self.redis = await aioredis.from_url(REDIS_URL)

    @tasks.loop(seconds=15)
    async def check_loop(self):
        now = int(time.time())
        # zrangebyscore to get due reminders
        items = await self.redis.zrangebyscore('reminders', 0, now)
        for item in items:
            obj = json.loads(item)
            ch = self.bot.get_channel(obj['channel_id'])
            user = self.bot.get_user(obj['user_id'])
            if ch:
                await ch.send(f'{user.mention} Reminder: {obj["message"]}')
            await self.redis.zrem('reminders', item)

    @commands.command(name='remindme')
    async def remindme(self, ctx, seconds: int, *, message: str):
        ts = int(time.time()) + seconds
        obj = json.dumps({'user_id': ctx.author.id, 'channel_id': ctx.channel.id, 'message': message})
        await self.redis.zadd('reminders', {obj: ts})
        await ctx.send('✅ Reminder scheduled.')

def setup(bot):
    bot.add_cog(RemindersRedis(bot))
