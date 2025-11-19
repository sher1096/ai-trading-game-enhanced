# 🚀 快速启动指南

## 第一次使用 (5分钟)

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果 `talib` 安装失败，暂时注释掉 requirements.txt 中的这一行，系统会降级为纯AI模式。

### 2. 启动应用

```bash
python app.py
```

看到这个输出表示成功：
```
* Running on http://127.0.0.1:5000
```

### 3. 打开浏览器

访问: `http://localhost:5000`

### 4. 添加AI提供商

点击右上角"API提供方"按钮

**推荐配置 (DeepSeek)**:
```
名称: DeepSeek
API URL: https://api.deepseek.com/v1
API Key: [你的密钥]
模型: deepseek-chat
```

点击"保存"

### 5. 创建交易模型

点击"添加模型"按钮

```
选择API提供方: DeepSeek
模型: deepseek-chat
模型显示名称: 我的第一个AI交易员
初始资金: 10000
技术指标策略: MovingAverage
自定义提示词: (使用默认或输入自己的)
```

点击"确认添加"

### 6. 开始交易！

- 系统会自动获取市场数据
- 根据设定的交易频率，AI会自动分析并交易
- 在首页可以看到实时账户价值和持仓情况

## 💡 示例配置

### 配置1: 保守型交易员

```
策略: MovingAverage
初始资金: 10000
提示词:
你是非常保守的交易员。
只在技术指标非常明确时交易。
单次交易风险<5%。
杠杆不超过2倍。
```

### 配置2: 激进型交易员

```
策略: None
初始资金: 10000
提示词:
你是激进的短线交易员。
捕捉市场短期波动机会。
可以使用高杠杆（最高15倍）。
单次交易可承担20-30%风险。
```

### 配置3: 平衡型交易员

```
策略: Combined
初始资金: 10000
提示词:
你是理性的交易员，技术分析和市场直觉并重。
参考技术指标策略的综合信号。
如果技术指标明确，应给予重视。
但如果市场有异常情况，可以不遵循。
单次风险10-15%，杠杆5-8倍。
```

## 🔧 常见问题

### Q: talib安装失败怎么办？

A:
1. Windows: 从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 下载whl文件安装
2. 或者暂时注释掉requirements.txt中的talib，只用纯AI模式

### Q: 如何获取DeepSeek API密钥？

A: 访问 https://platform.deepseek.com 注册并创建API密钥

### Q: 技术指标策略选哪个好？

A:
- **None**: 完全信任AI判断
- **MovingAverage**: 简单有效，适合趋势市场
- **RSI**: 适合震荡市场
- **MACD**: 适合中长期趋势
- **Combined**: 最稳健，但可能错过机会

### Q: AI总是选择hold怎么办？

A:
1. 优化自定义提示词，给出更明确的交易策略
2. 尝试更激进的策略描述
3. 降低风险控制要求
4. 检查市场数据是否正常

### Q: 如何查看AI的决策理由？

A: 在"AI对话"标签页可以看到AI每次决策的详细分析过程

## 📁 项目文件说明

```
nof1_enhanced/
├── app.py                    # 主应用 - 运行这个
├── ai_trader_enhanced.py     # AI引擎（已集成策略）
├── strategy.py               # 技术指标策略
├── database.py               # 数据库
├── market_data.py            # 市场数据
├── trading_engine.py         # 交易引擎
├── templates/                # Web界面
├── static/                   # 静态文件
├── requirements.txt          # 依赖
├── START.md                  # 本文件
├── ENHANCED_README.md        # 完整文档
└── UPGRADE_SUMMARY.md        # 改造总结
```

## 🎯 下一步

1. 查看 `ENHANCED_README.md` 了解详细功能
2. 尝试不同的策略组合
3. 分析AI的决策理由
4. 根据表现优化提示词

## ⚠️ 重要提示

- 这是模拟交易系统
- 建议先用小额测试
- 关注AI的决策理由
- 定期检查交易记录

---

**准备好了吗？运行 `python app.py` 开始吧！** 🚀
