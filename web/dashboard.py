# Lightweight Flask dashboard with Discord OAuth2 (template)
# Requires: Flask, requests, itsdangerous (for sessions) or Flask-Session for production
from flask import Flask, redirect, request, session, url_for, render_template_string
import os, requests, json

app = Flask(__name__)
app.secret_key = os.getenv('DASH_SECRET', 'change-me')

CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/callback')
BOT_INVITE = os.getenv('BOT_INVITE_URL', '')

DISCORD_OAUTH_URL = f'https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify%20guilds'

@app.route('/')
def index():
    user = session.get('user')
    return render_template_string('''
        <h1>Ultimate Bot Dashboard (v3)</h1>
        {% if user %}
            <p>Logged in as {{user['username']}}#{{user['discriminator']}}</p>
            <a href="/logout">Logout</a><br/>
            <a href="/guilds">My Guilds</a>
        {% else %}
            <a href="/login">Login with Discord</a>
        {% endif %}
        <p>Bot invite: <a href="{{bot_invite}}">{{bot_invite}}</a></p>
        ''', user=user, bot_invite=BOT_INVITE)

@app.route('/login')
def login():
    return redirect(DISCORD_OAUTH_URL)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Missing code', 400
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify guilds'
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    if r.status_code != 200:
        return 'OAuth token exchange failed: ' + r.text, 400
    token = r.json()
    me = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f"Bearer {token['access_token']}"})
    if me.status_code != 200:
        return 'Failed to fetch user', 400
    session['user'] = me.json()
    session['token'] = token
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/guilds')
def guilds():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    r = requests.get('https://discord.com/api/users/@me/guilds', headers={'Authorization': f"Bearer {token['access_token']}"})
    if r.status_code != 200:
        return 'Failed to fetch guilds', 400
    guilds = r.json()
    return render_template_string('<h2>Your Guilds</h2><ul>{% for g in guilds %}<li>{{g.name}} (id: {{g.id}})</li>{% endfor %}</ul>', guilds=guilds)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
