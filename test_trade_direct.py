"""
Direct test of trading execution without AI
"""
import sys
sys.path.insert(0, 'E:/code/nof1_enhanced')

from database import Database
from market_data import MarketDataFetcher
from trading_engine import TradingEngine

# 初始化
db = Database()
market_fetcher = MarketDataFetcher()

# 创建一个简化的交易引擎（不需要AI）
class SimpleTradingEngine:
    def __init__(self, model_id, db, market_fetcher):
        self.model_id = model_id
        self.db = db
        self.market_fetcher = market_fetcher
        self.trade_fee_rate = 0.001

    def test_buy(self):
        """测试买入并记录交易"""
        print("\n===== Testing Direct Buy Execution =====")

        # 模拟市场数据
        coin = 'BTC'
        quantity = 0.01
        price = 93000.0
        leverage = 2

        # 获取当前组合
        # 需要包含所有可能的币种价格，因为可能有其他持仓
        current_prices = {
            'BTC': price,
            'ETH': 3100.0,
            'SOL': 130.0,
            'BNB': 600.0,
            'XRP': 0.5,
            'DOGE': 0.08
        }
        portfolio = self.db.get_portfolio(self.model_id, current_prices)
        print(f"Before: Cash=${portfolio['cash']:.2f}")

        # 计算费用
        trade_amount = quantity * price
        trade_fee = trade_amount * self.trade_fee_rate
        required_margin = (quantity * price) / leverage
        total_required = required_margin + trade_fee

        print(f"Trade amount: ${trade_amount:.2f}")
        print(f"Trade fee: ${trade_fee:.2f}")
        print(f"Required margin: ${required_margin:.2f}")
        print(f"Total required: ${total_required:.2f}")

        if total_required > portfolio['cash']:
            print(f"ERROR: Insufficient cash!")
            return False

        try:
            # 步骤1: 更新持仓
            print(f"\n[1] Calling update_position...")
            self.db.update_position(
                self.model_id, coin, quantity, price, leverage, 'long'
            )
            print(f"[1] update_position SUCCESS")

            # 步骤2: 记录交易
            print(f"\n[2] Calling add_trade...")
            self.db.add_trade(
                self.model_id, coin, 'buy_to_enter', quantity,
                price, leverage, 'long', pnl=0, fee=trade_fee
            )
            print(f"[2] add_trade SUCCESS")

            # 验证
            print(f"\n[3] Verifying...")
            trades = self.db.get_trades(self.model_id, 10)
            print(f"Total trades: {len(trades)}")
            if trades:
                for trade in trades:
                    print(f"  Trade: {trade['coin']} {trade['signal']} qty={trade['quantity']} fee=${trade['fee']:.2f}")

            portfolio_after = self.db.get_portfolio(self.model_id, current_prices)
            print(f"\nAfter: Cash=${portfolio_after['cash']:.2f}")
            print(f"Positions: {len(portfolio_after['positions'])}")
            for pos in portfolio_after['positions']:
                print(f"  {pos['coin']}: {pos['quantity']} @ ${pos['avg_price']:.2f}")

            return True

        except Exception as e:
            print(f"\nEXCEPTION: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

# 运行测试
engine = SimpleTradingEngine(model_id=1, db=db, market_fetcher=market_fetcher)
success = engine.test_buy()

print(f"\n===== Test Result: {'SUCCESS' if success else 'FAILED'} =====")
