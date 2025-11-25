# Admin dashboard pages to manage per-guild settings stored in Postgres (improved UI)
from flask import Flask, session, redirect, url_for, request, render_template_string, jsonify
import os, psycopg2, json, requests
app = Flask(__name__)
app.secret_key = os.getenv('DASH_SECRET', 'change-me')

CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/callback')
BOT_INVITE = os.getenv('BOT_INVITE_URL', '')

def get_pg():
    dsn = os.getenv('PG_DSN', 'dbname=botdb user=bot password=botpass host=postgres')
    return psycopg2.connect(dsn)

@app.route('/guild/<int:guild_id>')
def guild_settings(guild_id):
    token = session.get('token')
    if not token:
        return redirect(url_for('index', _external=True))
    headers = {'Authorization': f"Bearer {token['access_token']}"}
    r = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)
    if r.status_code != 200:
        return 'Auth error', 400
    guilds = r.json()
    if not any(g['id']==str(guild_id) for g in guilds):
        return 'You are not in that guild or lack permissions', 403
    conn = get_pg(); cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS guild_settings(guild_id BIGINT PRIMARY KEY, settings JSONB DEFAULT %s)', (json.dumps({}),))
    cur.execute('SELECT settings FROM guild_settings WHERE guild_id=%s', (guild_id,))
    row = cur.fetchone()
    settings = row[0] if row else {}
    # fetch premium members for display
    cur.execute('CREATE TABLE IF NOT EXISTS premium_members(user_id BIGINT, guild_id BIGINT, stripe_session_id TEXT, PRIMARY KEY(user_id, guild_id))')
    cur.execute('SELECT user_id FROM premium_members WHERE guild_id=%s', (guild_id,))
    rows = cur.fetchall()
    premium_list = [r[0] for r in rows]
    cur.close(); conn.close()
    return render_template_string('''
        <h2>Settings for Guild {{guild_id}}</h2>
        <p>Invite link: <a href="{{bot_invite}}">{{bot_invite}}</a></p>
        <form method="post" action="/guild/{{guild_id}}/save">
        Premium role name: <input name="premium_role" value="{{settings.get('premium_role','Premium')}}"><br/>
        Automod enabled: <input type="checkbox" name="automod" {% if settings.get('automod', True) %}checked{% endif %}><br/>
        <button type="submit">Save</button>
        </form>
        <h3>Premium Members ({{premium_list|length}})</h3>
        <ul>{% for u in premium_list %}<li>{{u}}</li>{% endfor %}</ul>
        ''', guild_id=guild_id, settings=settings, premium_list=premium_list, bot_invite=BOT_INVITE)

@app.route('/guild/<int:guild_id>/save', methods=['POST'])
def guild_save(guild_id):
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    premium_role = request.form.get('premium_role', 'Premium')
    automod = True if request.form.get('automod')=='on' else False
    conn = get_pg(); cur = conn.cursor()
    cur.execute('INSERT INTO guild_settings(guild_id, settings) VALUES(%s,%s) ON CONFLICT (guild_id) DO UPDATE SET settings=EXCLUDED.settings', (guild_id, json.dumps({'premium_role': premium_role, 'automod': automod})))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('guild_settings', guild_id=guild_id))

if __name__ == '__main__':
    app.run(port=5002)
