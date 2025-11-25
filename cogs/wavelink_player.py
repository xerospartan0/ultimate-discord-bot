# Enhanced Wavelink player template using Redis for queue persistence.
# Requires: wavelink, redis, aioredis
import discord, asyncio, os, json
from discord.ext import commands
import wavelink, aioredis

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
LAVALINK_HOST = os.getenv('LAVALINK_HOST', 'lavalink')
LAVALINK_PORT = int(os.getenv('LAVALINK_PORT', 2333))
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', 'youshallnotpass')

class PersistentPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis = None
        bot.loop.create_task(self.init_redis())
        bot.loop.create_task(self.connect_nodes())

    async def init_redis(self):
        self.redis = await aioredis.from_url(REDIS_URL)

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        try:
            await wavelink.NodePool.create_node(bot=self.bot, host=LAVALINK_HOST, port=LAVALINK_PORT, password=LAVALINK_PASSWORD)
            print('Connected to Lavalink')
        except Exception as e:
            print('Lavalink connect error', e)

    async def save_queue(self, guild_id, queue):
        key = f'queue:{guild_id}'
        data = [json.dumps({'title': t.title, 'uri': t.uri}) for t in queue]
        await self.redis.delete(key)
        if data:
            await self.redis.rpush(key, *data)

    async def load_queue(self, guild_id):
        key = f'queue:{guild_id}'
        items = await self.redis.lrange(key, 0, -1)
        return [json.loads(i) for i in items] if items else []

    @commands.command(name='wplayp')
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice: return await ctx.send('Join voice channel first.')
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild.id)
        if not player or not player.is_connected():
            player = await node.get_node().connect(ctx.author.voice.channel.id)
        tracks = await wavelink.YouTubeTrack.search(query)
        track = tracks[0]
        # push to redis queue
        await self.redis.rpush(f'queue:{ctx.guild.id}', json.dumps({'title': track.title, 'uri': track.uri}))
        await ctx.send(f'Queued: {track.title}')

    @commands.command(name='wq')
    async def view_queue(self, ctx):
        items = await self.load_queue(ctx.guild.id)
        if not items:
            return await ctx.send('Queue empty.')
        msg = '\n'.join(f"{i+1}. {it['title']}" for i,it in enumerate(items))
        await ctx.send(f'Queue:\n{msg}')

    @commands.command(name='vote_skip')
    async def vote_skip(self, ctx):
        # simple vote skip stored in redis set
        key = f'voteskip:{ctx.guild.id}:{ctx.message.id}'
        user_set = await self.redis.sadd(key, ctx.author.id)
        votes = await self.redis.scard(key)
        if votes >= 3:
            node = wavelink.NodePool.get_node()
            player = node.get_player(ctx.guild.id)
            if player and player.is_playing():
                await player.stop()
                await ctx.send('Vote skip passed — skipping track.')
        else:
            await ctx.send(f'Vote registered ({votes}/3)')

def setup(bot):
    bot.add_cog(PersistentPlayer(bot))
