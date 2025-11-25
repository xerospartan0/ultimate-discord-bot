import discord
from discord.ext import commands
import shutil
import os

class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='backup')
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        data_dir = os.path.join(os.getcwd(), 'data')
        zip_path = os.path.join(os.getcwd(), 'backup_data.zip')
        try:
            shutil.make_archive('backup_data', 'zip', data_dir)
            await ctx.send('Backup created:', file=discord.File(zip_path))
        except Exception as e:
            await ctx.send(f'Error creating backup: {e}')

def setup(bot):
    bot.add_cog(Backup(bot))
