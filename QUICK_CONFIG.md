# 🚀 AI模型快速配置卡片

直接复制下面的配置信息到系统中！

---

## 📋 推荐配置 (复制即用)

### 1. OpenAI GPT-5 (2025最新最强)

```
【添加API提供方】
名称: OpenAI
API URL: https://api.openai.com/v1
API Key: sk-[你的密钥]
模型: gpt-5, gpt-5-mini, gpt-5-nano, gpt-4o-mini

【创建交易模型】
模型显示名称: GPT-5交易员
选择模型: gpt-5
技术指标策略: Combined
初始资金: 10000
```

---

### 2. Claude Sonnet 4.5 (2025最新版)

```
【添加API提供方】
名称: Claude
API URL: https://api.anthropic.com/v1
API Key: sk-ant-[你的密钥]
模型: claude-sonnet-4-5, claude-opus-4-1, claude-haiku-4-5

【创建交易模型】
模型显示名称: Claude交易员
选择模型: claude-sonnet-4-5
技术指标策略: MovingAverage
初始资金: 10000
```

---

### 3. DeepSeek V3.1 (国内推荐 - 性价比之王)

```
【添加API提供方】
名称: DeepSeek
API URL: https://api.deepseek.com/v1
API Key: [你的密钥]
模型: deepseek-chat, deepseek-reasoner

【创建交易模型】
模型显示名称: DeepSeek V3.1交易员
选择模型: deepseek-chat
技术指标策略: Combined
初始资金: 10000

【V3.1特点】
- 性能超越GPT-4o和Claude 3.5
- 仅0.14元/百万tokens (极低成本)
- 671B参数，37B激活
- 128K上下文长度
- 支持推理模式 (deepseek-reasoner)
```

**获取密钥**: https://platform.deepseek.com

---

### 4. 本地Ollama (完全免费)

**第一步 - 安装Ollama**:
```bash
# 访问 https://ollama.ai 下载安装

# 安装后运行模型
ollama run qwen2.5
```

**第二步 - 配置系统**:
```
【添加API提供方】
名称: Ollama
API URL: http://localhost:11434/v1
API Key: ollama
模型: qwen2.5, llama3.1, mistral

【创建交易模型】
模型显示名称: 本地AI交易员
选择模型: qwen2.5
技术指标策略: RSI
初始资金: 10000
```

---

## 🎯 模型选择速查表

### 按需求选择

| 需求 | 推荐模型 | 配置 |
|------|---------|------|
| **最强性能** | gpt-5 或 claude-opus-4-1 | OpenAI/Claude |
| **最强编码** | claude-sonnet-4-5 | Claude最新版 |
| **性价比** | gpt-5-mini 或 deepseek-chat | OpenAI/DeepSeek |
| **国内访问** | deepseek-chat | DeepSeek + Combined策略 |
| **完全免费** | qwen2.5 | Ollama本地运行 |

---

## 💡 完整配置示例

### 示例1: 专业交易员配置

```
提供商: OpenAI
模型: gpt-5
策略: Combined
提示词:
你是专业的量化交易员，结合技术分析和基本面。

策略要点:
1. 仔细分析技术指标策略的信号
2. 考虑市场整体趋势和情绪
3. 单次交易风险控制在10-15%
4. 使用5-8倍杠杆
5. 严格止损3%，止盈8%

如果多个技术指标一致看涨/看跌，应重视信号。
如果技术指标矛盾，优先观望(hold)。
详细说明每次决策的理由。
```

---

### 示例2: 保守型配置

```
提供商: DeepSeek
模型: deepseek-chat
策略: MovingAverage
提示词:
你是非常保守的交易员，资金安全第一。

交易原则:
1. 只在技术指标非常明确时交易
2. 必须MA金叉才考虑买入
3. 单次风险<5%
4. 杠杆不超过3倍
5. 止损2%，止盈5%

有任何不确定都选择观望。
宁可错过机会，不做错误交易。
```

---

### 示例3: 激进型配置

```
提供商: OpenAI
模型: gpt-5-mini
策略: None
提示词:
你是激进的短线交易员，追求高收益。

交易风格:
1. 不依赖技术指标，相信市场直觉
2. 捕捉短期波动机会
3. 可以使用10-15倍杠杆
4. 单次交易可承担20-30%风险
5. 快速止损5%，让利润奔跑(止盈15%+)

大胆交易，但要有充分理由。
```

---

## 🔑 API密钥快速获取

### OpenAI
1. 访问: https://platform.openai.com/api-keys
2. 注册并绑定支付方式
3. 创建密钥 → 复制到系统

### Claude
1. 访问: https://console.anthropic.com
2. 注册账号
3. 获取API密钥 → 复制到系统

### DeepSeek (支持国内支付)
1. 访问: https://platform.deepseek.com
2. 注册（手机号验证）
3. 充值（支付宝/微信）
4. 获取密钥 → 复制到系统

---

## ⚡ 快速测试步骤

### 1分钟快速测试

1. **添加DeepSeek提供商** (最快)
```
API URL: https://api.deepseek.com/v1
API Key: [你的密钥]
```

2. **创建测试模型**
```
名称: 测试交易员
模型: deepseek-chat
策略: MovingAverage
资金: 10000
```

3. **观察运行**
- 等待1-2分钟
- 查看AI对话标签
- 看到AI分析和决策

---

## 📊 多模型对比测试

创建3个模型同时运行，对比效果：

**模型A - 高性能**:
```
提供商: OpenAI
模型: gpt-5-mini
策略: Combined
风格: 平衡型
```

**模型B - 性价比**:
```
提供商: DeepSeek
模型: deepseek-chat
策略: RSI
风格: 保守型
```

**模型C - 免费**:
```
提供商: Ollama
模型: qwen2.5
策略: MACD
风格: 激进型
```

**观察7天，比较**:
- 盈利率
- 交易次数
- 决策质量
- API成本

---

## 🛠️ 常见问题快速解决

### Q: 模型名称怎么填？

**OpenAI系列 (2025)**:
- 最新旗舰: `gpt-5`
- 高性价比: `gpt-5-mini`
- 超快速: `gpt-5-nano`

**Claude系列 (2025)**:
- 最强编码: `claude-sonnet-4-5`
- 最强推理: `claude-opus-4-1`
- 快速经济: `claude-haiku-4-5`

**DeepSeek**:
- 通用: `deepseek-chat`

**Ollama**:
- 中文: `qwen2.5`
- 英文: `llama3.1`

### Q: API密钥从哪里获取？

看上面的"API密钥快速获取"部分 ⬆️

### Q: 哪个模型最好？

- **最强综合**: gpt-5, claude-opus-4-1
- **最强编码**: claude-sonnet-4-5
- **性价比**: gpt-5-mini, deepseek-chat
- **免费**: qwen2.5 (Ollama)

### Q: 支持哪些策略？

- `None` - 纯AI决策
- `MovingAverage` - 移动平均线
- `RSI` - 超买超卖
- `MACD` - 趋势动量
- `Combined` - 组合策略（最稳）

---

## 💾 保存这些配置

把这个文件收藏起来，需要时直接复制粘贴！

**文件位置**: `E:\code\nof1_enhanced\QUICK_CONFIG.md`

---

## 🎉 开始使用

1. 选择一个配置（推荐DeepSeek）
2. 复制配置信息
3. 粘贴到系统 http://localhost:5000
4. 开始交易！

祝好运！🚀
