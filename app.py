"""Flask application exposing minimal crypto tax endpoints."""

import os
from flask import Flask, request, jsonify, render_template

from data import fetch_transactions, calculate_tax
from logger import log_run, log_divider

app = Flask(__name__)

# In-memory store for wallets in current session
wallets = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_address', methods=['POST'])
def add_address():
    data = request.get_json()
    address = data.get('address')
    chain = data.get('chain', 'ethereum')
    wallets.append({'address': address, 'chain': chain})
    log_run(f"Address added: {address} on {chain}")
    return jsonify({'status': 'ok', 'wallets': wallets})


@app.route('/fetch_transactions', methods=['POST'])
def fetch_txs():
    results = []
    for wallet in wallets:
        txs = fetch_transactions(wallet['address'], wallet['chain'])
        results.append({'address': wallet['address'], 'transactions': txs})
    log_run(f"Fetched transactions for {len(wallets)} addresses")
    return jsonify(results)


@app.route('/calculate', methods=['POST'])
def calculate():
    report = calculate_tax(wallets)
    log_run("Tax calculation requested")
    log_divider()
    return jsonify(report)


if __name__ == '__main__':
    app.run(debug=True)
