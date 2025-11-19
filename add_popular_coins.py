"""
Pre-populate database with popular Binance trading pairs
"""
import requests

BASE_URL = 'http://localhost:5000'

# Popular Binance coins by market cap and trading volume
POPULAR_COINS = [
    # Top 10 by market cap (some already exist)
    {'symbol': 'BTC', 'name': 'Bitcoin', 'category': 'Layer1', 'binance_symbol': 'BTCUSDT', 'okx_symbol': 'BTC-USDT', 'coingecko_id': 'bitcoin', 'market_cap_rank': 1},
    {'symbol': 'ETH', 'name': 'Ethereum', 'category': 'Layer1', 'binance_symbol': 'ETHUSDT', 'okx_symbol': 'ETH-USDT', 'coingecko_id': 'ethereum', 'market_cap_rank': 2},
    {'symbol': 'BNB', 'name': 'BNB', 'category': 'Exchange', 'binance_symbol': 'BNBUSDT', 'okx_symbol': 'BNB-USDT', 'coingecko_id': 'binancecoin', 'market_cap_rank': 4},
    {'symbol': 'SOL', 'name': 'Solana', 'category': 'Layer1', 'binance_symbol': 'SOLUSDT', 'okx_symbol': 'SOL-USDT', 'coingecko_id': 'solana', 'market_cap_rank': 5},
    {'symbol': 'XRP', 'name': 'Ripple', 'category': 'Payment', 'binance_symbol': 'XRPUSDT', 'okx_symbol': 'XRP-USDT', 'coingecko_id': 'ripple', 'market_cap_rank': 6},
    {'symbol': 'ADA', 'name': 'Cardano', 'category': 'Layer1', 'binance_symbol': 'ADAUSDT', 'okx_symbol': 'ADA-USDT', 'coingecko_id': 'cardano', 'market_cap_rank': 9},
    {'symbol': 'DOGE', 'name': 'Dogecoin', 'category': 'Meme', 'binance_symbol': 'DOGEUSDT', 'okx_symbol': 'DOGE-USDT', 'coingecko_id': 'dogecoin', 'market_cap_rank': 10},
    {'symbol': 'DOT', 'name': 'Polkadot', 'category': 'Layer1', 'binance_symbol': 'DOTUSDT', 'okx_symbol': 'DOT-USDT', 'coingecko_id': 'polkadot', 'market_cap_rank': 12},

    # Additional popular trading pairs
    {'symbol': 'MATIC', 'name': 'Polygon', 'category': 'Layer2', 'binance_symbol': 'MATICUSDT', 'okx_symbol': 'MATIC-USDT', 'coingecko_id': 'matic-network', 'market_cap_rank': 13},
    {'symbol': 'LINK', 'name': 'Chainlink', 'category': 'Oracle', 'binance_symbol': 'LINKUSDT', 'okx_symbol': 'LINK-USDT', 'coingecko_id': 'chainlink', 'market_cap_rank': 14},
    {'symbol': 'AVAX', 'name': 'Avalanche', 'category': 'Layer1', 'binance_symbol': 'AVAXUSDT', 'okx_symbol': 'AVAX-USDT', 'coingecko_id': 'avalanche-2', 'market_cap_rank': 15},
    {'symbol': 'UNI', 'name': 'Uniswap', 'category': 'DeFi', 'binance_symbol': 'UNIUSDT', 'okx_symbol': 'UNI-USDT', 'coingecko_id': 'uniswap', 'market_cap_rank': 16},
    {'symbol': 'LTC', 'name': 'Litecoin', 'category': 'Layer1', 'binance_symbol': 'LTCUSDT', 'okx_symbol': 'LTC-USDT', 'coingecko_id': 'litecoin', 'market_cap_rank': 17},
    {'symbol': 'ATOM', 'name': 'Cosmos', 'category': 'Layer1', 'binance_symbol': 'ATOMUSDT', 'okx_symbol': 'ATOM-USDT', 'coingecko_id': 'cosmos', 'market_cap_rank': 18},
    {'symbol': 'FIL', 'name': 'Filecoin', 'category': 'Storage', 'binance_symbol': 'FILUSDT', 'okx_symbol': 'FIL-USDT', 'coingecko_id': 'filecoin', 'market_cap_rank': 19},
    {'symbol': 'ARB', 'name': 'Arbitrum', 'category': 'Layer2', 'binance_symbol': 'ARBUSDT', 'okx_symbol': 'ARB-USDT', 'coingecko_id': 'arbitrum', 'market_cap_rank': 20},

    # High volume trading pairs
    {'symbol': 'SHIB', 'name': 'Shiba Inu', 'category': 'Meme', 'binance_symbol': 'SHIBUSDT', 'okx_symbol': 'SHIB-USDT', 'coingecko_id': 'shiba-inu', 'market_cap_rank': 21},
    {'symbol': 'APT', 'name': 'Aptos', 'category': 'Layer1', 'binance_symbol': 'APTUSDT', 'okx_symbol': 'APT-USDT', 'coingecko_id': 'aptos', 'market_cap_rank': 22},
    {'symbol': 'SUI', 'name': 'Sui', 'category': 'Layer1', 'binance_symbol': 'SUIUSDT', 'okx_symbol': 'SUI-USDT', 'coingecko_id': 'sui', 'market_cap_rank': 23},
    {'symbol': 'OP', 'name': 'Optimism', 'category': 'Layer2', 'binance_symbol': 'OPUSDT', 'okx_symbol': 'OP-USDT', 'coingecko_id': 'optimism', 'market_cap_rank': 24},
    {'symbol': 'PEPE', 'name': 'Pepe', 'category': 'Meme', 'binance_symbol': 'PEPEUSDT', 'okx_symbol': 'PEPE-USDT', 'coingecko_id': 'pepe', 'market_cap_rank': 25},
    {'symbol': 'WIF', 'name': 'dogwifhat', 'category': 'Meme', 'binance_symbol': 'WIFUSDT', 'okx_symbol': 'WIF-USDT', 'coingecko_id': 'dogwifhat', 'market_cap_rank': 26},
    {'symbol': 'TRX', 'name': 'TRON', 'category': 'Layer1', 'binance_symbol': 'TRXUSDT', 'okx_symbol': 'TRX-USDT', 'coingecko_id': 'tron', 'market_cap_rank': 11},
    {'symbol': 'NEAR', 'name': 'NEAR Protocol', 'category': 'Layer1', 'binance_symbol': 'NEARUSDT', 'okx_symbol': 'NEAR-USDT', 'coingecko_id': 'near', 'market_cap_rank': 27},
    {'symbol': 'INJ', 'name': 'Injective', 'category': 'DeFi', 'binance_symbol': 'INJUSDT', 'okx_symbol': 'INJ-USDT', 'coingecko_id': 'injective-protocol', 'market_cap_rank': 28},
    {'symbol': 'HBAR', 'name': 'Hedera', 'category': 'Layer1', 'binance_symbol': 'HBARUSDT', 'okx_symbol': 'HBAR-USDT', 'coingecko_id': 'hedera-hashgraph', 'market_cap_rank': 29},
]

def add_coins():
    """Add all popular coins to the database"""
    print("\n" + "="*70)
    print("Adding popular Binance trading pairs to database")
    print("="*70)

    added = 0
    skipped = 0
    errors = 0

    for coin in POPULAR_COINS:
        print(f"\n[{POPULAR_COINS.index(coin)+1}/{len(POPULAR_COINS)}] Adding {coin['symbol']} ({coin['name']})...")

        try:
            response = requests.post(f'{BASE_URL}/api/coins', json=coin, timeout=5)

            if response.status_code == 201:
                print(f"  [OK] Added - Rank #{coin['market_cap_rank']}")
                added += 1
            elif response.status_code == 409:
                print(f"  [INFO] Already exists - skipped")
                skipped += 1
            elif response.status_code == 500:
                # Try to check if it already exists
                check_response = requests.get(f'{BASE_URL}/api/coins')
                if check_response.status_code == 200:
                    coins = check_response.json()
                    if any(c['symbol'] == coin['symbol'] for c in coins):
                        print(f"  [INFO] Already exists - skipped")
                        skipped += 1
                    else:
                        print(f"  [WARN] Error 500 - possible database lock")
                        errors += 1
            else:
                print(f"  [ERROR] Failed - status code: {response.status_code}")
                errors += 1

        except requests.exceptions.ConnectionError:
            print(f"  [ERROR] Cannot connect to server - please ensure Flask server is running")
            return False
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
            errors += 1

    print("\n" + "="*70)
    print("[OK] Complete!")
    print("="*70)
    print(f"Added: {added} | Skipped: {skipped} | Errors: {errors}")
    print(f"Total coins: {added + skipped}")

    return True

if __name__ == '__main__':
    try:
        success = add_coins()
        if success:
            print("\nVisit coin management page to view all coins:")
            print(f"  >> {BASE_URL}/coins-management")
    except KeyboardInterrupt:
        print("\n\nOperation cancelled")
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {e}")
        import traceback
        traceback.print_exc()
