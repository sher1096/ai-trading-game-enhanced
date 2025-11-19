from datetime import datetime
from typing import Dict
import json

class TradingEngine:
    def __init__(self, model_id: int, db, market_fetcher, ai_trader, trade_fee_rate: float = 0.001, live_executor=None):
        self.model_id = model_id
        self.db = db
        self.market_fetcher = market_fetcher
        self.ai_trader = ai_trader
        self.coins = self._load_model_coins()  # 从数据库加载模型的币种池
        self.trade_fee_rate = trade_fee_rate  # 从配置中传入费率
        self.live_executor = live_executor  # 实盘交易执行器

    def _load_model_coins(self):
        """从数据库加载该模型启用的币种列表"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.symbol
                FROM model_coin_pools mcp
                JOIN coins c ON mcp.coin_id = c.id
                WHERE mcp.model_id = ? AND mcp.is_enabled = 1 AND c.is_active = 1
                ORDER BY c.market_cap_rank ASC, c.symbol ASC
            """, (self.model_id,))

            coins = [row['symbol'] for row in cursor.fetchall()]
            conn.close()

            if not coins:
                print(f"[WARNING] Model {self.model_id} has no enabled coins, using default set")
                return ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']

            print(f"[INFO] Model {self.model_id} loaded {len(coins)} coins: {coins}")
            return coins

        except Exception as e:
            print(f"[ERROR] Failed to load coins for model {self.model_id}: {e}")
            print(f"[WARNING] Falling back to default coin set")
            return ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']

    def refresh_coins(self):
        """刷新币种列表（用于动态更新币种池）"""
        self.coins = self._load_model_coins()
    
    def execute_trading_cycle(self) -> Dict:
        try:
            market_state = self._get_market_state()
            
            current_prices = {coin: market_state[coin]['price'] for coin in market_state}
            
            portfolio = self.db.get_portfolio(self.model_id, current_prices)
            
            account_info = self._build_account_info(portfolio)
            
            decisions = self.ai_trader.make_decision(
                market_state, portfolio, account_info
            )
            
            self.db.add_conversation(
                self.model_id,
                user_prompt=self._format_prompt(market_state, portfolio, account_info),
                ai_response=json.dumps(decisions, ensure_ascii=False),
                cot_trace=''
            )
            
            execution_results = self._execute_decisions(decisions, market_state, portfolio)
            
            updated_portfolio = self.db.get_portfolio(self.model_id, current_prices)
            self.db.record_account_value(
                self.model_id,
                updated_portfolio['total_value'],
                updated_portfolio['cash'],
                updated_portfolio['positions_value']
            )
            
            return {
                'success': True,
                'decisions': decisions,
                'executions': execution_results,
                'portfolio': updated_portfolio
            }
            
        except Exception as e:
            print(f"[ERROR] Trading cycle failed (Model {self.model_id}): {e}")
            import traceback
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_market_state(self) -> Dict:
        market_state = {}
        prices = self.market_fetcher.get_current_prices(self.coins)
        
        for coin in self.coins:
            if coin in prices:
                market_state[coin] = prices[coin].copy()
                indicators = self.market_fetcher.calculate_technical_indicators(coin)
                market_state[coin]['indicators'] = indicators
        
        return market_state
    
    def _build_account_info(self, portfolio: Dict) -> Dict:
        model = self.db.get_model(self.model_id)
        initial_capital = model['initial_capital']
        total_value = portfolio['total_value']
        total_return = ((total_value - initial_capital) / initial_capital) * 100
        
        return {
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_return': total_return,
            'initial_capital': initial_capital
        }
    
    def _format_prompt(self, market_state: Dict, portfolio: Dict, 
                      account_info: Dict) -> str:
        return f"Market State: {len(market_state)} coins, Portfolio: {len(portfolio['positions'])} positions"
    
    def _execute_decisions(self, decisions: Dict, market_state: Dict,
                          portfolio: Dict) -> list:
        results = []

        for coin, decision in decisions.items():
            if coin not in self.coins:
                continue

            signal = decision.get('signal', '').lower()

            try:
                if signal == 'buy_to_enter':
                    result = self._execute_buy(coin, decision, market_state, portfolio)
                elif signal == 'sell_to_enter':
                    result = self._execute_sell(coin, decision, market_state, portfolio)
                elif signal == 'close_position':
                    result = self._execute_close(coin, decision, market_state, portfolio)
                elif signal == 'hold':
                    result = {'coin': coin, 'signal': 'hold', 'message': 'Hold position'}
                else:
                    result = {'coin': coin, 'error': f'Unknown signal: {signal}'}

                # 如果开启了实盘交易，同步执行到真实交易所
                if signal != 'hold' and 'error' not in result:
                    live_result = self._execute_live_trading(coin, signal, decision, market_state)
                    if live_result:
                        result['live_trading'] = live_result

                results.append(result)

            except Exception as e:
                print(f"[ERROR] Trading execution failed for {coin}: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                results.append({'coin': coin, 'error': str(e)})

        return results

    def _execute_live_trading(self, coin: str, signal: str, decision: Dict, market_state: Dict):
        """执行实盘交易"""
        # 检查是否启用实盘交易
        if not self.live_executor:
            return None

        try:
            model = self.db.get_model(self.model_id)
            if not model or not model.get('live_trading_enabled'):
                return None

            live_exchange = model.get('live_exchange')
            live_symbol = model.get('live_symbol', 'BTC/USDT')

            if not live_exchange:
                return {'success': False, 'message': '未配置实盘交易所'}

            # 将模拟交易信号转换为实盘信号格式
            live_signal = {
                'action': self._convert_to_live_action(signal),
                'confidence': int(decision.get('confidence', 75)),
                'reason': decision.get('reason', f'AI决策: {signal}')
            }

            # 执行实盘交易
            print(f"\n[实盘] Model {self.model_id} 执行: {live_exchange} {live_symbol} {live_signal['action']}")
            result = self.live_executor.execute_signal(live_exchange, live_symbol, live_signal)

            return result

        except Exception as e:
            print(f"[实盘错误] Model {self.model_id}: {e}")
            return {'success': False, 'error': str(e)}

    def _convert_to_live_action(self, signal: str) -> str:
        """将模拟信号转换为实盘操作"""
        if signal == 'buy_to_enter':
            return 'buy'
        elif signal == 'sell_to_enter':
            return 'sell'
        elif signal == 'close_position':
            return 'sell'  # 平仓等同于卖出
        else:
            return 'hold'
    
    def _execute_buy(self, coin: str, decision: Dict, market_state: Dict,
                    portfolio: Dict) -> Dict:
        quantity = float(decision.get('quantity', 0))
        leverage = int(decision.get('leverage', 1))
        price = market_state[coin]['price']

        if quantity <= 0:
            return {'coin': coin, 'error': 'Invalid quantity'}

        # 计算交易额和交易费（按交易额的比例）
        trade_amount = quantity * price  # 交易额
        trade_fee = trade_amount * self.trade_fee_rate  # 交易费（0.1%）
        required_margin = (quantity * price) / leverage  # 保证金

        # 总需资金 = 保证金 + 交易费
        total_required = required_margin + trade_fee
        if total_required > portfolio['cash']:
            return {'coin': coin, 'error': 'Insufficient cash (including fees)'}

        # 更新持仓
        self.db.update_position(
            self.model_id, coin, quantity, price, leverage, 'long'
        )

        # 记录交易（包含交易费）
        self.db.add_trade(
            self.model_id, coin, 'buy_to_enter', quantity,
            price, leverage, 'long', pnl=0, fee=trade_fee
        )
        
        return {
            'coin': coin,
            'signal': 'buy_to_enter',
            'quantity': quantity,
            'price': price,
            'leverage': leverage,
            'fee': trade_fee,  # 返回费用信息
            'message': f'Long {quantity:.4f} {coin} @ ${price:.2f} (Fee: ${trade_fee:.2f})'
        }
    
    def _execute_sell(self, coin: str, decision: Dict, market_state: Dict, 
                 portfolio: Dict) -> Dict:
        quantity = float(decision.get('quantity', 0))
        leverage = int(decision.get('leverage', 1))
        price = market_state[coin]['price']
        
        if quantity <= 0:
            return {'coin': coin, 'error': 'Invalid quantity'}
        
        # 计算交易额和交易费
        trade_amount = quantity * price
        trade_fee = trade_amount * self.trade_fee_rate
        required_margin = (quantity * price) / leverage
        
        # 总需资金 = 保证金 + 交易费
        total_required = required_margin + trade_fee
        if total_required > portfolio['cash']:
            return {'coin': coin, 'error': 'Insufficient cash (including fees)'}
        
        # 更新持仓
        self.db.update_position(
            self.model_id, coin, quantity, price, leverage, 'short'
        )
        
        # 记录交易（包含交易费）
        self.db.add_trade(
            self.model_id, coin, 'sell_to_enter', quantity, 
            price, leverage, 'short', pnl=0, fee=trade_fee  # 新增fee参数
        )
        
        return {
            'coin': coin,
            'signal': 'sell_to_enter',
            'quantity': quantity,
            'price': price,
            'leverage': leverage,
            'fee': trade_fee,
            'message': f'Short {quantity:.4f} {coin} @ ${price:.2f} (Fee: ${trade_fee:.2f})'
        }
    
    def _execute_close(self, coin: str, decision: Dict, market_state: Dict, 
                    portfolio: Dict) -> Dict:
        position = None
        for pos in portfolio['positions']:
            if pos['coin'] == coin:
                position = pos
                break
        
        if not position:
            return {'coin': coin, 'error': 'Position not found'}
        
        current_price = market_state[coin]['price']
        entry_price = position['avg_price']
        quantity = position['quantity']
        side = position['side']
        
        # 计算平仓利润（未扣费）
        if side == 'long':
            gross_pnl = (current_price - entry_price) * quantity
        else:  # short
            gross_pnl = (entry_price - current_price) * quantity
        
        # 计算平仓交易费（按平仓时的交易额）
        trade_amount = quantity * current_price
        trade_fee = trade_amount * self.trade_fee_rate
        net_pnl = gross_pnl - trade_fee  # 净利润 = 毛利润 - 交易费
        
        # 关闭持仓
        self.db.close_position(self.model_id, coin, side)
        
        # 记录平仓交易（包含费用和净利润）
        self.db.add_trade(
            self.model_id, coin, 'close_position', quantity,
            current_price, position['leverage'], side, pnl=net_pnl, fee=trade_fee  # 新增fee参数
        )
        
        return {
            'coin': coin,
            'signal': 'close_position',
            'quantity': quantity,
            'price': current_price,
            'pnl': net_pnl,
            'fee': trade_fee,
            'message': f'Close {coin}, Gross P&L: ${gross_pnl:.2f}, Fee: ${trade_fee:.2f}, Net P&L: ${net_pnl:.2f}'
        }
