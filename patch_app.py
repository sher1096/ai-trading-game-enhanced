"""
Patch app.py to use EnhancedAITrader
"""

# 读取文件
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 add_model 函数中的内容
old_code = '''        model_id = db.add_model(
            name=data['name'],
            provider_id=data['provider_id'],
            model_name=data['model_name'],
            initial_capital=float(data.get('initial_capital', 100000))
        )

        model = db.get_model(model_id)
        trading_engines[model_id] = TradingEngine(
            model_id=model_id,
            db=db,
            market_fetcher=market_fetcher,
            ai_trader=AITrader(
                api_key=model['api_key'],
                api_url=model['api_url'],
                model_name=model['model_name']
            ),
            trade_fee_rate=TRADE_FEE_RATE  # 新增：传入费率
        )
        print(f"[INFO] Model {model_id} ({data['name']}) initialized")'''

new_code = '''        # 获取策略配置
        strategy_name = data.get('strategy_name', 'None')
        custom_prompt = data.get('custom_prompt')

        model_id = db.add_model(
            name=data['name'],
            provider_id=data['provider_id'],
            model_name=data['model_name'],
            initial_capital=float(data.get('initial_capital', 100000)),
            strategy_name=strategy_name,
            custom_prompt=custom_prompt
        )

        model = db.get_model(model_id)
        trading_engines[model_id] = TradingEngine(
            model_id=model_id,
            db=db,
            market_fetcher=market_fetcher,
            ai_trader=EnhancedAITrader(
                api_key=model['api_key'],
                api_url=model['api_url'],
                model_name=model['model_name'],
                strategy_name=strategy_name,
                custom_prompt=custom_prompt
            ),
            trade_fee_rate=TRADE_FEE_RATE
        )
        print(f"[INFO] Model {model_id} ({data['name']}) initialized with strategy: {strategy_name}")'''

content = content.replace(old_code, new_code)

# 添加新的API端点（在文件末尾，app.run()之前）
api_endpoint = '''

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

'''

# 在 app.run() 之前插入
if "if __name__ == '__main__':" in content:
    content = content.replace("if __name__ == '__main__':", api_endpoint + "if __name__ == '__main__':")

# 写回文件
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] app.py has been patched!")
