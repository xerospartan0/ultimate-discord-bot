# Requires: wavelink, aiohttp
import discord
from discord.ext import commands
import wavelink
import asyncio
import os

LAVALINK_HOST = os.getenv('LAVALINK_HOST', '127.0.0.1')
LAVALINK_PORT = int(os.getenv('LAVALINK_PORT', 2333))
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', 'youshallnotpass')

class WaveMusic(commands.Cog):
    """Music cog using Wavelink (Lavalink)."""
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        try:
            node = await wavelink.NodePool.create_node(bot=self.bot,
                                                      host=LAVALINK_HOST,
                                                      port=LAVALINK_PORT,
                                                      password=LAVALINK_PASSWORD)
            print('Connected to Lavalink node:', node)
        except Exception as e:
            print('Failed to connect Lavalink node:', e)

    @commands.command(name='wplay')
    async def wplay(self, ctx, *, query: str):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('Join a voice channel first.')
        # get/create player
        player = wavelink.Player(client=self.bot, guild_id=ctx.guild.id)
        await player.connect(ctx.author.voice.channel.id)
        # search
        results = await wavelink.YouTubeTrack.search(query=query, return_first=False)
        if not results:
            return await ctx.send('No results.')
        track = results[0]
        await player.play(track)
        await ctx.send(f'▶ Playing: {track.title}')

    @commands.command(name='wstop')
    async def wstop(self, ctx):
        player = wavelink.NodePool.get_node().get_player(ctx.guild.id)
        if player:
            await player.disconnect()
            await ctx.send('Stopped and disconnected.')

def setup(bot):
    bot.add_cog(WaveMusic(bot))
