from flask import Flask, request, jsonify
import json
import time
import os

app = Flask(__name__)
KEYS_FILE = 'keys.json'

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE, 'r') as f:
        return json.load(f)

@app.route('/validate')
def validate():
    key = request.args.get('key')
    hwid = request.args.get('hwid')

    if not key or not hwid:
        return jsonify({'valid': False, 'message': 'Missing key or hwid'})

    keys = load_keys()
    data = keys.get(key)

    if not data:
        return jsonify({'valid': False, 'message': 'Invalid key'})

    if data['hwid'] != 'any' and data['hwid'] != hwid:
        return jsonify({'valid': False, 'message': 'Key not linked to your HWID'})

    if data['keyType'] == 'monthly':
        now = int(time.time())
        expiry = data['created'] + 30 * 24 * 60 * 60
        if now > expiry:
            return jsonify({'valid': False, 'message': 'Key expired'})
        days_left = (expiry - now) // 86400
        return jsonify({'valid': True, 'message': f'Monthly - {days_left} days left', 'keyType': 'monthly'})

    return jsonify({'valid': True, 'message': 'Lifetime key', 'keyType': 'lifetime'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)