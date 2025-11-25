import discord
from discord.ext import commands
from discord import File
import os

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, name='welcome')
            if channel:
                await channel.send(f'Welcome {member.mention} to **{member.guild.name}**! 🎉')
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, name='goodbye')
            if channel:
                await channel.send(f'{member.mention} has left **{member.guild.name}**. 😢')
        except Exception:
            pass

def setup(bot):
    bot.add_cog(Welcome(bot))
