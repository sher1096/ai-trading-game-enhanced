"""
Initialize comprehensive coin library with categories and popularity data
币种库初始化 - 包含分类和热度信息
"""
import sqlite3
from datetime import datetime

# 完整的币种库数据 - 按分类组织
COIN_LIBRARY = {
    "Layer1": [
        # 一线公链
        {"symbol": "BTC", "name": "Bitcoin", "binance": "BTCUSDT", "okx": "BTC-USDT", "coingecko": "bitcoin", "rank": 1, "popularity": "极高", "24h_volume": "500亿+"},
        {"symbol": "ETH", "name": "Ethereum", "binance": "ETHUSDT", "okx": "ETH-USDT", "coingecko": "ethereum", "rank": 2, "popularity": "极高", "24h_volume": "200亿+"},
        {"symbol": "SOL", "name": "Solana", "binance": "SOLUSDT", "okx": "SOL-USDT", "coingecko": "solana", "rank": 5, "popularity": "极高", "24h_volume": "50亿+"},
        {"symbol": "ADA", "name": "Cardano", "binance": "ADAUSDT", "okx": "ADA-USDT", "coingecko": "cardano", "rank": 9, "popularity": "高", "24h_volume": "10亿+"},
        {"symbol": "AVAX", "name": "Avalanche", "binance": "AVAXUSDT", "okx": "AVAX-USDT", "coingecko": "avalanche-2", "rank": 15, "popularity": "高", "24h_volume": "8亿+"},
        {"symbol": "DOT", "name": "Polkadot", "binance": "DOTUSDT", "okx": "DOT-USDT", "coingecko": "polkadot", "rank": 12, "popularity": "高", "24h_volume": "5亿+"},
        {"symbol": "ATOM", "name": "Cosmos", "binance": "ATOMUSDT", "okx": "ATOM-USDT", "coingecko": "cosmos", "rank": 18, "popularity": "中", "24h_volume": "3亿+"},
        {"symbol": "NEAR", "name": "NEAR Protocol", "binance": "NEARUSDT", "okx": "NEAR-USDT", "coingecko": "near", "rank": 27, "popularity": "中", "24h_volume": "2亿+"},
        {"symbol": "APT", "name": "Aptos", "binance": "APTUSDT", "okx": "APT-USDT", "coingecko": "aptos", "rank": 22, "popularity": "高", "24h_volume": "4亿+"},
        {"symbol": "SUI", "name": "Sui", "binance": "SUIUSDT", "okx": "SUI-USDT", "coingecko": "sui", "rank": 23, "popularity": "高", "24h_volume": "3亿+"},
        {"symbol": "TRX", "name": "TRON", "binance": "TRXUSDT", "okx": "TRX-USDT", "coingecko": "tron", "rank": 11, "popularity": "高", "24h_volume": "6亿+"},
        {"symbol": "TON", "name": "Toncoin", "binance": "TONUSDT", "okx": "TON-USDT", "coingecko": "the-open-network", "rank": 8, "popularity": "极高", "24h_volume": "5亿+"},
        {"symbol": "HBAR", "name": "Hedera", "binance": "HBARUSDT", "okx": "HBAR-USDT", "coingecko": "hedera-hashgraph", "rank": 29, "popularity": "中", "24h_volume": "1亿+"},
        {"symbol": "FTM", "name": "Fantom", "binance": "FTMUSDT", "okx": "FTM-USDT", "coingecko": "fantom", "rank": 35, "popularity": "中", "24h_volume": "1亿+"},
    ],

    "Layer2": [
        # 二层扩容
        {"symbol": "MATIC", "name": "Polygon", "binance": "MATICUSDT", "okx": "MATIC-USDT", "coingecko": "matic-network", "rank": 13, "popularity": "极高", "24h_volume": "5亿+"},
        {"symbol": "ARB", "name": "Arbitrum", "binance": "ARBUSDT", "okx": "ARB-USDT", "coingecko": "arbitrum", "rank": 20, "popularity": "高", "24h_volume": "3亿+"},
        {"symbol": "OP", "name": "Optimism", "binance": "OPUSDT", "okx": "OP-USDT", "coingecko": "optimism", "rank": 24, "popularity": "高", "24h_volume": "2亿+"},
        {"symbol": "IMX", "name": "Immutable X", "binance": "IMXUSDT", "okx": "IMX-USDT", "coingecko": "immutable-x", "rank": 40, "popularity": "中", "24h_volume": "500M+"},
    ],

    "DeFi": [
        # DeFi 协议
        {"symbol": "UNI", "name": "Uniswap", "binance": "UNIUSDT", "okx": "UNI-USDT", "coingecko": "uniswap", "rank": 16, "popularity": "极高", "24h_volume": "3亿+"},
        {"symbol": "LINK", "name": "Chainlink", "binance": "LINKUSDT", "okx": "LINK-USDT", "coingecko": "chainlink", "rank": 14, "popularity": "极高", "24h_volume": "4亿+"},
        {"symbol": "AAVE", "name": "Aave", "binance": "AAVEUSDT", "okx": "AAVE-USDT", "coingecko": "aave", "rank": 30, "popularity": "高", "24h_volume": "1亿+"},
        {"symbol": "MKR", "name": "Maker", "binance": "MKRUSDT", "okx": "MKR-USDT", "coingecko": "maker", "rank": 32, "popularity": "高", "24h_volume": "800M+"},
        {"symbol": "COMP", "name": "Compound", "binance": "COMPUSDT", "okx": "COMP-USDT", "coingecko": "compound-governance-token", "rank": 45, "popularity": "中", "24h_volume": "500M+"},
        {"symbol": "CRV", "name": "Curve DAO", "binance": "CRVUSDT", "okx": "CRV-USDT", "coingecko": "curve-dao-token", "rank": 50, "popularity": "中", "24h_volume": "400M+"},
        {"symbol": "SUSHI", "name": "SushiSwap", "binance": "SUSHIUSDT", "okx": "SUSHI-USDT", "coingecko": "sushi", "rank": 55, "popularity": "中", "24h_volume": "300M+"},
        {"symbol": "INJ", "name": "Injective", "binance": "INJUSDT", "okx": "INJ-USDT", "coingecko": "injective-protocol", "rank": 28, "popularity": "高", "24h_volume": "2亿+"},
        {"symbol": "SNX", "name": "Synthetix", "binance": "SNXUSDT", "okx": "SNX-USDT", "coingecko": "synthetix-network-token", "rank": 60, "popularity": "中", "24h_volume": "200M+"},
    ],

    "Exchange": [
        # 交易所代币
        {"symbol": "BNB", "name": "BNB", "binance": "BNBUSDT", "okx": "BNB-USDT", "coingecko": "binancecoin", "rank": 4, "popularity": "极高", "24h_volume": "30亿+"},
        {"symbol": "OKB", "name": "OKB", "binance": "OKBUSDT", "okx": "OKB-USDT", "coingecko": "okb", "rank": 38, "popularity": "高", "24h_volume": "500M+"},
        {"symbol": "CRO", "name": "Cronos", "binance": "CROUSDT", "okx": "CRO-USDT", "coingecko": "crypto-com-chain", "rank": 42, "popularity": "中", "24h_volume": "400M+"},
    ],

    "Meme": [
        # Meme 币
        {"symbol": "DOGE", "name": "Dogecoin", "binance": "DOGEUSDT", "okx": "DOGE-USDT", "coingecko": "dogecoin", "rank": 10, "popularity": "极高", "24h_volume": "10亿+"},
        {"symbol": "SHIB", "name": "Shiba Inu", "binance": "SHIBUSDT", "okx": "SHIB-USDT", "coingecko": "shiba-inu", "rank": 21, "popularity": "极高", "24h_volume": "5亿+"},
        {"symbol": "PEPE", "name": "Pepe", "binance": "PEPEUSDT", "okx": "PEPE-USDT", "coingecko": "pepe", "rank": 25, "popularity": "高", "24h_volume": "3亿+"},
        {"symbol": "WIF", "name": "dogwifhat", "binance": "WIFUSDT", "okx": "WIF-USDT", "coingecko": "dogwifhat", "rank": 26, "popularity": "高", "24h_volume": "2亿+"},
        {"symbol": "FLOKI", "name": "FLOKI", "binance": "FLOKIUSDT", "okx": "FLOKI-USDT", "coingecko": "floki", "rank": 48, "popularity": "中", "24h_volume": "500M+"},
        {"symbol": "BONK", "name": "Bonk", "binance": "BONKUSDT", "okx": "BONK-USDT", "coingecko": "bonk", "rank": 52, "popularity": "中", "24h_volume": "400M+"},
    ],

    "Payment": [
        # 支付类
        {"symbol": "XRP", "name": "Ripple", "binance": "XRPUSDT", "okx": "XRP-USDT", "coingecko": "ripple", "rank": 6, "popularity": "极高", "24h_volume": "20亿+"},
        {"symbol": "LTC", "name": "Litecoin", "binance": "LTCUSDT", "okx": "LTC-USDT", "coingecko": "litecoin", "rank": 17, "popularity": "高", "24h_volume": "4亿+"},
        {"symbol": "XLM", "name": "Stellar", "binance": "XLMUSDT", "okx": "XLM-USDT", "coingecko": "stellar", "rank": 33, "popularity": "中", "24h_volume": "800M+"},
        {"symbol": "BCH", "name": "Bitcoin Cash", "binance": "BCHUSDT", "okx": "BCH-USDT", "coingecko": "bitcoin-cash", "rank": 19, "popularity": "高", "24h_volume": "3亿+"},
    ],

    "Storage": [
        # 存储类
        {"symbol": "FIL", "name": "Filecoin", "binance": "FILUSDT", "okx": "FIL-USDT", "coingecko": "filecoin", "rank": 19, "popularity": "高", "24h_volume": "2亿+"},
        {"symbol": "AR", "name": "Arweave", "binance": "ARUSDT", "okx": "AR-USDT", "coingecko": "arweave", "rank": 44, "popularity": "中", "24h_volume": "500M+"},
    ],

    "Oracle": [
        # 预言机
        {"symbol": "LINK", "name": "Chainlink", "binance": "LINKUSDT", "okx": "LINK-USDT", "coingecko": "chainlink", "rank": 14, "popularity": "极高", "24h_volume": "4亿+"},
        {"symbol": "BAND", "name": "Band Protocol", "binance": "BANDUSDT", "okx": "BAND-USDT", "coingecko": "band-protocol", "rank": 65, "popularity": "低", "24h_volume": "100M+"},
    ],

    "Gaming": [
        # 游戏/元宇宙
        {"symbol": "SAND", "name": "The Sandbox", "binance": "SANDUSDT", "okx": "SAND-USDT", "coingecko": "the-sandbox", "rank": 47, "popularity": "中", "24h_volume": "500M+"},
        {"symbol": "MANA", "name": "Decentraland", "binance": "MANAUSDT", "okx": "MANA-USDT", "coingecko": "decentraland", "rank": 49, "popularity": "中", "24h_volume": "400M+"},
        {"symbol": "AXS", "name": "Axie Infinity", "binance": "AXSUSDT", "okx": "AXS-USDT", "coingecko": "axie-infinity", "rank": 51, "popularity": "中", "24h_volume": "300M+"},
        {"symbol": "GALA", "name": "Gala", "binance": "GALAUSDT", "okx": "GALA-USDT", "coingecko": "gala", "rank": 53, "popularity": "中", "24h_volume": "200M+"},
    ],

    "AI": [
        # AI 相关
        {"symbol": "RNDR", "name": "Render Token", "binance": "RNDRUSDT", "okx": "RNDR-USDT", "coingecko": "render-token", "rank": 36, "popularity": "高", "24h_volume": "1亿+"},
        {"symbol": "FET", "name": "Fetch.ai", "binance": "FETUSDT", "okx": "FET-USDT", "coingecko": "fetch-ai", "rank": 41, "popularity": "中", "24h_volume": "500M+"},
        {"symbol": "AGIX", "name": "SingularityNET", "binance": "AGIXUSDT", "okx": "AGIX-USDT", "coingecko": "singularitynet", "rank": 43, "popularity": "中", "24h_volume": "400M+"},
    ],
}

def initialize_database():
    """初始化币种库到数据库"""
    conn = sqlite3.connect('AITradeGame.db')
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("初始化币种库 - Comprehensive Coin Library")
    print("="*70)

    total_added = 0
    total_skipped = 0

    for category, coins in COIN_LIBRARY.items():
        print(f"\n[{category}] 分类 - 共 {len(coins)} 个币种")

        for coin in coins:
            try:
                # 检查是否已存在
                cursor.execute('SELECT id FROM coins WHERE symbol = ?', (coin['symbol'],))
                existing = cursor.fetchone()

                if existing:
                    print(f"  [SKIP] {coin['symbol']:8s} - 已存在")
                    total_skipped += 1
                else:
                    # 插入新币种
                    cursor.execute('''
                        INSERT INTO coins (
                            symbol, name, category,
                            binance_symbol, okx_symbol, coingecko_id,
                            market_cap_rank, is_active,
                            created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                    ''', (
                        coin['symbol'],
                        coin['name'],
                        category,
                        coin['binance'],
                        coin['okx'],
                        coin['coingecko'],
                        coin['rank'],
                        datetime.now().isoformat()
                    ))

                    print(f"  [OK]   {coin['symbol']:8s} - {coin['name']:20s} | 热度: {coin['popularity']:4s} | 24h: {coin['24h_volume']}")
                    total_added += 1

            except Exception as e:
                print(f"  [ERROR] {coin['symbol']:8s} - {e}")

    conn.commit()
    conn.close()

    print("\n" + "="*70)
    print(f"[完成] 币种库初始化完成!")
    print("="*70)
    print(f"新增: {total_added} | 跳过: {total_skipped} | 总计: {total_added + total_skipped}")

    # 分类统计
    print(f"\n分类统计:")
    for category, coins in COIN_LIBRARY.items():
        print(f"  {category:15s}: {len(coins):3d} 个币种")

    return total_added, total_skipped

def show_statistics():
    """显示币种库统计信息"""
    conn = sqlite3.connect('AITradeGame.db')
    cursor = conn.cursor()

    print("\n" + "="*70)
    print("数据库统计")
    print("="*70)

    # 总币种数
    cursor.execute('SELECT COUNT(*) FROM coins WHERE is_active = 1')
    total = cursor.fetchone()[0]
    print(f"\n总币种数: {total}")

    # 按分类统计
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM coins
        WHERE is_active = 1
        GROUP BY category
        ORDER BY count DESC
    ''')

    print(f"\n按分类分布:")
    for row in cursor.fetchall():
        print(f"  {row[0]:15s}: {row[1]:3d} 个")

    # 按市值排名前10
    cursor.execute('''
        SELECT symbol, name, category, market_cap_rank
        FROM coins
        WHERE is_active = 1
        ORDER BY market_cap_rank
        LIMIT 10
    ''')

    print(f"\n市值排名前10:")
    for row in cursor.fetchall():
        print(f"  #{row[3]:3d} {row[0]:8s} - {row[1]:20s} ({row[2]})")

    conn.close()

if __name__ == '__main__':
    try:
        print("\n开始初始化币种库...")
        added, skipped = initialize_database()

        if added > 0 or skipped > 0:
            show_statistics()

        print(f"\n访问币种管理页面查看完整币种库:")
        print(f"  http://localhost:5000/coins-management")

    except Exception as e:
        print(f"\n[ERROR] 初始化失败: {e}")
        import traceback
        traceback.print_exc()
