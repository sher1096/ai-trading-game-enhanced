"""
简化版技术指标策略模块 - 不依赖TA-Lib
使用纯Python实现技术指标
"""
import pandas as pd
import numpy as np
from typing import Dict


class BaseStrategy:
    """策略基类"""

    def __init__(self, name: str):
        self.name = name
        self.position = 0  # 0: 空仓, 1: 多头, -1: 空头
        self.entry_price = 0

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        raise NotImplementedError

    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """生成交易信号"""
        raise NotImplementedError

    def update_position(self, action: str, price: float):
        """更新持仓状态"""
        if action == 'buy':
            self.position = 1
            self.entry_price = price
        elif action == 'sell':
            self.position = -1
            self.entry_price = price
        elif action == 'hold':
            pass


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """计算简单移动平均线 SMA"""
    return data.rolling(window=period).mean()


def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """计算指数移动平均线 EMA"""
    return data.ewm(span=period, adjust=False).mean()


def calculate_boll(data: pd.Series, period: int = 20, std_dev: float = 2) -> Dict:
    """计算布林带 Bollinger Bands

    Args:
        data: 价格序列
        period: 周期，默认20
        std_dev: 标准差倍数，默认2

    Returns:
        dict: {'upper': 上轨, 'middle': 中轨, 'lower': 下轨}
    """
    middle = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return {
        'upper': upper,
        'middle': middle,
        'lower': lower
    }


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """计算RSI指标"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """计算MACD指标"""
    exp1 = data.ewm(span=fast, adjust=False).mean()
    exp2 = data.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal

    return {
        'macd': macd,
        'macd_signal': macd_signal,
        'macd_hist': macd_hist
    }


class MovingAverageStrategy(BaseStrategy):
    """移动平均线策略"""

    def __init__(self, fast_period: int = 5, slow_period: int = 20):
        super().__init__("MovingAverage")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算MA指标"""
        df['sma_fast'] = calculate_sma(df['close'], self.fast_period)
        df['sma_slow'] = calculate_sma(df['close'], self.slow_period)
        return df

    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """生成交易信号"""
        if len(df) < self.slow_period:
            return {'action': 'hold', 'confidence': 0}

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else last_row

        # 金叉/死叉判断
        if prev_row['sma_fast'] <= prev_row['sma_slow'] and last_row['sma_fast'] > last_row['sma_slow']:
            return {'action': 'buy', 'confidence': 0.8}
        elif prev_row['sma_fast'] >= prev_row['sma_slow'] and last_row['sma_fast'] < last_row['sma_slow']:
            return {'action': 'sell', 'confidence': 0.8}
        elif last_row['sma_fast'] > last_row['sma_slow']:
            return {'action': 'hold', 'confidence': 0.6}  # 多头趋势，观望
        else:
            return {'action': 'hold', 'confidence': 0.6}  # 空头趋势，观望


class RSIStrategy(BaseStrategy):
    """RSI策略"""

    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__("RSI")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算RSI指标"""
        df['rsi'] = calculate_rsi(df['close'], self.period)
        return df

    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """生成交易信号"""
        if len(df) < self.period + 1:
            return {'action': 'hold', 'confidence': 0}

        last_row = df.iloc[-1]
        rsi = last_row['rsi']

        if pd.isna(rsi):
            return {'action': 'hold', 'confidence': 0}

        if rsi < self.oversold:
            confidence = min(0.9, (self.oversold - rsi) / self.oversold)
            return {'action': 'buy', 'confidence': confidence}
        elif rsi > self.overbought:
            confidence = min(0.9, (rsi - self.overbought) / (100 - self.overbought))
            return {'action': 'sell', 'confidence': confidence}
        else:
            return {'action': 'hold', 'confidence': 0.5}


class MACDStrategy(BaseStrategy):
    """MACD策略"""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__("MACD")
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算MACD指标"""
        macd_data = calculate_macd(df['close'], self.fast, self.slow, self.signal_period)
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['macd_signal']
        df['macd_hist'] = macd_data['macd_hist']
        return df

    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """生成交易信号"""
        if len(df) < self.slow + self.signal_period:
            return {'action': 'hold', 'confidence': 0}

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else last_row

        if pd.isna(last_row['macd']) or pd.isna(last_row['macd_signal']):
            return {'action': 'hold', 'confidence': 0}

        # MACD金叉/死叉
        if prev_row['macd'] <= prev_row['macd_signal'] and last_row['macd'] > last_row['macd_signal']:
            return {'action': 'buy', 'confidence': 0.75}
        elif prev_row['macd'] >= prev_row['macd_signal'] and last_row['macd'] < last_row['macd_signal']:
            return {'action': 'sell', 'confidence': 0.75}
        elif last_row['macd'] > last_row['macd_signal']:
            return {'action': 'hold', 'confidence': 0.6}
        else:
            return {'action': 'hold', 'confidence': 0.6}


class CombinedStrategy(BaseStrategy):
    """组合策略"""

    def __init__(self):
        super().__init__("Combined")
        self.ma_strategy = MovingAverageStrategy()
        self.rsi_strategy = RSIStrategy()
        self.macd_strategy = MACDStrategy()

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有指标"""
        df = self.ma_strategy.calculate_indicators(df)
        df = self.rsi_strategy.calculate_indicators(df)
        df = self.macd_strategy.calculate_indicators(df)
        return df

    def generate_signal(self, df: pd.DataFrame) -> Dict:
        """综合所有策略的信号"""
        ma_signal = self.ma_strategy.generate_signal(df)
        rsi_signal = self.rsi_strategy.generate_signal(df)
        macd_signal = self.macd_strategy.generate_signal(df)

        signals = [ma_signal, rsi_signal, macd_signal]

        # 统计买入/卖出信号数量
        buy_count = sum(1 for s in signals if s['action'] == 'buy')
        sell_count = sum(1 for s in signals if s['action'] == 'sell')

        # 至少2个策略同意才执行
        if buy_count >= 2:
            avg_confidence = sum(s['confidence'] for s in signals if s['action'] == 'buy') / buy_count
            return {'action': 'buy', 'confidence': avg_confidence}
        elif sell_count >= 2:
            avg_confidence = sum(s['confidence'] for s in signals if s['action'] == 'sell') / sell_count
            return {'action': 'sell', 'confidence': avg_confidence}
        else:
            return {'action': 'hold', 'confidence': 0.5}


def create_strategy(name: str) -> BaseStrategy:
    """创建策略实例"""
    strategies = {
        'MovingAverage': MovingAverageStrategy,
        'RSI': RSIStrategy,
        'MACD': MACDStrategy,
        'Combined': CombinedStrategy
    }

    strategy_class = strategies.get(name)
    if strategy_class is None:
        raise ValueError(f"Unknown strategy: {name}")

    return strategy_class()
