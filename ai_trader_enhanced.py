"""
Enhanced AI Trader - Combines Technical Strategy with AI Judgment
结合技术指标策略和AI判断的增强版交易引擎
"""
import json
import pandas as pd
from typing import Dict, Optional, List
from openai import OpenAI, APIConnectionError, APIError
from strategy import create_strategy
from indicators_advanced import create_multi_indicator_analyzer
from trading_knowledge_modules import TradingKnowledgeManager


class EnhancedAITrader:
    """增强版AI交易员 - 结合技术分析策略和AI智能"""

    def __init__(self, api_key: str, api_url: str, model_name: str,
                 strategy_name: Optional[str] = None, custom_prompt: Optional[str] = None,
                 indicators_config: Optional[str] = None,
                 knowledge_modules: Optional[List[str]] = None,
                 knowledge_params: Optional[Dict] = None):
        """
        初始化增强版AI交易引擎

        Args:
            api_key: AI服务API密钥
            api_url: AI服务URL
            model_name: AI模型名称
            strategy_name: 技术指标策略名称 (MovingAverage, RSI, MACD, Combined, MultiIndicator)
            custom_prompt: 自定义系统提示词（可选）
            indicators_config: 多指标配置JSON字符串（当strategy_name为MultiIndicator时使用）
            knowledge_modules: 启用的交易知识模块列表（可选）
            knowledge_params: 知识模块参数（如止损比例、仓位大小等）
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model_name = model_name
        self.strategy_name = strategy_name
        self.custom_prompt = custom_prompt
        self.indicators_config = indicators_config
        self.knowledge_modules = knowledge_modules or []
        self.knowledge_params = knowledge_params or {}

        # 初始化交易知识模块管理器
        self.knowledge_manager = TradingKnowledgeManager()

        # 初始化技术指标策略（如果指定）
        self.strategy = None
        self.multi_indicator_analyzer = None

        if strategy_name and strategy_name != 'None':
            if strategy_name == 'MultiIndicator':
                # 使用多指标分析器
                try:
                    if indicators_config:
                        config_dict = json.loads(indicators_config)
                        self.multi_indicator_analyzer = create_multi_indicator_analyzer(config_dict)
                        print(f"[INFO] Multi-indicator analyzer loaded with config: {list(config_dict.keys())}")
                    else:
                        print(f"[WARNING] MultiIndicator strategy selected but no config provided")
                except Exception as e:
                    print(f"[WARNING] Failed to load multi-indicator analyzer: {e}")
            else:
                # 使用单一策略
                try:
                    self.strategy = create_strategy(strategy_name)
                    print(f"[INFO] Technical strategy loaded: {strategy_name}")
                except Exception as e:
                    print(f"[WARNING] Failed to load strategy {strategy_name}: {e}")
                    self.strategy = None

        # 打印已启用的知识模块
        if self.knowledge_modules:
            print(f"[INFO] Trading knowledge modules enabled: {', '.join(self.knowledge_modules)}")

    def make_decision(self, market_state: Dict, portfolio: Dict,
                     account_info: Dict, historical_data: Optional[Dict] = None) -> Dict:
        """
        综合决策：技术指标策略 + AI判断

        Args:
            market_state: 市场状态数据
            portfolio: 投资组合状态
            account_info: 账户信息
            historical_data: 历史数据（用于技术指标计算）

        Returns:
            交易决策字典
        """
        # 步骤1: 如果有技术指标策略，先获取策略建议
        strategy_signals = {}
        if (self.strategy or self.multi_indicator_analyzer) and historical_data:
            strategy_signals = self._get_strategy_signals(historical_data)

        # 步骤2: 构建包含策略建议的提示词
        prompt = self._build_enhanced_prompt(
            market_state, portfolio, account_info, strategy_signals
        )

        # 步骤3: 调用AI获取决策
        response = self._call_llm(prompt)

        # 步骤4: 解析AI响应
        decisions = self._parse_response(response)

        return decisions

    def _get_strategy_signals(self, historical_data: Dict) -> Dict:
        """
        获取技术指标策略的信号

        Args:
            historical_data: 历史价格数据字典 {coin: [prices]}

        Returns:
            策略信号字典 {coin: {action, confidence, reason, indicators_detail}}
        """
        signals = {}

        for coin, prices in historical_data.items():
            if not prices or len(prices) < 20:
                continue

            try:
                # 构建DataFrame
                df = pd.DataFrame({
                    'timestamp': range(len(prices)),
                    'open': prices,
                    'high': prices,
                    'low': prices,
                    'close': prices,
                    'volume': [0] * len(prices)  # 简化处理
                })

                # 使用多指标分析器或单一策略
                if self.multi_indicator_analyzer:
                    # 使用多指标分析器
                    result = self.multi_indicator_analyzer.generate_combined_signal(df)
                    signals[coin] = {
                        'action': result['action'],
                        'confidence': result['confidence'] / 100.0,  # 转换为0-1范围
                        'reason': result['reason'],
                        'indicators_detail': result.get('indicators_detail', [])
                    }
                elif self.strategy:
                    # 使用单一策略
                    df = self.strategy.calculate_indicators(df)
                    signal = self.strategy.generate_signal(df)
                    signals[coin] = {
                        'action': signal['action'],
                        'confidence': signal.get('confidence', 0.5),
                        'reason': self._get_signal_reason(df, signal['action']),
                        'indicators_detail': []
                    }

            except Exception as e:
                print(f"[WARNING] Strategy analysis failed for {coin}: {e}")
                import traceback
                traceback.print_exc()
                continue

        return signals

    def _get_signal_reason(self, df: pd.DataFrame, action: str) -> str:
        """根据技术指标生成信号理由"""
        if len(df) == 0:
            return "Insufficient data"

        last_row = df.iloc[-1]
        reasons = []

        # 移动平均线
        if 'sma_fast' in last_row and 'sma_slow' in last_row:
            if last_row['sma_fast'] > last_row['sma_slow']:
                reasons.append(f"SMA bullish (Fast:{last_row['sma_fast']:.2f} > Slow:{last_row['sma_slow']:.2f})")
            else:
                reasons.append(f"SMA bearish (Fast:{last_row['sma_fast']:.2f} < Slow:{last_row['sma_slow']:.2f})")

        # RSI
        if 'rsi' in last_row:
            rsi = last_row['rsi']
            if rsi < 30:
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 70:
                reasons.append(f"RSI overbought ({rsi:.1f})")
            else:
                reasons.append(f"RSI neutral ({rsi:.1f})")

        # MACD
        if 'macd' in last_row and 'macd_signal' in last_row:
            if last_row['macd'] > last_row['macd_signal']:
                reasons.append(f"MACD bullish")
            else:
                reasons.append(f"MACD bearish")

        return "; ".join(reasons) if reasons else "Technical analysis"

    def _build_enhanced_prompt(self, market_state: Dict, portfolio: Dict,
                              account_info: Dict, strategy_signals: Dict) -> str:
        """构建增强版提示词，包含技术指标分析和交易知识"""

        # 使用知识模块构建基础提示词
        if self.knowledge_modules:
            # 如果启用了知识模块，使用知识管理器构建提示词
            system_prompt = self.knowledge_manager.build_enhanced_prompt(
                enabled_modules=self.knowledge_modules,
                base_prompt=self.custom_prompt or "",
                **self.knowledge_params
            )
        else:
            # 否则使用传统方式
            system_prompt = self.custom_prompt if self.custom_prompt else \
                "You are a professional cryptocurrency trader combining technical analysis with market insights."

        prompt = f"""{system_prompt}

MARKET DATA:
"""
        for coin, data in market_state.items():
            prompt += f"{coin}: ${data['price']:.2f} ({data['change_24h']:+.2f}%)\n"

        # 首先单独展示各指标详细分析（如果有）
        has_indicators_detail = any('indicators_detail' in signal and signal['indicators_detail']
                                    for signal in strategy_signals.values()) if strategy_signals else False

        if has_indicators_detail:
            prompt += f"\nTECHNICAL INDICATORS ANALYSIS:\n"
            for coin, signal in strategy_signals.items():
                if 'indicators_detail' in signal and signal['indicators_detail']:
                    prompt += f"{coin}:\n"
                    for detail in signal['indicators_detail']:
                        prompt += f"  • {detail}\n"
                    prompt += "\n"

        # 然后展示综合分析结论
        if strategy_signals:
            prompt += f"\nTECHNICAL ANALYSIS SUMMARY:\n"
            for coin, signal in strategy_signals.items():
                prompt += f"{coin}:\n"
                prompt += f"  - Signal: {signal['action'].upper()}\n"
                prompt += f"  - Confidence: {signal['confidence']:.0%}\n"
                prompt += f"  - Reason: {signal['reason']}\n"

            prompt += "\n⚠️ IMPORTANT: The technical analysis provides baseline signals, but you should:\n"
            prompt += "1. Consider these signals as important references\n"
            prompt += "2. Add your own market analysis and judgment\n"
            prompt += "3. Make final decisions that balance technical signals with current market conditions\n"
            prompt += "4. You can agree, disagree, or partially follow the signals based on your analysis\n\n"

        prompt += f"""
ACCOUNT STATUS:
- Initial Capital: ${account_info['initial_capital']:.2f}
- Total Value: ${portfolio['total_value']:.2f}
- Cash: ${portfolio['cash']:.2f}
- Total Return: {account_info['total_return']:.2f}%

CURRENT POSITIONS:
"""
        if portfolio['positions']:
            for pos in portfolio['positions']:
                prompt += f"- {pos['coin']} {pos['side']}: {pos['quantity']:.4f} @ ${pos['avg_price']:.2f} ({pos['leverage']}x)\n"
        else:
            prompt += "None\n"

        prompt += """
TRADING RULES:
1. Signals: buy_to_enter (long), sell_to_enter (short), close_position, hold
2. Risk Management:
   - Max 3 positions
   - Risk 1-5% per trade
   - Use appropriate leverage (1-20x)
3. Decision Making:
   - CAREFULLY CONSIDER technical indicator signals (if provided)
   - Combine with your own analysis
   - Provide detailed justification for agreeing/disagreeing with technical signals
4. Exit Strategy:
   - Close losing positions quickly
   - Let winners run
   - Use stop-loss and profit targets

OUTPUT FORMAT (JSON only):
```json
{
  "COIN": {
    "signal": "buy_to_enter|sell_to_enter|hold|close_position",
    "quantity": 0.5,
    "leverage": 10,
    "profit_target": 45000.0,
    "stop_loss": 42000.0,
    "confidence": 0.75,
    "justification": "Explain your decision, referencing technical indicators if applicable"
  }
}
```

Analyze and output JSON only.
"""

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        try:
            base_url = self.api_url.rstrip('/')
            if not base_url.endswith('/v1'):
                if '/v1' in base_url:
                    base_url = base_url.split('/v1')[0] + '/v1'
                else:
                    base_url = base_url + '/v1'

            client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )

            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional cryptocurrency trader. Combine technical analysis with market insights. Output JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except APIConnectionError as e:
            error_msg = f"API connection failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg)
        except APIError as e:
            error_msg = f"API error ({e.status_code}): {e.message}"
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"LLM call failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            print(traceback.format_exc())
            raise Exception(error_msg)

    def _parse_response(self, response: str) -> Dict:
        """解析AI响应"""
        response = response.strip()

        if '```json' in response:
            response = response.split('```json')[1].split('```')[0]
        elif '```' in response:
            response = response.split('```')[1].split('```')[0]

        try:
            decisions = json.loads(response.strip())
            return decisions
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse failed: {e}")
            print(f"[DATA] Response:\n{response}")
            return {}


# 保持向后兼容
class AITrader(EnhancedAITrader):
    """向后兼容的AITrader类"""
    def __init__(self, api_key: str, api_url: str, model_name: str):
        super().__init__(api_key, api_url, model_name, strategy_name=None)
