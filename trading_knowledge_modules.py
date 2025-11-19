"""
交易知识模块库 - Trading Knowledge Modules
可选择性地为AI注入专业交易知识

用户可以在创建模型时选择想要的知识模块，系统会自动构建增强的提示词
"""

class TradingKnowledgeModule:
    """交易知识模块基类"""

    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category
        self.enabled = False

    def get_prompt_content(self, **kwargs) -> str:
        """获取该模块的提示词内容"""
        raise NotImplementedError


# ============================================
# 1. 风险管理模块
# ============================================

class RiskManagementModule(TradingKnowledgeModule):
    """风险管理知识模块"""

    def __init__(self):
        super().__init__(
            name="风险管理",
            description="包含止损、止盈、仓位控制等风险管理原则",
            category="核心"
        )

    def get_prompt_content(self, max_position_size=0.3, stop_loss_pct=0.05, take_profit_pct=0.15, **kwargs) -> str:
        return f"""
## 风险管理原则 (Risk Management)

你必须严格遵守以下风险管理规则：

1. **仓位控制** (Position Sizing)
   - 单笔交易最大仓位：{max_position_size*100:.0f}%
   - 永远不要满仓操作
   - 根据市场波动性调整仓位大小

2. **止损纪律** (Stop Loss)
   - 每笔交易必须设置止损
   - 默认止损：{stop_loss_pct*100:.1f}%
   - 止损触发后立即执行，不要犹豫

3. **止盈策略** (Take Profit)
   - 目标盈利：{take_profit_pct*100:.1f}%
   - 可以分批止盈（50%仓位在{take_profit_pct*50}%，剩余在{take_profit_pct*100}%）
   - 不要贪婪，达到目标即止盈

4. **风险收益比** (Risk-Reward Ratio)
   - 最小风险收益比：1:2
   - 只在风险收益比有利时开仓

5. **最大回撤控制**
   - 单日最大亏损：5%
   - 连续亏损3次后，降低仓位50%
   - 总回撤超过20%时，暂停交易

**记住：保护本金永远是第一位的！**
"""


class PositionSizingModule(TradingKnowledgeModule):
    """仓位管理模块"""

    def __init__(self):
        super().__init__(
            name="仓位管理",
            description="动态仓位管理和资金分配策略",
            category="风控"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 仓位管理策略 (Position Sizing Strategies)

根据不同市场情况调整仓位：

1. **固定比例法**
   - 趋势明确时：30%仓位
   - 震荡市场时：10-20%仓位
   - 不确定时：观望（0%）

2. **凯利公式法** (Kelly Criterion)
   - 仓位 = (胜率 × 盈亏比 - (1 - 胜率)) / 盈亏比
   - 实际使用时建议减半（Half Kelly）

3. **金字塔加仓**
   - 首次建仓：30%
   - 盈利5%后加仓：20%
   - 盈利10%后加仓：10%
   - 永远不要在亏损时加仓

4. **分批建仓**
   - 将计划仓位分3次建立
   - 避免一次性重仓

5. **波动率调整**
   - 高波动品种：减少仓位
   - 低波动品种：可适当增加
   - 公式：基础仓位 × (平均波动率 / 当前波动率)
"""


# ============================================
# 2. 技术分析理论模块
# ============================================

class TechnicalAnalysisTheoryModule(TradingKnowledgeModule):
    """技术分析理论模块"""

    def __init__(self):
        super().__init__(
            name="技术分析理论",
            description="道氏理论、趋势分析、支撑阻力等核心概念",
            category="技术分析"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 技术分析核心理论

1. **道氏理论 (Dow Theory)**
   - 趋势有三种：主要趋势（1年+）、次要趋势（3周-3月）、短期波动
   - 趋势的三个阶段：累积期、公众参与期、派发期
   - 成交量必须验证趋势
   - 趋势持续直到明确的反转信号出现

2. **趋势判断**
   - **上升趋势**：高点不断抬高，低点不断抬高
   - **下降趋势**：高点不断降低，低点不断降低
   - **震荡趋势**：横向波动，无明确方向

3. **支撑位与阻力位**
   - 前期高点/低点
   - 密集成交区
   - 整数关口（如10000）
   - 均线位置（MA20, MA50, MA200）
   - 突破确认：需要成交量配合 + 收盘价确认

4. **背离 (Divergence)**
   - **顶背离**：价格创新高，指标未创新高 → 看跌信号
   - **底背离**：价格创新低，指标未创新低 → 看涨信号
   - 背离是强烈的反转信号

5. **共振原则**
   - 多个时间周期同时发出信号
   - 多个指标同时确认
   - 共振信号可靠性更高
"""


class CandlestickPatternModule(TradingKnowledgeModule):
    """K线形态模块"""

    def __init__(self):
        super().__init__(
            name="K线形态分析",
            description="经典K线形态识别和应用",
            category="技术分析"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## K线形态分析 (Candlestick Patterns)

**反转形态 (Reversal Patterns)**

1. **看涨反转**
   - 锤子线 (Hammer)：下影线很长，实体小
   - 早晨之星 (Morning Star)：三根K线组合
   - 多头吞没 (Bullish Engulfing)：阳线吞没前一阴线
   - 刺透形态 (Piercing Pattern)：阳线深入前阴线

2. **看跌反转**
   - 流星 (Shooting Star)：上影线很长，实体小
   - 黄昏之星 (Evening Star)：三根K线组合
   - 空头吞没 (Bearish Engulfing)：阴线吞没前一阳线
   - 乌云盖顶 (Dark Cloud Cover)：阴线深入前阳线

**持续形态 (Continuation Patterns)**

1. **上升三法**：上涨趋势中的短暂整理
2. **下降三法**：下跌趋势中的短暂整理
3. **旗形整理**：强势趋势中的窄幅震荡

**注意事项**
- K线形态需要结合成交量
- 在关键支撑/阻力位出现更可靠
- 等待形态完成后的确认信号
"""


# ============================================
# 3. 市场周期与趋势模块
# ============================================

class MarketCycleModule(TradingKnowledgeModule):
    """市场周期模块"""

    def __init__(self):
        super().__init__(
            name="市场周期认知",
            description="牛市、熊市、震荡市的特征和应对策略",
            category="市场分析"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 市场周期认知 (Market Cycles)

1. **牛市特征** (Bull Market)
   - 价格持续上涨，回调浅且短
   - 成交量放大
   - 利好消息被放大，利空被忽视
   - **策略**：趋势跟随，回调买入，持股为主

2. **熊市特征** (Bear Market)
   - 价格持续下跌，反弹弱且短
   - 成交量萎缩
   - 利空消息被放大，利好被忽视
   - **策略**：空仓为主，严格止损，不抄底

3. **震荡市特征** (Sideways Market)
   - 价格在区间内波动
   - 无明确趋势
   - **策略**：高抛低吸，区间交易，减少仓位

4. **市场阶段判断**
   - **底部累积期**：成交量低，价格横盘，散户悲观
   - **上升期**：成交量放大，价格突破，趋势明朗
   - **顶部派发期**：成交量巨大，价格滞涨，散户狂热
   - **下跌期**：成交量萎缩，价格破位，恐慌蔓延

5. **周期轮动**
   - 加密货币有明显的4年周期（比特币减半周期）
   - 山寨币通常滞后比特币2-4周
   - 注意板块轮动：BTC → ETH → 主流币 → 山寨币
"""


class TrendStrengthModule(TradingKnowledgeModule):
    """趋势强度评估模块"""

    def __init__(self):
        super().__init__(
            name="趋势强度评估",
            description="评估当前趋势的强度和持续性",
            category="市场分析"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 趋势强度评估 (Trend Strength Assessment)

1. **ADX指标应用**
   - ADX > 25：趋势明显
   - ADX > 40：强趋势
   - ADX < 20：无趋势（震荡）

2. **斜率分析**
   - 陡峭上升：强势，但警惕过热
   - 缓慢上升：健康，可持续性强
   - 横盘：趋势减弱

3. **成交量确认**
   - 上涨伴随放量：健康
   - 上涨但缩量：警惕，可能反转
   - 下跌放量：恐慌，可能见底
   - 下跌缩量：继续看跌

4. **波动率分析**
   - 波动率扩大：趋势可能加速
   - 波动率收缩：可能即将突破
   - 极端波动：警惕反转

5. **趋势线测试**
   - 多次触碰未破：趋势强
   - 频繁假突破：趋势弱
   - 成交量减少的触碰：趋势可能改变
"""


# ============================================
# 4. 交易心理学模块
# ============================================

class TradingPsychologyModule(TradingKnowledgeModule):
    """交易心理学模块"""

    def __init__(self):
        super().__init__(
            name="交易心理学",
            description="控制情绪，避免常见心理陷阱",
            category="心理"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 交易心理学 (Trading Psychology)

**必须避免的心理陷阱：**

1. **贪婪 (Greed)**
   - 症状：看到盈利不想止盈，总想赚更多
   - 对策：严格执行止盈计划，落袋为安

2. **恐惧 (Fear)**
   - 症状：亏损时不敢止损，幻想回本
   - 对策：承认错误，果断止损

3. **报复性交易 (Revenge Trading)**
   - 症状：亏损后急于翻本，加大仓位
   - 对策：亏损后休息，冷静分析

4. **过度自信 (Overconfidence)**
   - 症状：连续盈利后认为自己无所不能
   - 对策：保持谦卑，市场永远是对的

5. **锚定效应 (Anchoring)**
   - 症状：盯着买入价格，不看当前市场
   - 对策：只关注当前走势，过去的价格不重要

6. **确认偏误 (Confirmation Bias)**
   - 症状：只看支持自己观点的信息
   - 对策：主动寻找反对意见

**正确的交易心态：**

- 接受不确定性，没有100%的交易
- 关注过程，而非单次盈亏
- 资金管理比预测方向更重要
- 耐心等待高质量机会
- 保持情绪稳定，机械化执行
"""


# ============================================
# 5. 多时间框架分析模块
# ============================================

class MultiTimeframeModule(TradingKnowledgeModule):
    """多时间框架分析模块"""

    def __init__(self):
        super().__init__(
            name="多时间框架分析",
            description="从不同时间周期分析市场，提高胜率",
            category="技术分析"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 多时间框架分析 (Multi-Timeframe Analysis)

**分析框架：**

1. **大周期看方向** (Daily/Weekly)
   - 判断主要趋势
   - 找出关键支撑阻力
   - 确定大方向后，只做顺势交易

2. **中周期找位置** (4H/1H)
   - 寻找入场时机
   - 确认趋势延续或反转信号
   - 识别关键形态

3. **小周期定入场** (15min/5min)
   - 精确入场点
   - 减少回撤
   - 快速止损

**三重确认原则：**
- 大周期趋势向上 + 中周期回调结束 + 小周期突破 = 买入
- 大周期趋势向下 + 中周期反弹结束 + 小周期破位 = 卖出

**时间周期选择：**
- 长线：周线 + 日线 + 4小时
- 中线：日线 + 4小时 + 1小时
- 短线：4小时 + 1小时 + 15分钟
- 超短线：1小时 + 15分钟 + 5分钟

**注意事项：**
- 大周期优先级高于小周期
- 不要逆大周期趋势交易
- 各周期指标共振时可靠性最高
"""


# ============================================
# 6. 指标组合与共振模块
# ============================================

class IndicatorCombinationModule(TradingKnowledgeModule):
    """指标组合与共振模块"""

    def __init__(self):
        super().__init__(
            name="指标组合与共振",
            description="多个指标相互验证，提高信号可靠性",
            category="技术分析"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 指标组合与共振 (Indicator Combination & Confluence)

**经典组合策略：**

1. **趋势 + 动量 组合**
   - 均线(MA) + MACD
   - 均线金叉 + MACD金叉 = 强买入信号
   - 均线死叉 + MACD死叉 = 强卖出信号

2. **趋势 + 超买超卖 组合**
   - 均线(MA) + RSI
   - 上升趋势 + RSI从超卖区回升 = 买入
   - 下降趋势 + RSI从超买区回落 = 卖出

3. **动量 + 波动率 组合**
   - MACD + 布林带(BOLL)
   - 价格突破布林上轨 + MACD金叉 = 强势突破
   - 价格跌破布林下轨 + MACD死叉 = 弱势破位

4. **三重确认**
   - MA + MACD + RSI
   - 三个指标同时看涨 = 高确定性做多
   - 三个指标同时看跌 = 高确定性做空

**共振信号识别：**

✅ **看涨共振**
- 均线多头排列
- MACD金叉且柱状图放大
- RSI在50上方上行
- 成交量放大
- K线收阳线

✅ **看跌共振**
- 均线空头排列
- MACD死叉且柱状图放大
- RSI在50下方下行
- 成交量放大
- K线收阴线

**背离共振（反转信号）：**
- 价格创新高/低
- MACD和RSI同时背离
- 成交量萎缩
- = 强烈反转信号

**注意事项：**
- 指标越多不代表越好（3-4个足够）
- 避免使用相似类型指标（如多个动量指标）
- 等待多个指标共振后再行动
- 单一指标信号可靠性低，需要确认
"""


# ============================================
# 7. 资金管理模块
# ============================================

class MoneyManagementModule(TradingKnowledgeModule):
    """资金管理模块"""

    def __init__(self):
        super().__init__(
            name="资金管理",
            description="专业的资金分配和管理策略",
            category="风控"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 资金管理策略 (Money Management)

1. **账户分配**
   - 交易资金：70%
   - 备用资金：20%
   - 应急资金：10%

2. **品种分散**
   - 不要把所有资金投入单一品种
   - 建议：3-5个品种分散
   - 相关性低的品种搭配

3. **仓位梯度**
   - 高确定性机会：20-30%
   - 中等确定性：10-15%
   - 低确定性：5-10%
   - 不确定：0%（观望）

4. **加仓规则**
   - 只在盈利时加仓
   - 加仓递减（例如：30% → 20% → 10%）
   - 总仓位不超过60%

5. **减仓规则**
   - 触及止损：立即平仓
   - 目标位：分批减仓
   - 趋势减弱：减少50%仓位
   - 反向信号：全部平仓

6. **盈亏比计算**
   - 每笔交易前计算盈亏比
   - 最小盈亏比：1:2
   - 理想盈亏比：1:3或更高
   - 盈亏比不佳：放弃交易

7. **日内交易限制**
   - 单日最大亏损：总资金的3-5%
   - 连续亏损3次：停止交易
   - 连续盈利5次：谨防过度自信
"""


# ============================================
# 8. 量化指标模块
# ============================================

class QuantitativeMetricsModule(TradingKnowledgeModule):
    """量化指标模块"""

    def __init__(self):
        super().__init__(
            name="量化指标分析",
            description="夏普比率、最大回撤等量化指标",
            category="量化"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## 量化指标分析 (Quantitative Metrics)

**绩效评估指标：**

1. **夏普比率 (Sharpe Ratio)**
   - 公式：(收益率 - 无风险利率) / 收益波动率
   - > 1：良好
   - > 2：优秀
   - > 3：卓越

2. **最大回撤 (Maximum Drawdown)**
   - 从高点到低点的最大跌幅
   - 评估：< 10%优秀，< 20%良好，> 30%需要改进

3. **胜率 (Win Rate)**
   - 盈利交易次数 / 总交易次数
   - 结合盈亏比看：高胜率未必好

4. **盈亏比 (Profit/Loss Ratio)**
   - 平均盈利 / 平均亏损
   - > 2：优秀
   - > 3：卓越

5. **收益回撤比 (Return/Drawdown Ratio)**
   - 总收益 / 最大回撤
   - > 2：良好
   - > 5：优秀

**决策应用：**
- 定期评估策略表现
- 夏普比率下降 → 检查策略
- 回撤超过阈值 → 减少仓位
- 胜率突然变化 → 市场环境改变
"""


# ============================================
# 12. 趋势方向识别与顺势交易模块（重要！）
# ============================================

class TrendDirectionModule(TradingKnowledgeModule):
    """趋势方向识别与顺势交易模块"""

    def __init__(self):
        super().__init__(
            name="趋势方向识别与顺势交易",
            description="多时间框架趋势判断，顺大逆小交易原则",
            category="核心"
        )

    def get_prompt_content(self, **kwargs) -> str:
        return """
## ⚠️ 趋势方向识别与顺势交易（CRITICAL！）

**这是最重要的交易原则！必须严格遵守！**

---

### 第一步：多时间框架趋势分析（必做！）

在做出任何交易决策之前，你必须先分析以下时间框架的趋势：

**1. 大周期（主趋势）- 日线/4小时**
   - 判断标准：
     * 上升趋势：高点不断抬高 + 低点不断抬高
     * 下降趋势：高点不断降低 + 低点不断降低
     * 横盘震荡：在区间内反复波动

   - 观察指标：
     * MA20、MA50、MA200均线排列
     * MACD柱状图方向
     * 价格相对均线的位置

**2. 中周期（次级趋势）- 1小时/15分钟**
   - 用于确认大周期趋势
   - 寻找回调/反弹的结束点
   - 观察短期支撑阻力位

**3. 小周期（入场点）- 5分钟/1分钟**
   - 仅用于寻找精确的入场时机
   - 不用于判断主趋势方向

---

### 第二步：综合判断主趋势方向

根据多时间框架分析，得出结论：

**多头趋势（Bullish Trend）**
- 日线：上升
- 4小时：上升或横盘（不是明确下降）
- 均线：多头排列（短期 > 中期 > 长期）
- 结论：**只能做多（buy_to_enter），禁止做空！**

**空头趋势（Bearish Trend）**
- 日线：下降
- 4小时：下降或横盘（不是明确上升）
- 均线：空头排列（短期 < 中期 < 长期）
- 结论：**只能做空（sell_to_enter），禁止做多！**

**震荡趋势（Sideways）**
- 日线：横盘
- 4小时：横盘
- 结论：**减少交易，等待趋势明朗，或做区间高抛低吸**

---

### 第三步：顺大逆小 - 入场时机选择

**核心原则：顺应大周期趋势，在小周期回调时入场**

**多头趋势中（只做多）：**

1. **等待回调**
   - 价格回调到支撑位（MA20、MA50、前低点）
   - 不要追涨，等待价格回到合理位置

2. **确认反弹信号**
   - 小周期（1小时/15分钟）出现看涨K线形态
   - RSI从超卖区反弹
   - MACD底背离或金叉

3. **开多单（buy_to_enter）**
   - 止损设在支撑位下方
   - 止盈设在前高或阻力位

**空头趋势中（只做空）：**

1. **等待反弹**
   - 价格反弹到阻力位（MA20、MA50、前高点）
   - 不要追空，等待价格反弹到合理位置

2. **确认下跌信号**
   - 小周期出现看跌K线形态
   - RSI从超买区回落
   - MACD顶背离或死叉

3. **开空单（sell_to_enter）**
   - 止损设在阻力位上方
   - 止盈设在前低或支撑位

---

### 第四步：严格的交易纪律

**禁止的操作：**

❌ **绝对禁止逆势交易！**
   - 多头趋势中做空 → 100%失败
   - 空头趋势中做多 → 100%失败

❌ **不要试图抄底摸顶！**
   - 下跌途中不抄底
   - 上涨途中不摸顶
   - "顶和底"是走出来的，不是猜出来的

❌ **震荡市不要频繁交易！**
   - 无明确趋势时，持币观望
   - 等待趋势明朗再入场

**必须的操作：**

✓ **趋势不明时，选择 hold（观望）**

✓ **每次交易前，先在心里问自己：**
   1. 大周期是什么趋势？
   2. 我的方向是否顺应大周期？
   3. 当前是否是合适的入场点？

✓ **记录你的分析过程：**
   - 在justification中必须说明：
     * "日线趋势：XXX"
     * "4小时趋势：XXX"
     * "综合判断：XXX趋势"
     * "当前操作：顺势XXX"

---

### 示例：正确的思考流程

**示例1：多头趋势做多**
```
分析过程：
- 日线：价格在MA50上方，高点不断抬高 → 上升趋势
- 4小时：价格在MA20上方，均线多头排列 → 上升趋势
- 1小时：刚刚回调到MA50支撑，出现锤子线 → 回调结束信号

综合判断：明确的多头趋势
当前操作：等待回调结束后做多（buy_to_enter）
理由：顺大周期多头趋势，小周期回调到支撑位，符合"顺大逆小"

止损：MA50下方
止盈：前高
```

**示例2：空头趋势做空**
```
分析过程：
- 日线：价格跌破MA200，均线空头排列 → 下降趋势
- 4小时：价格在MA20下方，持续新低 → 下降趋势
- 1小时：反弹到MA20阻力，出现黄昏之星 → 反弹结束信号

综合判断：明确的空头趋势
当前操作：反弹到阻力位后做空（sell_to_enter）
理由：顺大周期空头趋势，小周期反弹到阻力位，符合"顺大逆小"

止损：MA20上方
止盈：前低
```

**示例3：震荡市观望**
```
分析过程：
- 日线：在区间内反复横盘 → 震荡
- 4小时：无明确方向 → 震荡
- 1小时：来回波动

综合判断：震荡市，趋势不明
当前操作：观望（hold）
理由：无明确趋势，等待突破方向明确后再入场
```

---

### 重要提醒

**永远记住：**
1. 趋势是你的朋友，顺势者昌，逆势者亡
2. 不要试图战胜市场，要追随市场
3. 大周期决定方向，小周期寻找时机
4. 没有把握时，选择观望永远是最明智的

**一句话总结：看清大势，顺势而为，逆小入场，严守纪律！**
"""


# ============================================
# 模块管理器
# ============================================

class TradingKnowledgeManager:
    """交易知识模块管理器"""

    def __init__(self):
        self.modules = {
            'risk_management': RiskManagementModule(),
            'position_sizing': PositionSizingModule(),
            'technical_theory': TechnicalAnalysisTheoryModule(),
            'candlestick': CandlestickPatternModule(),
            'market_cycle': MarketCycleModule(),
            'trend_strength': TrendStrengthModule(),
            'psychology': TradingPsychologyModule(),
            'multi_timeframe': MultiTimeframeModule(),
            'indicator_combination': IndicatorCombinationModule(),
            'money_management': MoneyManagementModule(),
            'quantitative': QuantitativeMetricsModule(),
            'trend_direction': TrendDirectionModule(),  # 新增：趋势方向识别
        }

    def get_module(self, module_id: str):
        """获取指定模块"""
        return self.modules.get(module_id)

    def get_all_modules(self):
        """获取所有模块"""
        return self.modules

    def get_modules_by_category(self, category: str):
        """按类别获取模块"""
        return {k: v for k, v in self.modules.items() if v.category == category}

    def build_enhanced_prompt(self, enabled_modules: list, base_prompt: str = "", **kwargs) -> str:
        """
        构建增强的提示词

        Args:
            enabled_modules: 启用的模块ID列表
            base_prompt: 基础提示词
            **kwargs: 模块参数

        Returns:
            完整的增强提示词
        """
        prompt_parts = []

        # 添加基础提示词
        if base_prompt:
            prompt_parts.append(base_prompt)
        else:
            prompt_parts.append(
                "You are a professional cryptocurrency trader with deep knowledge of "
                "technical analysis, risk management, and market psychology."
            )

        # 添加启用的知识模块
        if enabled_modules:
            prompt_parts.append("\n# TRADING KNOWLEDGE BASE\n")
            prompt_parts.append("Apply the following trading knowledge in your decision-making:\n")

            for module_id in enabled_modules:
                module = self.modules.get(module_id)
                if module:
                    prompt_parts.append(module.get_prompt_content(**kwargs))
                    prompt_parts.append("\n" + "="*60 + "\n")

        return "\n".join(prompt_parts)

    def get_module_list_for_ui(self):
        """
        获取用于UI显示的模块列表

        Returns:
            list: [{id, name, description, category}, ...]
        """
        return [
            {
                'id': module_id,
                'name': module.name,
                'description': module.description,
                'category': module.category
            }
            for module_id, module in self.modules.items()
        ]


# ============================================
# 预设模板
# ============================================

PRESET_TEMPLATES = {
    'conservative': {
        'name': '保守型（重风控）',
        'description': '适合稳健投资者，重视风险控制',
        'modules': ['risk_management', 'position_sizing', 'money_management', 'psychology'],
        'params': {
            'max_position_size': 0.2,
            'stop_loss_pct': 0.03,
            'take_profit_pct': 0.10
        }
    },
    'aggressive': {
        'name': '激进型（高收益）',
        'description': '追求高收益，能承受较高风险',
        'modules': ['technical_theory', 'candlestick', 'trend_strength', 'indicator_combination'],
        'params': {
            'max_position_size': 0.5,
            'stop_loss_pct': 0.08,
            'take_profit_pct': 0.25
        }
    },
    'balanced': {
        'name': '平衡型',
        'description': '风险收益平衡，适合大多数交易者',
        'modules': [
            'risk_management', 'technical_theory', 'market_cycle',
            'psychology', 'indicator_combination'
        ],
        'params': {
            'max_position_size': 0.3,
            'stop_loss_pct': 0.05,
            'take_profit_pct': 0.15
        }
    },
    'quantitative': {
        'name': '量化型',
        'description': '基于数据和指标的系统化交易',
        'modules': [
            'risk_management', 'indicator_combination', 'quantitative',
            'multi_timeframe', 'trend_strength'
        ],
        'params': {
            'max_position_size': 0.3,
            'stop_loss_pct': 0.05,
            'take_profit_pct': 0.15
        }
    },
    'trend_following': {
        'name': '趋势跟随型（顺大逆小）',
        'description': '先判断趋势方向，只做趋势，顺大逆小入场',
        'modules': [
            'trend_direction',  # 第一模块：趋势方向识别（最重要！）
            'multi_timeframe',  # 多时间框架分析
            'technical_theory', # 技术分析理论
            'trend_strength',   # 趋势强度评估
            'risk_management'   # 风险管理
        ],
        'params': {
            'max_position_size': 0.4,
            'stop_loss_pct': 0.06,
            'take_profit_pct': 0.20
        }
    }
}


def get_preset_template(template_id: str):
    """获取预设模板"""
    return PRESET_TEMPLATES.get(template_id)


def get_all_templates():
    """获取所有预设模板"""
    return PRESET_TEMPLATES


# ============================================
# 使用示例
# ============================================

if __name__ == '__main__':
    # 创建管理器
    manager = TradingKnowledgeManager()

    # 示例1：使用预设模板
    template = get_preset_template('balanced')
    prompt = manager.build_enhanced_prompt(
        enabled_modules=template['modules'],
        **template['params']
    )
    print("=== 平衡型模板提示词 ===")
    print(prompt[:500])
    print("\n...")

    # 示例2：自定义选择模块
    custom_modules = ['risk_management', 'psychology', 'candlestick']
    custom_prompt = manager.build_enhanced_prompt(
        enabled_modules=custom_modules,
        base_prompt="You are an expert crypto trader.",
        max_position_size=0.25,
        stop_loss_pct=0.04
    )
    print("\n\n=== 自定义模块提示词 ===")
    print(custom_prompt[:500])

    # 示例3：获取UI模块列表
    print("\n\n=== 可用模块列表 ===")
    for module in manager.get_module_list_for_ui():
        print(f"{module['id']}: {module['name']} ({module['category']})")
        print(f"  {module['description']}\n")
