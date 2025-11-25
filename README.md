Modular Discord bot scaffold.

Install dependencies:
pip install -r requirements.txt

Setup .env with:
DISCORD_TOKEN=your_token
OPENAI_API_KEY=your_key
LOG_CHANNEL_ID=optional_channel_id
WELCOME_CHANNEL_ID=optional_channel_id

How to run:
python bot.py

Files:
- bot.py : loader and entrypoint
- cogs/ : modules for features (AI, moderation, leveling, economy, fun, utility, reaction roles)
- data/ : sqlite files will be created here
