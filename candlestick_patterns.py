"""
K线形态分析模块 - 识别关键K线形态
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any


class CandlestickPatternAnalyzer:
    """
    K线形态分析器
    识别涨吞没、Pinbar、盘整洗盘、均线支撑等形态
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化K线形态分析器

        Args:
            config: 配置字典
            {
                "enabled": True,
                "lookback_bars": 20,  # 回看K线数量
                "pinbar_wick_ratio": 2.5,  # Pinbar下影线与实体比例
                "consolidation_bars": 3  # 盘整形态最少K线数
            }
        """
        self.enabled = config.get('enabled', True)
        self.lookback_bars = config.get('lookback_bars', 20)
        self.pinbar_wick_ratio = config.get('pinbar_wick_ratio', 2.5)
        self.consolidation_bars = config.get('consolidation_bars', 3)

    def analyze_bullish_engulfing(self, df: pd.DataFrame) -> Dict:
        """
        识别涨吞没形态
        阳线的收盘价高于前一根阴线的开盘价，立马收复了所有跌幅

        Returns:
            {
                'detected': bool,
                'strength': 0-100,
                'detail': str
            }
        """
        if len(df) < 2:
            return {'detected': False, 'strength': 0, 'detail': ''}

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # 检查前一根是阴线
        prev_is_bearish = previous['close'] < previous['open']
        if not prev_is_bearish:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查当前是阳线
        curr_is_bullish = latest['close'] > latest['open']
        if not curr_is_bullish:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查阳线收盘价是否高于前一根阴线开盘价（完全吞没）
        if latest['close'] > previous['open']:
            # 计算吞没强度
            prev_body = abs(previous['open'] - previous['close'])
            curr_body = abs(latest['close'] - latest['open'])

            # 当前阳线实体越大，强度越高
            strength_ratio = min(curr_body / prev_body, 3.0) if prev_body > 0 else 1.0
            strength = min(90, int(60 + strength_ratio * 10))

            return {
                'detected': True,
                'strength': strength,
                'detail': f'涨吞没：阳线({latest["close"]:.2f})完全吞没前阴线({previous["open"]:.2f})'
            }

        return {'detected': False, 'strength': 0, 'detail': ''}

    def analyze_pinbar(self, df: pd.DataFrame) -> Dict:
        """
        识别Pinbar形态（长下影线反转）
        向下假跌破，创下近N根K线最低价，然后回攻，收长下影线

        Returns:
            {
                'detected': bool,
                'strength': 0-100,
                'detail': str
            }
        """
        if len(df) < max(3, self.lookback_bars):
            return {'detected': False, 'strength': 0, 'detail': ''}

        latest = df.iloc[-1]
        recent_bars = df.iloc[-self.lookback_bars:]

        # 计算K线各部分
        body_size = abs(latest['close'] - latest['open'])
        lower_wick = min(latest['open'], latest['close']) - latest['low']
        upper_wick = latest['high'] - max(latest['open'], latest['close'])

        # 检查是否有长下影线（下影线是实体的2.5倍以上）
        if body_size > 0 and lower_wick / body_size >= self.pinbar_wick_ratio:
            # 检查是否创下近期新低
            is_recent_low = latest['low'] <= recent_bars['low'].min()

            if is_recent_low:
                # 检查是否收盘价回到相对高位（至少在K线50%以上）
                candle_range = latest['high'] - latest['low']
                close_position = (latest['close'] - latest['low']) / candle_range if candle_range > 0 else 0

                if close_position >= 0.5:
                    strength = int(70 + close_position * 20)  # 收盘位置越高，强度越大

                    return {
                        'detected': True,
                        'strength': strength,
                        'detail': f'Pinbar：创新低{latest["low"]:.2f}后强势反弹，下影线/实体={lower_wick/body_size:.1f}'
                    }

        return {'detected': False, 'strength': 0, 'detail': ''}

    def analyze_consolidation_after_rally(self, df: pd.DataFrame) -> Dict:
        """
        识别大阳线后的盘整洗盘形态
        大阳线后跟一个或几个小K线或十字星，不隐隐向下而是准备继续向上

        Returns:
            {
                'detected': bool,
                'strength': 0-100,
                'detail': str
            }
        """
        if len(df) < self.consolidation_bars + 1:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查第一根是否是大阳线
        rally_bar = df.iloc[-(self.consolidation_bars + 1)]
        rally_body = rally_bar['close'] - rally_bar['open']
        rally_range = rally_bar['high'] - rally_bar['low']

        # 判断是否是大阳线（实体占K线80%以上）
        if rally_body <= 0 or rally_body / rally_range < 0.8:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查后续的小K线
        consolidation_bars = df.iloc[-self.consolidation_bars:]

        # 计算盘整K线的平均实体大小
        avg_consol_body = consolidation_bars.apply(
            lambda x: abs(x['close'] - x['open']), axis=1
        ).mean()

        # 小K线实体应该明显小于大阳线（不超过30%）
        if avg_consol_body > rally_body * 0.3:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查盘整K线的趋势：不应该隐隐向下
        consolidation_highs = consolidation_bars['high'].values
        consolidation_lows = consolidation_bars['low'].values

        # 低点不应该持续走低（允许一次回踩）
        lower_lows_count = sum(
            1 for i in range(1, len(consolidation_lows))
            if consolidation_lows[i] < consolidation_lows[i-1]
        )

        if lower_lows_count > 1:  # 超过1次创新低，视为向下
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 最后一根K线应该在相对高位
        latest = df.iloc[-1]
        if latest['close'] < consolidation_bars['low'].min():
            return {'detected': False, 'strength': 0, 'detail': ''}

        strength = 75
        return {
            'detected': True,
            'strength': strength,
            'detail': f'洗盘整理：大阳线后{self.consolidation_bars}根小K线盘整，准备下一波进攻'
        }

    def analyze_support_at_ma(self, df: pd.DataFrame) -> Dict:
        """
        识别均线支撑企稳形态
        从高位一路大跌到某一根均线附近开始徘徊，不再跌破

        Returns:
            {
                'detected': bool,
                'strength': 0-100,
                'detail': str
            }
        """
        if len(df) < 20:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 计算关键均线
        df_copy = df.copy()
        df_copy['MA5'] = df_copy['close'].rolling(window=5).mean()
        df_copy['MA10'] = df_copy['close'].rolling(window=10).mean()
        df_copy['MA20'] = df_copy['close'].rolling(window=20).mean()

        latest = df_copy.iloc[-1]
        recent_bars = df_copy.iloc[-10:]  # 最近10根K线

        # 检查价格是否从高位下跌
        high_20 = df_copy.iloc[-20:]['high'].max()
        current_price = latest['close']
        decline_pct = (high_20 - current_price) / high_20 if high_20 > 0 else 0

        if decline_pct < 0.05:  # 至少有5%的跌幅
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查是否在某根均线附近企稳（允许3%的偏差）
        tolerance = 0.03

        for ma_name, ma_period in [('MA5', 5), ('MA10', 10), ('MA20', 20)]:
            ma_value = latest[ma_name]
            if pd.isna(ma_value):
                continue

            # 检查价格是否接近均线
            price_deviation = abs(current_price - ma_value) / ma_value
            if price_deviation > tolerance:
                continue

            # 检查最近几根K线是否都未跌破均线
            recent_lows = recent_bars['low'].values
            recent_mas = recent_bars[ma_name].values

            breaks_below = sum(
                1 for low, ma in zip(recent_lows, recent_mas)
                if not pd.isna(ma) and low < ma * 0.97  # 允许短暂刺穿3%
            )

            if breaks_below <= 1:  # 最多允许1次短暂刺穿
                # 检查K线是否变小（企稳信号）
                recent_bodies = recent_bars.apply(
                    lambda x: abs(x['close'] - x['open']), axis=1
                )
                avg_recent_body = recent_bodies.mean()
                earlier_bodies = df_copy.iloc[-20:-10].apply(
                    lambda x: abs(x['close'] - x['open']), axis=1
                ).mean()

                if avg_recent_body < earlier_bodies * 0.7:  # K线明显变小
                    strength = 70
                    return {
                        'detected': True,
                        'strength': strength,
                        'detail': f'{ma_name}支撑企稳：从{high_20:.2f}跌至{ma_name}({ma_value:.2f})后企稳'
                    }

        return {'detected': False, 'strength': 0, 'detail': ''}

    def analyze_oversold_bounce(self, df: pd.DataFrame) -> Dict:
        """
        识别超跌反弹形态
        - 连续4根或更多中阴线形成持续下跌
        - 随后出现一根阳线终止下跌
        - 代表超跌企稳，时间周期越长越好

        Returns:
            {
                'detected': bool,
                'strength': 0-100,
                'detail': str
            }
        """
        if len(df) < 6:  # 至少需要4根阴线 + 1根阳线 + 1根用于比较
            return {'detected': False, 'strength': 0, 'detail': ''}

        latest = df.iloc[-1]

        # 检查最后一根是否为阳线（已收盘）
        if latest['close'] <= latest['open']:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 向前查找连续阴线
        consecutive_bearish = 0
        total_decline = 0

        # 从倒数第二根开始往前找阴线
        for i in range(len(df) - 2, -1, -1):
            bar = df.iloc[i]

            # 检查是否为阴线（中阴线：收盘价 < 开盘价）
            if bar['close'] < bar['open']:
                consecutive_bearish += 1
                # 累计跌幅
                decline_pct = (bar['open'] - bar['close']) / bar['open']
                total_decline += decline_pct
            else:
                # 遇到非阴线，停止计数
                break

            # 已经找到足够多的连续阴线
            if consecutive_bearish >= 10:  # 设置上限，避免过度回溯
                break

        # 至少需要4根连续阴线
        if consecutive_bearish < 4:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查阳线是否有力度（不是十字星）
        bullish_body = latest['close'] - latest['open']
        bullish_range = latest['high'] - latest['low']

        if bullish_range == 0:
            return {'detected': False, 'strength': 0, 'detail': ''}

        body_ratio = bullish_body / bullish_range

        # 阳线实体至少占K线的40%
        if body_ratio < 0.4:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 计算强度
        # 基础强度：65分
        base_strength = 65

        # 连续阴线越多，强度越高（最多+15分）
        bearish_bonus = min(consecutive_bearish - 4, 6) * 2.5  # 每多1根+2.5分，最多6根

        # 阳线实体越大，强度越高（最多+10分）
        body_bonus = min(body_ratio - 0.4, 0.4) * 25  # 从0.4到0.8，最多+10分

        # 累计跌幅越大，反弹潜力越大（最多+10分）
        decline_bonus = min(total_decline, 0.2) * 50  # 跌幅20%以上给满分

        strength = int(base_strength + bearish_bonus + body_bonus + decline_bonus)
        strength = min(strength, 90)  # 上限90分

        # 计算平均每根阴线的跌幅
        avg_decline = (total_decline / consecutive_bearish * 100) if consecutive_bearish > 0 else 0

        return {
            'detected': True,
            'strength': strength,
            'detail': f'超跌反弹：连续{consecutive_bearish}根阴线(累计跌{total_decline*100:.1f}%)后阳线企稳'
        }

    def analyze_bearish_engulfing(self, df: pd.DataFrame) -> Dict:
        """
        识别跌吞没形态（看空）
        阴线的收盘价低于前一根阳线的开盘价

        Returns:
            {
                'detected': bool,
                'strength': 0-100,
                'detail': str
            }
        """
        if len(df) < 2:
            return {'detected': False, 'strength': 0, 'detail': ''}

        latest = df.iloc[-1]
        previous = df.iloc[-2]

        # 检查前一根是阳线
        prev_is_bullish = previous['close'] > previous['open']
        if not prev_is_bullish:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查当前是阴线
        curr_is_bearish = latest['close'] < latest['open']
        if not curr_is_bearish:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查阴线收盘价是否低于前一根阳线开盘价（完全吞没）
        if latest['close'] < previous['open']:
            # 计算吞没强度
            prev_body = abs(previous['open'] - previous['close'])
            curr_body = abs(latest['close'] - latest['open'])

            # 当前阴线实体越大，强度越高（但做空谨慎，降低评分）
            strength_ratio = min(curr_body / prev_body, 3.0) if prev_body > 0 else 1.0
            strength = min(75, int(50 + strength_ratio * 8))  # 做空谨慎：最高75分

            return {
                'detected': True,
                'strength': strength,
                'detail': f'跌吞没：阴线({latest["close"]:.2f})完全吞没前阳线({previous["open"]:.2f}) [谨慎]'
            }

        return {'detected': False, 'strength': 0, 'detail': ''}

    def analyze_shooting_star(self, df: pd.DataFrame) -> Dict:
        """
        识别射击之星/反向Pinbar（长上影线，看空）
        向上假突破，创下近N根K线最高价，然后回落，收长上影线

        Returns:
            {
                'detected': bool,
                'strength': 0-100,
                'detail': str
            }
        """
        if len(df) < max(3, self.lookback_bars):
            return {'detected': False, 'strength': 0, 'detail': ''}

        latest = df.iloc[-1]
        recent_bars = df.iloc[-self.lookback_bars:]

        # 计算K线各部分
        body_size = abs(latest['close'] - latest['open'])
        lower_wick = min(latest['open'], latest['close']) - latest['low']
        upper_wick = latest['high'] - max(latest['open'], latest['close'])

        # 检查是否有长上影线（上影线是实体的2.5倍以上）
        if body_size > 0 and upper_wick / body_size >= self.pinbar_wick_ratio:
            # 检查是否创下近期新高
            is_recent_high = latest['high'] >= recent_bars['high'].max()

            if is_recent_high:
                # 检查是否收盘价回到相对低位（至少在K线50%以下）
                candle_range = latest['high'] - latest['low']
                close_position = (latest['close'] - latest['low']) / candle_range if candle_range > 0 else 0

                if close_position <= 0.5:
                    strength = int(60 + (0.5 - close_position) * 20)  # 做空谨慎：最高70分

                    return {
                        'detected': True,
                        'strength': min(strength, 70),
                        'detail': f'射击之星：创新高{latest["high"]:.2f}后回落，上影线/实体={upper_wick/body_size:.1f} [谨慎]'
                    }

        return {'detected': False, 'strength': 0, 'detail': ''}

    def analyze_overbought_pullback(self, df: pd.DataFrame) -> Dict:
        """
        识别超涨回调形态（看空）
        连续4根或更多阳线后出现阴线

        Returns:
            {
                'detected': bool,
                'strength': 0-100,
                'detail': str
            }
        """
        if len(df) < 6:
            return {'detected': False, 'strength': 0, 'detail': ''}

        latest = df.iloc[-1]

        # 检查最后一根是否为阴线（已收盘）
        if latest['close'] >= latest['open']:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 向前查找连续阳线
        consecutive_bullish = 0
        total_rise = 0

        for i in range(len(df) - 2, -1, -1):
            bar = df.iloc[i]

            if bar['close'] > bar['open']:
                consecutive_bullish += 1
                rise_pct = (bar['close'] - bar['open']) / bar['open']
                total_rise += rise_pct
            else:
                break

            if consecutive_bullish >= 10:
                break

        if consecutive_bullish < 4:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 检查阴线是否有力度
        bearish_body = latest['open'] - latest['close']
        bearish_range = latest['high'] - latest['low']

        if bearish_range == 0:
            return {'detected': False, 'strength': 0, 'detail': ''}

        body_ratio = bearish_body / bearish_range

        if body_ratio < 0.4:
            return {'detected': False, 'strength': 0, 'detail': ''}

        # 计算强度（做空谨慎，降低评分）
        base_strength = 55
        bullish_bonus = min(consecutive_bullish - 4, 6) * 2
        body_bonus = min(body_ratio - 0.4, 0.4) * 20
        rise_bonus = min(total_rise, 0.2) * 40

        strength = int(base_strength + bullish_bonus + body_bonus + rise_bonus)
        strength = min(strength, 75)  # 做空谨慎：上限75分

        return {
            'detected': True,
            'strength': strength,
            'detail': f'超涨回调：连续{consecutive_bullish}根阳线(累计涨{total_rise*100:.1f}%)后阴线回调 [谨慎]'
        }

    def analyze_support_resistance(self, df: pd.DataFrame) -> Dict:
        """
        分析支撑阻力位
        - 前高形成阻力位（看空参考）
        - 前低形成支撑位（看多参考）
        - 多空共通

        Returns:
            {
                'near_resistance': bool,
                'near_support': bool,
                'detail': str,
                'resistance_level': float,
                'support_level': float
            }
        """
        if len(df) < 20:
            return {
                'near_resistance': False,
                'near_support': False,
                'detail': '',
                'resistance_level': 0,
                'support_level': 0
            }

        # 分析最近20根K线
        recent_bars = df.iloc[-20:]
        current_price = df.iloc[-1]['close']

        # 找前高（阻力位）
        resistance_level = recent_bars['high'].max()

        # 找前低（支撑位）
        support_level = recent_bars['low'].min()

        # 计算价格距离阻力位和支撑位的距离（百分比）
        resistance_distance = (resistance_level - current_price) / current_price if current_price > 0 else 1
        support_distance = (current_price - support_level) / current_price if current_price > 0 else 1

        # 判断是否接近（3%以内视为接近）
        tolerance = 0.03
        near_resistance = resistance_distance <= tolerance and resistance_distance >= 0
        near_support = support_distance <= tolerance and support_distance >= 0

        detail_parts = []
        if near_resistance:
            detail_parts.append(f'接近阻力位{resistance_level:.2f}(+{resistance_distance*100:.1f}%)')
        if near_support:
            detail_parts.append(f'接近支撑位{support_level:.2f}(-{support_distance*100:.1f}%)')

        detail = '、'.join(detail_parts) if detail_parts else ''

        return {
            'near_resistance': near_resistance,
            'near_support': near_support,
            'detail': detail,
            'resistance_level': resistance_level,
            'support_level': support_level
        }

    def check_trend_health(self, df: pd.DataFrame) -> Dict:
        """
        检查趋势健康度
        - 强势上涨：K线收盘价不应低于MA5
        - 健康上涨：K线收盘价不应低于BOLL中轨

        Returns:
            {
                'is_healthy': bool,
                'strength': 0-100,
                'violations': list,
                'detail': str
            }
        """
        if len(df) < 20:
            return {
                'is_healthy': True,
                'strength': 50,
                'violations': [],
                'detail': '数据不足'
            }

        # 计算MA5和BOLL
        df_copy = df.copy()
        df_copy['MA5'] = df_copy['close'].rolling(window=5).mean()
        df_copy['BOLL_MIDDLE'] = df_copy['close'].rolling(window=20).mean()

        # 检查最近10根K线
        recent_bars = df_copy.iloc[-10:]

        violations = []
        ma5_violations = 0
        boll_violations = 0

        for idx, bar in recent_bars.iterrows():
            if not pd.isna(bar['MA5']) and bar['close'] < bar['MA5']:
                ma5_violations += 1
                violations.append(f"K线收盘{bar['close']:.2f} < MA5({bar['MA5']:.2f})")

            if not pd.isna(bar['BOLL_MIDDLE']) and bar['close'] < bar['BOLL_MIDDLE']:
                boll_violations += 1

        # 判断健康度
        if ma5_violations == 0:
            return {
                'is_healthy': True,
                'strength': 90,
                'violations': [],
                'detail': '强势上涨：所有K线收盘价均高于MA5生命线'
            }
        elif boll_violations <= 1:
            return {
                'is_healthy': True,
                'strength': 70,
                'violations': violations[:2],  # 只显示前2个
                'detail': f'健康上涨：仅{boll_violations}根K线低于BOLL中轨'
            }
        else:
            return {
                'is_healthy': False,
                'strength': 40,
                'violations': violations[:3],  # 只显示前3个
                'detail': f'趋势疲弱：{ma5_violations}根K线破MA5，{boll_violations}根破BOLL中轨'
            }

    def analyze_all_patterns(self, df: pd.DataFrame) -> Dict:
        """
        综合分析所有K线形态

        Returns:
            {
                'action': 'buy' | 'sell' | 'hold',
                'confidence': 0-100,
                'reason': str,
                'patterns_detail': [list of pattern details]
            }
        """
        if not self.enabled:
            return {
                'action': 'hold',
                'confidence': 0,
                'reason': '未启用K线形态分析',
                'patterns_detail': []
            }

        if len(df) < max(20, self.lookback_bars):
            return {
                'action': 'hold',
                'confidence': 0,
                'reason': '数据不足',
                'patterns_detail': []
            }

        patterns = []
        bullish_signals = []
        bearish_signals = []

        # 1. 涨吞没
        engulfing = self.analyze_bullish_engulfing(df)
        if engulfing['detected']:
            patterns.append(f"✓ {engulfing['detail']}")
            bullish_signals.append(('涨吞没', engulfing['strength']))

        # 2. Pinbar
        pinbar = self.analyze_pinbar(df)
        if pinbar['detected']:
            patterns.append(f"✓ {pinbar['detail']}")
            bullish_signals.append(('Pinbar反转', pinbar['strength']))

        # 3. 洗盘整理
        consolidation = self.analyze_consolidation_after_rally(df)
        if consolidation['detected']:
            patterns.append(f"✓ {consolidation['detail']}")
            bullish_signals.append(('洗盘整理', consolidation['strength']))

        # 4. 均线支撑
        support = self.analyze_support_at_ma(df)
        if support['detected']:
            patterns.append(f"✓ {support['detail']}")
            bullish_signals.append(('均线支撑', support['strength']))

        # 5. 超跌反弹
        oversold = self.analyze_oversold_bounce(df)
        if oversold['detected']:
            patterns.append(f"✓ {oversold['detail']}")
            bullish_signals.append(('超跌反弹', oversold['strength']))

        # 6. 跌吞没（看空）
        bearish_engulfing = self.analyze_bearish_engulfing(df)
        if bearish_engulfing['detected']:
            patterns.append(f"⚠ {bearish_engulfing['detail']}")
            bearish_signals.append(('跌吞没', bearish_engulfing['strength']))

        # 7. 射击之星（看空）
        shooting_star = self.analyze_shooting_star(df)
        if shooting_star['detected']:
            patterns.append(f"⚠ {shooting_star['detail']}")
            bearish_signals.append(('射击之星', shooting_star['strength']))

        # 8. 超涨回调（看空）
        overbought = self.analyze_overbought_pullback(df)
        if overbought['detected']:
            patterns.append(f"⚠ {overbought['detail']}")
            bearish_signals.append(('超涨回调', overbought['strength']))

        # 9. 支撑阻力位（多空共通）
        sr = self.analyze_support_resistance(df)
        if sr['detail']:
            patterns.append(f"ℹ {sr['detail']}")
            # 接近阻力位增加看空信号
            if sr['near_resistance']:
                bearish_signals.append(('接近阻力', 60))
            # 接近支撑位增加看多信号
            if sr['near_support']:
                bullish_signals.append(('接近支撑', 60))

        # 10. 趋势健康度
        health = self.check_trend_health(df)
        if health['is_healthy']:
            patterns.append(f"✓ {health['detail']}")
            bullish_signals.append(('趋势健康', health['strength']))
        else:
            patterns.append(f"⚠ {health['detail']}")
            if health['violations']:
                patterns.extend([f"  - {v}" for v in health['violations']])
            bearish_signals.append(('趋势疲弱', 100 - health['strength']))

        # 综合判断
        if not patterns:
            return {
                'action': 'hold',
                'confidence': 0,
                'reason': '未检测到明确K线形态',
                'patterns_detail': []
            }

        bullish_score = sum(s[1] for s in bullish_signals)
        bearish_score = sum(s[1] for s in bearish_signals)

        # 做空要谨慎：看空信号需要更强的确认，将看空评分打7折
        bearish_score_adjusted = bearish_score * 0.7

        if bullish_score > bearish_score_adjusted and bullish_score > 70:
            action = 'buy'
            confidence = min(90, bullish_score // len(bullish_signals)) if bullish_signals else 0
            reason = f'看涨形态：{len(bullish_signals)}个多头信号'
        elif bearish_score_adjusted > bullish_score and bearish_score_adjusted > 60:
            # 做空需要更高门槛（60分 vs 70分）
            action = 'sell'
            # 做空信号置信度上限75分（vs 买入90分）
            confidence = min(75, int(bearish_score_adjusted / len(bearish_signals))) if bearish_signals else 0
            reason = f'看空形态：{len(bearish_signals)}个空头信号 [谨慎做空]'
        else:
            action = 'hold'
            confidence = 50
            if bullish_signals and bearish_signals:
                reason = f'多空信号混合（多{len(bullish_signals)}空{len(bearish_signals)}），观望为主'
            else:
                reason = '形态不明确，观望为主'

        return {
            'action': action,
            'confidence': confidence,
            'reason': reason,
            'patterns_detail': patterns
        }


def create_candlestick_pattern_analyzer(config: Dict[str, Any]) -> CandlestickPatternAnalyzer:
    """创建K线形态分析器实例"""
    return CandlestickPatternAnalyzer(config)
