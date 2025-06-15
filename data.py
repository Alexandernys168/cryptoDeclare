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
    if chain == "ethereum":
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
    elif chain == "solana":
        url = "https://api.solscan.io/account/transactions"
        params = {"address": address}
    else:
        raise ValueError("Unsupported chain")
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        log_run(f"{chain.capitalize()} API called for {address}")
        return data.get("result", [])
    except Exception as exc:
        log_run(f"{chain.capitalize()} API error: {exc}")
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


def process_transactions(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute gains and losses using the average cost method."""
    holdings: Dict[str, Dict[str, float]] = {}
    events: List[Dict[str, Any]] = []
    totals: Dict[str, float] = {}

    txs = sorted(transactions, key=lambda t: t.get("timestamp", 0))
    for tx in txs:
        cur = tx.get("currency")
        if not cur:
            log_run("Transaction missing currency field")
            continue
        holdings.setdefault(cur, {"qty": 0.0, "cost": 0.0})
        totals.setdefault(cur, 0.0)
        h = holdings[cur]
        typ = tx.get("type", "unknown").lower()
        qty = float(tx.get("amount", 0))
        sek_value = float(tx.get("sek_value", 0))

        if typ in {"buy", "incoming", "airdrop", "receive", "swap_in"}:
            h["qty"] += qty
            h["cost"] += sek_value
        elif typ in {"sell", "payment", "swap_out", "fee"}:
            avg = h["cost"] / h["qty"] if h["qty"] else 0
            cost_basis = avg * qty
            gain = sek_value - cost_basis
            events.append({
                "date": tx.get("timestamp"),
                "quantity": qty,
                "currency": cur,
                "selling_price": sek_value,
                "cost_basis": cost_basis,
                "gain_loss": gain,
                "hash": tx.get("tx_hash"),
            })
            totals[cur] += gain
            h["qty"] -= qty
            h["cost"] -= cost_basis
        else:
            log_run(f"Unknown tx type: {typ}")

    summary = [{"currency": c, "gain_loss": round(v, 2)} for c, v in totals.items()]
    return {"events": events, "summary": summary}


def calculate_tax(wallets: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Calculate tax reports for provided wallets."""
    report = []
    for wallet in wallets:
        txs = fetch_transactions(wallet["address"], wallet["chain"])
        processed = process_transactions(txs)
        entry = {
            "address": wallet["address"],
            "events": processed["events"],
            "summary": processed["summary"],
        }
        report.append(entry)
    log_run("Tax calculation executed")
    return report
