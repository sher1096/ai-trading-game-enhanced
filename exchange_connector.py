"""
交易所接口模块 - 支持币安和欧意实盘交易
"""
import ccxt
import pandas as pd
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExchangeConnector:
    """交易所连接器基类"""

    def __init__(self, exchange_id: str, api_key: str = None, api_secret: str = None, testnet: bool = False):
        """
        初始化交易所连接

        Args:
            exchange_id: 交易所ID ('binance' 或 'okx')
            api_key: API密钥
            api_secret: API密钥secret
            testnet: 是否使用测试网
        """
        self.exchange_id = exchange_id
        self.testnet = testnet

        # 初始化交易所
        try:
            if exchange_id == 'binance':
                self.exchange = ccxt.binance({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'future' if not testnet else 'future',  # 合约交易
                    }
                })
                if testnet:
                    self.exchange.set_sandbox_mode(True)

            elif exchange_id == 'okx':
                self.exchange = ccxt.okx({
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'swap',  # 永续合约
                    }
                })
                if testnet:
                    self.exchange.set_sandbox_mode(True)

            else:
                raise ValueError(f"不支持的交易所: {exchange_id}")

            logger.info(f"[{exchange_id.upper()}] 连接初始化成功 (testnet={testnet})")

        except Exception as e:
            logger.error(f"[{exchange_id.upper()}] 连接初始化失败: {e}")
            raise

    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> pd.DataFrame:
        """
        获取K线数据

        Args:
            symbol: 交易对，例如 'BTC/USDT'
            timeframe: 时间周期 ('1m', '5m', '15m', '1h', '4h', '1d'等)
            limit: 获取数量

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            logger.info(f"[{self.exchange_id.upper()}] 获取K线数据成功: {symbol} {timeframe} ({len(df)}条)")
            return df

        except Exception as e:
            logger.error(f"[{self.exchange_id.upper()}] 获取K线数据失败: {e}")
            raise

    def fetch_ticker(self, symbol: str) -> Dict:
        """
        获取ticker数据（最新价格等）

        Args:
            symbol: 交易对

        Returns:
            ticker信息字典
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.info(f"[{self.exchange_id.upper()}] 获取ticker成功: {symbol} 价格={ticker['last']}")
            return ticker

        except Exception as e:
            logger.error(f"[{self.exchange_id.upper()}] 获取ticker失败: {e}")
            raise

    def create_order(self, symbol: str, side: str, order_type: str, amount: float, price: float = None) -> Dict:
        """
        下单

        Args:
            symbol: 交易对
            side: 'buy' 或 'sell'
            order_type: 'market' 或 'limit'
            amount: 数量
            price: 价格（限价单必填）

        Returns:
            订单信息
        """
        try:
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount)
            elif order_type == 'limit':
                if price is None:
                    raise ValueError("限价单必须指定价格")
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            else:
                raise ValueError(f"不支持的订单类型: {order_type}")

            logger.info(f"[{self.exchange_id.upper()}] 下单成功: {symbol} {side} {order_type} "
                       f"数量={amount} 价格={price} 订单ID={order.get('id')}")
            return order

        except Exception as e:
            logger.error(f"[{self.exchange_id.upper()}] 下单失败: {e}")
            raise

    def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """
        撤单

        Args:
            order_id: 订单ID
            symbol: 交易对

        Returns:
            撤单结果
        """
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"[{self.exchange_id.upper()}] 撤单成功: 订单ID={order_id}")
            return result

        except Exception as e:
            logger.error(f"[{self.exchange_id.upper()}] 撤单失败: {e}")
            raise

    def fetch_order(self, order_id: str, symbol: str) -> Dict:
        """
        查询订单

        Args:
            order_id: 订单ID
            symbol: 交易对

        Returns:
            订单信息
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            logger.info(f"[{self.exchange_id.upper()}] 查询订单成功: {order_id} 状态={order.get('status')}")
            return order

        except Exception as e:
            logger.error(f"[{self.exchange_id.upper()}] 查询订单失败: {e}")
            raise

    def fetch_balance(self) -> Dict:
        """
        查询账户余额

        Returns:
            余额信息
        """
        try:
            balance = self.exchange.fetch_balance()
            logger.info(f"[{self.exchange_id.upper()}] 查询余额成功")
            return balance

        except Exception as e:
            logger.error(f"[{self.exchange_id.upper()}] 查询余额失败: {e}")
            raise

    def fetch_positions(self, symbol: str = None) -> List[Dict]:
        """
        查询持仓

        Args:
            symbol: 交易对（可选，为None时查询所有持仓）

        Returns:
            持仓列表
        """
        try:
            positions = self.exchange.fetch_positions(symbol)
            # 过滤掉空持仓
            active_positions = [p for p in positions if float(p.get('contracts', 0)) > 0]

            logger.info(f"[{self.exchange_id.upper()}] 查询持仓成功: {len(active_positions)}个活跃持仓")
            return active_positions

        except Exception as e:
            logger.error(f"[{self.exchange_id.upper()}] 查询持仓失败: {e}")
            raise

    def close_position(self, symbol: str, side: str = 'auto') -> Dict:
        """
        平仓

        Args:
            symbol: 交易对
            side: 平仓方向 ('auto'自动判断, 'buy'平空, 'sell'平多)

        Returns:
            平仓结果
        """
        try:
            # 获取当前持仓
            positions = self.fetch_positions(symbol)

            if not positions:
                logger.warning(f"[{self.exchange_id.upper()}] 没有找到{symbol}的持仓")
                return {'success': False, 'message': '无持仓'}

            position = positions[0]
            position_side = position.get('side')  # 'long' or 'short'
            amount = abs(float(position.get('contracts', 0)))

            # 确定平仓方向
            if side == 'auto':
                close_side = 'sell' if position_side == 'long' else 'buy'
            else:
                close_side = side

            # 使用市价单平仓
            order = self.create_order(symbol, close_side, 'market', amount)

            logger.info(f"[{self.exchange_id.upper()}] 平仓成功: {symbol} {position_side} 数量={amount}")
            return order

        except Exception as e:
            logger.error(f"[{self.exchange_id.upper()}] 平仓失败: {e}")
            raise


class ExchangeManager:
    """交易所管理器 - 管理多个交易所连接"""

    def __init__(self, config_file: str = 'exchange_config.json'):
        """
        初始化交易所管理器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.exchanges: Dict[str, ExchangeConnector] = {}
        self.load_config()

    def load_config(self):
        """从配置文件加载交易所配置"""
        if not os.path.exists(self.config_file):
            logger.warning(f"配置文件不存在: {self.config_file}，使用默认配置")
            self.save_config({})
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            for exchange_id, exchange_config in config.items():
                if exchange_config.get('enabled', False):
                    self.add_exchange(
                        exchange_id=exchange_id,
                        api_key=exchange_config.get('api_key'),
                        api_secret=exchange_config.get('api_secret'),
                        testnet=exchange_config.get('testnet', False)
                    )

            logger.info(f"加载了{len(self.exchanges)}个交易所配置")

        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")

    def save_config(self, config: Dict):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"配置已保存到: {self.config_file}")

        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def add_exchange(self, exchange_id: str, api_key: str, api_secret: str, testnet: bool = False):
        """添加交易所连接"""
        try:
            connector = ExchangeConnector(exchange_id, api_key, api_secret, testnet)
            self.exchanges[exchange_id] = connector
            logger.info(f"成功添加交易所: {exchange_id}")

        except Exception as e:
            logger.error(f"添加交易所失败 {exchange_id}: {e}")

    def get_exchange(self, exchange_id: str) -> Optional[ExchangeConnector]:
        """获取交易所连接"""
        return self.exchanges.get(exchange_id)

    def list_exchanges(self) -> List[str]:
        """列出所有已连接的交易所"""
        return list(self.exchanges.keys())


# 使用示例
if __name__ == '__main__':
    # 创建交易所管理器
    manager = ExchangeManager()

    # 示例：添加币安测试网
    # manager.add_exchange('binance', 'YOUR_API_KEY', 'YOUR_API_SECRET', testnet=True)

    # 获取K线数据
    # binance = manager.get_exchange('binance')
    # if binance:
    #     df = binance.fetch_ohlcv('BTC/USDT', '1h', 100)
    #     print(df.tail())

    print("交易所连接器模块加载成功")
