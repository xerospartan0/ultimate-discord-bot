import discord, asyncio, os
from discord.ext import commands
import yt_dlp as youtube_dl

YDL_OPTS = {'format': 'bestaudio', 'noplaylist': True}

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_url(cls, url, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL(YDL_OPTS).extract_info(url, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'), data=data)

class MusicV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # guild_id -> asyncio.Queue()

    async def ensure_voice(self, ctx):
        if not ctx.author.voice:
            await ctx.send('You must be in a voice channel.')
            return None
        channel = ctx.author.voice.channel
        vc = ctx.guild.voice_client
        if not vc or vc.channel.id != channel.id:
            vc = await channel.connect()
        return vc

    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        vc = await self.ensure_voice(ctx)
        if not vc: return
        q = self.queues.setdefault(ctx.guild.id, asyncio.Queue())
        await ctx.send('⏳ Searching and queuing...')
        try:
            player = await YTDLSource.from_url(query, loop=self.bot.loop)
            await q.put(player)
            await ctx.send(f'✅ Queued: {player.title}')
            if not vc.is_playing():
                await self._play_next(ctx, vc)
        except Exception as e:
            await ctx.send(f'Error: {e}')

    async def _play_next(self, ctx, vc):
        q = self.queues.get(ctx.guild.id)
        if not q: return
        try:
            item = await q.get()
            vc.play(item, after=lambda e: self.bot.loop.create_task(self._after_play(ctx, vc, e)))
            await ctx.send(f'▶ Now playing: {item.title}')
        except Exception as e:
            await ctx.send(f'Queue error: {e}')

    async def _after_play(self, ctx, vc, error):
        if error:
            await ctx.send(f'Playback error: {error}')
        await asyncio.sleep(1)
        if not vc.is_playing():
            # play next if available
            q = self.queues.get(ctx.guild.id)
            if q and not q.empty():
                await self._play_next(ctx, vc)

    @commands.command(name='skip')
    async def skip(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.stop(); await ctx.send('⏭ Skipped.')
        else:
            await ctx.send('Nothing is playing.')

    @commands.command(name='stop')
    async def stop(self, ctx):
        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect()
            await ctx.send('Disconnected and cleared queue.')
            self.queues.pop(ctx.guild.id, None)

def setup(bot):
    bot.add_cog(MusicV2(bot))
