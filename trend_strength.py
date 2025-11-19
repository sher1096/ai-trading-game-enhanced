"""
趋势强度分析模块 - 基于高低点抬升判断
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any


class TrendStrengthAnalyzer:
    """
    趋势强度分析器
    通过分析多个时间周期的高低点是否同步抬升/下降来判断趋势强度
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化趋势强度分析器

        Args:
            config: 配置字典
            {
                "enabled": True,
                "periods": ["1h", "4h", "1d"],  # 要分析的周期
                "bars_count": 3  # 分析最近几根K线
            }
        """
        self.enabled = config.get('enabled', True)
        self.periods = config.get('periods', ['1h', '4h', '1d'])
        self.bars_count = config.get('bars_count', 3)

    def analyze_high_low_trend(self, df: pd.DataFrame, period_name: str = "default") -> Dict:
        """
        分析单个周期的高低点趋势

        Args:
            df: 价格数据 DataFrame，需要包含 high, low 列
            period_name: 周期名称（用于显示）

        Returns:
            {
                'period': '1h',
                'trend': 'bullish' | 'bearish' | 'neutral',
                'high_trend': 'rising' | 'falling' | 'neutral',
                'low_trend': 'rising' | 'falling' | 'neutral',
                'strength': 0-100,
                'detail': '详细描述'
            }
        """
        if len(df) < self.bars_count:
            return {
                'period': period_name,
                'trend': 'neutral',
                'high_trend': 'neutral',
                'low_trend': 'neutral',
                'strength': 0,
                'detail': '数据不足'
            }

        # 取最近N根K线
        recent_bars = df.tail(self.bars_count)

        # 分析高点趋势
        highs = recent_bars['high'].values
        high_trend = self._analyze_price_sequence(highs)

        # 分析低点趋势
        lows = recent_bars['low'].values
        low_trend = self._analyze_price_sequence(lows)

        # 综合判断
        if high_trend == 'rising' and low_trend == 'rising':
            trend = 'bullish'
            strength = 85
            detail = f'{period_name}周期：高点和低点同步抬高，强势多头'
        elif high_trend == 'falling' and low_trend == 'falling':
            trend = 'bearish'
            strength = 85
            detail = f'{period_name}周期：高点和低点同步降低，强势空头'
        elif high_trend == 'rising' and low_trend == 'neutral':
            trend = 'bullish'
            strength = 60
            detail = f'{period_name}周期：高点抬高但低点未明确，偏多'
        elif high_trend == 'neutral' and low_trend == 'rising':
            trend = 'bullish'
            strength = 60
            detail = f'{period_name}周期：低点抬高但高点未明确，偏多'
        elif high_trend == 'falling' and low_trend == 'neutral':
            trend = 'bearish'
            strength = 60
            detail = f'{period_name}周期：高点降低但低点未明确，偏空'
        elif high_trend == 'neutral' and low_trend == 'falling':
            trend = 'bearish'
            strength = 60
            detail = f'{period_name}周期：低点降低但高点未明确，偏空'
        elif high_trend == 'rising' and low_trend == 'falling':
            trend = 'neutral'
            strength = 40
            detail = f'{period_name}周期：震荡扩大，高点抬高但低点降低'
        elif high_trend == 'falling' and low_trend == 'rising':
            trend = 'neutral'
            strength = 40
            detail = f'{period_name}周期：震荡收窄，趋势不明'
        else:
            trend = 'neutral'
            strength = 30
            detail = f'{period_name}周期：横盘整理'

        return {
            'period': period_name,
            'trend': trend,
            'high_trend': high_trend,
            'low_trend': low_trend,
            'strength': strength,
            'detail': detail
        }

    def _analyze_price_sequence(self, prices: np.ndarray) -> str:
        """
        分析价格序列的趋势

        Args:
            prices: 价格数组

        Returns:
            'rising' | 'falling' | 'neutral'
        """
        if len(prices) < 2:
            return 'neutral'

        # 计算价格变化
        rising_count = 0
        falling_count = 0

        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                rising_count += 1
            elif prices[i] < prices[i-1]:
                falling_count += 1

        total_changes = len(prices) - 1

        # 判断趋势
        if rising_count >= total_changes * 0.7:  # 70%以上上涨
            return 'rising'
        elif falling_count >= total_changes * 0.7:  # 70%以上下跌
            return 'falling'
        else:
            return 'neutral'

    def analyze_multi_timeframe(self, price_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        分析多个时间周期的趋势强度

        Args:
            price_data: {
                '1h': DataFrame,
                '4h': DataFrame,
                '1d': DataFrame,
                ...
            }

        Returns:
            {
                'action': 'buy' | 'sell' | 'hold',
                'confidence': 0-100,
                'reason': '综合原因',
                'details': [各周期详细分析]
            }
        """
        if not self.enabled:
            return {
                'action': 'hold',
                'confidence': 0,
                'reason': '趋势强度分析未启用',
                'details': []
            }

        results = []
        bullish_periods = []
        bearish_periods = []

        # 分析每个周期
        for period in self.periods:
            if period in price_data and price_data[period] is not None:
                result = self.analyze_high_low_trend(price_data[period], period)
                results.append(result)

                if result['trend'] == 'bullish' and result['strength'] >= 60:
                    bullish_periods.append(f"{period}({result['strength']}%)")
                elif result['trend'] == 'bearish' and result['strength'] >= 60:
                    bearish_periods.append(f"{period}({result['strength']}%)")

        # 综合判断
        bullish_count = len(bullish_periods)
        bearish_count = len(bearish_periods)
        total_periods = len(results)

        if total_periods == 0:
            return {
                'action': 'hold',
                'confidence': 0,
                'reason': '无有效周期数据',
                'details': []
            }

        # 生成信号
        if bullish_count >= total_periods * 0.6:  # 60%以上周期看多
            action = 'buy'
            confidence = min(90, 60 + bullish_count * 10)
            reason = f'多周期共振看多：{", ".join(bullish_periods)}'
        elif bearish_count >= total_periods * 0.6:  # 60%以上周期看空
            action = 'sell'
            confidence = min(90, 60 + bearish_count * 10)
            reason = f'多周期共振看空：{", ".join(bearish_periods)}'
        else:
            action = 'hold'
            confidence = 40
            reason = f'多周期分歧，看多{bullish_count}个周期，看空{bearish_count}个周期'

        return {
            'action': action,
            'confidence': confidence,
            'reason': reason,
            'details': results
        }

    def convert_prices_to_klines(self, prices: List[float], period_minutes: int) -> pd.DataFrame:
        """
        将价格序列转换为K线数据（简化版）

        Args:
            prices: 价格列表（假设是等时间间隔的）
            period_minutes: K线周期（分钟）

        Returns:
            DataFrame with columns: open, high, low, close
        """
        if not prices or len(prices) < period_minutes:
            return pd.DataFrame(columns=['open', 'high', 'low', 'close'])

        # 将价格按周期分组
        klines = []
        for i in range(0, len(prices) - period_minutes + 1, period_minutes):
            period_prices = prices[i:i + period_minutes]
            if len(period_prices) > 0:
                klines.append({
                    'open': period_prices[0],
                    'high': max(period_prices),
                    'low': min(period_prices),
                    'close': period_prices[-1]
                })

        return pd.DataFrame(klines)


def create_trend_strength_analyzer(config: Dict[str, Any]) -> TrendStrengthAnalyzer:
    """创建趋势强度分析器实例"""
    return TrendStrengthAnalyzer(config)
