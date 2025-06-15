"""Data access and tax calculation utilities."""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests

from logger import log_run

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
COINGECKO_URL = "https://api.coingecko.com/api/v3"


def fetch_transactions(address: str, chain: str = "ethereum") -> List[Dict[str, Any]]:
    """Retrieve transactions for a given wallet address."""
    if chain != "ethereum":
        raise ValueError("Only Ethereum is currently supported")

    url = "https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        log_run(f"Etherscan API called for {address}")
        return data.get("result", [])
    except Exception as exc:
        log_run(f"Etherscan API error: {exc}")
        return []


def get_price_in_sek(coin_id: str, date: datetime) -> Optional[float]:
    """Fetch historical price in SEK from CoinGecko."""
    url = f"{COINGECKO_URL}/coins/{coin_id}/history"
    params = {"date": date.strftime("%d-%m-%Y"), "localization": "false"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data["market_data"]["current_price"]["sek"]
        log_run(f"CoinGecko price fetched for {coin_id} on {date.date()}")
        return price
    except Exception as exc:
        log_run(f"CoinGecko API error: {exc}")
        return None


def calculate_tax(wallets: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Placeholder tax calculation using transaction count."""
    report = []
    for wallet in wallets:
        txs = fetch_transactions(wallet["address"], wallet["chain"])
        entry = {
            "address": wallet["address"],
            "total_transactions": len(txs),
        }
        report.append(entry)
    log_run("Tax calculation executed (placeholder)")
    return report
