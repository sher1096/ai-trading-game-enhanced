"""
实盘交易执行器 - 将交易信号转换为实际订单
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime
import json
from exchange_connector import ExchangeManager, ExchangeConnector

logger = logging.getLogger(__name__)


class RiskManager:
    """风险控制管理器"""

    def __init__(self, config: Dict):
        """
        初始化风险管理器

        Args:
            config: 风险控制配置
            {
                'max_position_size': 0.1,      # 单个币种最大仓位（BTC数量）
                'max_position_usdt': 1000,     # 单个币种最大仓位（USDT金额）
                'max_total_position': 0.5,     # 总仓位比例（占总资金）
                'stop_loss_pct': 0.02,         # 止损百分比（2%）
                'take_profit_pct': 0.05,       # 止盈百分比（5%）
                'min_confidence': 70,          # 最小信号置信度
                'leverage': 5                   # 杠杆倍数
            }
        """
        self.max_position_size = config.get('max_position_size', 0.1)
        self.max_position_usdt = config.get('max_position_usdt', 1000)
        self.max_total_position = config.get('max_total_position', 0.5)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.02)
        self.take_profit_pct = config.get('take_profit_pct', 0.05)
        self.min_confidence = config.get('min_confidence', 70)
        self.leverage = config.get('leverage', 5)

        logger.info(f"[风控] 初始化完成: 止损{self.stop_loss_pct*100}%, "
                   f"止盈{self.take_profit_pct*100}%, 最小信号{self.min_confidence}%")

    def calculate_position_size(self, signal: Dict, current_price: float,
                               balance: float, existing_position: float = 0) -> float:
        """
        计算开仓数量

        Args:
            signal: 交易信号 {'action': 'buy', 'confidence': 85}
            current_price: 当前价格
            balance: 账户余额（USDT）
            existing_position: 现有持仓数量

        Returns:
            建议开仓数量
        """
        # 检查信号置信度
        if signal['confidence'] < self.min_confidence:
            logger.info(f"[风控] 信号置信度{signal['confidence']}%低于阈值{self.min_confidence}%，拒绝开仓")
            return 0

        # 计算可用资金（考虑总仓位限制）
        max_usdt = balance * self.max_total_position

        # 根据置信度调整仓位（置信度越高，仓位越大）
        confidence_factor = signal['confidence'] / 100
        target_usdt = min(self.max_position_usdt, max_usdt) * confidence_factor

        # 计算目标持仓数量
        target_size = target_usdt / current_price

        # 限制最大持仓
        target_size = min(target_size, self.max_position_size)

        # 计算实际需要开仓的数量（目标持仓 - 现有持仓）
        order_size = target_size - existing_position

        # 确保不超过账户余额
        max_affordable = (balance * 0.95) / current_price  # 留5%余量
        order_size = min(order_size, max_affordable)

        logger.info(f"[风控] 计算开仓数量: 信号={signal['action']} "
                   f"置信度={signal['confidence']}% "
                   f"建议数量={order_size:.4f}")

        return max(0, order_size)  # 确保非负

    def should_close_position(self, entry_price: float, current_price: float,
                             side: str) -> tuple:
        """
        判断是否应该平仓（止损或止盈）

        Args:
            entry_price: 开仓价格
            current_price: 当前价格
            side: 仓位方向 ('long' 或 'short')

        Returns:
            (should_close, reason)
        """
        if side == 'long':
            pnl_pct = (current_price - entry_price) / entry_price
        else:  # short
            pnl_pct = (entry_price - current_price) / entry_price

        # 止损检查
        if pnl_pct <= -self.stop_loss_pct:
            return True, f'止损: 亏损{abs(pnl_pct)*100:.2f}%'

        # 止盈检查
        if pnl_pct >= self.take_profit_pct:
            return True, f'止盈: 盈利{pnl_pct*100:.2f}%'

        return False, ''


class PositionManager:
    """仓位管理器"""

    def __init__(self):
        self.positions: Dict[str, Dict] = {}  # symbol -> position info

    def update_position(self, symbol: str, position_data: Dict):
        """更新持仓信息"""
        self.positions[symbol] = {
            'side': position_data.get('side'),
            'size': float(position_data.get('contracts', 0)),
            'entry_price': float(position_data.get('entryPrice', 0)),
            'unrealized_pnl': float(position_data.get('unrealizedPnl', 0)),
            'updated_at': datetime.now()
        }

    def get_position(self, symbol: str) -> Optional[Dict]:
        """获取持仓信息"""
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        """检查是否有持仓"""
        pos = self.positions.get(symbol)
        return pos is not None and pos['size'] > 0


class LiveTradeExecutor:
    """实盘交易执行器"""

    def __init__(self, exchange_manager: ExchangeManager, risk_config: Dict,
                 dry_run: bool = True):
        """
        初始化实盘交易执行器

        Args:
            exchange_manager: 交易所管理器
            risk_config: 风险控制配置
            dry_run: 是否为模拟模式（不实际下单）
        """
        self.exchange_manager = exchange_manager
        self.risk_manager = RiskManager(risk_config)
        self.position_manager = PositionManager()
        self.dry_run = dry_run

        self.active_orders: Dict[str, List] = {}  # symbol -> [order_ids]
        self.trade_history: List[Dict] = []

        logger.info(f"[执行器] 初始化完成 (模拟模式: {dry_run})")

    def execute_signal(self, exchange_id: str, symbol: str, signal: Dict) -> Dict:
        """
        执行交易信号

        Args:
            exchange_id: 交易所ID ('binance' 或 'okx')
            symbol: 交易对 (如 'BTC/USDT')
            signal: 交易信号
            {
                'action': 'buy' | 'sell' | 'hold',
                'confidence': 0-100,
                'reason': '信号原因'
            }

        Returns:
            执行结果
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"[执行器] 收到信号: {exchange_id} {symbol}")
        logger.info(f"         动作={signal['action']} 置信度={signal['confidence']}%")
        logger.info(f"         原因={signal['reason']}")

        # 获取交易所连接
        exchange = self.exchange_manager.get_exchange(exchange_id)
        if not exchange:
            return {'success': False, 'message': f'交易所{exchange_id}未连接'}

        try:
            # 获取当前价格
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']

            # 获取账户余额
            balance = exchange.fetch_balance()
            usdt_balance = float(balance.get('USDT', {}).get('free', 0))

            # 获取当前持仓
            positions = exchange.fetch_positions(symbol)
            existing_position = positions[0] if positions else None

            logger.info(f"[执行器] 当前价格={current_price} USDT余额={usdt_balance:.2f}")

            # 根据信号执行不同操作
            if signal['action'] == 'buy':
                return self._execute_buy(exchange, symbol, signal, current_price,
                                        usdt_balance, existing_position)

            elif signal['action'] == 'sell':
                return self._execute_sell(exchange, symbol, signal, current_price,
                                         existing_position)

            else:  # hold
                # 检查是否需要止损止盈
                if existing_position and existing_position.get('contracts', 0) > 0:
                    return self._check_stop_loss_take_profit(exchange, symbol,
                                                             existing_position,
                                                             current_price)
                return {'success': True, 'action': 'hold', 'message': '保持观望'}

        except Exception as e:
            logger.error(f"[执行器] 执行失败: {e}")
            return {'success': False, 'message': str(e)}

    def _execute_buy(self, exchange: ExchangeConnector, symbol: str, signal: Dict,
                    current_price: float, balance: float,
                    existing_position: Optional[Dict]) -> Dict:
        """执行买入信号"""
        # 检查是否已有多头持仓
        if existing_position and existing_position.get('side') == 'long':
            logger.info(f"[执行器] 已有多头持仓，跳过买入")
            return {'success': True, 'action': 'skip', 'message': '已有多头持仓'}

        # 如果有空头持仓，先平仓
        if existing_position and existing_position.get('side') == 'short':
            logger.info(f"[执行器] 检测到空头持仓，先平仓")
            exchange.close_position(symbol, 'auto')

        # 计算开仓数量
        position_size = self.risk_manager.calculate_position_size(
            signal, current_price, balance, 0
        )

        if position_size <= 0:
            return {'success': True, 'action': 'skip',
                   'message': '风控拒绝：仓位计算为0'}

        # 模拟模式
        if self.dry_run:
            logger.info(f"[执行器] 【模拟】买入 {symbol} 数量={position_size:.4f} "
                       f"价格={current_price}")
            return {
                'success': True,
                'action': 'buy_simulated',
                'symbol': symbol,
                'size': position_size,
                'price': current_price,
                'message': '模拟买入成功'
            }

        # 实盘下单
        try:
            order = exchange.create_order(symbol, 'buy', 'market', position_size)

            logger.info(f"[执行器] ✅ 买入成功: {symbol} "
                       f"数量={position_size:.4f} 订单ID={order['id']}")

            # 记录交易历史
            self.trade_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'action': 'buy',
                'size': position_size,
                'price': current_price,
                'order_id': order['id'],
                'signal': signal
            })

            return {
                'success': True,
                'action': 'buy',
                'order': order,
                'message': '买入成功'
            }

        except Exception as e:
            logger.error(f"[执行器] ❌ 买入失败: {e}")
            return {'success': False, 'message': str(e)}

    def _execute_sell(self, exchange: ExchangeConnector, symbol: str, signal: Dict,
                     current_price: float, existing_position: Optional[Dict]) -> Dict:
        """执行卖出信号"""
        # 检查是否有多头持仓需要平仓
        if existing_position and existing_position.get('side') == 'long':
            logger.info(f"[执行器] 检测到多头持仓，执行平仓")

            if self.dry_run:
                logger.info(f"[执行器] 【模拟】平多仓 {symbol}")
                return {'success': True, 'action': 'close_long_simulated',
                       'message': '模拟平多仓'}

            order = exchange.close_position(symbol, 'auto')
            logger.info(f"[执行器] ✅ 平多仓成功")
            return {'success': True, 'action': 'close_long', 'order': order}

        # 注意：做空需谨慎，这里只平仓不开空单
        # 如果要开空单，可以参考_execute_buy的逻辑
        logger.info(f"[执行器] 卖出信号但无多头持仓，不执行（做空谨慎）")
        return {'success': True, 'action': 'skip',
               'message': '无多头持仓，做空谨慎不执行'}

    def _check_stop_loss_take_profit(self, exchange: ExchangeConnector,
                                    symbol: str, position: Dict,
                                    current_price: float) -> Dict:
        """检查止损止盈"""
        entry_price = float(position.get('entryPrice', 0))
        side = position.get('side')

        should_close, reason = self.risk_manager.should_close_position(
            entry_price, current_price, side
        )

        if should_close:
            logger.warning(f"[执行器] ⚠️ 触发{reason}，执行平仓")

            if self.dry_run:
                return {'success': True, 'action': 'close_simulated',
                       'message': f'模拟平仓：{reason}'}

            order = exchange.close_position(symbol, 'auto')
            return {'success': True, 'action': 'close', 'order': order,
                   'reason': reason}

        return {'success': True, 'action': 'hold', 'message': '持仓监控中'}

    def get_trade_summary(self) -> Dict:
        """获取交易摘要"""
        return {
            'total_trades': len(self.trade_history),
            'recent_trades': self.trade_history[-10:],  # 最近10笔
            'positions': self.position_manager.positions
        }


# 使用示例
if __name__ == '__main__':
    # 配置
    risk_config = {
        'max_position_size': 0.01,      # 0.01 BTC
        'max_position_usdt': 500,       # 500 USDT
        'max_total_position': 0.3,      # 30%总资金
        'stop_loss_pct': 0.02,          # 2%止损
        'take_profit_pct': 0.05,        # 5%止盈
        'min_confidence': 70,           # 最小70%信号
        'leverage': 5
    }

    # 初始化（模拟模式）
    from exchange_connector import ExchangeManager

    manager = ExchangeManager()
    executor = LiveTradeExecutor(manager, risk_config, dry_run=True)

    # 模拟信号
    signal = {
        'action': 'buy',
        'confidence': 85,
        'reason': '【第一档主导】EMA多头排列 + 高低点抬升'
    }

    # 执行（如果有配置的交易所）
    # result = executor.execute_signal('binance', 'BTC/USDT', signal)
    # print(result)

    print("实盘交易执行器加载成功")
