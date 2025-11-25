# Stripe checkout creation endpoint (template)
# Creates a Checkout Session and stores client_reference_id to map to guild/user
from flask import Flask, request, jsonify, redirect, url_for
import stripe, os, json
app = Flask(__name__)
stripe.api_key = os.getenv('STRIPE_API_KEY')

# Example products/prices should be set in Stripe dashboard.
PRICE_ID_PREMIUM = os.getenv('STRIPE_PRICE_PREMIUM', '')

@app.route('/create_checkout', methods=['POST'])
def create_checkout():
    data = request.json or {}
    customer_id = data.get('customer_id')  # optional mapping
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{'price': PRICE_ID_PREMIUM, 'quantity': 1}],
            success_url=os.getenv('CHECKOUT_SUCCESS_URL', 'http://localhost:5000/checkout_success'),
            cancel_url=os.getenv('CHECKOUT_CANCEL_URL', 'http://localhost:5000/checkout_cancel'),
            client_reference_id=json.dumps({'user_id': data.get('user_id'), 'guild_id': data.get('guild_id')})
        )
        return jsonify({'url': session.url})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/checkout_success')
def checkout_success():
    return 'Checkout succeeded (you can close this window).'

@app.route('/checkout_cancel')
def checkout_cancel():
    return 'Checkout canceled.'

if __name__ == '__main__':
    app.run(port=5001)
