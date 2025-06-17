import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data import process_transactions


def test_process_transactions_example():
    txs = [
        {"timestamp": 1, "type": "buy", "currency": "DOGE", "amount": 10, "sek_value": 10000, "tx_hash": "a"},
        {"timestamp": 2, "type": "buy", "currency": "DOGE", "amount": 10, "sek_value": 50000, "tx_hash": "b"},
        {"timestamp": 3, "type": "sell", "currency": "DOGE", "amount": 15, "sek_value": 60000, "tx_hash": "c"},
        {"timestamp": 4, "type": "buy", "currency": "DOGE", "amount": 5, "sek_value": 25000, "tx_hash": "d"},
    ]
    result = process_transactions(txs)
    summary = result["summary"][0]
    assert summary["currency"] == "DOGE"
    assert round(summary["gain_loss"], 2) == 15000
