import os
import io
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client_ai = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

class AICog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="summarize", description="Summarize the given text")
    @app_commands.describe(text="Text to summarize")
    async def summarize(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer()
        prompt = f"Summarize this in 3 sentences:\\n\\n{text}"
        if not client_ai:
            await interaction.followup.send("OpenAI key not configured.")
            return
        try:
            resp = await asyncio.wait_for(
                client_ai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}],
                    max_tokens=120
                ), timeout=20
            )
            await interaction.followup.send(resp.choices[0].message.content)
        except Exception as e:
            await interaction.followup.send("Error generating summary.")
            ch = os.getenv("LOG_CHANNEL_ID")
            if ch:
                try:
                    log = self.bot.get_channel(int(ch))
                    await log.send(f"Summarize error: {e}")
                except: pass

    @app_commands.command(name="translate", description="Translate text to target language")
    @app_commands.describe(text="Text to translate", target_lang="Target language code, e.g., en, es")
    async def translate(self, interaction: discord.Interaction, text: str, target_lang: str):
        await interaction.response.defer()
        if not client_ai:
            await interaction.followup.send("OpenAI key not configured.")
            return
        prompt = f"Translate the following text to {target_lang} keeping meaning and tone:\\n\\n{text}"
        try:
            resp = await asyncio.wait_for(
                client_ai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}],
                    max_tokens=200
                ), timeout=25
            )
            await interaction.followup.send(resp.choices[0].message.content)
        except Exception as e:
            await interaction.followup.send("Error translating text.")
            ch = os.getenv("LOG_CHANNEL_ID")
            if ch:
                try:
                    log = self.bot.get_channel(int(ch))
                    await log.send(f"Translate error: {e}")
                except: pass

    @app_commands.command(name="image", description="Generate a free image (Unsplash fallback).")
    @app_commands.describe(prompt="Image prompt")
    async def image(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        url = f"https://source.unsplash.com/1024x1024/?{prompt.replace(' ',',')}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        await interaction.followup.send(file=discord.File(io.BytesIO(data), filename="image.jpg"))
                        ch = os.getenv("LOG_CHANNEL_ID")
                        if ch:
                            try:
                                log = self.bot.get_channel(int(ch))
                                await log.send(f"Image generated for {interaction.user}: {prompt}")
                            except: pass
                    else:
                        await interaction.followup.send("Image generation failed.")
        except Exception as e:
            await interaction.followup.send("Image generation failed.")
            ch = os.getenv("LOG_CHANNEL_ID")
            if ch:
                try:
                    log = self.bot.get_channel(int(ch))
                    await log.send(f"Image generation error: {e}")
                except: pass

async def setup(bot):
    await bot.add_cog(AICog(bot))
