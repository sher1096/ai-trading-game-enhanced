# 实盘交易接入指南

## 📋 系统架构

### 已完成模块

1. **交易所接口模块** (`exchange_connector.py`)
   - ✅ 币安（Binance）API封装
   - ✅ 欧意（OKX）API封装
   - ✅ 支持测试网和实盘切换
   - ✅ K线数据获取
   - ✅ 下单/撤单功能
   - ✅ 持仓查询
   - ✅ 余额查询
   - ✅ 平仓功能

2. **两档优先级决策系统**
   - ✅ 第一档：EMA多空排列 + 高低点抬升判断
   - ✅ 第二档：K线形态分析（10种模式）
   - ✅ 风险控制：做空谨慎原则

## 🚀 快速开始

### 1. 配置API密钥

复制配置文件模板：
```bash
cp exchange_config.json.example exchange_config.json
```

编辑 `exchange_config.json`，填入你的API密钥：

```json
{
  "binance": {
    "enabled": true,
    "api_key": "你的币安API密钥",
    "api_secret": "你的币安API密钥Secret",
    "testnet": true  // 建议先使用测试网
  },
  "okx": {
    "enabled": true,
    "api_key": "你的欧意API密钥",
    "api_secret": "你的欧意API密钥Secret",
    "testnet": true  // 建议先使用测试网
  }
}
```

### 2. 获取测试网API密钥

**币安测试网：**
1. 访问：https://testnet.binancefuture.com/
2. 使用GitHub账号登录
3. 生成API密钥

**欧意测试网：**
1. 访问：https://www.okx.com/
2. 注册账户后，在API管理中创建测试API

### 3. 使用示例

```python
from exchange_connector import ExchangeManager

# 初始化交易所管理器
manager = ExchangeManager()

# 获取币安连接
binance = manager.get_exchange('binance')

# 获取BTC/USDT的K线数据
df = binance.fetch_ohlcv('BTC/USDT', '1h', 100)
print(df.tail())

# 查询当前价格
ticker = binance.fetch_ticker('BTC/USDT')
print(f"当前价格: {ticker['last']}")

# 查询账户余额
balance = binance.fetch_balance()
print(f"USDT余额: {balance['USDT']['free']}")

# 下单示例（市价买入）
# order = binance.create_order('BTC/USDT', 'buy', 'market', 0.001)
# print(f"订单ID: {order['id']}")

# 查询持仓
positions = binance.fetch_positions('BTC/USDT')
for pos in positions:
    print(f"持仓: {pos['symbol']} {pos['side']} {pos['contracts']}")
```

## ⚠️ 安全提示

### API权限设置
1. **只开启必要权限：**
   - ✅ 读取权限
   - ✅ 交易权限
   - ❌ 提币权限（强烈不建议开启）

2. **IP白名单：**
   - 建议设置IP白名单，只允许你的服务器IP访问

3. **API密钥安全：**
   - ⚠️ 绝不要将API密钥提交到Git仓库
   - ⚠️ 定期更换API密钥
   - ⚠️ 使用不同的API密钥用于测试和实盘

### 交易风险控制

1. **从小额开始：**
   - 建议从测试网开始
   - 实盘初期使用小额资金测试（如10-100 USDT）
   - 逐步增加仓位

2. **设置止损：**
   - 每笔交易都应设置止损
   - 单笔亏损不超过总资金的2%

3. **仓位管理：**
   - 单个币种仓位不超过总资金的20%
   - 总持仓不超过总资金的50%

4. **定期检查：**
   - 每天检查持仓和订单状态
   - 及时处理异常订单
   - 定期回顾交易记录

## 📊 支持的交易所

| 交易所 | 状态 | 测试网 | 永续合约 | 现货 |
|--------|------|--------|----------|------|
| 币安 Binance | ✅ 已支持 | ✅ | ✅ | ✅ |
| 欧意 OKX | ✅ 已支持 | ✅ | ✅ | ✅ |

## 🔧 主要功能

### 交易所操作
- `fetch_ohlcv()` - 获取K线数据
- `fetch_ticker()` - 获取最新价格
- `create_order()` - 创建订单（市价/限价）
- `cancel_order()` - 撤销订单
- `fetch_order()` - 查询订单状态
- `fetch_balance()` - 查询账户余额
- `fetch_positions()` - 查询持仓
- `close_position()` - 平仓

### 决策系统
- 两档优先级信号生成
- 多指标综合分析
- 风险控制（做空谨慎）

## 📝 配置说明

### exchange_config.json 参数

```json
{
  "binance": {
    "enabled": true,        // 是否启用
    "api_key": "...",       // API密钥
    "api_secret": "...",    // API密钥Secret
    "testnet": true         // 测试网/实盘切换
  },
  "trading_config": {
    "max_position_size": 0.1,      // 最大仓位（BTC数量）
    "max_position_usdt": 1000,     // 最大仓位（USDT金额）
    "stop_loss_pct": 0.02,         // 止损百分比（2%）
    "take_profit_pct": 0.05,       // 止盈百分比（5%）
    "leverage": 5                   // 杠杆倍数
  }
}
```

## 🐛 故障排查

### 常见问题

1. **连接失败：**
   - 检查API密钥是否正确
   - 检查网络连接
   - 确认testnet设置正确

2. **下单失败：**
   - 检查余额是否充足
   - 检查订单参数（数量、价格）
   - 查看交易所错误信息

3. **持仓查询为空：**
   - 确认已有持仓
   - 检查symbol格式（如'BTC/USDT'）
   - 确认账户类型（现货/合约）

## 📚 下一步开发计划

- [ ] Web UI配置界面
- [ ] 自动交易执行引擎
- [ ] 完善的风险控制系统
- [ ] 交易记录和回测分析
- [ ] 报警通知（邮件/微信/Telegram）
- [ ] 多策略组合

## ⚡ 重要提醒

**实盘交易涉及真实资金，请务必：**

1. ✅ 先在测试网充分测试
2. ✅ 理解交易逻辑和风险
3. ✅ 设置合理的止损止盈
4. ✅ 使用小额资金测试
5. ✅ 不要使用全部资金
6. ✅ 保持理性，不要频繁交易
7. ✅ 定期检查和调整策略

**投资有风险，入市需谨慎！**
