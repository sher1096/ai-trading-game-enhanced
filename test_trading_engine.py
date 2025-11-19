"""
测试 TradingEngine 是否正确使用数据库币种
"""
import requests

def test_trading_engine_coins():
    print("\n" + "="*60)
    print("测试 TradingEngine 币种动态加载")
    print("="*60)

    # 测试1: 查看 Model 1 的币种池
    print("\n[测试1] 查看 Model 1 的币种池...")
    response = requests.get('http://localhost:5000/api/models/1/coins')
    if response.status_code == 200:
        data = response.json()
        enabled_coins = [coin['symbol'] for coin in data['coins'] if coin['is_enabled']]
        print(f"Model 1 启用的币种: {enabled_coins}")
        print(f"预期应该是: ['ETH', 'BNB', 'SOL', 'XRP']")
        assert enabled_coins == ['ETH', 'BNB', 'SOL', 'XRP'], "币种列表不匹配！"
        print("[OK] 币种列表正确")
    else:
        print(f"[ERROR] Failed: {response.status_code}")
        return

    # 测试2: 添加新币种 ADA 到 Model 1
    print("\n[测试2] 添加 ADA 到 Model 1...")

    # 先查看 ADA 是否存在，如果不存在则创建
    response = requests.get('http://localhost:5000/api/coins?is_active=0')
    if response.status_code == 200:
        all_coins = response.json()
        ada_coin = next((c for c in all_coins if c['symbol'] == 'ADA'), None)
        if ada_coin:
            # 重新激活 ADA
            response = requests.put(f'http://localhost:5000/api/coins/{ada_coin["id"]}',
                                   json={'is_active': 1})
            print(f"  - 重新激活 ADA (ID: {ada_coin['id']})")
            ada_id = ada_coin['id']
        else:
            # 创建新的 ADA
            response = requests.post('http://localhost:5000/api/coins', json={
                'symbol': 'ADA',
                'name': 'Cardano',
                'category': 'Layer1',
                'binance_symbol': 'ADAUSDT',
                'okx_symbol': 'ADA-USDT',
                'coingecko_id': 'cardano',
                'market_cap_rank': 8
            })
            if response.status_code == 201:
                ada_id = response.json()['id']
                print(f"  - 创建 ADA (ID: {ada_id})")
            else:
                print(f"[ERROR] 无法创建 ADA: {response.status_code}")
                return

    # 将 ADA 添加到 Model 1 的币种池
    response = requests.post('http://localhost:5000/api/models/1/coins',
                            json={'coin_ids': [ada_id]})
    if response.status_code == 200:
        print(f"  - ADA 已添加到 Model 1 的币种池")
    else:
        print(f"[ERROR] 添加失败: {response.status_code}")
        return

    # 测试3: 查看更新后的币种池
    print("\n[测试3] 查看更新后的 Model 1 币种池...")
    response = requests.get('http://localhost:5000/api/models/1/coins')
    if response.status_code == 200:
        data = response.json()
        enabled_coins = [coin['symbol'] for coin in data['coins'] if coin['is_enabled']]
        print(f"Model 1 启用的币种: {enabled_coins}")
        assert 'ADA' in enabled_coins, "ADA 应该在币种列表中！"
        print("[OK] ADA 已成功添加")
    else:
        print(f"[ERROR] Failed: {response.status_code}")
        return

    # 测试4: 触发手动交易周期，查看日志
    print("\n[测试4] 触发 Model 1 的手动交易周期...")
    response = requests.post('http://localhost:5000/api/trade/1')
    if response.status_code == 200:
        result = response.json()
        print(f"  - 交易周期执行成功")
        print(f"  - 决策数量: {len(result.get('decisions', {}))}")
        coins_in_decisions = list(result.get('decisions', {}).keys())
        print(f"  - 决策币种: {coins_in_decisions}")
        print("\n  注意: TradingEngine 在初始化时加载了币种，需要重启服务器才能看到 ADA")
        print("  这正是 refresh_coins() 方法的用途")
    else:
        print(f"[ERROR] 交易失败: {response.status_code}")
        return

    print("\n" + "="*60)
    print("[测试总结]")
    print("1. Model 1 从数据库正确加载了 4 个币种 (ETH, BNB, SOL, XRP)")
    print("2. 成功通过 API 添加了 ADA 到 Model 1 的币种池")
    print("3. TradingEngine 在初始化时加载币种列表")
    print("4. 要使新币种生效，需要重启服务器或调用 refresh_coins()")
    print("="*60)

if __name__ == '__main__':
    try:
        test_trading_engine_coins()
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
