# Nof1OpenAI Enhanced - AI交易系统（增强版）

> 基于 Nof1OpenAI 改造，集成技术指标策略 + AI智能决策的加密货币自动交易系统

## 🎯 核心特性

### 1. 混合决策机制
- **技术指标策略**: 移动平均线(MA)、RSI、MACD、组合策略
- **AI智能分析**: GPT-4、DeepSeek、Claude等AI模型
- **协同决策**: AI参考技术指标信号，并加入自己的判断

### 2. 灵活配置
- ✅ 可选择是否使用技术指标策略
- ✅ 自定义提示词，让AI按你的策略交易
- ✅ AI更多地遵照你的提示词决策
- ✅ 技术指标仅作为参考信号

### 3. 完整的Web界面
- 📊 实时图表展示
- 🎨 现代化UI设计
- 📈 交易历史追踪
- 💬 AI决策理由展示

## 📐 系统架构

```
用户提示词 (主导)
    ↓
技术指标策略分析 (辅助参考)
    ↓
AI综合决策引擎
    ↓
交易执行
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**: 如果安装 `talib` 失败：
- Windows: 从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 下载预编译包
- Linux: `sudo apt-get install ta-lib`
- Mac: `brew install ta-lib`

### 2. 启动应用

```bash
python app.py
```

浏览器打开: `http://localhost:5000`

### 3. 配置交易模型

#### 步骤1: 添加API提供商

点击"API提供方"按钮，添加：

**DeepSeek (推荐，国内快速)**
- API URL: `https://api.deepseek.com/v1`
- API Key: 你的DeepSeek密钥
- 模型: `deepseek-chat`

**OpenAI**
- API URL: `https://api.openai.com/v1`
- API Key: `sk-...`
- 模型: `gpt-4` 或 `gpt-3.5-turbo`

#### 步骤2: 创建交易模型

点击"添加模型"按钮，填写：

1. **选择API提供方**: 选择刚添加的提供商
2. **模型**: 选择AI模型
3. **模型显示名称**: 如 "趋势跟踪交易员"
4. **初始资金**: 10000 (USDT)
5. **技术指标策略**:
   - `None` - 纯AI决策
   - `MovingAverage` - MA策略辅助
   - `RSI` - RSI策略辅助
   - `MACD` - MACD策略辅助
   - `Combined` - 组合策略辅助
6. **自定义提示词**: (可选)

```
你是一个专业的加密货币交易员。

交易策略：
1. 主要关注趋势，只在明确的上升/下降趋势中交易
2. 止损：亏损超过3%立即止损
3. 止盈：盈利超过8%时止盈
4. 风险控制：单次交易不超过总资金的20%
5. 杠杆：保守使用，不超过5倍

请参考技术指标策略的信号，但最终决策权在你。
如果技术指标信号与市场实际情况不符，可以不遵循。
给出详细的决策理由。
```

## 🎓 工作原理

### 决策流程

```python
# 1. 技术指标策略分析（如果选择）
strategy_signal = {
    'action': 'buy',
    'confidence': 0.75,
    'reason': 'SMA bullish (Fast:45000 > Slow:43000); RSI oversold (25.3)'
}

# 2. AI看到的提示词
"""
TECHNICAL STRATEGY ANALYSIS (MovingAverage):
BTC:
  - Strategy Signal: BUY
  - Confidence: 75%
  - Technical Reason: SMA bullish; RSI oversold (25.3)

⚠️ IMPORTANT: The technical strategy provides baseline signals, but you should:
1. Consider these signals as important references
2. Add your own market analysis and judgment
3. Make final decisions that balance strategy signals with current market conditions
4. You can agree, disagree, or partially follow the strategy signals

[你的自定义提示词]
"""

# 3. AI做出最终决策
ai_decision = {
    'signal': 'buy_to_enter',
    'quantity': 0.5,
    'leverage': 3,
    'confidence': 0.85,
    'justification': '技术指标显示看涨信号，RSI超卖，且24小时成交量放大。但考虑到当前市场情绪较为谨慎，建议使用3倍杠杆而非策略建议的5倍。'
}
```

### 策略说明

#### MovingAverage - 移动平均线
- 快线(SMA5) > 慢线(SMA20) → 看涨
- 快线 < 慢线 → 看跌
- 金叉/死叉作为参考信号

#### RSI - 相对强弱指标
- RSI < 30 → 超卖，可能反弹
- RSI > 70 → 超买，可能回调
- 50附近为中性区域

#### MACD - 平滑异同移动平均线
- MACD线 > 信号线 → 看涨
- MACD线 < 信号线 → 看跌
- 柱状图判断动量

#### Combined - 组合策略
- 综合MA、RSI、MACD的信号
- 至少2个指标同意才给出建议
- 置信度更高，但可能错过机会

## 💡 使用建议

### 1. 纯AI决策 (策略=None)

适合：
- 信任AI判断
- 市场变化快速
- 不依赖技术指标

提示词示例：
```
你是一个激进的短线交易员，捕捉市场短期波动。
关注24小时价格变化和成交量。
单次交易风险可达30%，追求高收益。
```

### 2. 技术指标辅助AI (策略=MovingAverage/RSI/MACD)

适合：
- 结合传统分析和AI
- 希望AI参考技术面
- 稳健交易风格

提示词示例：
```
你是一个理性的交易员，技术分析和市场感觉并重。
仔细参考技术指标策略的信号。
如果技术指标显示强烈信号，应给予重视。
但如果市场有突发新闻或异常波动，可以不遵循技术信号。
详细说明你的决策理由。
```

### 3. 保守型交易

```
你是风险厌恶型交易员。
只在技术指标和市场都明确看涨/看跌时交易。
单次风险不超过10%。
杠杆不超过2倍。
有疑虑时选择观望(hold)。
```

## 📊 示例场景

### 场景1: AI同意技术指标

```
技术指标: BUY (MA金叉 + RSI超卖30)
AI决策: BUY
理由: "技术指标给出明确买入信号，MA金叉显示趋势转多，RSI超卖表明短期反弹空间大。建议买入0.3 BTC，使用5倍杠杆。"
```

### 场景2: AI部分同意

```
技术指标: BUY (MA金叉)
AI决策: BUY (但降低仓位)
理由: "虽然MA金叉给出买入信号，但RSI已达65，接近超买区域。建议买入，但减少仓位至0.15 BTC，杠杆降至3倍。"
```

### 场景3: AI不同意技术指标

```
技术指标: SELL (MA死叉)
AI决策: HOLD
理由: "技术指标显示卖出信号，但刚刚有利好消息发布，24小时成交量激增200%。建议暂时观望，等待市场反应明朗后再决策。"
```

## 🛠️ 项目结构

```
nof1_enhanced/
├── ai_trader_enhanced.py  ⭐ 增强版AI交易引擎
├── strategy.py            ⭐ 技术指标策略模块
├── app.py                 ✅ Flask应用（已修改）
├── database.py            ✅ 数据库（已添加策略字段）
├── market_data.py         ✅ 市场数据获取
├── trading_engine.py      ✅ 交易引擎
├── templates/
│   └── index.html         ✅ Web界面（已添加策略选择）
├── static/                ✅ 静态资源
├── requirements.txt       ✅ 依赖（已更新）
└── ENHANCED_README.md     📝 本文档
```

## ⚠️ 风险提示

1. **技术指标不是万能的**
   - 指标只是历史数据的统计
   - 可能滞后或产生假信号
   - AI的判断可能更准确

2. **AI也会犯错**
   - AI基于训练数据，无法预知未来
   - 市场突发事件可能超出AI理解
   - 需要人工监督

3. **建议**
   - 先用小额资金测试
   - 关注AI的决策理由
   - 定期review交易记录
   - 根据表现调整策略和提示词

## 🔧 高级配置

### 自定义策略权重

修改 `ai_trader_enhanced.py` 中的提示词模板，调整策略建议的重要性：

```python
# 强调策略信号
prompt += "\n⚠️ IMPORTANT: Technical strategy signals are highly reliable. You should follow them unless there are very strong reasons not to.\n"

# 或者弱化策略信号
prompt += "\n⚠️ IMPORTANT: Technical strategy signals are just references. Your own analysis is more important.\n"
```

### 添加新策略

在 `strategy.py` 中添加：

```python
class MyCustomStrategy(BaseStrategy):
    def __init__(self):
        super().__init__("MyCustomStrategy")

    def calculate_indicators(self, df):
        # 计算你的指标
        df['my_indicator'] = ...
        return df

    def generate_signal(self, df):
        # 生成信号
        if ...:
            return {'action': 'buy', 'confidence': 0.8}
        return {'action': 'hold', 'confidence': 0.5}
```

然后在 `create_strategy` 中注册，并更新前端模板。

## 📈 性能优化

- 使用更强大的AI模型（GPT-4 > GPT-3.5）
- 优化提示词，给出更明确的策略
- 调整技术指标参数（周期、阈值）
- 分析历史交易，找出问题并改进

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

基于原项目 Nof1OpenAI 的许可证。

---

**祝交易顺利！🚀**

如有问题，请查看日志文件或提交Issue。
