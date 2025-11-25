import re
import discord
from discord.ext import commands

BAD_WORDS = {'badword1', 'badword2'}  # customize or load from DB
LINK_REGEX = re.compile(r'https?://\S+')

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None or message.author.bot:
            return
        # simple bad words filter
        lowered = message.content.lower()
        if any(b in lowered for b in BAD_WORDS):
            try:
                await message.delete()
                await message.channel.send(f'⚠️ {message.author.mention}, your message was removed (bad language).')
            except Exception:
                pass
            return
        # link moderation (example: restrict non-admins from posting links)
        if LINK_REGEX.search(message.content):
            if not message.author.guild_permissions.manage_messages:
                try:
                    await message.delete()
                    await message.channel.send(f'🔗 {message.author.mention}, links are not allowed here.')
                except Exception:
                    pass

def setup(bot):
    bot.add_cog(AutoMod(bot))
