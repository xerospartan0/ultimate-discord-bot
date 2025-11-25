# Stripe webhook handler (enhanced): grants premium by writing to Postgres mapping table.
from flask import Flask, request, jsonify
import stripe, os, json, psycopg2
app = Flask(__name__)
stripe.api_key = os.getenv('STRIPE_API_KEY')

endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRET', '')

def get_pg_conn():
    dsn = os.getenv('PG_DSN', 'dbname=botdb user=bot password=botpass host=postgres')
    return psycopg2.connect(dsn)

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', '')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        client_ref = session.get('client_reference_id')
        if client_ref:
            try:
                info = json.loads(client_ref)
                user_id = info.get('user_id')
                guild_id = info.get('guild_id')
                # write to pg premium table
                conn = get_pg_conn()
                cur = conn.cursor()
                cur.execute('CREATE TABLE IF NOT EXISTS premium_members(user_id BIGINT, guild_id BIGINT, stripe_session_id TEXT, PRIMARY KEY(user_id, guild_id))')
                cur.execute('INSERT INTO premium_members(user_id, guild_id, stripe_session_id) VALUES(%s,%s,%s) ON CONFLICT (user_id,guild_id) DO UPDATE SET stripe_session_id=EXCLUDED.stripe_session_id', (user_id, guild_id, session.get('id')))
                conn.commit(); cur.close(); conn.close()
                print('Granted premium for', user_id, 'in guild', guild_id)
            except Exception as e:
                print('Error processing client_ref:', e)
    return jsonify({'status': 'ok'})
