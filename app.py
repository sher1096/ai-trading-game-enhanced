from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time
import threading
import json
import re
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from trading_engine import TradingEngine
from market_data import MarketDataFetcher
from ai_trader_enhanced import EnhancedAITrader
from database import Database
from version import __version__, __github_owner__, __repo__, GITHUB_REPO_URL, LATEST_RELEASE_URL
from exchange_connector import ExchangeManager
from live_trade_executor import LiveTradeExecutor

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)

db = Database('AITradeGame.db')
market_fetcher = MarketDataFetcher()
trading_engines = {}
auto_trading = True
TRADE_FEE_RATE = 0.001  # 默认交易费率

# 实盘交易管理器
exchange_manager = None
live_executor = None

# 调度器：为每个模型创建独立的定时任务
scheduler = BackgroundScheduler()
model_jobs = {}  # 存储每个模型的任务ID {model_id: job_id}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/coins-management')
def coins_management():
    """币种管理页面"""
    return render_template('coin_management.html')

# ============ Health Check ============

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点 - 用于Docker和负载均衡器"""
    try:
        # 检查数据库连接
        db.get_all_models()

        # 检查调度器状态
        scheduler_running = scheduler.running

        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'scheduler': 'running' if scheduler_running else 'stopped',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

# ============ Provider API Endpoints ============

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Get all API providers"""
    providers = db.get_all_providers()
    return jsonify(providers)

@app.route('/api/providers', methods=['POST'])
def add_provider():
    """Add new API provider"""
    data = request.json
    try:
        provider_id = db.add_provider(
            name=data['name'],
            api_url=data['api_url'],
            api_key=data['api_key'],
            models=data.get('models', '')
        )
        return jsonify({'id': provider_id, 'message': 'Provider added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/providers/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    """Delete API provider"""
    try:
        db.delete_provider(provider_id)
        return jsonify({'message': 'Provider deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/providers/models', methods=['POST'])
def fetch_provider_models():
    """Fetch available models from provider's API - Returns 2025 latest models"""
    data = request.json
    api_url = data.get('api_url')
    api_key = data.get('api_key')

    if not api_url or not api_key:
        return jsonify({'error': 'API URL and key are required'}), 400

    try:
        # 2025最新推荐模型列表
        recommended_models_2025 = {
            'openai': ['gpt-5', 'gpt-5-mini', 'gpt-5-nano'],
            'claude': ['claude-sonnet-4-5', 'claude-opus-4-1', 'claude-haiku-4-5'],
            'anthropic': ['claude-sonnet-4-5', 'claude-opus-4-1', 'claude-haiku-4-5'],
            'deepseek': ['deepseek-chat', 'deepseek-reasoner'],
            'qwen': ['qwen-plus', 'qwen-plus-latest', 'qwen-turbo', 'qwen-max-2025-01-25'],
            'dashscope': ['qwen-plus', 'qwen-plus-latest', 'qwen-turbo', 'qwen-max-2025-01-25'],
        }

        models = []

        # 根据API URL检测提供商类型并返回推荐模型
        api_url_lower = api_url.lower()

        if 'openai.com' in api_url_lower:
            models = recommended_models_2025['openai']
            print(f"[INFO] Returning OpenAI 2025 models: {models}")
        elif 'anthropic.com' in api_url_lower or 'claude' in api_url_lower:
            models = recommended_models_2025['claude']
            print(f"[INFO] Returning Claude 2025 models: {models}")
        elif 'deepseek' in api_url_lower:
            models = recommended_models_2025['deepseek']
            print(f"[INFO] Returning DeepSeek 2025 models: {models}")
        elif 'dashscope' in api_url_lower or 'aliyun' in api_url_lower or 'qwen' in api_url_lower:
            models = recommended_models_2025['qwen']
            print(f"[INFO] Returning Qwen 2025 models: {models}")
        else:
            # 尝试调用API获取，但只保留2025最新模型
            try:
                import requests
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                response = requests.get(f'{api_url}/models', headers=headers, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    all_models = [m['id'] for m in result.get('data', [])]

                    # 过滤出2025最新模型
                    models_2025 = ['gpt-5', 'gpt-5-mini', 'gpt-5-nano',
                                   'claude-sonnet-4-5', 'claude-opus-4-1', 'claude-haiku-4-5',
                                   'deepseek-chat', 'deepseek-reasoner',
                                   'qwen-plus', 'qwen-turbo', 'qwen-max']

                    models = [m for m in all_models if any(latest in m for latest in models_2025)]

                    if not models:
                        # 如果没有找到2025模型，返回通用推荐
                        models = ['gpt-5', 'gpt-5-mini', 'claude-sonnet-4-5']
                        print(f"[WARN] No 2025 models found in API, returning defaults")
                else:
                    # API调用失败，返回通用推荐
                    models = ['gpt-5', 'gpt-5-mini', 'claude-sonnet-4-5']
                    print(f"[WARN] API call failed, returning default 2025 models")
            except:
                # 出错时返回通用推荐
                models = ['gpt-5', 'gpt-5-mini', 'claude-sonnet-4-5']
                print(f"[WARN] Error fetching models, returning default 2025 models")

        return jsonify({'models': models})
    except Exception as e:
        print(f"[ERROR] Fetch models failed: {e}")
        return jsonify({'error': f'Failed to fetch models: {str(e)}'}), 500

# ============ Model API Endpoints ============

@app.route('/api/models', methods=['GET'])
def get_models():
    models = db.get_all_models()
    return jsonify(models)

@app.route('/api/models', methods=['POST'])
def add_model():
    data = request.json
    try:
        # Get provider info
        provider = db.get_provider(data['provider_id'])
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404

        # 获取配置
        custom_prompt = data.get('custom_prompt')
        indicators_config = data.get('indicators_config')  # JSON string from frontend

        # 自动设置strategy_name：如果有指标配置则使用MultiIndicator，否则为None
        strategy_name = 'MultiIndicator' if indicators_config else 'None'

        # 实盘交易配置
        live_trading_enabled = data.get('live_trading_enabled', False)
        live_exchange = data.get('live_exchange')
        live_symbol = data.get('live_symbol', 'BTC/USDT')

        # 交易间隔配置（每个模型独立设置）
        trading_interval_minutes = int(data.get('trading_interval_minutes', 60))

        model_id = db.add_model(
            name=data['name'],
            provider_id=data['provider_id'],
            model_name=data['model_name'],
            initial_capital=float(data.get('initial_capital', 100000)),
            strategy_name=strategy_name,
            custom_prompt=custom_prompt,
            indicators_config=indicators_config,
            live_trading_enabled=live_trading_enabled,
            live_exchange=live_exchange,
            live_symbol=live_symbol,
            trading_interval_minutes=trading_interval_minutes
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
                custom_prompt=custom_prompt,
                indicators_config=indicators_config
            ),
            trade_fee_rate=TRADE_FEE_RATE,
            live_executor=live_executor  # 传入实盘执行器
        )

        if indicators_config:
            print(f"[INFO] Model {model_id} ({data['name']}) initialized with technical indicators")
        else:
            print(f"[INFO] Model {model_id} ({data['name']}) initialized without technical indicators")

        # 为新模型添加定时任务
        add_model_job(model_id, trading_interval_minutes)
        print(f"[INFO] Model {model_id} scheduled with {trading_interval_minutes} minute interval")

        return jsonify({'id': model_id, 'message': 'Model added successfully'})

    except Exception as e:
        print(f"[ERROR] Failed to add model: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    try:
        model = db.get_model(model_id)
        model_name = model['name'] if model else f"ID-{model_id}"

        db.delete_model(model_id)

        # 移除模型的定时任务
        remove_model_job(model_id)

        if model_id in trading_engines:
            del trading_engines[model_id]

        print(f"[INFO] Model {model_id} ({model_name}) deleted")
        return jsonify({'message': 'Model deleted successfully'})
    except Exception as e:
        print(f"[ERROR] Delete model {model_id} failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/portfolio', methods=['GET'])
def get_portfolio(model_id):
    prices_data = market_fetcher.get_current_prices(['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE'])
    current_prices = {coin: prices_data[coin]['price'] for coin in prices_data}
    
    portfolio = db.get_portfolio(model_id, current_prices)
    account_value = db.get_account_value_history(model_id, limit=100)
    
    return jsonify({
        'portfolio': portfolio,
        'account_value_history': account_value
    })

@app.route('/api/models/<int:model_id>/trades', methods=['GET'])
def get_trades(model_id):
    limit = request.args.get('limit', 50, type=int)
    trades = db.get_trades(model_id, limit=limit)
    return jsonify(trades)

@app.route('/api/models/<int:model_id>/conversations', methods=['GET'])
def get_conversations(model_id):
    limit = request.args.get('limit', 20, type=int)
    conversations = db.get_conversations(model_id, limit=limit)
    return jsonify(conversations)

@app.route('/api/aggregated/portfolio', methods=['GET'])
def get_aggregated_portfolio():
    """Get aggregated portfolio data across all models"""
    prices_data = market_fetcher.get_current_prices(['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE'])
    current_prices = {coin: prices_data[coin]['price'] for coin in prices_data}

    # Get aggregated data
    models = db.get_all_models()
    total_portfolio = {
        'total_value': 0,
        'cash': 0,
        'positions_value': 0,
        'realized_pnl': 0,
        'unrealized_pnl': 0,
        'initial_capital': 0,
        'positions': []
    }

    all_positions = {}

    for model in models:
        portfolio = db.get_portfolio(model['id'], current_prices)
        if portfolio:
            total_portfolio['total_value'] += portfolio.get('total_value', 0)
            total_portfolio['cash'] += portfolio.get('cash', 0)
            total_portfolio['positions_value'] += portfolio.get('positions_value', 0)
            total_portfolio['realized_pnl'] += portfolio.get('realized_pnl', 0)
            total_portfolio['unrealized_pnl'] += portfolio.get('unrealized_pnl', 0)
            total_portfolio['initial_capital'] += portfolio.get('initial_capital', 0)

            # Aggregate positions by coin and side
            for pos in portfolio.get('positions', []):
                key = f"{pos['coin']}_{pos['side']}"
                if key not in all_positions:
                    all_positions[key] = {
                        'coin': pos['coin'],
                        'side': pos['side'],
                        'quantity': 0,
                        'avg_price': 0,
                        'total_cost': 0,
                        'leverage': pos['leverage'],
                        'current_price': pos['current_price'],
                        'pnl': 0
                    }

                # Weighted average calculation
                current_pos = all_positions[key]
                current_cost = current_pos['quantity'] * current_pos['avg_price']
                new_cost = pos['quantity'] * pos['avg_price']
                total_quantity = current_pos['quantity'] + pos['quantity']

                if total_quantity > 0:
                    current_pos['avg_price'] = (current_cost + new_cost) / total_quantity
                    current_pos['quantity'] = total_quantity
                    current_pos['total_cost'] = current_cost + new_cost
                    current_pos['pnl'] = (pos['current_price'] - current_pos['avg_price']) * total_quantity

    total_portfolio['positions'] = list(all_positions.values())

    # Get multi-model chart data
    chart_data = db.get_multi_model_chart_data(limit=100)

    return jsonify({
        'portfolio': total_portfolio,
        'chart_data': chart_data,
        'model_count': len(models)
    })

@app.route('/api/models/chart-data', methods=['GET'])
def get_models_chart_data():
    """Get chart data for all models"""
    limit = request.args.get('limit', 100, type=int)
    chart_data = db.get_multi_model_chart_data(limit=limit)
    return jsonify(chart_data)

@app.route('/api/market/prices', methods=['GET'])
def get_market_prices():
    coins = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']
    prices = market_fetcher.get_current_prices(coins)
    return jsonify(prices)

@app.route('/api/models/<int:model_id>/execute', methods=['POST'])
def execute_trading(model_id):
    if model_id not in trading_engines:
        model = db.get_model(model_id)
        if not model:
            return jsonify({'error': 'Model not found'}), 404

        # Get provider info
        provider = db.get_provider(model['provider_id'])
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404

        trading_engines[model_id] = TradingEngine(
            model_id=model_id,
            db=db,
            market_fetcher=market_fetcher,
            ai_trader=EnhancedAITrader(
                api_key=provider['api_key'],
                api_url=provider['api_url'],
                model_name=model['model_name']
            ),
            trade_fee_rate=TRADE_FEE_RATE,  # 新增：传入费率
            live_executor=live_executor
        )
    
    try:
        result = trading_engines[model_id].execute_trading_cycle()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def trading_loop():
    print("[INFO] Trading loop started")
    
    while auto_trading:
        try:
            if not trading_engines:
                time.sleep(30)
                continue
            
            print(f"\n{'='*60}")
            print(f"[CYCLE] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[INFO] Active models: {len(trading_engines)}")
            print(f"{'='*60}")
            
            for model_id, engine in list(trading_engines.items()):
                try:
                    print(f"\n[EXEC] Model {model_id}")
                    result = engine.execute_trading_cycle()
                    
                    if result.get('success'):
                        print(f"[OK] Model {model_id} completed")
                        if result.get('executions'):
                            for exec_result in result['executions']:
                                signal = exec_result.get('signal', 'unknown')
                                coin = exec_result.get('coin', 'unknown')
                                msg = exec_result.get('message', '')
                                if signal != 'hold':
                                    print(f"  [TRADE] {coin}: {msg}")
                    else:
                        error = result.get('error', 'Unknown error')
                        print(f"[WARN] Model {model_id} failed: {error}")
                        
                except Exception as e:
                    print(f"[ERROR] Model {model_id} exception: {e}")
                    import traceback
                    print(traceback.format_exc())
                    continue
            
            print(f"\n{'='*60}")
            print(f"[SLEEP] Waiting 3 minutes for next cycle")
            print(f"{'='*60}\n")
            
            time.sleep(180)
            
        except Exception as e:
            print(f"\n[CRITICAL] Trading loop error: {e}")
            import traceback
            print(traceback.format_exc())
            print("[RETRY] Retrying in 60 seconds\n")
            time.sleep(60)
    
    print("[INFO] Trading loop stopped")

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    models = db.get_all_models()
    leaderboard = []
    
    prices_data = market_fetcher.get_current_prices(['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE'])
    current_prices = {coin: prices_data[coin]['price'] for coin in prices_data}
    
    for model in models:
        portfolio = db.get_portfolio(model['id'], current_prices)
        account_value = portfolio.get('total_value', model['initial_capital'])
        returns = ((account_value - model['initial_capital']) / model['initial_capital']) * 100
        
        leaderboard.append({
            'model_id': model['id'],
            'model_name': model['name'],
            'account_value': account_value,
            'returns': returns,
            'initial_capital': model['initial_capital']
        })
    
    leaderboard.sort(key=lambda x: x['returns'], reverse=True)
    return jsonify(leaderboard)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    try:
        settings = db.get_settings()
        return jsonify(settings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    """Update system settings"""
    try:
        data = request.json
        trading_frequency_minutes = int(data.get('trading_frequency_minutes', 60))
        trading_fee_rate = float(data.get('trading_fee_rate', 0.001))

        success = db.update_settings(trading_frequency_minutes, trading_fee_rate)

        if success:
            return jsonify({'success': True, 'message': 'Settings updated successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update settings'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/version', methods=['GET'])
def get_version():
    """Get current version information"""
    return jsonify({
        'current_version': __version__,
        'github_repo': GITHUB_REPO_URL,
        'latest_release_url': LATEST_RELEASE_URL
    })

@app.route('/api/check-update', methods=['GET'])
def check_update():
    """Check for GitHub updates"""
    try:
        import requests

        # Get latest release from GitHub
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AITradeGame/1.0'
        }

        # Try to get latest release
        try:
            response = requests.get(
                f"https://api.github.com/repos/{__github_owner__}/{__repo__}/releases/latest",
                headers=headers,
                timeout=5
            )

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').lstrip('v')
                release_url = release_data.get('html_url', '')
                release_notes = release_data.get('body', '')

                # Compare versions
                is_update_available = compare_versions(latest_version, __version__) > 0

                return jsonify({
                    'update_available': is_update_available,
                    'current_version': __version__,
                    'latest_version': latest_version,
                    'release_url': release_url,
                    'release_notes': release_notes,
                    'repo_url': GITHUB_REPO_URL
                })
            else:
                # If API fails, still return current version info
                return jsonify({
                    'update_available': False,
                    'current_version': __version__,
                    'error': 'Could not check for updates'
                })
        except Exception as e:
            print(f"[WARN] GitHub API error: {e}")
            return jsonify({
                'update_available': False,
                'current_version': __version__,
                'error': 'Network error checking updates'
            })

    except Exception as e:
        print(f"[ERROR] Check update failed: {e}")
        return jsonify({
            'update_available': False,
            'current_version': __version__,
            'error': str(e)
        }), 500

def compare_versions(version1, version2):
    """Compare two version strings.

    Returns:
        1 if version1 > version2
        0 if version1 == version2
        -1 if version1 < version2
    """
    def normalize(v):
        # Extract numeric parts from version string
        parts = re.findall(r'\d+', v)
        # Pad with zeros to make them comparable
        return [int(p) for p in parts]

    v1_parts = normalize(version1)
    v2_parts = normalize(version2)

    # Pad shorter version with zeros
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))

    # Compare
    if v1_parts > v2_parts:
        return 1
    elif v1_parts < v2_parts:
        return -1
    else:
        return 0

def init_trading_engines():
    try:
        models = db.get_all_models()

        if not models:
            print("[WARN] No trading models found")
            return

        print(f"\n[INIT] Initializing trading engines...")
        for model in models:
            model_id = model['id']
            model_name = model['name']

            try:
                # Get provider info
                provider = db.get_provider(model['provider_id'])
                if not provider:
                    print(f"  [WARN] Model {model_id} ({model_name}): Provider not found")
                    continue

                trading_engines[model_id] = TradingEngine(
                    model_id=model_id,
                    db=db,
                    market_fetcher=market_fetcher,
                    ai_trader=EnhancedAITrader(
                        api_key=provider['api_key'],
                        api_url=provider['api_url'],
                        model_name=model['model_name']
                    ),
                    trade_fee_rate=TRADE_FEE_RATE,
                    live_executor=live_executor
                )

                # 为该模型添加定时任务
                interval_minutes = model.get('trading_interval_minutes', 60)
                if add_model_job(model_id, interval_minutes):
                    print(f"  [OK] Model {model_id} ({model_name}) - Interval: {interval_minutes}min")
                else:
                    print(f"  [WARN] Model {model_id} ({model_name}) - Failed to schedule")
            except Exception as e:
                print(f"  [ERROR] Model {model_id} ({model_name}): {e}")
                continue

        print(f"[INFO] Initialized {len(trading_engines)} engine(s)\n")

    except Exception as e:
        print(f"[ERROR] Init engines failed: {e}\n")



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

# ============ Coin Management API Endpoints ============

@app.route('/api/coins', methods=['GET'])
def get_coins():
    """Get all coins with optional filtering"""
    category = request.args.get('category')
    is_active = request.args.get('is_active', '1')

    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM coins WHERE is_active = ?"
        params = [int(is_active)]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY market_cap_rank ASC, symbol ASC"

        cursor.execute(query, params)
        coins = cursor.fetchall()

        # Convert to list of dictionaries
        result = []
        for coin in coins:
            result.append({
                'id': coin['id'],
                'symbol': coin['symbol'],
                'name': coin['name'],
                'category': coin['category'],
                'is_active': coin['is_active'],
                'binance_symbol': coin['binance_symbol'],
                'okx_symbol': coin['okx_symbol'],
                'coingecko_id': coin['coingecko_id'],
                'market_cap_rank': coin['market_cap_rank'],
                'notes': coin['notes'],
                'created_at': coin['created_at'],
                'updated_at': coin['updated_at']
            })

        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/coins', methods=['POST'])
def create_coin():
    """Add a new coin to the system"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'symbol' not in data or 'name' not in data:
            return jsonify({'error': 'Missing required fields: symbol, name'}), 400

        conn = db.get_connection()
        cursor = conn.cursor()

        # Insert new coin
        cursor.execute("""
            INSERT INTO coins
            (symbol, name, category, binance_symbol, okx_symbol, coingecko_id, market_cap_rank, notes, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['symbol'].upper(),
            data['name'],
            data.get('category'),
            data.get('binance_symbol'),
            data.get('okx_symbol'),
            data.get('coingecko_id'),
            data.get('market_cap_rank'),
            data.get('notes'),
            data.get('is_active', 1)
        ))

        conn.commit()
        coin_id = cursor.lastrowid

        # Retrieve the created coin
        cursor.execute("SELECT * FROM coins WHERE id = ?", (coin_id,))
        coin = cursor.fetchone()

        result = {
            'id': coin['id'],
            'symbol': coin['symbol'],
            'name': coin['name'],
            'category': coin['category'],
            'is_active': coin['is_active'],
            'binance_symbol': coin['binance_symbol'],
            'okx_symbol': coin['okx_symbol'],
            'coingecko_id': coin['coingecko_id'],
            'market_cap_rank': coin['market_cap_rank'],
            'notes': coin['notes'],
            'created_at': coin['created_at'],
            'updated_at': coin['updated_at']
        }

        conn.close()
        return jsonify(result), 201
    except sqlite3.IntegrityError as e:
        return jsonify({'error': f'Coin with symbol {data.get("symbol")} already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/coins/<int:coin_id>', methods=['PUT'])
def update_coin(coin_id):
    """Update an existing coin"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        conn = db.get_connection()
        cursor = conn.cursor()

        # Check if coin exists
        cursor.execute("SELECT * FROM coins WHERE id = ?", (coin_id,))
        coin = cursor.fetchone()

        if not coin:
            conn.close()
            return jsonify({'error': f'Coin with ID {coin_id} not found'}), 404

        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []

        allowed_fields = ['symbol', 'name', 'category', 'binance_symbol', 'okx_symbol',
                         'coingecko_id', 'market_cap_rank', 'notes', 'is_active']

        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                # Convert symbol to uppercase
                if field == 'symbol':
                    update_values.append(data[field].upper())
                else:
                    update_values.append(data[field])

        if not update_fields:
            conn.close()
            return jsonify({'error': 'No valid fields to update'}), 400

        # Add updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        # Execute update
        query = f"UPDATE coins SET {', '.join(update_fields)} WHERE id = ?"
        update_values.append(coin_id)
        cursor.execute(query, update_values)
        conn.commit()

        # Retrieve updated coin
        cursor.execute("SELECT * FROM coins WHERE id = ?", (coin_id,))
        coin = cursor.fetchone()

        result = {
            'id': coin['id'],
            'symbol': coin['symbol'],
            'name': coin['name'],
            'category': coin['category'],
            'is_active': coin['is_active'],
            'binance_symbol': coin['binance_symbol'],
            'okx_symbol': coin['okx_symbol'],
            'coingecko_id': coin['coingecko_id'],
            'market_cap_rank': coin['market_cap_rank'],
            'notes': coin['notes'],
            'created_at': coin['created_at'],
            'updated_at': coin['updated_at']
        }

        conn.close()
        return jsonify(result)
    except sqlite3.IntegrityError as e:
        return jsonify({'error': 'Coin with this symbol already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/coins/<int:coin_id>', methods=['DELETE'])
def delete_coin(coin_id):
    """Soft delete a coin (set is_active = 0)"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Check if coin exists
        cursor.execute("SELECT * FROM coins WHERE id = ?", (coin_id,))
        coin = cursor.fetchone()

        if not coin:
            conn.close()
            return jsonify({'error': f'Coin with ID {coin_id} not found'}), 404

        # Soft delete (set is_active = 0)
        cursor.execute("""
            UPDATE coins
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (coin_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'message': f'Coin {coin["symbol"]} ({coin["name"]}) has been deactivated',
            'id': coin_id,
            'symbol': coin['symbol']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ Model Coin Pool API Endpoints ============

@app.route('/api/models/<int:model_id>/coins', methods=['GET'])
def get_model_coins(model_id):
    """Get all coins assigned to a specific model"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Check if model exists
        cursor.execute("SELECT * FROM models WHERE id = ?", (model_id,))
        model = cursor.fetchone()

        if not model:
            conn.close()
            return jsonify({'error': f'Model with ID {model_id} not found'}), 404

        # Get all coins for this model with details
        cursor.execute("""
            SELECT
                c.id,
                c.symbol,
                c.name,
                c.category,
                c.binance_symbol,
                c.okx_symbol,
                c.coingecko_id,
                c.market_cap_rank,
                mcp.is_enabled,
                mcp.weight,
                mcp.added_at
            FROM model_coin_pools mcp
            JOIN coins c ON mcp.coin_id = c.id
            WHERE mcp.model_id = ?
            ORDER BY c.market_cap_rank ASC, c.symbol ASC
        """, (model_id,))

        coins = cursor.fetchall()

        result = []
        for coin in coins:
            result.append({
                'coin_id': coin['id'],
                'symbol': coin['symbol'],
                'name': coin['name'],
                'category': coin['category'],
                'binance_symbol': coin['binance_symbol'],
                'okx_symbol': coin['okx_symbol'],
                'coingecko_id': coin['coingecko_id'],
                'market_cap_rank': coin['market_cap_rank'],
                'is_enabled': coin['is_enabled'],
                'weight': coin['weight'],
                'added_at': coin['added_at']
            })

        conn.close()
        return jsonify({
            'model_id': model_id,
            'model_name': model['name'],
            'coins': result,
            'total_coins': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/coins', methods=['POST'])
def add_model_coins(model_id):
    """Add coins to a model's pool"""
    try:
        data = request.get_json()

        if not data or 'coin_ids' not in data:
            return jsonify({'error': 'Missing required field: coin_ids'}), 400

        conn = db.get_connection()
        cursor = conn.cursor()

        # Check if model exists
        cursor.execute("SELECT * FROM models WHERE id = ?", (model_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': f'Model with ID {model_id} not found'}), 404

        coin_ids = data['coin_ids']
        if not isinstance(coin_ids, list):
            coin_ids = [coin_ids]

        added_coins = []
        for coin_id in coin_ids:
            # Check if coin exists
            cursor.execute("SELECT * FROM coins WHERE id = ? AND is_active = 1", (coin_id,))
            coin = cursor.fetchone()

            if not coin:
                continue

            # Add to model's pool
            try:
                cursor.execute("""
                    INSERT INTO model_coin_pools (model_id, coin_id, is_enabled, weight)
                    VALUES (?, ?, ?, ?)
                """, (model_id, coin_id, 1, 1.0))
                added_coins.append({'coin_id': coin_id, 'symbol': coin['symbol']})
            except sqlite3.IntegrityError:
                # Coin already in pool, skip
                pass

        conn.commit()
        conn.close()

        return jsonify({
            'message': f'Added {len(added_coins)} coins to model {model_id}',
            'added_coins': added_coins
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/coins/<int:coin_id>', methods=['PUT'])
def update_model_coin(model_id, coin_id):
    """Update coin settings for a model"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        conn = db.get_connection()
        cursor = conn.cursor()

        # Check if the association exists
        cursor.execute("""
            SELECT * FROM model_coin_pools
            WHERE model_id = ? AND coin_id = ?
        """, (model_id, coin_id))

        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Coin not found in model pool'}), 404

        # Build update query
        update_fields = []
        update_values = []

        if 'is_enabled' in data:
            update_fields.append("is_enabled = ?")
            update_values.append(int(data['is_enabled']))

        if 'weight' in data:
            update_fields.append("weight = ?")
            update_values.append(float(data['weight']))

        if not update_fields:
            conn.close()
            return jsonify({'error': 'No valid fields to update'}), 400

        # Execute update
        query = f"UPDATE model_coin_pools SET {', '.join(update_fields)} WHERE model_id = ? AND coin_id = ?"
        update_values.extend([model_id, coin_id])
        cursor.execute(query, update_values)
        conn.commit()
        conn.close()

        return jsonify({'message': 'Model coin settings updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/coins/<int:coin_id>', methods=['DELETE'])
def remove_model_coin(model_id, coin_id):
    """Remove a coin from model's pool"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        # Check if the association exists
        cursor.execute("""
            SELECT c.symbol, c.name FROM model_coin_pools mcp
            JOIN coins c ON mcp.coin_id = c.id
            WHERE mcp.model_id = ? AND mcp.coin_id = ?
        """, (model_id, coin_id))

        coin = cursor.fetchone()

        if not coin:
            conn.close()
            return jsonify({'error': 'Coin not found in model pool'}), 404

        # Remove from pool
        cursor.execute("""
            DELETE FROM model_coin_pools
            WHERE model_id = ? AND coin_id = ?
        """, (model_id, coin_id))
        conn.commit()
        conn.close()

        return jsonify({
            'message': f'Removed {coin["symbol"]} ({coin["name"]}) from model {model_id}',
            'coin_id': coin_id,
            'symbol': coin['symbol']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ Live Trading API Endpoints ============

@app.route('/api/exchange/config', methods=['GET'])
def get_exchange_config():
    """获取交易所配置（不包含密钥）"""
    import os
    config_file = 'exchange_config.json'

    if not os.path.exists(config_file):
        return jsonify({
            'binance': {'enabled': False, 'testnet': True},
            'okx': {'enabled': False, 'testnet': True},
            'trading_config': {
                'max_position_size': 0.1,
                'max_position_usdt': 1000,
                'max_total_position': 0.5,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.05,
                'min_confidence': 70,
                'leverage': 5
            }
        })

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 移除敏感信息
        safe_config = {}
        for exchange_id in ['binance', 'okx']:
            if exchange_id in config:
                safe_config[exchange_id] = {
                    'enabled': config[exchange_id].get('enabled', False),
                    'testnet': config[exchange_id].get('testnet', True),
                    'has_api_key': bool(config[exchange_id].get('api_key'))
                }

        safe_config['trading_config'] = config.get('trading_config', {})

        return jsonify(safe_config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange/config', methods=['POST'])
def save_exchange_config():
    """保存交易所配置"""
    global exchange_manager, live_executor

    try:
        data = request.json
        config_file = 'exchange_config.json'

        # 加载现有配置（如果存在）
        existing_config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

        # 更新配置
        for exchange_id in ['binance', 'okx']:
            if exchange_id in data:
                if exchange_id not in existing_config:
                    existing_config[exchange_id] = {}

                existing_config[exchange_id]['enabled'] = data[exchange_id].get('enabled', False)
                existing_config[exchange_id]['testnet'] = data[exchange_id].get('testnet', True)

                # 只有提供了新密钥时才更新
                if data[exchange_id].get('api_key'):
                    existing_config[exchange_id]['api_key'] = data[exchange_id]['api_key']
                if data[exchange_id].get('api_secret'):
                    existing_config[exchange_id]['api_secret'] = data[exchange_id]['api_secret']

        # 更新交易配置
        if 'trading_config' in data:
            existing_config['trading_config'] = data['trading_config']

        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2, ensure_ascii=False)

        # 重新初始化交易所连接
        exchange_manager = ExchangeManager(config_file)

        # 初始化执行器
        risk_config = existing_config.get('trading_config', {})
        live_executor = LiveTradeExecutor(exchange_manager, risk_config, dry_run=True)

        return jsonify({'success': True, 'message': '配置保存成功'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange/status', methods=['GET'])
def get_exchange_status():
    """获取交易所连接状态"""
    if not exchange_manager:
        return jsonify({'connected': False, 'exchanges': []})

    exchanges = exchange_manager.list_exchanges()
    status = []

    for exchange_id in exchanges:
        try:
            exchange = exchange_manager.get_exchange(exchange_id)
            # 尝试获取ticker来测试连接
            ticker = exchange.fetch_ticker('BTC/USDT')
            status.append({
                'exchange': exchange_id,
                'connected': True,
                'testnet': exchange.testnet
            })
        except Exception as e:
            status.append({
                'exchange': exchange_id,
                'connected': False,
                'error': str(e)
            })

    return jsonify({'connected': len(status) > 0, 'exchanges': status})

@app.route('/api/exchange/balance', methods=['GET'])
def get_exchange_balance():
    """获取账户余额"""
    exchange_id = request.args.get('exchange', 'binance')

    if not exchange_manager:
        return jsonify({'error': '交易所未初始化'}), 400

    try:
        exchange = exchange_manager.get_exchange(exchange_id)
        if not exchange:
            return jsonify({'error': f'交易所{exchange_id}未连接'}), 400

        balance = exchange.fetch_balance()

        # 提取主要币种余额
        main_balances = {}
        for currency in ['USDT', 'BTC', 'ETH']:
            if currency in balance:
                main_balances[currency] = {
                    'free': float(balance[currency].get('free', 0)),
                    'used': float(balance[currency].get('used', 0)),
                    'total': float(balance[currency].get('total', 0))
                }

        return jsonify({
            'exchange': exchange_id,
            'balances': main_balances
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange/positions', methods=['GET'])
def get_exchange_positions():
    """获取持仓信息"""
    exchange_id = request.args.get('exchange', 'binance')
    symbol = request.args.get('symbol', None)

    if not exchange_manager:
        return jsonify({'error': '交易所未初始化'}), 400

    try:
        exchange = exchange_manager.get_exchange(exchange_id)
        if not exchange:
            return jsonify({'error': f'交易所{exchange_id}未连接'}), 400

        positions = exchange.fetch_positions(symbol)

        # 格式化持仓数据
        formatted_positions = []
        for pos in positions:
            formatted_positions.append({
                'symbol': pos.get('symbol'),
                'side': pos.get('side'),
                'contracts': float(pos.get('contracts', 0)),
                'entry_price': float(pos.get('entryPrice', 0)),
                'unrealized_pnl': float(pos.get('unrealizedPnl', 0)),
                'leverage': int(pos.get('leverage', 1))
            })

        return jsonify({
            'exchange': exchange_id,
            'positions': formatted_positions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange/execute', methods=['POST'])
def execute_live_trade():
    """执行实盘交易信号"""
    if not live_executor:
        return jsonify({'error': '实盘执行器未初始化'}), 400

    try:
        data = request.json
        exchange_id = data.get('exchange', 'binance')
        symbol = data.get('symbol', 'BTC/USDT')
        signal = data.get('signal')

        if not signal:
            return jsonify({'error': '缺少交易信号'}), 400

        # 执行交易
        result = live_executor.execute_signal(exchange_id, symbol, signal)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange/history', methods=['GET'])
def get_trade_history():
    """获取交易历史"""
    if not live_executor:
        return jsonify({'trades': [], 'total': 0})

    try:
        summary = live_executor.get_trade_summary()
        return jsonify({
            'total_trades': summary['total_trades'],
            'recent_trades': summary['recent_trades']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exchange/dry-run', methods=['POST'])
def toggle_dry_run():
    """切换模拟/实盘模式"""
    global live_executor

    if not live_executor:
        return jsonify({'error': '实盘执行器未初始化'}), 400

    try:
        data = request.json
        dry_run = data.get('dry_run', True)

        live_executor.dry_run = dry_run

        return jsonify({
            'success': True,
            'dry_run': dry_run,
            'message': f'已切换到{"模拟" if dry_run else "实盘"}模式'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ 调度管理函数 ============

def execute_model_trading(model_id):
    """执行指定模型的交易周期（由调度器调用）"""
    try:
        if model_id in trading_engines:
            print(f"[SCHEDULER] Executing trading cycle for model {model_id}")
            result = trading_engines[model_id].execute_trading_cycle()
            if result['success']:
                print(f"[SCHEDULER] Model {model_id} trading cycle completed successfully")
            else:
                print(f"[SCHEDULER] Model {model_id} trading cycle failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"[SCHEDULER] Model {model_id} not found in trading engines")
    except Exception as e:
        print(f"[SCHEDULER] Error executing trading cycle for model {model_id}: {e}")

def add_model_job(model_id, interval_minutes):
    """为模型添加定时任务"""
    try:
        # 如果该模型已有任务，先移除
        if model_id in model_jobs:
            remove_model_job(model_id)

        # 创建新的定时任务
        job = scheduler.add_job(
            func=execute_model_trading,
            trigger=IntervalTrigger(minutes=interval_minutes),
            args=[model_id],
            id=f'model_{model_id}',
            replace_existing=True,
            max_instances=1  # 防止任务重叠
        )

        model_jobs[model_id] = job.id
        print(f"[SCHEDULER] Added job for model {model_id} with interval {interval_minutes} minutes")
        return True
    except Exception as e:
        print(f"[SCHEDULER] Error adding job for model {model_id}: {e}")
        return False

def remove_model_job(model_id):
    """移除模型的定时任务"""
    try:
        if model_id in model_jobs:
            job_id = model_jobs[model_id]
            scheduler.remove_job(job_id)
            del model_jobs[model_id]
            print(f"[SCHEDULER] Removed job for model {model_id}")
            return True
        return False
    except Exception as e:
        print(f"[SCHEDULER] Error removing job for model {model_id}: {e}")
        return False

if __name__ == '__main__':
    import webbrowser
    import os

    print("\n" + "=" * 60)
    print("AITradeGame - Starting...")
    print("=" * 60)
    print("[INFO] Initializing database...")

    db.init_db()

    print("[INFO] Database initialized")
    print("[INFO] Initializing trading engines...")

    init_trading_engines()

    # 启动调度器
    print("[INFO] Starting scheduler...")
    scheduler.start()
    print("[OK] Scheduler started - models will execute on their configured intervals")

    # 初始化实盘交易
    print("[INFO] Initializing live trading...")
    try:
        config_file = 'exchange_config.json'
        if os.path.exists(config_file):
            exchange_manager = ExchangeManager(config_file)

            # 加载风险配置
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            risk_config = config.get('trading_config', {})

            live_executor = LiveTradeExecutor(exchange_manager, risk_config, dry_run=True)
            print(f"[INFO] Live trading initialized ({len(exchange_manager.list_exchanges())} exchanges)")
        else:
            print("[INFO] No exchange config found, live trading disabled")
    except Exception as e:
        print(f"[WARN] Live trading init failed: {e}")

    # 旧的统一交易循环已被替换为per-model scheduler
    # if auto_trading:
    #     trading_thread = threading.Thread(target=trading_loop, daemon=True)
    #     trading_thread.start()
    #     print("[INFO] Auto-trading enabled")

    print("\n" + "=" * 60)
    print("AITradeGame is running!")
    print("Server: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")
    
    # 自动打开浏览器
    def open_browser():
        time.sleep(1.5)  # 等待服务器启动
        url = "http://localhost:5000"
        try:
            webbrowser.open(url)
            print(f"[INFO] Browser opened: {url}")
        except Exception as e:
            print(f"[WARN] Could not open browser: {e}")
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
