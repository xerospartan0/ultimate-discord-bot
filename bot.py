import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load .env if running locally
try:
    load_dotenv()
except Exception:
    pass

# =====================================
# ENV VALIDATION (Fix for missing token)
# =====================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

if not DISCORD_TOKEN:
    print("❌ ERROR: DISCORD_TOKEN is missing! Add it in Render → Environment Variables")
    raise SystemExit

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Main bot setup
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ==========================
# Slash Command Fix Handler
# ==========================
@bot.tree.error
async def on_app_command_error(interaction, error):
    print("❌ Slash command error:", error)

# ==========================
# On Ready Event
# ==========================
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Synced {len(synced)} slash commands.")
    except Exception as e:
        print("Slash sync error:", e)

    print(f"🤖 Bot is ready: {bot.user} (ID: {bot.user.id})")

# ==========================
# Load all cogs
# ==========================
cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")

for filename in os.listdir(cogs_dir):
    if filename.endswith(".py"):
        try:
            bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ Loaded: {filename}")
        except Exception as e:
            print(f"❌ Failed to load {filename}:", e)

# ==========================
# TRY TO START WEB DASHBOARD
# ==========================
def run_dashboard():
    try:
        from web.app import app
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        print("Dashboard error:", e)

# Start web dashboard in background thread
import threading
threading.Thread(target=run_dashboard).start()

# ==========================
# Run the bot
# ==========================
bot.run(DISCORD_TOKEN)
