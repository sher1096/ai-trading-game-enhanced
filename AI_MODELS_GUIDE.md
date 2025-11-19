# AI模型完整配置指南

## 📋 支持的AI模型概览

当前系统使用 **OpenAI兼容API**，支持以下所有AI提供商的最新模型：

---

## 1. OpenAI (GPT系列) - 2025最新

### 配置方式

```
名称: OpenAI
API URL: https://api.openai.com/v1
API Key: sk-...
```

### 支持的模型 (2025)

| 模型名称 | 发布日期 | 性能 | 成本 |
|---------|---------|------|------|
| **gpt-5** ⭐ | 2025-08-07 | ⭐⭐⭐⭐⭐ | $$ |
| **gpt-5-mini** | 2025-08-07 | ⭐⭐⭐⭐⭐ | $ |
| **gpt-5-nano** | 2025-08-07 | ⭐⭐⭐⭐ | $ |
| **gpt-4o-mini** | 2024 | ⭐⭐⭐⭐ | $$ |
| ~~gpt-4o~~ | 2024 (已过时) | ⭐⭐⭐⭐⭐ | $$$ |
| ~~gpt-4-turbo~~ | 2024 (已过时) | ⭐⭐⭐⭐ | $$$ |
| ~~gpt-3.5-turbo~~ | 2023 (已过时) | ⭐⭐⭐ | $ |

### 推荐配置 (2025)

**最佳性能**:
```
模型: gpt-5
说明: 2025年8月发布，OpenAI最新旗舰模型
性能: 数学能力94.6%, 编码能力74.9%
成本: 比gpt-4o便宜50%
```

**性价比之选**:
```
模型: gpt-5-mini
说明: 性能接近GPT-5，成本更低
适合: 日常交易场景
```

**超快速**:
```
模型: gpt-5-nano
说明: 超快响应，成本最低
适合: 高频交易
```

---

## 2. Anthropic Claude (2025最新)

### 配置方式

```
名称: Claude
API URL: https://api.anthropic.com/v1
API Key: sk-ant-...
```

### 支持的模型 (2025)

| 模型名称 | 发布日期 | 定位 | 成本 |
|---------|---------|------|------|
| **claude-sonnet-4-5** ⭐ | 2025-09-29 | 最强编码 | $$$ |
| **claude-opus-4-1** | 2025-08-05 | 最强推理 | $$$$ |
| **claude-haiku-4-5** | 2025-10-15 | 快速低成本 | $ |
| **claude-sonnet-4** | 2025-05-22 | 平衡性能 | $$$ |
| **claude-opus-4** | 2025-05-22 | 强大性能 | $$$$ |
| ~~claude-3-5-sonnet-20241022~~ | 2024 (已过时) | - | - |
| ~~claude-3-opus-20240229~~ | 2024 (已过时) | - | - |

### 推荐配置 (2025)

**最强编码能力**:
```
模型: claude-sonnet-4-5
说明: 2025年9月发布，世界第一编码能力
适合: 复杂交易策略分析
成本: $3/$15 每百万tokens
```

**最强推理能力**:
```
模型: claude-opus-4-1
说明: 2025年8月发布，推理能力极致
适合: 高级交易决策
成本: $15/$75 每百万tokens
```

**快速经济型**:
```
模型: claude-haiku-4-5
说明: 2025年10月发布，快速低成本
适合: 日常交易
成本: $1/$5 每百万tokens
```

---

## 3. DeepSeek V3.1/V3.2 (2025最新 - 国内推荐)

### 配置方式

```
名称: DeepSeek
API URL: https://api.deepseek.com/v1
API Key: [你的密钥]
```

### 支持的模型 (2025)

| 模型名称 | 发布日期 | 性能 | 成本 |
|---------|---------|------|------|
| **deepseek-chat** | 2025-08 (V3.1) | ⭐⭐⭐⭐⭐ | 💰 极低 |
| **deepseek-reasoner** | 2025-08 (V3.1) | ⭐⭐⭐⭐⭐ | 💰 极低 |

### DeepSeek V3.1 重大更新 (2025年8月)

**技术突破**:
- 671B总参数，37B激活参数
- 支持128K超长上下文
- 混合推理模式：thinking + 非thinking
- 一个模型覆盖通用和推理场景

**性能提升**:
- 超越GPT-4o和Claude 3.5
- 推理能力显著增强
- 编码能力世界领先

### V3.2-Exp (2025年9月)

**最新特性**:
- DeepSeek稀疏注意力(DSA)
- 长文本训练和推理效率提升
- API价格降低50%+

### 推荐配置 (2025)

**通用交易 (非思考模式)**:
```
模型: deepseek-chat
说明: V3.1自动升级，性能超GPT-4o
成本: 仅0.14元/百万tokens (极低)
适合: 日常交易，高性价比
```

**深度分析 (思考模式)**:
```
模型: deepseek-reasoner
说明: V3.1推理模式，深度思考
成本: 略高于chat模式但仍极低
适合: 复杂决策，重要交易
```

---

## 4. Qwen3 通义千问 (2025最新 - 阿里巴巴)

### 配置方式

```
名称: Qwen-Alibaba
API URL: https://dashscope.aliyuncs.com/compatible-mode/v1
API Key: [你的DashScope密钥]
```

### 支持的模型 (2025)

| 模型名称 | 发布日期 | 定位 | 成本 |
|---------|---------|------|------|
| **qwen-plus** ⭐ | 2025-09 | Qwen3-Plus最新 | 💰 低 |
| **qwen-plus-latest** | - | 自动最新版本 | 💰 低 |
| **qwen-plus-2025-09-11** | 2025-09-11 | Qwen3固定版本 | 💰 低 |
| **qwen-max-2025-01-25** | 2025-01-25 | Qwen2.5-Max | 💰💰 中 |
| **qwen-turbo** | - | 快速经济型 | 💰 极低 |
| **qwen-coder-plus** | 2025 | Qwen3代码专用 | 💰 低 |

### Qwen3 重大更新 (2025年9月5日)

**性能突破**:
- 超越Claude 4 Opus非思考模式
- 超越DeepSeek V3.1
- 中文能力世界第一
- 支持100+种语言和方言

**混合思考模式**:
- 可通过`enable_thinking`参数切换
- 思考模式：深度推理，适合复杂决策
- 非思考模式：快速响应，适合日常交易
- 一个模型覆盖两种场景

**专用模型**:
- **qwen-coder-plus**: 强大Coding Agent能力
- **qwen-omni**: 多模态（文本+图片+音频+视频）
- **qwen-vl**: 视觉语言模型

### 推荐配置 (2025)

**最强中文 (推荐)**:
```
模型: qwen-plus
说明: Qwen3-Plus，2025年9月最新版本
中文能力: 世界第一
成本: 阿里云价格极具竞争力
适合: 国内用户，中文市场分析
特色: 免费100万tokens试用
```

**极致性能**:
```
模型: qwen-max-2025-01-25
说明: Qwen2.5-Max超大模型
性能: 超越GPT-4o和Claude 3.5
适合: 追求极致性能
```

**高频交易**:
```
模型: qwen-turbo
说明: 快速经济型
响应: 极快
成本: 极低
适合: 高频交易场景
```

**代码分析**:
```
模型: qwen-coder-plus
说明: Qwen3-Coder-Plus
特长: 代码生成，策略编写
适合: 需要AI辅助编程
```

**获取密钥**: https://dashscope.console.aliyun.com

**支付方式**: 支付宝/微信，国内用户友好

---

## 5. Google Gemini

### 配置方式

```
名称: Gemini
API URL: https://generativelanguage.googleapis.com/v1beta
API Key: [你的API密钥]
```

### 支持的模型

| 模型名称 | 用途 | 性能 | 成本 |
|---------|------|------|------|
| **gemini-pro** | Gemini Pro | ⭐⭐⭐⭐ | $$ |
| **gemini-ultra** | Gemini Ultra | ⭐⭐⭐⭐⭐ | $$$ |

---

## 6. 本地模型 (Ollama)

### 配置方式

```
名称: Ollama
API URL: http://localhost:11434/v1
API Key: ollama (任意值)
```

### 支持的模型

| 模型名称 | 说明 | 性能 |
|---------|------|------|
| **qwen2.5** | 通义千问2.5 | ⭐⭐⭐⭐ |
| **llama3.1** | Meta Llama 3.1 | ⭐⭐⭐⭐ |
| **mistral** | Mistral | ⭐⭐⭐ |
| **deepseek-coder** | DeepSeek Coder | ⭐⭐⭐⭐ |
| **qwen** | 通义千问 | ⭐⭐⭐ |
| **phi** | Microsoft Phi | ⭐⭐⭐ |

### 使用步骤

1. 安装Ollama: https://ollama.ai
2. 运行模型:
```bash
ollama run qwen2.5
```
3. 在系统中添加提供商（URL: http://localhost:11434/v1）

---

## 📊 模型选择建议

### 按场景选择

#### 专业交易分析 (最高性能) - 2025推荐
```
推荐: gpt-5, claude-opus-4-1, claude-sonnet-4-5
适合: 需要最准确的市场分析和复杂决策
成本: 较高但性价比更好
```

#### 日常交易 (平衡性能) - 2025推荐
```
推荐: gpt-5-mini, claude-sonnet-4-5, deepseek-chat
适合: 日常交易，性价比高
成本: 中等
```

#### 测试学习 (经济型) - 2025推荐
```
推荐: gpt-5-mini, claude-haiku-4-5, deepseek-chat
适合: 学习测试，降低成本
成本: 低
```

#### 完全免费 (本地运行)
```
推荐: qwen2.5 (Ollama), llama3.1
适合: 不想付费，有本地GPU
成本: 0
```

---

## 🔧 如何在系统中配置

### 方法1: 通过Web界面

1. 打开 http://localhost:5000
2. 点击"API提供方"
3. 填写配置信息
4. 点击保存

### 方法2: 多个提供商并存

你可以同时添加多个提供商：

**示例配置**:
```
提供商1:
  名称: OpenAI-GPT5
  API URL: https://api.openai.com/v1
  API Key: sk-...
  模型: gpt-5

提供商2:
  名称: Claude-Sonnet-4-5
  API URL: https://api.anthropic.com/v1
  API Key: sk-ant-...
  模型: claude-sonnet-4-5

提供商3:
  名称: DeepSeek-V3
  API URL: https://api.deepseek.com/v1
  API Key: [密钥]
  模型: deepseek-chat

提供商4:
  名称: Qwen-Alibaba
  API URL: https://dashscope.aliyuncs.com/compatible-mode/v1
  API Key: [密钥]
  模型: qwen-plus
```

然后创建不同的交易模型使用不同的AI：
- 模型A: 使用 GPT-5 (2025最新)
- 模型B: 使用 Claude Sonnet 4.5 (最强编码)
- 模型C: 使用 DeepSeek V3.1 (极致性价比)
- 模型D: 使用 Qwen3-Plus (中文最强)

---

## 💰 成本对比

### 按1000次API调用估算 (2025更新)

| 提供商 | 模型 | 估算成本 |
|-------|------|---------|
| OpenAI | gpt-5 | $6-15 |
| OpenAI | gpt-5-mini | $0.3-1 |
| OpenAI | gpt-5-nano | $0.1-0.5 |
| Claude | claude-sonnet-4-5 | $10-20 |
| Claude | claude-opus-4-1 | $20-40 |
| Claude | claude-haiku-4-5 | $0.3-1 |
| DeepSeek | deepseek-chat (V3.1) | ¥0.14-0.28 (极低) |
| DeepSeek | deepseek-reasoner (V3.1) | ¥0.55-1.1 (低) |
| Qwen | qwen-plus (Qwen3) | ¥1-2 (低) |
| Qwen | qwen-turbo | ¥0.3-0.6 (极低) |
| Ollama | 本地模型 | $0 |

---

## 🎯 实战配置示例

### 配置1: 高性能组合 (2025推荐)

```
主力模型 (70%交易):
  提供商: OpenAI
  模型: gpt-5-mini
  策略: Combined
  提示词: 保守稳健型

辅助模型 (30%交易):
  提供商: Claude
  模型: claude-sonnet-4-5
  策略: MovingAverage
  提示词: 激进型
```

### 配置2: 性价比组合 (2025推荐)

```
主力模型:
  提供商: DeepSeek
  模型: deepseek-chat (V3.1)
  策略: Combined
  提示词: 平衡型
  成本: 极低 (0.14元/百万tokens)

辅助模型:
  提供商: Qwen-Alibaba
  模型: qwen-plus (Qwen3)
  策略: MovingAverage
  提示词: 中文市场分析
  成本: 低

备用模型:
  提供商: Ollama
  模型: qwen2.5
  策略: RSI
  提示词: 本地备用
  成本: 免费
```

### 配置3: 免费测试

```
模型1:
  提供商: Ollama
  模型: qwen2.5
  策略: MovingAverage

模型2:
  提供商: Ollama
  模型: llama3.1
  策略: MACD
```

---

## 🔑 获取API密钥

### OpenAI
1. 访问: https://platform.openai.com/api-keys
2. 注册登录
3. 创建API密钥
4. 充值使用

### Claude (Anthropic)
1. 访问: https://console.anthropic.com
2. 注册账号
3. 获取API密钥
4. 充值使用

### DeepSeek
1. 访问: https://platform.deepseek.com
2. 注册账号
3. 获取API密钥
4. 充值（支持支付宝/微信）

### Ollama (免费)
1. 下载: https://ollama.ai
2. 安装运行
3. 拉取模型: `ollama run qwen2.5`
4. 无需API密钥

---

## ⚙️ 高级配置

### 使用OpenAI兼容的第三方服务

很多服务提供OpenAI兼容的API，都可以使用：

**示例 - 使用Azure OpenAI**:
```
名称: Azure-OpenAI
API URL: https://YOUR-RESOURCE.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT
API Key: [Azure密钥]
模型: gpt-4
```

**示例 - 使用国内镜像服务** (如果有):
```
名称: OpenAI-Mirror
API URL: https://api.example-mirror.com/v1
API Key: [密钥]
模型: gpt-4
```

---

## 📈 性能测试建议

建议创建多个模型进行对比测试：

1. **创建测试组 (2025推荐)**:
   - GPT-5-mini + MA策略
   - Claude-Sonnet-4-5 + MACD策略
   - DeepSeek + Combined策略

2. **观察指标**:
   - 决策质量
   - 响应速度
   - 成本效益
   - 盈利率

3. **优化选择**:
   - 保留表现最好的模型
   - 调整策略和提示词
   - 平衡性能和成本

---

## 🛡️ 注意事项

1. **API密钥安全**
   - 不要泄露给他人
   - 定期更换密钥
   - 设置使用限额

2. **成本控制**
   - 先用便宜模型测试
   - 监控API调用次数
   - 设置预算警报

3. **模型选择**
   - 不同场景用不同模型
   - 定期评估性能
   - 根据市场调整

---

## 📞 技术支持

如有问题：
1. 查看应用日志: `trading.log`
2. 检查API密钥是否正确
3. 确认网络连接正常
4. 尝试不同的模型

---

**更新日期**: 2025-11-17
**支持的模型数**: 30+
**最新模型**: GPT-5, Claude Sonnet 4.5, Claude Opus 4.1
**推荐更新频率**: 每月检查新模型

**⚠️ 重要**: 2025年已发布多个新模型，建议使用：
- OpenAI: gpt-5, gpt-5-mini (而非 gpt-4o)
- Claude: claude-sonnet-4-5, claude-opus-4-1 (而非 claude-3-5-sonnet)
- 详见 AI_MODELS_2025_LATEST.md 获取完整2025模型信息
