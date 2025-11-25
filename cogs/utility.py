import discord
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Show a user's avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        await interaction.response.send_message(user.display_avatar.url)

    @app_commands.command(name="serverinfo", description="Show basic server info")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        await interaction.response.send_message(f"Server: {g.name} | Members: {g.member_count}")

async def setup(bot):
    await bot.add_cog(Utility(bot))
