# App.py 修改说明

## 需要修改的地方

### 1. 导入增强版AI交易引擎

在文件顶部，修改导入：

```python
# 原来的
from ai_trader import AITrader

# 改为
from ai_trader_enhanced import EnhancedAITrader
```

### 2. 修改 /api/models POST 端点

在 add_model() 函数中，添加策略参数：

```python
@app.route('/api/models', methods=['POST'])
def add_model():
    data = request.json
    try:
        # Get provider info
        provider = db.get_provider(data['provider_id'])
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404

        # 新增：获取策略配置
        strategy_name = data.get('strategy_name', 'None')
        custom_prompt = data.get('custom_prompt')

        model_id = db.add_model(
            name=data['name'],
            provider_id=data['provider_id'],
            model_name=data['model_name'],
            initial_capital=float(data.get('initial_capital', 100000)),
            strategy_name=strategy_name,          # 新增
            custom_prompt=custom_prompt           # 新增
        )

        model = db.get_model(model_id)

        # 使用增强版AI交易引擎
        trading_engines[model_id] = TradingEngine(
            model_id=model_id,
            db=db,
            market_fetcher=market_fetcher,
            ai_trader=EnhancedAITrader(
                api_key=model['api_key'],
                api_url=model['api_url'],
                model_name=model['model_name'],
                strategy_name=strategy_name,       # 新增
                custom_prompt=custom_prompt        # 新增
            ),
            trade_fee_rate=TRADE_FEE_RATE
        )
        print(f"[INFO] Model {model_id} ({data['name']}) initialized with strategy: {strategy_name}")

        return jsonify({'id': model_id, 'message': 'Model added successfully'})

    except Exception as e:
        print(f"[ERROR] Failed to add model: {e}")
        return jsonify({'error': str(e)}), 500
```

### 3. 添加获取可用策略的API端点

在文件中添加新的路由：

```python
@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get available trading strategies"""
    strategies = [
        {
            'name': 'None',
            'description': 'No technical strategy, pure AI decision'
        },
        {
            'name': 'MovingAverage',
            'description': 'Moving Average Crossover (SMA 5/20)'
        },
        {
            'name': 'RSI',
            'description': 'Relative Strength Index (RSI < 30 buy, RSI > 70 sell)'
        },
        {
            'name': 'MACD',
            'description': 'MACD (Moving Average Convergence Divergence)'
        },
        {
            'name': 'Combined',
            'description': 'Combined Strategy (MA + RSI + MACD)'
        }
    ]
    return jsonify(strategies)
```

### 4. 更新依赖

在 requirements.txt 中添加：

```
pandas
numpy
talib  # 如果使用技术指标
```
