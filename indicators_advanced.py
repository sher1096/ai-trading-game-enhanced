"""
高级技术指标模块 - 支持多指标组合分析
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from strategy import calculate_sma, calculate_ema, calculate_rsi, calculate_macd, calculate_boll
from trend_strength import create_trend_strength_analyzer
from candlestick_patterns import create_candlestick_pattern_analyzer


class MultiIndicatorAnalyzer:
    """多指标分析器 - 支持任意组合指标"""

    def __init__(self, indicators_config: Dict[str, Any]):
        """
        初始化多指标分析器

        Args:
            indicators_config: 指标配置，格式：
            {
                "EMA_144": {"enabled": True, "period": 144},
                "EMA_169": {"enabled": True, "period": 169},
                "EMA_576": {"enabled": True, "period": 576},
                "EMA_676": {"enabled": True, "period": 676},
                "BOLL": {"enabled": True, "period": 20, "std_dev": 2},
                "RSI": {"enabled": True, "period": 14},
                "MACD": {"enabled": True, "fast": 12, "slow": 26, "signal": 9},
                "TREND_STRENGTH": {
                    "enabled": True,
                    "periods": ["1h", "4h", "1d"],
                    "bars_count": 3
                }
            }
        """
        self.config = indicators_config
        self.signals = {}

        # 初始化趋势强度分析器
        if 'TREND_STRENGTH' in indicators_config and indicators_config['TREND_STRENGTH'].get('enabled', False):
            self.trend_strength_analyzer = create_trend_strength_analyzer(indicators_config['TREND_STRENGTH'])
        else:
            self.trend_strength_analyzer = None

        # 初始化K线形态分析器
        if 'CANDLESTICK_PATTERNS' in indicators_config and indicators_config['CANDLESTICK_PATTERNS'].get('enabled', False):
            self.candlestick_analyzer = create_candlestick_pattern_analyzer(indicators_config['CANDLESTICK_PATTERNS'])
        else:
            self.candlestick_analyzer = None

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有启用的指标"""
        result_df = df.copy()

        # MA指标
        for key, config in self.config.items():
            if key.startswith('MA_') and config.get('enabled', False):
                period = config['period']
                result_df[f'MA_{period}'] = calculate_sma(df['close'], period)

        # EMA指标
        for key, config in self.config.items():
            if key.startswith('EMA_') and config.get('enabled', False):
                period = config['period']
                result_df[f'EMA_{period}'] = calculate_ema(df['close'], period)

        # BOLL指标
        if self.config.get('BOLL', {}).get('enabled', False):
            boll_config = self.config['BOLL']
            period = boll_config.get('period', 20)
            std_dev = boll_config.get('std_dev', 2)
            boll = calculate_boll(df['close'], period, std_dev)
            result_df['BOLL_UPPER'] = boll['upper']
            result_df['BOLL_MIDDLE'] = boll['middle']
            result_df['BOLL_LOWER'] = boll['lower']

        # RSI指标
        if self.config.get('RSI', {}).get('enabled', False):
            period = self.config['RSI'].get('period', 14)
            result_df['RSI'] = calculate_rsi(df['close'], period)

        # MACD指标
        if self.config.get('MACD', {}).get('enabled', False):
            macd_config = self.config['MACD']
            fast = macd_config.get('fast', 12)
            slow = macd_config.get('slow', 26)
            signal = macd_config.get('signal', 9)
            macd = calculate_macd(df['close'], fast, slow, signal)
            result_df['MACD'] = macd['macd']
            result_df['MACD_SIGNAL'] = macd['macd_signal']
            result_df['MACD_HIST'] = macd['macd_hist']

        return result_df

    def analyze_ma_trend(self, df: pd.DataFrame) -> Dict:
        """分析MA趋势"""
        if len(df) < 2:
            return {'action': 'hold', 'confidence': 0, 'reason': '数据不足'}

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # 获取所有MA列
        ma_cols = [col for col in df.columns if col.startswith('MA_')]
        if not ma_cols:
            return {'action': 'hold', 'confidence': 0, 'reason': '未启用MA指标'}

        # 按周期排序（短周期到长周期）
        ma_cols_sorted = sorted(ma_cols, key=lambda x: int(x.split('_')[1]))

        # 检查多头排列：短期MA > 长期MA
        bullish_aligned = True
        bearish_aligned = True

        for i in range(len(ma_cols_sorted) - 1):
            short_ma = latest[ma_cols_sorted[i]]
            long_ma = latest[ma_cols_sorted[i + 1]]

            if pd.isna(short_ma) or pd.isna(long_ma):
                continue

            if short_ma <= long_ma:
                bullish_aligned = False
            if short_ma >= long_ma:
                bearish_aligned = False

        # 价格与MA关系
        price = latest['close']
        shortest_ma = latest[ma_cols_sorted[0]] if not pd.isna(latest[ma_cols_sorted[0]]) else price
        longest_ma = latest[ma_cols_sorted[-1]] if not pd.isna(latest[ma_cols_sorted[-1]]) else price

        # 生成信号
        if bullish_aligned and price > shortest_ma:
            return {
                'action': 'buy',
                'confidence': 80,
                'reason': f'MA多头排列：价格{price:.2f} > MA均线，趋势向上'
            }
        elif bearish_aligned and price < shortest_ma:
            return {
                'action': 'sell',
                'confidence': 80,
                'reason': f'MA空头排列：价格{price:.2f} < MA均线，趋势向下'
            }
        else:
            return {
                'action': 'hold',
                'confidence': 50,
                'reason': f'MA均线交织，趋势不明'
            }

    def analyze_ema_trend(self, df: pd.DataFrame) -> Dict:
        """分析EMA趋势"""
        if len(df) < 2:
            return {'action': 'hold', 'confidence': 0, 'reason': '数据不足'}

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # 获取所有EMA列
        ema_cols = [col for col in df.columns if col.startswith('EMA_')]
        if not ema_cols:
            return {'action': 'hold', 'confidence': 0, 'reason': '未启用EMA指标'}

        # 按周期排序（短周期到长周期）
        ema_cols_sorted = sorted(ema_cols, key=lambda x: int(x.split('_')[1]))

        # 检查多头排列：短期EMA > 长期EMA
        bullish_aligned = True
        bearish_aligned = True

        for i in range(len(ema_cols_sorted) - 1):
            short_ema = latest[ema_cols_sorted[i]]
            long_ema = latest[ema_cols_sorted[i + 1]]

            if pd.isna(short_ema) or pd.isna(long_ema):
                continue

            if short_ema <= long_ema:
                bullish_aligned = False
            if short_ema >= long_ema:
                bearish_aligned = False

        # 价格与EMA关系
        price = latest['close']
        shortest_ema = latest[ema_cols_sorted[0]] if not pd.isna(latest[ema_cols_sorted[0]]) else price
        longest_ema = latest[ema_cols_sorted[-1]] if not pd.isna(latest[ema_cols_sorted[-1]]) else price

        # 生成信号
        if bullish_aligned and price > shortest_ema:
            return {
                'action': 'buy',
                'confidence': 85,
                'reason': f'多头排列：价格{price:.2f} > EMA均线，趋势向上'
            }
        elif bearish_aligned and price < shortest_ema:
            return {
                'action': 'sell',
                'confidence': 85,
                'reason': f'空头排列：价格{price:.2f} < EMA均线，趋势向下'
            }
        else:
            return {
                'action': 'hold',
                'confidence': 50,
                'reason': 'EMA均线未形成明确排列，观望'
            }

    def analyze_ema_alignment(self, df: pd.DataFrame) -> Dict:
        """
        分析EMA多空排列（第一档信号）
        多头排列: ema144 > ema576 且 ema169 > ema676
        空头排列: ema144 < ema576 且 ema169 < ema676

        Returns:
            {
                'action': 'buy' | 'sell' | 'hold',
                'confidence': 0-100,
                'reason': str,
                'tier': 1,  # 第一档信号
                'alignment_detail': str
            }
        """
        if len(df) < 1:
            return {'action': 'hold', 'confidence': 0, 'reason': '数据不足', 'tier': 1}

        latest = df.iloc[-1]

        # 检查必需的EMA列是否存在
        required_emas = ['EMA_144', 'EMA_576', 'EMA_169', 'EMA_676']
        for ema in required_emas:
            if ema not in df.columns:
                return {
                    'action': 'hold',
                    'confidence': 0,
                    'reason': f'缺少{ema}指标',
                    'tier': 1
                }

        ema144 = latest['EMA_144']
        ema576 = latest['EMA_576']
        ema169 = latest['EMA_169']
        ema676 = latest['EMA_676']

        # 检查是否有NaN值
        if pd.isna(ema144) or pd.isna(ema576) or pd.isna(ema169) or pd.isna(ema676):
            return {
                'action': 'hold',
                'confidence': 0,
                'reason': 'EMA数据不足',
                'tier': 1
            }

        # 检查两对EMA的排列
        pair1_bullish = ema144 > ema576  # 第一对多头
        pair2_bullish = ema169 > ema676  # 第二对多头
        pair1_bearish = ema144 < ema576  # 第一对空头
        pair2_bearish = ema169 < ema676  # 第二对空头

        # 计算偏离程度（用于确定信号强度）
        pair1_deviation = abs(ema144 - ema576) / ema576 * 100 if ema576 > 0 else 0
        pair2_deviation = abs(ema169 - ema676) / ema676 * 100 if ema676 > 0 else 0
        avg_deviation = (pair1_deviation + pair2_deviation) / 2

        # 判断多头排列
        if pair1_bullish and pair2_bullish:
            # 偏离越大，趋势越强
            confidence = min(95, int(80 + avg_deviation * 3))  # 基础80分，最高95分
            return {
                'action': 'buy',
                'confidence': confidence,
                'reason': f'【第一档】EMA多头排列：144>{ema576:.2f}，169>{ema676:.2f}',
                'tier': 1,
                'alignment_detail': f'EMA144({ema144:.2f})>EMA576({ema576:.2f})，EMA169({ema169:.2f})>EMA676({ema676:.2f})'
            }

        # 判断空头排列（做空谨慎，信号强度降低）
        elif pair1_bearish and pair2_bearish:
            # 空头信号谨慎处理，置信度上限75分
            confidence = min(75, int(60 + avg_deviation * 3))
            return {
                'action': 'sell',
                'confidence': confidence,
                'reason': f'【第一档】EMA空头排列：144<{ema576:.2f}，169<{ema676:.2f} [谨慎]',
                'tier': 1,
                'alignment_detail': f'EMA144({ema144:.2f})<EMA576({ema576:.2f})，EMA169({ema169:.2f})<EMA676({ema676:.2f})'
            }

        # 排列不一致，观望
        else:
            alignment_status = []
            if pair1_bullish:
                alignment_status.append(f'144>{ema576:.2f}(多)')
            else:
                alignment_status.append(f'144<{ema576:.2f}(空)')

            if pair2_bullish:
                alignment_status.append(f'169>{ema676:.2f}(多)')
            else:
                alignment_status.append(f'169<{ema676:.2f}(空)')

            return {
                'action': 'hold',
                'confidence': 40,
                'reason': f'【第一档】EMA排列分歧：{" ".join(alignment_status)}',
                'tier': 1,
                'alignment_detail': ', '.join(alignment_status)
            }

    def analyze_boll(self, df: pd.DataFrame) -> Dict:
        """分析布林带信号"""
        if 'BOLL_UPPER' not in df.columns:
            return {'action': 'hold', 'confidence': 0, 'reason': '未启用BOLL指标'}

        if len(df) < 2:
            return {'action': 'hold', 'confidence': 0, 'reason': '数据不足'}

        latest = df.iloc[-1]
        price = latest['close']
        upper = latest['BOLL_UPPER']
        middle = latest['BOLL_MIDDLE']
        lower = latest['BOLL_LOWER']

        if pd.isna(upper) or pd.isna(middle) or pd.isna(lower):
            return {'action': 'hold', 'confidence': 0, 'reason': 'BOLL数据不足'}

        # 布林带策略
        if price <= lower:
            return {
                'action': 'buy',
                'confidence': 80,
                'reason': f'价格{price:.2f}触及下轨{lower:.2f}，超卖信号'
            }
        elif price >= upper:
            return {
                'action': 'sell',
                'confidence': 80,
                'reason': f'价格{price:.2f}触及上轨{upper:.2f}，超买信号'
            }
        elif price > middle:
            return {
                'action': 'hold',
                'confidence': 60,
                'reason': f'价格{price:.2f}在中轨{middle:.2f}上方，偏多'
            }
        else:
            return {
                'action': 'hold',
                'confidence': 60,
                'reason': f'价格{price:.2f}在中轨{middle:.2f}下方，偏空'
            }

    def analyze_rsi(self, df: pd.DataFrame) -> Dict:
        """分析RSI信号"""
        if 'RSI' not in df.columns:
            return {'action': 'hold', 'confidence': 0, 'reason': '未启用RSI指标'}

        if len(df) < 2:
            return {'action': 'hold', 'confidence': 0, 'reason': '数据不足'}

        latest = df.iloc[-1]
        rsi = latest['RSI']

        if pd.isna(rsi):
            return {'action': 'hold', 'confidence': 0, 'reason': 'RSI数据不足'}

        if rsi < 30:
            return {
                'action': 'buy',
                'confidence': 75,
                'reason': f'RSI={rsi:.1f} < 30，超卖'
            }
        elif rsi > 70:
            return {
                'action': 'sell',
                'confidence': 75,
                'reason': f'RSI={rsi:.1f} > 70，超买'
            }
        else:
            return {
                'action': 'hold',
                'confidence': 50,
                'reason': f'RSI={rsi:.1f}，中性区域'
            }

    def analyze_macd(self, df: pd.DataFrame) -> Dict:
        """分析MACD信号"""
        if 'MACD' not in df.columns:
            return {'action': 'hold', 'confidence': 0, 'reason': '未启用MACD指标'}

        if len(df) < 2:
            return {'action': 'hold', 'confidence': 0, 'reason': '数据不足'}

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        macd = latest['MACD']
        signal = latest['MACD_SIGNAL']
        hist = latest['MACD_HIST']

        prev_macd = previous['MACD']
        prev_signal = previous['MACD_SIGNAL']

        if pd.isna(macd) or pd.isna(signal):
            return {'action': 'hold', 'confidence': 0, 'reason': 'MACD数据不足'}

        # 金叉死叉
        if prev_macd <= prev_signal and macd > signal:
            return {
                'action': 'buy',
                'confidence': 80,
                'reason': 'MACD金叉，买入信号'
            }
        elif prev_macd >= prev_signal and macd < signal:
            return {
                'action': 'sell',
                'confidence': 80,
                'reason': 'MACD死叉，卖出信号'
            }
        else:
            return {
                'action': 'hold',
                'confidence': 50,
                'reason': 'MACD无明确信号'
            }

    def analyze_trend_strength(self, price_data_by_timeframe: Dict[str, pd.DataFrame]) -> Dict:
        """
        分析多周期趋势强度（第一档信号 - 高低点抬升判断）

        Args:
            price_data_by_timeframe: 各周期的价格数据，如 {'1h': df, '4h': df, ...}

        Returns:
            趋势强度分析结果（第一档信号）
        """
        if not self.trend_strength_analyzer:
            return {'action': 'hold', 'confidence': 0, 'reason': '未启用趋势强度分析', 'tier': 1}

        result = self.trend_strength_analyzer.analyze_multi_timeframe(price_data_by_timeframe)

        # 标记为第一档信号，并添加【第一档】标签
        result['tier'] = 1
        if result.get('reason'):
            result['reason'] = f"【第一档】{result['reason']}"

        return result

    def generate_combined_signal(self, df: pd.DataFrame, price_data_by_timeframe: Dict[str, pd.DataFrame] = None) -> Dict:
        """
        综合所有指标生成信号（两档优先级系统）

        优先级系统：
        - 第一档（最高优先级）：EMA多空排列 + 高低点抬升判断
        - 第二档（辅助判断）：K线形态分析
        - 其他指标：MA、BOLL、RSI、MACD（辅助参考）

        Args:
            df: 主时间周期的价格数据
            price_data_by_timeframe: 可选，各周期的价格数据用于趋势强度分析
        """
        # 计算所有指标
        df_with_indicators = self.calculate_all_indicators(df)

        # ========== 第一档信号（最高优先级）==========
        tier1_signals = []

        # 1. EMA多空排列判断
        ema_alignment_signal = self.analyze_ema_alignment(df_with_indicators)
        if ema_alignment_signal['confidence'] > 0:
            tier1_signals.append(ema_alignment_signal)

        # 2. 高低点抬升判断（趋势强度分析）
        if price_data_by_timeframe:
            trend_strength_signal = self.analyze_trend_strength(price_data_by_timeframe)
            if trend_strength_signal['confidence'] > 0:
                tier1_signals.append(trend_strength_signal)

        # ========== 第二档信号（K线形态）==========
        tier2_signals = []

        # K线形态分析
        if self.candlestick_analyzer:
            candlestick_signal = self.candlestick_analyzer.analyze_all_patterns(df)
            if candlestick_signal['confidence'] > 0:
                candlestick_signal['tier'] = 2  # 标记为第二档
                tier2_signals.append(candlestick_signal)

        # ========== 其他辅助信号 ==========
        auxiliary_signals = []

        # MA趋势
        ma_signal = self.analyze_ma_trend(df_with_indicators)
        if ma_signal['confidence'] > 0:
            auxiliary_signals.append(ma_signal)

        # EMA趋势（通用）
        ema_signal = self.analyze_ema_trend(df_with_indicators)
        if ema_signal['confidence'] > 0:
            auxiliary_signals.append(ema_signal)

        # BOLL
        boll_signal = self.analyze_boll(df_with_indicators)
        if boll_signal['confidence'] > 0:
            auxiliary_signals.append(boll_signal)

        # RSI
        rsi_signal = self.analyze_rsi(df_with_indicators)
        if rsi_signal['confidence'] > 0:
            auxiliary_signals.append(rsi_signal)

        # MACD
        macd_signal = self.analyze_macd(df_with_indicators)
        if macd_signal['confidence'] > 0:
            auxiliary_signals.append(macd_signal)

        # ========== 综合所有信号 ==========
        all_signals = tier1_signals + tier2_signals + auxiliary_signals

        if not all_signals:
            return {
                'action': 'hold',
                'confidence': 0,
                'reason': '无有效指标信号',
                'indicators_detail': [],
                'tier_breakdown': {'tier1': 0, 'tier2': 0, 'auxiliary': 0}
            }

        # ========== 两档优先级决策逻辑 ==========

        # 统计第一档信号
        tier1_buy = [s for s in tier1_signals if s['action'] == 'buy']
        tier1_sell = [s for s in tier1_signals if s['action'] == 'sell']
        tier1_buy_conf = sum(s['confidence'] for s in tier1_buy) / len(tier1_signals) if tier1_buy else 0
        tier1_sell_conf = sum(s['confidence'] for s in tier1_sell) / len(tier1_signals) if tier1_sell else 0

        # 统计第二档信号
        tier2_buy = [s for s in tier2_signals if s['action'] == 'buy']
        tier2_sell = [s for s in tier2_signals if s['action'] == 'sell']
        tier2_buy_conf = sum(s['confidence'] for s in tier2_buy) / len(tier2_signals) if tier2_buy and tier2_signals else 0
        tier2_sell_conf = sum(s['confidence'] for s in tier2_sell) / len(tier2_signals) if tier2_sell and tier2_signals else 0

        # 统计辅助信号
        aux_buy = [s for s in auxiliary_signals if s['action'] == 'buy']
        aux_sell = [s for s in auxiliary_signals if s['action'] == 'sell']
        aux_buy_conf = sum(s['confidence'] for s in aux_buy) / len(auxiliary_signals) if aux_buy and auxiliary_signals else 0
        aux_sell_conf = sum(s['confidence'] for s in aux_sell) / len(auxiliary_signals) if aux_sell and auxiliary_signals else 0

        # 决策逻辑：
        # 1. 第一档信号明确（confidence > 60）时，主要依据第一档
        # 2. 第二档和辅助信号可以加强或削弱第一档信号
        # 3. 第一档信号不明确时，综合考虑第二档和辅助信号

        if tier1_buy_conf > 60 or tier1_sell_conf > 60:
            # 第一档信号明确
            if tier1_buy_conf > tier1_sell_conf:
                action = 'buy'
                # 第二档和辅助信号可以加强置信度
                boost = 0
                if tier2_buy_conf > tier2_sell_conf:
                    boost += 5
                if aux_buy_conf > aux_sell_conf:
                    boost += 3
                confidence = min(95, tier1_buy_conf + boost)
                reason = f'【第一档主导】看多 (第一档{len(tier1_buy)}/{len(tier1_signals)}，第二档{len(tier2_buy)}/{len(tier2_signals)}，辅助{len(aux_buy)}/{len(auxiliary_signals)})'
            else:
                action = 'sell'
                boost = 0
                if tier2_sell_conf > tier2_buy_conf:
                    boost += 5
                if aux_sell_conf > aux_buy_conf:
                    boost += 3
                confidence = min(80, tier1_sell_conf + boost)  # 做空谨慎，上限80
                reason = f'【第一档主导】看空 (第一档{len(tier1_sell)}/{len(tier1_signals)}，第二档{len(tier2_sell)}/{len(tier2_signals)}，辅助{len(aux_sell)}/{len(auxiliary_signals)}) [谨慎]'
        else:
            # 第一档信号不明确，综合考虑所有信号
            # 权重：第一档50%，第二档30%，辅助20%
            total_buy_conf = tier1_buy_conf * 0.5 + tier2_buy_conf * 0.3 + aux_buy_conf * 0.2
            total_sell_conf = tier1_sell_conf * 0.5 + tier2_sell_conf * 0.3 + aux_sell_conf * 0.2

            if total_buy_conf > total_sell_conf and total_buy_conf > 40:
                action = 'buy'
                confidence = int(total_buy_conf)
                reason = f'综合信号看多 (第一档{len(tier1_buy)}，第二档{len(tier2_buy)}，辅助{len(aux_buy)})'
            elif total_sell_conf > total_buy_conf and total_sell_conf > 40:
                action = 'sell'
                confidence = int(total_sell_conf * 0.85)  # 做空谨慎，打85折
                reason = f'综合信号看空 (第一档{len(tier1_sell)}，第二档{len(tier2_sell)}，辅助{len(aux_sell)}) [谨慎]'
            else:
                action = 'hold'
                confidence = 50
                reason = f'信号分歧，观望 (多空力量接近)'

        return {
            'action': action,
            'confidence': int(confidence),
            'reason': reason,
            'indicators_detail': [
                f"【第一档】 {s['action'].upper()} ({s['confidence']}%): {s['reason']}"
                if s.get('tier') == 1 else
                f"【第二档】 {s['action'].upper()} ({s['confidence']}%): {s['reason']}"
                if s.get('tier') == 2 else
                f"[辅助] {s['action'].upper()} ({s['confidence']}%): {s['reason']}"
                for s in all_signals
            ],
            'tier_breakdown': {
                'tier1': f'{len(tier1_buy)}买/{len(tier1_sell)}卖',
                'tier2': f'{len(tier2_buy)}买/{len(tier2_sell)}卖',
                'auxiliary': f'{len(aux_buy)}买/{len(aux_sell)}卖'
            }
        }


def create_multi_indicator_analyzer(indicators_config: Dict[str, Any]) -> MultiIndicatorAnalyzer:
    """创建多指标分析器的工厂函数"""
    return MultiIndicatorAnalyzer(indicators_config)
