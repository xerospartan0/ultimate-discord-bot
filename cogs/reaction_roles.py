import discord
from discord.ext import commands
from discord import app_commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="createrr", description="Create a reaction role message")
    @app_commands.describe(role="Role to give", emoji="Emoji to react with")
    async def createrr(self, interaction: discord.Interaction, role: discord.Role, emoji: str):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You need Manage Roles permission.", ephemeral=True)
            return
        msg = await interaction.channel.send(f"React with {emoji} to get the {role.name} role")
        await msg.add_reaction(emoji)
        await interaction.response.send_message("Reaction role message created.", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member is None or payload.member.bot:
            return
        guild = self.bot.get_guild(payload.guild_id)
        msg = await guild.fetch_message(payload.message_id)
        if msg and isinstance(msg, discord.Message):
            for role in guild.roles:
                if role.name in msg.content:
                    member = payload.member
                    await member.add_roles(role)
                    return

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
