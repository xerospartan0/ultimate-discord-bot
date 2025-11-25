import discord, aiohttp, random
from discord.ext import commands
from discord import app_commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="meme", description="Fetch a random meme (r/dankmemes)")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        url = "https://meme-api.herokuapp.com/gimme"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                if r.status == 200:
                    j = await r.json()
                    embed = discord.Embed(title=j.get('title'))
                    embed.set_image(url=j.get('url'))
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("Couldn't fetch a meme.")

    @app_commands.command(name="8ball", description="Ask the magic 8ball")
    async def eightball(self, interaction: discord.Interaction, question: str):
        responses = ["Yes","No","Maybe","Ask later","Definitely"]
        await interaction.response.send_message(random.choice(responses))

async def setup(bot):
    await bot.add_cog(Fun(bot))
