import os, sys
required = [
    'DISCORD_TOKEN',
    'DISCORD_CLIENT_ID',
    'DISCORD_CLIENT_SECRET',
    'DISCORD_REDIRECT_URI',
    'STRIPE_API_KEY',
    'STRIPE_ENDPOINT_SECRET',
    'PG_DSN',
    'REDIS_URL',
]
missing = [k for k in required if not os.getenv(k)]
if missing:
    print('ERROR: Missing required environment variables:', ', '.join(missing))
    # do not exit here; allow developer to run with .env for dev, but warn
else:
    print('All required environment variables present.')
