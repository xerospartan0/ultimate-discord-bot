import discord
from discord import app_commands
from discord.ext import commands
import asyncio

# Simple storage for daily cooldowns (resets when bot restarts)
last_daily = {}

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="daily", description="Claim your daily reward!")
    async def daily(self, interaction: discord.Interaction):
        user = interaction.user.id

        # 24-hour cooldown in seconds
        cooldown = 24 * 60 * 60  

        # If user already claimed today
        if user in last_daily:
            remaining = cooldown - (discord.utils.utcnow().timestamp() - last_daily[user])
            if remaining > 0:
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                seconds = int(remaining % 60)
                return await interaction.response.send_message(
                    f"⏳ You already claimed your daily reward!\n"
                    f"Come back in **{hours}h {minutes}m {seconds}s**.",
                    ephemeral=True
                )

        # No cooldown or cooldown expired
        last_daily[user] = discord.utils.utcnow().timestamp()
        await interaction.response.send_message(
            f"🎉 **Daily reward claimed!**\n"
            f"You received **100 coins**!"
        )

async def setup(bot):
    await bot.add_cog(Daily(bot))
