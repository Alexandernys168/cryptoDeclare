# Crypto Declare

Prototype web service for calculating Swedish crypto taxes.
Ethereum and Solana wallets are supported. Solana data is fetched using the
official JSON-RPC API at `https://api.mainnet-beta.solana.com`.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set required environment variables:
   ```bash
   export ETHERSCAN_API_KEY=<your key>
   ```
3. Run the application:
   ```bash
   python app.py
   ```

API calls and calculations are logged in `logg.md`.

