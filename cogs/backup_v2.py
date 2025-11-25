import discord, os, shutil, time
from discord.ext import commands

class BackupV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='backup_all')
    @commands.has_permissions(administrator=True)
    async def backup_all(self, ctx):
        timestamp = int(time.time())
        zip_name = f'backup_all_{timestamp}.zip'
        base = os.path.join(os.getcwd(), 'data')
        try:
            shutil.make_archive(f'backup_all_{timestamp}', 'zip', base)
            await ctx.send('Backup created:', file=discord.File(zip_name))
        except Exception as e:
            await ctx.send(f'Error: {e}')

def setup(bot):
    bot.add_cog(BackupV2(bot))
