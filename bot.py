import os, threading, time
import discord
from discord.ext import commands
from utils.logging_conf import logger
from dotenv import load_dotenv

load_dotenv()

# Validate environment (warning only)
try:
    import utils.validate_env
except Exception:
    pass
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('PREFIX', '!')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Bot ready: {bot.user} (ID: {bot.user.id})')

# Load cogs
cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
for filename in os.listdir(cogs_dir):
    if filename.endswith('.py'):
        try:
            bot.load_extension(f'cogs.{filename[:-3]}')
            print('Loaded', filename)
        except Exception as e:
            print('Failed to load', filename, e)

# Try to launch the Flask dashboard if present
def run_dashboard():
    try:
        from web.app import app
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print('Dashboard failed to start:', e)

try:
    t = threading.Thread(target=run_dashboard, daemon=True)
    t.start()
except Exception as e:
    print('Could not start dashboard thread', e)

if __name__ == '__main__':
    if not TOKEN:
        print('DISCORD_TOKEN missing in .env')
    else:
        bot.run(TOKEN)

# --- AUTO-LOADED NEW COGS (v4) ---
extra_cogs = [
    'cogs.wavelink_player',
    'cogs.reminders_redis',
    'cogs.wavelink_music',  # optional older template
]
for c in extra_cogs:
    try:
        bot.load_extension(c)
        print('Loaded extra cog', c)
    except Exception as e:
        print('Could not load', c, e)

# Start health and webhook dashboards if present
def run_web_apps():
    try:
        from web.health import app as health_app
        from web.dashboard import app as dash_app
        from web.dashboard_admin import app as admin_app
        from web.stripe_webhook import app as stripe_app
        # run each on different ports using threads in production you might use gunicorn
        import threading
        threading.Thread(target=lambda: health_app.run(port=5200), daemon=True).start()
        threading.Thread(target=lambda: dash_app.run(port=5000), daemon=True).start()
        threading.Thread(target=lambda: admin_app.run(port=5002), daemon=True).start()
        threading.Thread(target=lambda: stripe_app.run(port=8000), daemon=True).start()
    except Exception as e:
        print('Could not start web app(s):', e)

try:
    run_web_apps()
except Exception as e:
    print('Error starting web services', e)
