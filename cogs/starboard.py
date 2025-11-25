import discord
from discord.ext import commands

STAR_THRESHOLD = 3
STAR_EMOJI = '⭐'

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starboard_channel = None  # could be set per-guild

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot: return
        if str(reaction.emoji) == STAR_EMOJI and reaction.count >= STAR_THRESHOLD:
            channel = reaction.message.channel
            guild = reaction.message.guild
            sb = discord.utils.get(guild.text_channels, name='starboard')
            if not sb:
                sb = await guild.create_text_channel('starboard')
            author = reaction.message.author
            embed = discord.Embed(description=reaction.message.content or '', timestamp=reaction.message.created_at)
            embed.set_author(name=str(author), icon_url=author.avatar.url if author.avatar else None)
            embed.add_field(name='Jump to message', value=f'[Jump]({reaction.message.jump_url})')
            await sb.send(embed=embed)

def setup(bot):
    bot.add_cog(Starboard(bot))
