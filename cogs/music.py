import discord
from discord.ext import commands
# NOTE: This is a template. For reliable music you should use wavelink (Lavalink) or yt-dlp + ffmpeg.
# Add wavelink and a running Lavalink server for production.
#
# Minimal commands below use youtube_dl to fetch audio and discord.FFmpegPCMAudio to play.
# The bot requires 'ffmpeg' installed on the host and 'yt-dlp' in requirements.

import asyncio
import functools
import youtube_dl
import os

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}  # guild_id -> player state

    async def ensure_voice(self, ctx):
        if ctx.author.voice is None:
            await ctx.send('You must be in a voice channel.')
            return None
        channel = ctx.author.voice.channel
        vc = ctx.guild.voice_client
        if vc and vc.channel.id == channel.id:
            return vc
        if vc:
            await vc.move_to(channel)
            return vc
        return await channel.connect()

    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        """Play audio from YouTube (query or url)."""
        vc = await self.ensure_voice(ctx)
        if not vc:
            return
        await ctx.send('⏳ Searching...')
        loop = self.bot.loop
        ydl = youtube_dl.YoutubeDL(YDL_OPTIONS)
        try:
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
            if 'entries' in data:
                data = data['entries'][0]
            url = data['url']
            title = data.get('title', 'Unknown')
            source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            if not vc.is_playing():
                vc.play(source)
                await ctx.send(f'▶ Now playing: **{title}**')
            else:
                await ctx.send('❗ Already playing. Queueing is not implemented in this simple template.')
        except Exception as e:
            await ctx.send(f'Error: {e}')

    @commands.command(name='stop')
    async def stop(self, ctx):
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send('⏹ Stopped.')
        else:
            await ctx.send('Nothing is playing.')

def setup(bot):
    bot.add_cog(Music(bot))
