import os
import discord
from discord.ext import commands
from discord import app_commands

BANNED_WORDS = {"badword1","badword2"}  # customize

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        content = message.content.lower() if message.content else ""
        if any(w in content for w in BANNED_WORDS):
            try:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, your message was removed for violating rules.")
                ch = os.getenv("LOG_CHANNEL_ID")
                if ch:
                    try:
                        log = self.bot.get_channel(int(ch))
                        await log.send(f"Deleted message from {message.author}: {message.content}")
                    except: pass
            except: pass

    @app_commands.command(name="clear", description="Bulk delete messages (admin only).")
    @app_commands.describe(amount="Number of messages to delete (max 100)")
    async def clear(self, interaction: discord.Interaction, amount: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("You don't have permission.", ephemeral=True)
            return
        await interaction.response.defer()
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
