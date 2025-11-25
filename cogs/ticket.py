import discord
from discord.ext import commands

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = {}  # user_id -> channel_id

    @commands.command(name='ticket')
    async def open_ticket(self, ctx, *, reason: str = None):
        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        category = discord.utils.get(guild.categories, name='Support')
        if not category:
            category = await guild.create_category('Support')
        channel = await guild.create_text_channel(f'ticket-{ctx.author.name}', overwrites=overwrites, category=category)
        self.tickets[ctx.author.id] = channel.id
        await channel.send(f'{ctx.author.mention} opened a ticket. Reason: {reason or "No reason provided."}')
        await ctx.send(f'✅ Ticket created: {channel.mention}')

    @commands.command(name='close')
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        try:
            await channel.delete()
        except Exception as e:
            await ctx.send(f'Error closing ticket: {e}')

def setup(bot):
    bot.add_cog(Ticket(bot))
