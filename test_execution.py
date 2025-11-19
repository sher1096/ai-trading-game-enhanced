import sys
sys.path.insert(0, 'E:/code/nof1_enhanced')

from database import Database
from market_data import MarketDataFetcher
from ai_trader_enhanced import EnhancedAITrader
from trading_engine import TradingEngine

# 初始化
db = Database()
market_fetcher = MarketDataFetcher()

# 获取模型1的信息
model = db.get_model(1)
if not model:
    print("Model 1 not found!")
    sys.exit(1)

print(f"Model: {model}")

# 获取provider信息
provider = db.get_provider(model['provider_id'])
if not provider:
    print(f"Provider {model['provider_id']} not found!")
    sys.exit(1)

print(f"Provider: {provider['name']}")

# 创建交易引擎
ai_trader = EnhancedAITrader(
    api_key=provider['api_key'],
    api_url=provider['api_url'],
    model_name=model['model_name']
)

engine = TradingEngine(
    model_id=1,
    db=db,
    market_fetcher=market_fetcher,
    ai_trader=ai_trader,
    trade_fee_rate=0.001
)

print("\n===== Executing Trading Cycle =====")
try:
    result = engine.execute_trading_cycle()
    print(f"\nResult: {result}")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

# 检查数据库
print("\n===== Checking Database =====")
trades = db.get_trades(1, 10)
print(f"Total trades for model 1: {len(trades)}")
for trade in trades:
    print(f"  {trade}")

portfolio = db.get_portfolio(1, {'BTC': {'price': 40000}, 'ETH': {'price': 2500}, 'SOL': {'price': 100}})
print(f"\nPortfolio: cash=${portfolio['cash']:.2f}, total=${portfolio['total_value']:.2f}")
print(f"Positions: {len(portfolio['positions'])}")
for pos in portfolio['positions']:
    print(f"  {pos}")
