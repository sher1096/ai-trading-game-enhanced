# AI Trading System Enhancement - Technical Design Document

## 文档版本
- **版本**: 1.0
- **日期**: 2025-01-18
- **作者**: Claude Code
- **状态**: 设计阶段

---

## 1. Executive Summary (执行摘要)

### 1.1 当前系统限制

当前的 AI 交易系统存在以下核心限制：

1. **硬编码币种限制**: 仅支持 6 个固定币种 (BTC, ETH, SOL, BNB, XRP, DOGE)
2. **单一数据源**: 仅依赖 CoinGecko API，存在速率限制和数据延迟
3. **缺乏可视化**: 无图表展示，仅有基础 HTML 表格
4. **无回测功能**: 无法对历史数据进行策略回测
5. **数据获取有限**: 仅有基础价格和技术指标，缺少深度市场数据

### 1.2 提议的增强功能

本设计文档提出以下核心增强：

1. **动态币种管理系统**
   - 数据库驱动的币种配置
   - 币种分组管理 (DeFi, Layer1, Layer2, Meme, Stablecoins)
   - 每个模型独立的币种池选择

2. **多数据源集成**
   - Binance API (主流币种，高流动性数据)
   - OKX API (衍生品，期权，小市值币种)
   - 统一数据聚合层，支持故障转移

3. **数据可视化系统**
   - TradingView Lightweight Charts 集成
   - 实时 K 线图表
   - 持仓和收益可视化

4. **回测系统**
   - 历史数据回放
   - 策略性能评估
   - 多维度指标报告

### 1.3 预期收益

- **灵活性提升**: 支持 100+ 币种，可动态添加/移除
- **数据质量**: 多源数据，降低单点故障风险
- **用户体验**: 专业级图表，直观的数据展示
- **策略优化**: 回测功能助力策略迭代

---

## 2. System Architecture (系统架构)

### 2.1 当前架构

```
┌─────────────────┐
│   Flask App     │
│   (app.py)      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────────┐
│ DB   │  │ CoinGecko │
│(SQLite)│  │   API     │
└──────┘  └───────────┘

固定币种: ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']
```

**限制**:
- 硬编码币种列表
- 单一数据源
- 无缓存层
- 无数据聚合

### 2.2 提议架构

```
┌───────────────────────────────────────────────────┐
│              Flask Application Layer              │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐│
│  │ Trading  │  │   Web    │  │  Visualization  ││
│  │  Engine  │  │   API    │  │     Module      ││
│  └──────────┘  └──────────┘  └─────────────────┘│
└───────┬───────────────┬──────────────────────────┘
        │               │
┌───────▼───────┐   ┌───▼──────────────────────┐
│  Data Layer   │   │   Frontend Layer         │
│               │   │                          │
│ ┌───────────┐ │   │ ┌──────────────────────┐│
│ │ Multi-    │ │   │ │ TradingView          ││
│ │ Source    │ │   │ │ Lightweight Charts   ││
│ │ Aggregator│ │   │ └──────────────────────┘│
│ └─────┬─────┘ │   │                          │
│       │       │   │ ┌──────────────────────┐│
│   ┌───┴────┐  │   │ │ Dashboard UI         ││
│   │ Cache  │  │   │ └──────────────────────┘│
│   │ Layer  │  │   └──────────────────────────┘
│   └────────┘  │
│               │
│ ┌───────────┐ │
│ │  SQLite   │ │
│ │ Database  │ │
│ └───────────┘ │
└───────────────┘
        │
        │
┌───────┴──────────────────────────────────┐
│         External Data Sources            │
│                                          │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐│
│  │ Binance │  │   OKX   │  │CoinGecko ││
│  │   API   │  │   API   │  │   API    ││
│  └─────────┘  └─────────┘  └──────────┘│
└──────────────────────────────────────────┘
```

**核心组件**:

1. **Multi-Source Data Aggregator (多源数据聚合器)**
   - 统一接口封装不同数据源
   - 智能路由：根据币种和数据类型选择最佳源
   - 故障转移和降级策略

2. **Cache Layer (缓存层)**
   - Redis: 热数据 (最近 7 天，TTL 5-60 秒)
   - SQLite: 温数据 (3 个月历史数据)
   - 可选 S3/OSS: 冷数据归档

3. **Dynamic Coin Management (动态币种管理)**
   - 数据库驱动的币种配置
   - 分组和标签系统
   - 每个模型独立币种池

4. **Visualization Module (可视化模块)**
   - TradingView Lightweight Charts
   - 实时数据流
   - 历史数据回放

---

## 3. Database Design (数据库设计)

### 3.1 新增表结构

#### 3.1.1 `coins` 表 (币种主表)

```sql
CREATE TABLE coins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20) NOT NULL UNIQUE,          -- 例如: BTC, ETH
    name VARCHAR(100) NOT NULL,                   -- 例如: Bitcoin, Ethereum
    category VARCHAR(50),                         -- 例如: Layer1, DeFi, Meme
    is_active BOOLEAN DEFAULT 1,                  -- 是否启用
    binance_symbol VARCHAR(20),                   -- Binance 交易对: BTCUSDT
    okx_symbol VARCHAR(20),                       -- OKX 交易对: BTC-USDT
    coingecko_id VARCHAR(50),                     -- CoinGecko ID: bitcoin
    market_cap_rank INTEGER,                      -- 市值排名
    notes TEXT,                                   -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_coins_symbol ON coins(symbol);
CREATE INDEX idx_coins_category ON coins(category);
CREATE INDEX idx_coins_is_active ON coins(is_active);
```

**示例数据**:
```sql
INSERT INTO coins (symbol, name, category, binance_symbol, okx_symbol, coingecko_id, market_cap_rank)
VALUES
('BTC', 'Bitcoin', 'Layer1', 'BTCUSDT', 'BTC-USDT', 'bitcoin', 1),
('ETH', 'Ethereum', 'Layer1', 'ETHUSDT', 'ETH-USDT', 'ethereum', 2),
('SOL', 'Solana', 'Layer1', 'SOLUSDT', 'SOL-USDT', 'solana', 5),
('UNI', 'Uniswap', 'DeFi', 'UNIUSDT', 'UNI-USDT', 'uniswap', 18),
('DOGE', 'Dogecoin', 'Meme', 'DOGEUSDT', 'DOGE-USDT', 'dogecoin', 10);
```

#### 3.1.2 `coin_groups` 表 (币种分组)

```sql
CREATE TABLE coin_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,             -- 例如: Top10, DeFi, Meme
    description TEXT,                             -- 分组描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 示例数据
INSERT INTO coin_groups (name, description) VALUES
('Top10', '市值前 10 的主流币种'),
('DeFi', 'DeFi 生态币种'),
('Layer1', 'Layer1 公链'),
('Layer2', 'Layer2 扩容方案'),
('Meme', 'Meme 币种');
```

#### 3.1.3 `coin_group_members` 表 (分组成员关系)

```sql
CREATE TABLE coin_group_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    coin_id INTEGER NOT NULL,
    sort_order INTEGER DEFAULT 0,                 -- 排序权重
    FOREIGN KEY (group_id) REFERENCES coin_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (coin_id) REFERENCES coins(id) ON DELETE CASCADE,
    UNIQUE(group_id, coin_id)
);

CREATE INDEX idx_cgm_group ON coin_group_members(group_id);
CREATE INDEX idx_cgm_coin ON coin_group_members(coin_id);
```

#### 3.1.4 `model_coin_pools` 表 (模型币种池)

```sql
CREATE TABLE model_coin_pools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    coin_id INTEGER NOT NULL,
    is_enabled BOOLEAN DEFAULT 1,                 -- 是否启用该币种
    weight REAL DEFAULT 1.0,                      -- 权重（可用于资金分配）
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    FOREIGN KEY (coin_id) REFERENCES coins(id) ON DELETE CASCADE,
    UNIQUE(model_id, coin_id)
);

CREATE INDEX idx_mcp_model ON model_coin_pools(model_id);
CREATE INDEX idx_mcp_coin ON model_coin_pools(coin_id);
```

#### 3.1.5 `market_data_cache` 表 (市场数据缓存)

```sql
CREATE TABLE market_data_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coin_id INTEGER NOT NULL,
    data_type VARCHAR(50) NOT NULL,               -- price, kline_1m, kline_5m, depth
    data_source VARCHAR(50) NOT NULL,             -- binance, okx, coingecko
    data_json TEXT NOT NULL,                      -- JSON 格式的数据
    timestamp TIMESTAMP NOT NULL,                 -- 数据时间戳
    expires_at TIMESTAMP NOT NULL,                -- 过期时间
    FOREIGN KEY (coin_id) REFERENCES coins(id) ON DELETE CASCADE
);

CREATE INDEX idx_mdc_coin_type ON market_data_cache(coin_id, data_type);
CREATE INDEX idx_mdc_expires ON market_data_cache(expires_at);
```

### 3.2 现有表修改

#### 3.2.1 `trades` 表 - 添加币种外键

```sql
-- 添加列
ALTER TABLE trades ADD COLUMN coin_id INTEGER;

-- 创建外键（需要重建表，SQLite 不支持直接添加外键）
-- 迁移时需要特殊处理
```

#### 3.2.2 `positions` 表 - 添加币种外键

```sql
-- 添加列
ALTER TABLE positions ADD COLUMN coin_id INTEGER;
```

### 3.3 数据迁移策略

```python
def migrate_to_dynamic_coins(db):
    """
    迁移现有硬编码币种到新的 coins 表
    """
    # 步骤 1: 创建新表
    db.execute("""CREATE TABLE coins ...""")

    # 步骤 2: 插入现有币种
    existing_coins = [
        ('BTC', 'Bitcoin', 'Layer1', 'BTCUSDT', 'BTC-USDT', 'bitcoin', 1),
        ('ETH', 'Ethereum', 'Layer1', 'ETHUSDT', 'ETH-USDT', 'ethereum', 2),
        ('SOL', 'Solana', 'Layer1', 'SOLUSDT', 'SOL-USDT', 'solana', 5),
        ('BNB', 'BNB', 'Exchange', 'BNBUSDT', 'BNB-USDT', 'binancecoin', 4),
        ('XRP', 'Ripple', 'Payment', 'XRPUSDT', 'XRP-USDT', 'ripple', 6),
        ('DOGE', 'Dogecoin', 'Meme', 'DOGEUSDT', 'DOGE-USDT', 'dogecoin', 10)
    ]
    for coin in existing_coins:
        db.execute("INSERT INTO coins (...) VALUES (...)", coin)

    # 步骤 3: 将所有现有模型关联到这 6 个币种
    models = db.execute("SELECT id FROM models").fetchall()
    for model in models:
        for coin_id in range(1, 7):  # 假设币种 ID 1-6
            db.execute("""
                INSERT INTO model_coin_pools (model_id, coin_id, is_enabled)
                VALUES (?, ?, 1)
            """, (model['id'], coin_id))

    # 步骤 4: 更新 trades 和 positions 表
    # 将 coin symbol 转换为 coin_id
    db.execute("""
        UPDATE trades
        SET coin_id = (SELECT id FROM coins WHERE symbol = trades.coin)
    """)

    db.execute("""
        UPDATE positions
        SET coin_id = (SELECT id FROM coins WHERE symbol = positions.coin)
    """)
```

---

## 4. Data Source Integration (数据源集成)

### 4.1 Binance API 集成

#### 4.1.1 API 特性

- **速率限制**: 6,000 weight/分钟 (IP 级别)
- **WebSocket**: 5 消息/秒，1,024 流/连接
- **推荐 SDK**: `python-binance` (7,000+ stars)

#### 4.1.2 数据类型

| 数据类型 | REST Endpoint | WebSocket Stream | 权重 | 更新频率 |
|---------|---------------|------------------|------|----------|
| 实时价格 | /api/v3/ticker/price | <symbol>@trade | 2 | 实时 |
| K线数据 | /api/v3/klines | <symbol>@kline_<interval> | 2 | 实时 |
| 深度数据 | /api/v3/depth | <symbol>@depth | 10-50 | 实时 |
| 24h统计 | /api/v3/ticker/24hr | <symbol>@ticker | 2 | 1秒 |

#### 4.1.3 实现代码

```python
from binance.client import Client
from binance.streams import ThreadedWebsocketManager

class BinanceDataFetcher:
    def __init__(self, api_key=None, api_secret=None):
        """
        api_key 和 api_secret 可选，仅在需要交易或私有数据时提供
        """
        self.client = Client(api_key, api_secret)
        self.wsm = None  # WebSocket Manager

    def get_current_price(self, symbol: str) -> float:
        """获取当前价格"""
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])

    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100):
        """
        获取 K 线数据
        interval: 1m, 5m, 15m, 1h, 4h, 1d, 1w
        """
        klines = self.client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        # 转换为标准格式
        return [{
            'timestamp': k[0],
            'open': float(k[1]),
            'high': float(k[2]),
            'low': float(k[3]),
            'close': float(k[4]),
            'volume': float(k[5])
        } for k in klines]

    def get_orderbook(self, symbol: str, limit: int = 100):
        """获取订单簿"""
        depth = self.client.get_order_book(symbol=symbol, limit=limit)
        return {
            'bids': [[float(p), float(q)] for p, q in depth['bids']],
            'asks': [[float(p), float(q)] for p, q in depth['asks']]
        }

    def start_websocket_price_stream(self, symbols: list, callback):
        """
        启动 WebSocket 实时价格流
        symbols: ['BTCUSDT', 'ETHUSDT']
        callback: 回调函数 callback(msg)
        """
        if not self.wsm:
            self.wsm = ThreadedWebsocketManager()
            self.wsm.start()

        # 订阅多个币种的交易流
        streams = [f"{s.lower()}@trade" for s in symbols]
        self.wsm.start_multiplex_socket(
            callback=callback,
            streams=streams
        )

    def stop_websocket(self):
        if self.wsm:
            self.wsm.stop()
```

### 4.2 OKX API 集成

#### 4.2.1 API 特性

- **速率限制**: 3 请求/秒 (更简单的限流)
- **产品类型**: SPOT, MARGIN, SWAP, FUTURES, OPTION
- **推荐 SDK**: `python-okx` 或 `okx-sdk`

#### 4.2.2 实现代码

```python
import okx.MarketData as MarketAPI

class OKXDataFetcher:
    def __init__(self, api_key=None, secret_key=None, passphrase=None):
        """
        公开数据不需要认证
        """
        self.market_api = MarketAPI.MarketAPI(
            api_key=api_key or "",
            api_secret_key=secret_key or "",
            passphrase=passphrase or "",
            flag='0'  # 0: 实盘, 1: 模拟盘
        )

    def get_current_price(self, inst_id: str) -> float:
        """
        获取当前价格
        inst_id: BTC-USDT, ETH-USDT
        """
        result = self.market_api.get_ticker(instId=inst_id)
        if result['code'] == '0':
            return float(result['data'][0]['last'])
        return 0.0

    def get_klines(self, inst_id: str, bar: str = '1H', limit: int = 100):
        """
        获取 K 线数据
        bar: 1m, 5m, 15m, 1H, 4H, 1D
        """
        result = self.market_api.get_candlesticks(
            instId=inst_id,
            bar=bar,
            limit=str(limit)
        )

        if result['code'] == '0':
            return [{
                'timestamp': int(k[0]),
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5])
            } for k in result['data']]
        return []
```

### 4.3 统一数据聚合器

```python
class MultiSourceDataAggregator:
    """
    统一多个数据源的聚合器
    """
    def __init__(self, db):
        self.db = db
        self.binance = BinanceDataFetcher()
        self.okx = OKXDataFetcher()
        self.coingecko = MarketDataFetcher()  # 现有的

        # 数据源优先级配置
        self.source_priority = {
            'price': ['binance', 'okx', 'coingecko'],
            'klines': ['binance', 'okx'],
            'depth': ['binance', 'okx']
        }

    def get_coin_config(self, coin_symbol: str):
        """从数据库获取币种配置"""
        return self.db.execute("""
            SELECT * FROM coins WHERE symbol = ?
        """, (coin_symbol,)).fetchone()

    def get_current_price(self, coin_symbol: str) -> float:
        """
        智能获取价格：尝试多个数据源，直到成功
        """
        coin = self.get_coin_config(coin_symbol)
        if not coin:
            raise ValueError(f"Coin {coin_symbol} not found")

        for source in self.source_priority['price']:
            try:
                if source == 'binance' and coin['binance_symbol']:
                    price = self.binance.get_current_price(coin['binance_symbol'])
                    if price > 0:
                        return price

                elif source == 'okx' and coin['okx_symbol']:
                    price = self.okx.get_current_price(coin['okx_symbol'])
                    if price > 0:
                        return price

                elif source == 'coingecko' and coin['coingecko_id']:
                    data = self.coingecko.get_price(coin['coingecko_id'])
                    return data['price']

            except Exception as e:
                print(f"[WARNING] Failed to get price from {source}: {e}")
                continue

        raise Exception(f"Failed to get price for {coin_symbol} from all sources")

    def get_klines(self, coin_symbol: str, interval: str = '1h', limit: int = 100):
        """智能获取 K 线数据"""
        coin = self.get_coin_config(coin_symbol)
        if not coin:
            raise ValueError(f"Coin {coin_symbol} not found")

        # 优先使用 Binance (数据质量更好)
        if coin['binance_symbol']:
            try:
                return self.binance.get_klines(
                    coin['binance_symbol'],
                    interval=interval,
                    limit=limit
                )
            except Exception as e:
                print(f"[WARNING] Binance klines failed: {e}")

        # 降级到 OKX
        if coin['okx_symbol']:
            try:
                # 转换时间间隔格式 (1h -> 1H)
                okx_interval = interval.upper()
                return self.okx.get_klines(
                    coin['okx_symbol'],
                    bar=okx_interval,
                    limit=limit
                )
            except Exception as e:
                print(f"[WARNING] OKX klines failed: {e}")

        return []

    def get_market_state_for_model(self, model_id: int):
        """
        获取模型的市场状态（仅获取该模型关注的币种）
        """
        # 获取模型的币种池
        coins = self.db.execute("""
            SELECT c.* FROM coins c
            JOIN model_coin_pools mcp ON c.id = mcp.coin_id
            WHERE mcp.model_id = ? AND mcp.is_enabled = 1
        """, (model_id,)).fetchall()

        market_state = {}
        for coin in coins:
            try:
                price = self.get_current_price(coin['symbol'])
                market_state[coin['symbol']] = {
                    'price': price,
                    'coin_id': coin['id'],
                    'name': coin['name']
                }
            except Exception as e:
                print(f"[ERROR] Failed to get price for {coin['symbol']}: {e}")

        return market_state
```

### 4.4 缓存策略

```python
import json
from datetime import datetime, timedelta

class DataCache:
    """
    数据缓存层（基于 SQLite，可扩展到 Redis）
    """
    def __init__(self, db):
        self.db = db

    def get_cached_data(self, coin_id: int, data_type: str, max_age_seconds: int = 60):
        """
        从缓存获取数据
        data_type: 'price', 'kline_1m', 'kline_1h', 'depth'
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=max_age_seconds)

        result = self.db.execute("""
            SELECT data_json, timestamp FROM market_data_cache
            WHERE coin_id = ? AND data_type = ? AND timestamp > ?
            ORDER BY timestamp DESC LIMIT 1
        """, (coin_id, data_type, cutoff)).fetchone()

        if result:
            return json.loads(result['data_json'])
        return None

    def set_cached_data(self, coin_id: int, data_type: str, data: dict,
                        data_source: str, ttl_seconds: int = 60):
        """设置缓存数据"""
        now = datetime.now()
        expires = now + timedelta(seconds=ttl_seconds)

        self.db.execute("""
            INSERT INTO market_data_cache
            (coin_id, data_type, data_source, data_json, timestamp, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (coin_id, data_type, data_source, json.dumps(data), now, expires))

        self.db.commit()

    def cleanup_expired(self):
        """清理过期缓存"""
        self.db.execute("""
            DELETE FROM market_data_cache WHERE expires_at < ?
        """, (datetime.now(),))
        self.db.commit()
```

---

## 5. Dynamic Coin Management (动态币种管理)

### 5.1 后端 API 设计

#### 5.1.1 币种管理 API

```python
# app.py 新增路由

@app.route('/api/coins', methods=['GET'])
def get_coins():
    """获取所有币种列表"""
    category = request.args.get('category')
    is_active = request.args.get('is_active', '1')

    query = "SELECT * FROM coins WHERE is_active = ?"
    params = [int(is_active)]

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY market_cap_rank ASC"

    coins = db.execute(query, params).fetchall()
    return jsonify([dict(c) for c in coins])

@app.route('/api/coins', methods=['POST'])
def add_coin():
    """添加新币种"""
    data = request.json

    required = ['symbol', 'name']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        cursor = db.execute("""
            INSERT INTO coins
            (symbol, name, category, binance_symbol, okx_symbol, coingecko_id, market_cap_rank)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['symbol'],
            data['name'],
            data.get('category'),
            data.get('binance_symbol'),
            data.get('okx_symbol'),
            data.get('coingecko_id'),
            data.get('market_cap_rank')
        ))
        db.commit()

        return jsonify({'id': cursor.lastrowid, 'message': 'Coin added'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/coins/<int:coin_id>', methods=['PUT'])
def update_coin(coin_id):
    """更新币种信息"""
    data = request.json

    # 构建动态更新语句
    fields = []
    values = []

    for field in ['name', 'category', 'binance_symbol', 'okx_symbol',
                  'coingecko_id', 'market_cap_rank', 'is_active']:
        if field in data:
            fields.append(f"{field} = ?")
            values.append(data[field])

    if not fields:
        return jsonify({'error': 'No fields to update'}), 400

    values.append(coin_id)
    query = f"UPDATE coins SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"

    db.execute(query, values)
    db.commit()

    return jsonify({'message': 'Coin updated'})

@app.route('/api/coins/<int:coin_id>', methods=['DELETE'])
def delete_coin(coin_id):
    """删除币种（软删除）"""
    db.execute("UPDATE coins SET is_active = 0 WHERE id = ?", (coin_id,))
    db.commit()
    return jsonify({'message': 'Coin deactivated'})
```

#### 5.1.2 模型币种池 API

```python
@app.route('/api/models/<int:model_id>/coins', methods=['GET'])
def get_model_coins(model_id):
    """获取模型的币种池"""
    coins = db.execute("""
        SELECT c.*, mcp.is_enabled, mcp.weight
        FROM coins c
        JOIN model_coin_pools mcp ON c.id = mcp.coin_id
        WHERE mcp.model_id = ?
        ORDER BY c.symbol
    """, (model_id,)).fetchall()

    return jsonify([dict(c) for c in coins])

@app.route('/api/models/<int:model_id>/coins', methods=['POST'])
def add_model_coin(model_id):
    """为模型添加币种"""
    data = request.json
    coin_id = data.get('coin_id')

    if not coin_id:
        return jsonify({'error': 'coin_id required'}), 400

    try:
        db.execute("""
            INSERT INTO model_coin_pools (model_id, coin_id, is_enabled, weight)
            VALUES (?, ?, ?, ?)
        """, (model_id, coin_id, data.get('is_enabled', 1), data.get('weight', 1.0)))
        db.commit()

        return jsonify({'message': 'Coin added to model'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/coins/<int:coin_id>', methods=['PUT'])
def update_model_coin(model_id, coin_id):
    """更新模型币种配置"""
    data = request.json

    db.execute("""
        UPDATE model_coin_pools
        SET is_enabled = ?, weight = ?
        WHERE model_id = ? AND coin_id = ?
    """, (data.get('is_enabled', 1), data.get('weight', 1.0), model_id, coin_id))
    db.commit()

    return jsonify({'message': 'Model coin config updated'})

@app.route('/api/models/<int:model_id>/coins/<int:coin_id>', methods=['DELETE'])
def remove_model_coin(model_id, coin_id):
    """从模型移除币种"""
    db.execute("""
        DELETE FROM model_coin_pools
        WHERE model_id = ? AND coin_id = ?
    """, (model_id, coin_id))
    db.commit()

    return jsonify({'message': 'Coin removed from model'})
```

#### 5.1.3 币种分组 API

```python
@app.route('/api/coin-groups', methods=['GET'])
def get_coin_groups():
    """获取所有币种分组"""
    groups = db.execute("SELECT * FROM coin_groups ORDER BY name").fetchall()

    result = []
    for group in groups:
        coins = db.execute("""
            SELECT c.* FROM coins c
            JOIN coin_group_members cgm ON c.id = cgm.coin_id
            WHERE cgm.group_id = ?
            ORDER BY cgm.sort_order, c.symbol
        """, (group['id'],)).fetchall()

        result.append({
            'id': group['id'],
            'name': group['name'],
            'description': group['description'],
            'coins': [dict(c) for c in coins]
        })

    return jsonify(result)

@app.route('/api/models/<int:model_id>/add-group/<int:group_id>', methods=['POST'])
def add_group_to_model(model_id, group_id):
    """将整个分组的币种添加到模型"""
    # 获取分组的所有币种
    coins = db.execute("""
        SELECT coin_id FROM coin_group_members
        WHERE group_id = ?
    """, (group_id,)).fetchall()

    added = 0
    for coin in coins:
        try:
            db.execute("""
                INSERT OR IGNORE INTO model_coin_pools (model_id, coin_id, is_enabled)
                VALUES (?, ?, 1)
            """, (model_id, coin['coin_id']))
            added += 1
        except:
            pass

    db.commit()
    return jsonify({'message': f'Added {added} coins from group'})
```

### 5.2 前端 UI 设计

#### 5.2.1 币种管理页面

```html
<!-- templates/coin_management.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Coin Management</title>
    <style>
        .coin-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }

        .coin-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: white;
        }

        .coin-card.inactive {
            opacity: 0.5;
        }

        .coin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .coin-symbol {
            font-size: 20px;
            font-weight: bold;
        }

        .coin-category {
            display: inline-block;
            padding: 3px 8px;
            background: #007bff;
            color: white;
            border-radius: 4px;
            font-size: 12px;
        }

        .coin-details {
            font-size: 14px;
            color: #666;
        }

        .coin-actions {
            margin-top: 10px;
            display: flex;
            gap: 10px;
        }

        .btn {
            padding: 5px 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .btn-edit {
            background: #28a745;
            color: white;
        }

        .btn-delete {
            background: #dc3545;
            color: white;
        }

        .add-coin-form {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            display: none;
            z-index: 1000;
        }

        .add-coin-form.show {
            display: block;
        }

        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: none;
            z-index: 999;
        }

        .overlay.show {
            display: block;
        }
    </style>
</head>
<body>
    <div style="padding: 20px;">
        <h1>Coin Management</h1>

        <div style="margin-bottom: 20px;">
            <button class="btn btn-add" onclick="showAddCoinForm()">+ Add New Coin</button>

            <select id="categoryFilter" onchange="filterCoins()">
                <option value="">All Categories</option>
                <option value="Layer1">Layer1</option>
                <option value="DeFi">DeFi</option>
                <option value="Meme">Meme</option>
                <option value="Layer2">Layer2</option>
            </select>

            <label>
                <input type="checkbox" id="showInactive" onchange="filterCoins()">
                Show Inactive
            </label>
        </div>

        <div class="coin-list" id="coinList">
            <!-- Coins will be loaded here -->
        </div>
    </div>

    <!-- Add/Edit Coin Form -->
    <div class="overlay" id="overlay" onclick="hideAddCoinForm()"></div>
    <div class="add-coin-form" id="addCoinForm">
        <h2>Add New Coin</h2>
        <form onsubmit="saveCoin(event)">
            <div style="margin-bottom: 10px;">
                <label>Symbol *</label><br>
                <input type="text" id="coinSymbol" required style="width: 100%;">
            </div>

            <div style="margin-bottom: 10px;">
                <label>Name *</label><br>
                <input type="text" id="coinName" required style="width: 100%;">
            </div>

            <div style="margin-bottom: 10px;">
                <label>Category</label><br>
                <select id="coinCategory" style="width: 100%;">
                    <option value="">Select...</option>
                    <option value="Layer1">Layer1</option>
                    <option value="DeFi">DeFi</option>
                    <option value="Meme">Meme</option>
                    <option value="Layer2">Layer2</option>
                </select>
            </div>

            <div style="margin-bottom: 10px;">
                <label>Binance Symbol</label><br>
                <input type="text" id="binanceSymbol" placeholder="e.g., BTCUSDT" style="width: 100%;">
            </div>

            <div style="margin-bottom: 10px;">
                <label>OKX Symbol</label><br>
                <input type="text" id="okxSymbol" placeholder="e.g., BTC-USDT" style="width: 100%;">
            </div>

            <div style="margin-bottom: 10px;">
                <label>CoinGecko ID</label><br>
                <input type="text" id="coingeckoId" placeholder="e.g., bitcoin" style="width: 100%;">
            </div>

            <div style="margin-top: 20px;">
                <button type="submit" class="btn btn-edit">Save</button>
                <button type="button" class="btn btn-delete" onclick="hideAddCoinForm()">Cancel</button>
            </div>
        </form>
    </div>

    <script>
        let allCoins = [];

        async function loadCoins() {
            const response = await fetch('/api/coins?is_active=1');
            allCoins = await response.json();
            renderCoins();
        }

        function renderCoins() {
            const category = document.getElementById('categoryFilter').value;
            const showInactive = document.getElementById('showInactive').checked;

            let filtered = allCoins;

            if (category) {
                filtered = filtered.filter(c => c.category === category);
            }

            if (!showInactive) {
                filtered = filtered.filter(c => c.is_active === 1);
            }

            const html = filtered.map(coin => `
                <div class="coin-card ${coin.is_active ? '' : 'inactive'}">
                    <div class="coin-header">
                        <div>
                            <span class="coin-symbol">${coin.symbol}</span>
                            ${coin.category ? `<span class="coin-category">${coin.category}</span>` : ''}
                        </div>
                    </div>
                    <div class="coin-details">
                        <div><strong>${coin.name}</strong></div>
                        <div>Rank: #${coin.market_cap_rank || 'N/A'}</div>
                        <div>Binance: ${coin.binance_symbol || 'N/A'}</div>
                        <div>OKX: ${coin.okx_symbol || 'N/A'}</div>
                    </div>
                    <div class="coin-actions">
                        <button class="btn btn-edit" onclick="editCoin(${coin.id})">Edit</button>
                        <button class="btn btn-delete" onclick="deleteCoin(${coin.id})">Delete</button>
                    </div>
                </div>
            `).join('');

            document.getElementById('coinList').innerHTML = html;
        }

        function filterCoins() {
            renderCoins();
        }

        function showAddCoinForm() {
            document.getElementById('overlay').classList.add('show');
            document.getElementById('addCoinForm').classList.add('show');
        }

        function hideAddCoinForm() {
            document.getElementById('overlay').classList.remove('show');
            document.getElementById('addCoinForm').classList.remove('show');
        }

        async function saveCoin(event) {
            event.preventDefault();

            const data = {
                symbol: document.getElementById('coinSymbol').value.toUpperCase(),
                name: document.getElementById('coinName').value,
                category: document.getElementById('coinCategory').value,
                binance_symbol: document.getElementById('binanceSymbol').value,
                okx_symbol: document.getElementById('okxSymbol').value,
                coingecko_id: document.getElementById('coingeckoId').value
            };

            const response = await fetch('/api/coins', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            if (response.ok) {
                alert('Coin added successfully!');
                hideAddCoinForm();
                loadCoins();
            } else {
                const error = await response.json();
                alert('Error: ' + error.error);
            }
        }

        async function deleteCoin(coinId) {
            if (!confirm('Are you sure you want to deactivate this coin?')) return;

            await fetch(`/api/coins/${coinId}`, {method: 'DELETE'});
            loadCoins();
        }

        // 初始加载
        loadCoins();
    </script>
</body>
</html>
```

#### 5.2.2 模型币种选择页面

```html
<!-- templates/model_coins.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Model Coin Selection - Model {{ model_id }}</title>
    <style>
        .coin-selector {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }

        .available-coins, .selected-coins {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: white;
        }

        .coin-item {
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #eee;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .coin-item:hover {
            background: #f8f9fa;
        }

        .quick-add-groups {
            margin-bottom: 20px;
            padding: 15px;
            background: #e9ecef;
            border-radius: 8px;
        }

        .group-btn {
            margin: 5px;
            padding: 8px 15px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .group-btn:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div style="padding: 20px;">
        <h1>Coin Selection for Model {{ model_id }}</h1>

        <div class="quick-add-groups">
            <h3>Quick Add Groups:</h3>
            <button class="group-btn" onclick="addGroup('Top10')">Top 10</button>
            <button class="group-btn" onclick="addGroup('DeFi')">DeFi</button>
            <button class="group-btn" onclick="addGroup('Layer1')">Layer1</button>
            <button class="group-btn" onclick="addGroup('Meme')">Meme</button>
        </div>

        <div class="coin-selector">
            <div class="available-coins">
                <h3>Available Coins</h3>
                <input type="text" id="searchCoins" placeholder="Search..."
                       onkeyup="searchCoins()" style="width: 100%; margin-bottom: 10px;">
                <div id="availableCoinList"></div>
            </div>

            <div class="selected-coins">
                <h3>Selected Coins ({{ selected_count }})</h3>
                <div id="selectedCoinList"></div>
            </div>
        </div>
    </div>

    <script>
        const modelId = {{ model_id }};
        let allCoins = [];
        let selectedCoins = [];

        async function loadData() {
            // 加载所有币种
            const coinsResp = await fetch('/api/coins');
            allCoins = await coinsResp.json();

            // 加载模型已选币种
            const selectedResp = await fetch(`/api/models/${modelId}/coins`);
            selectedCoins = await selectedResp.json();

            renderCoins();
        }

        function renderCoins() {
            const selectedIds = new Set(selectedCoins.map(c => c.id));

            // 未选中的币种
            const available = allCoins.filter(c => !selectedIds.has(c.id) && c.is_active);

            document.getElementById('availableCoinList').innerHTML = available.map(coin => `
                <div class="coin-item">
                    <span><strong>${coin.symbol}</strong> - ${coin.name}</span>
                    <button class="btn btn-add" onclick="addCoin(${coin.id})">+</button>
                </div>
            `).join('');

            // 已选中的币种
            document.getElementById('selectedCoinList').innerHTML = selectedCoins.map(coin => `
                <div class="coin-item">
                    <span><strong>${coin.symbol}</strong> - ${coin.name}</span>
                    <button class="btn btn-delete" onclick="removeCoin(${coin.id})">×</button>
                </div>
            `).join('');
        }

        async function addCoin(coinId) {
            await fetch(`/api/models/${modelId}/coins`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({coin_id: coinId})
            });
            loadData();
        }

        async function removeCoin(coinId) {
            await fetch(`/api/models/${modelId}/coins/${coinId}`, {method: 'DELETE'});
            loadData();
        }

        async function addGroup(groupName) {
            // 此处简化，实际需要通过 API 获取分组 ID
            alert(`Adding ${groupName} group (to be implemented)`);
        }

        function searchCoins() {
            const query = document.getElementById('searchCoins').value.toLowerCase();
            // 实现搜索过滤逻辑
        }

        loadData();
    </script>
</body>
</html>
```

### 5.3 TradingEngine 适配

```python
# trading_engine.py 修改

class TradingEngine:
    def __init__(self, model_id: int, db, data_aggregator, ai_trader,
                 trade_fee_rate: float = 0.001, live_executor=None):
        self.model_id = model_id
        self.db = db
        self.data_aggregator = data_aggregator  # 使用新的数据聚合器
        self.ai_trader = ai_trader
        self.trade_fee_rate = trade_fee_rate
        self.live_executor = live_executor

        # 不再硬编码币种，从数据库获取
        self.coins = self._load_model_coins()

    def _load_model_coins(self) -> list:
        """从数据库加载模型的币种列表"""
        coins = self.db.execute("""
            SELECT c.symbol FROM coins c
            JOIN model_coin_pools mcp ON c.id = mcp.coin_id
            WHERE mcp.model_id = ? AND mcp.is_enabled = 1 AND c.is_active = 1
            ORDER BY c.symbol
        """, (self.model_id,)).fetchall()

        return [coin['symbol'] for coin in coins]

    def _get_market_state(self) -> Dict:
        """使用新的数据聚合器获取市场状态"""
        return self.data_aggregator.get_market_state_for_model(self.model_id)
```

---

## 6. Data Visualization (数据可视化)

### 6.1 TradingView Lightweight Charts 集成

#### 6.1.1 选择理由

- **开源免费**: Apache 2.0 许可
- **轻量级**: 45 KB gzipped
- **高性能**: 支持数千根 K 线，60 FPS 渲染
- **易于集成**: 3 行代码即可启动
- **无品牌要求**: 不需要显示 TradingView 标识

#### 6.1.2 安装和基础集成

```html
<!-- templates/charts.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Trading Charts</title>
    <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        #chart-container {
            width: 100%;
            height: 600px;
            margin: 20px 0;
        }

        .chart-controls {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .interval-btn {
            margin: 0 5px;
            padding: 8px 15px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
        }

        .interval-btn.active {
            background: #007bff;
            color: white;
        }
    </style>
</head>
<body>
    <div style="padding: 20px;">
        <h1>Trading Charts</h1>

        <div class="chart-controls">
            <label>
                Coin:
                <select id="coinSelect" onchange="loadChart()">
                    <option value="BTC">Bitcoin (BTC)</option>
                    <option value="ETH">Ethereum (ETH)</option>
                    <option value="SOL">Solana (SOL)</option>
                </select>
            </label>

            <span style="margin: 0 20px;">Interval:</span>
            <button class="interval-btn active" onclick="setInterval('1m')">1m</button>
            <button class="interval-btn" onclick="setInterval('5m')">5m</button>
            <button class="interval-btn" onclick="setInterval('15m')">15m</button>
            <button class="interval-btn" onclick="setInterval('1h')">1h</button>
            <button class="interval-btn" onclick="setInterval('4h')">4h</button>
            <button class="interval-btn" onclick="setInterval('1d')">1D</button>
        </div>

        <div id="chart-container"></div>

        <div style="margin-top: 20px;">
            <h3>Trading Signals on Chart</h3>
            <label>
                <input type="checkbox" id="showSignals" onchange="toggleSignals()">
                Show AI Trading Signals
            </label>
        </div>
    </div>

    <script>
        let chart = null;
        let candlestickSeries = null;
        let markerSeries = null;
        let currentInterval = '1m';
        let currentCoin = 'BTC';

        // 初始化图表
        function initChart() {
            const container = document.getElementById('chart-container');

            chart = LightweightCharts.createChart(container, {
                width: container.clientWidth,
                height: 600,
                layout: {
                    background: { color: '#ffffff' },
                    textColor: '#333',
                },
                grid: {
                    vertLines: { color: '#e1e1e1' },
                    horzLines: { color: '#e1e1e1' },
                },
                crosshair: {
                    mode: LightweightCharts.CrosshairMode.Normal,
                },
                rightPriceScale: {
                    borderColor: '#cccccc',
                },
                timeScale: {
                    borderColor: '#cccccc',
                    timeVisible: true,
                    secondsVisible: false,
                },
            });

            candlestickSeries = chart.addCandlestickSeries({
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderVisible: false,
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
            });

            // 响应式调整
            window.addEventListener('resize', () => {
                chart.applyOptions({ width: container.clientWidth });
            });
        }

        // 加载图表数据
        async function loadChart() {
            currentCoin = document.getElementById('coinSelect').value;

            const response = await fetch(`/api/klines/${currentCoin}?interval=${currentInterval}&limit=500`);
            const data = await response.json();

            // 转换为 Lightweight Charts 格式
            const chartData = data.map(k => ({
                time: k.timestamp / 1000,  // 转换为秒
                open: k.open,
                high: k.high,
                low: k.low,
                close: k.close
            }));

            candlestickSeries.setData(chartData);

            // 加载交易信号
            if (document.getElementById('showSignals').checked) {
                loadTradingSignals();
            }
        }

        // 加载交易信号（显示为标记）
        async function loadTradingSignals() {
            const response = await fetch(`/api/models/1/trades?coin=${currentCoin}&limit=50`);
            const trades = await response.json();

            const markers = trades.map(trade => {
                let color = '#2196F3';
                let position = 'belowBar';
                let shape = 'arrowUp';

                if (trade.signal === 'buy_to_enter') {
                    color = '#26a69a';
                    position = 'belowBar';
                    shape = 'arrowUp';
                } else if (trade.signal === 'sell_to_enter') {
                    color = '#ef5350';
                    position = 'aboveBar';
                    shape = 'arrowDown';
                } else if (trade.signal === 'close_position') {
                    color = '#ff9800';
                    position = 'aboveBar';
                    shape = 'circle';
                }

                return {
                    time: new Date(trade.timestamp).getTime() / 1000,
                    position: position,
                    color: color,
                    shape: shape,
                    text: trade.signal.toUpperCase()
                };
            });

            candlestickSeries.setMarkers(markers);
        }

        function setInterval(interval) {
            currentInterval = interval;

            // 更新按钮样式
            document.querySelectorAll('.interval-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');

            loadChart();
        }

        function toggleSignals() {
            if (document.getElementById('showSignals').checked) {
                loadTradingSignals();
            } else {
                candlestickSeries.setMarkers([]);
            }
        }

        // 初始化
        initChart();
        loadChart();
    </script>
</body>
</html>
```

#### 6.1.3 后端 K 线数据 API

```python
# app.py 新增路由

@app.route('/api/klines/<coin_symbol>', methods=['GET'])
def get_klines_api(coin_symbol):
    """
    获取 K 线数据 API
    参数:
        interval: 1m, 5m, 15m, 1h, 4h, 1d
        limit: 默认 100，最大 1000
    """
    interval = request.args.get('interval', '1h')
    limit = int(request.args.get('limit', 100))

    try:
        # 使用数据聚合器获取 K 线
        klines = data_aggregator.get_klines(coin_symbol, interval, limit)
        return jsonify(klines)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/<int:model_id>/trades', methods=['GET'])
def get_model_trades_api(model_id):
    """
    获取模型的交易记录（用于图表标记）
    """
    coin = request.args.get('coin')
    limit = int(request.args.get('limit', 50))

    query = """
        SELECT t.*, c.symbol as coin
        FROM trades t
        JOIN coins c ON t.coin_id = c.id
        WHERE t.model_id = ?
    """
    params = [model_id]

    if coin:
        query += " AND c.symbol = ?"
        params.append(coin)

    query += " ORDER BY t.timestamp DESC LIMIT ?"
    params.append(limit)

    trades = db.execute(query, params).fetchall()
    return jsonify([dict(t) for t in trades])
```

### 6.2 仪表板可视化

```html
<!-- templates/dashboard_enhanced.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Trading Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 20px;
        }

        .widget {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .metric-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            margin-bottom: 10px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }

        .metric-label {
            font-size: 14px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- 总览指标 -->
        <div class="widget">
            <h3>Portfolio Overview</h3>
            <div class="metric-card">
                <div>
                    <div class="metric-label">Total Value</div>
                    <div class="metric-value" id="totalValue">$10,000</div>
                </div>
                <div class="metric-label">↑ +15.3%</div>
            </div>

            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div>
                    <div class="metric-label">Total Return</div>
                    <div class="metric-value" id="totalReturn">+$1,530</div>
                </div>
            </div>
        </div>

        <!-- 账户价值趋势图 -->
        <div class="widget">
            <h3>Account Value Trend</h3>
            <canvas id="valueChart"></canvas>
        </div>

        <!-- 持仓分布饼图 -->
        <div class="widget">
            <h3>Position Distribution</h3>
            <canvas id="positionChart"></canvas>
        </div>

        <!-- 收益率对比柱状图 -->
        <div class="widget">
            <h3>Coin Performance</h3>
            <canvas id="performanceChart"></canvas>
        </div>
    </div>

    <script>
        // 账户价值趋势图
        const valueCtx = document.getElementById('valueChart').getContext('2d');
        const valueChart = new Chart(valueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Account Value',
                    data: [10000, 10500, 10200, 11000, 10800, 11500],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });

        // 持仓分布饼图
        const positionCtx = document.getElementById('positionChart').getContext('2d');
        const positionChart = new Chart(positionCtx, {
            type: 'doughnut',
            data: {
                labels: ['BTC', 'ETH', 'SOL', 'Cash'],
                datasets: [{
                    data: [30, 25, 15, 30],
                    backgroundColor: [
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 205, 86)',
                        'rgb(75, 192, 192)'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });

        // 币种表现柱状图
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        const performanceChart = new Chart(performanceCtx, {
            type: 'bar',
            data: {
                labels: ['BTC', 'ETH', 'SOL', 'BNB', 'XRP'],
                datasets: [{
                    label: 'Return %',
                    data: [12, 19, -3, 5, 8],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });

        // 定期刷新数据
        setInterval(async () => {
            const response = await fetch('/api/models/1/portfolio');
            const data = await response.json();
            // 更新图表...
        }, 10000);  // 每 10 秒刷新
    </script>
</body>
</html>
```

---

## 7. Backtesting System (回测系统)

### 7.1 回测架构

```python
# backtesting.py

from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

class BacktestEngine:
    """
    回测引擎：使用历史数据测试交易策略
    """
    def __init__(self, db, data_aggregator, ai_trader, initial_capital: float = 10000):
        self.db = db
        self.data_aggregator = data_aggregator
        self.ai_trader = ai_trader
        self.initial_capital = initial_capital

        # 回测状态
        self.cash = initial_capital
        self.positions = {}  # {coin: {quantity, avg_price, side, leverage}}
        self.trades = []
        self.account_values = []

    def run_backtest(self, start_date: str, end_date: str, coins: list,
                     interval: str = '1h', trade_fee_rate: float = 0.001):
        """
        运行回测

        参数:
            start_date: '2024-01-01'
            end_date: '2024-12-31'
            coins: ['BTC', 'ETH', 'SOL']
            interval: '1h', '4h', '1d'
        """
        print(f"\\n===== Starting Backtest =====")
        print(f"Period: {start_date} to {end_date}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Coins: {', '.join(coins)}")

        # 获取历史数据
        historical_data = self._load_historical_data(coins, start_date, end_date, interval)

        # 获取时间戳列表
        timestamps = sorted(set([
            ts for coin_data in historical_data.values()
            for ts in coin_data.keys()
        ]))

        print(f"Total time periods: {len(timestamps)}")

        # 逐个时间点模拟交易
        for i, timestamp in enumerate(timestamps):
            # 构建当前市场状态
            market_state = {}
            for coin in coins:
                if timestamp in historical_data.get(coin, {}):
                    market_state[coin] = historical_data[coin][timestamp]

            if not market_state:
                continue

            # 计算当前组合价值
            portfolio = self._calculate_portfolio(market_state)

            # AI 决策
            account_info = {
                'current_time': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                'total_return': ((portfolio['total_value'] - self.initial_capital) / self.initial_capital) * 100,
                'initial_capital': self.initial_capital
            }

            try:
                decisions = self.ai_trader.make_decision(market_state, portfolio, account_info)
            except Exception as e:
                print(f"[ERROR] AI decision failed at {account_info['current_time']}: {e}")
                continue

            # 执行交易
            for coin, decision in decisions.items():
                if coin not in market_state:
                    continue

                signal = decision.get('signal', '').lower()

                if signal == 'buy_to_enter':
                    self._backtest_buy(coin, decision, market_state, trade_fee_rate, timestamp)
                elif signal == 'sell_to_enter':
                    self._backtest_sell(coin, decision, market_state, trade_fee_rate, timestamp)
                elif signal == 'close_position':
                    self._backtest_close(coin, market_state, trade_fee_rate, timestamp)

            # 记录账户价值
            portfolio = self._calculate_portfolio(market_state)
            self.account_values.append({
                'timestamp': timestamp,
                'value': portfolio['total_value'],
                'cash': self.cash,
                'positions_value': portfolio['positions_value']
            })

            # 进度显示
            if (i + 1) % 100 == 0:
                print(f"Progress: {i+1}/{len(timestamps)}, Value: ${portfolio['total_value']:,.2f}")

        # 生成报告
        return self._generate_report()

    def _load_historical_data(self, coins: list, start_date: str, end_date: str, interval: str):
        """加载历史数据"""
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

        historical_data = {}

        for coin in coins:
            print(f"Loading data for {coin}...")

            # 从数据源获取历史 K 线
            klines = self.data_aggregator.get_klines(coin, interval, limit=1000)

            # 转换为 {timestamp: data} 格式
            coin_data = {}
            for k in klines:
                ts = k['timestamp'] // 1000  # 转换为秒
                if start_ts <= ts <= end_ts:
                    coin_data[ts] = {
                        'price': k['close'],  # 使用收盘价
                        'open': k['open'],
                        'high': k['high'],
                        'low': k['low'],
                        'volume': k['volume']
                    }

            historical_data[coin] = coin_data

        return historical_data

    def _calculate_portfolio(self, market_state: Dict):
        """计算当前组合"""
        positions_value = 0
        positions_list = []

        for coin, pos in self.positions.items():
            if coin in market_state:
                current_price = market_state[coin]['price']

                # 计算持仓价值
                if pos['side'] == 'long':
                    value = pos['quantity'] * current_price
                    unrealized_pnl = (current_price - pos['avg_price']) * pos['quantity']
                else:  # short
                    value = pos['quantity'] * pos['avg_price']  # 保证金
                    unrealized_pnl = (pos['avg_price'] - current_price) * pos['quantity']

                positions_value += value

                positions_list.append({
                    'coin': coin,
                    'quantity': pos['quantity'],
                    'avg_price': pos['avg_price'],
                    'current_price': current_price,
                    'side': pos['side'],
                    'leverage': pos['leverage'],
                    'value': value,
                    'unrealized_pnl': unrealized_pnl
                })

        return {
            'cash': self.cash,
            'positions': positions_list,
            'positions_value': positions_value,
            'total_value': self.cash + positions_value
        }

    def _backtest_buy(self, coin: str, decision: Dict, market_state: Dict,
                     fee_rate: float, timestamp: int):
        """回测买入"""
        quantity = float(decision.get('quantity', 0))
        leverage = int(decision.get('leverage', 1))
        price = market_state[coin]['price']

        if quantity <= 0:
            return

        trade_amount = quantity * price
        trade_fee = trade_amount * fee_rate
        required_margin = trade_amount / leverage
        total_required = required_margin + trade_fee

        if total_required > self.cash:
            return  # 资金不足

        # 更新持仓
        if coin in self.positions:
            pos = self.positions[coin]
            new_quantity = pos['quantity'] + quantity
            pos['avg_price'] = ((pos['avg_price'] * pos['quantity']) + (price * quantity)) / new_quantity
            pos['quantity'] = new_quantity
        else:
            self.positions[coin] = {
                'quantity': quantity,
                'avg_price': price,
                'side': 'long',
                'leverage': leverage
            }

        self.cash -= total_required

        # 记录交易
        self.trades.append({
            'timestamp': timestamp,
            'coin': coin,
            'signal': 'buy_to_enter',
            'quantity': quantity,
            'price': price,
            'leverage': leverage,
            'fee': trade_fee,
            'pnl': 0
        })

    def _backtest_sell(self, coin: str, decision: Dict, market_state: Dict,
                      fee_rate: float, timestamp: int):
        """回测卖出（做空）"""
        # 类似 _backtest_buy，但 side = 'short'
        pass

    def _backtest_close(self, coin: str, market_state: Dict,
                       fee_rate: float, timestamp: int):
        """回测平仓"""
        if coin not in self.positions:
            return

        pos = self.positions[coin]
        current_price = market_state[coin]['price']

        # 计算盈亏
        if pos['side'] == 'long':
            gross_pnl = (current_price - pos['avg_price']) * pos['quantity']
        else:
            gross_pnl = (pos['avg_price'] - current_price) * pos['quantity']

        trade_amount = pos['quantity'] * current_price
        trade_fee = trade_amount * fee_rate
        net_pnl = gross_pnl - trade_fee

        # 更新现金
        if pos['side'] == 'long':
            self.cash += trade_amount - trade_fee
        else:
            self.cash += (pos['quantity'] * pos['avg_price']) + net_pnl

        # 记录交易
        self.trades.append({
            'timestamp': timestamp,
            'coin': coin,
            'signal': 'close_position',
            'quantity': pos['quantity'],
            'price': current_price,
            'leverage': pos['leverage'],
            'fee': trade_fee,
            'pnl': net_pnl
        })

        # 移除持仓
        del self.positions[coin]

    def _generate_report(self):
        """生成回测报告"""
        final_value = self.account_values[-1]['value'] if self.account_values else self.initial_capital
        total_return = final_value - self.initial_capital
        return_pct = (total_return / self.initial_capital) * 100

        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown()

        # 交易统计
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('pnl', 0) < 0]

        win_rate = len(winning_trades) / len(self.trades) * 100 if self.trades else 0

        total_fees = sum(t['fee'] for t in self.trades)

        report = {
            'summary': {
                'initial_capital': self.initial_capital,
                'final_value': final_value,
                'total_return': total_return,
                'return_percentage': return_pct,
                'max_drawdown': max_drawdown,
                'total_trades': len(self.trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_fees': total_fees
            },
            'trades': self.trades,
            'account_values': self.account_values
        }

        # 打印报告
        print("\\n===== Backtest Report =====")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Value: ${final_value:,.2f}")
        print(f"Total Return: ${total_return:,.2f} ({return_pct:.2f}%)")
        print(f"Max Drawdown: {max_drawdown:.2f}%")
        print(f"Total Trades: {len(self.trades)}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total Fees: ${total_fees:,.2f}")

        return report

    def _calculate_max_drawdown(self):
        """计算最大回撤"""
        if not self.account_values:
            return 0

        values = [v['value'] for v in self.account_values]
        peak = values[0]
        max_dd = 0

        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd
```

### 7.2 回测 Web 界面

```python
# app.py 新增路由

@app.route('/backtest')
def backtest_page():
    """回测页面"""
    return render_template('backtest.html')

@app.route('/api/backtest/run', methods=['POST'])
def run_backtest_api():
    """运行回测 API"""
    data = request.json

    model_id = data.get('model_id', 1)
    start_date = data.get('start_date', '2024-01-01')
    end_date = data.get('end_date', '2024-12-31')
    coins = data.get('coins', ['BTC', 'ETH', 'SOL'])
    interval = data.get('interval', '1h')
    initial_capital = data.get('initial_capital', 10000)

    # 获取 AI trader
    model = db.get_model(model_id)
    provider = db.get_provider(model['provider_id'])
    ai_trader = EnhancedAITrader(
        api_key=provider['api_key'],
        api_url=provider['api_url'],
        model_name=model['model_name']
    )

    # 创建回测引擎
    backtest_engine = BacktestEngine(
        db=db,
        data_aggregator=data_aggregator,
        ai_trader=ai_trader,
        initial_capital=initial_capital
    )

    # 运行回测（在后台线程中运行，避免阻塞）
    try:
        report = backtest_engine.run_backtest(
            start_date=start_date,
            end_date=end_date,
            coins=coins,
            interval=interval
        )

        return jsonify(report)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

```html
<!-- templates/backtest.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Strategy Backtesting</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div style="padding: 20px;">
        <h1>Strategy Backtesting</h1>

        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h3>Backtest Configuration</h3>

            <label>Start Date: <input type="date" id="startDate" value="2024-01-01"></label>
            <label>End Date: <input type="date" id="endDate" value="2024-12-31"></label>

            <label>
                Initial Capital: $<input type="number" id="initialCapital" value="10000">
            </label>

            <label>
                Interval:
                <select id="interval">
                    <option value="1h">1 Hour</option>
                    <option value="4h">4 Hours</option>
                    <option value="1d">1 Day</option>
                </select>
            </label>

            <div style="margin-top: 10px;">
                <label>Coins:</label><br>
                <label><input type="checkbox" value="BTC" checked> BTC</label>
                <label><input type="checkbox" value="ETH" checked> ETH</label>
                <label><input type="checkbox" value="SOL" checked> SOL</label>
            </div>

            <button onclick="runBacktest()" style="margin-top: 15px; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Run Backtest
            </button>
        </div>

        <div id="results" style="display: none;">
            <h3>Results</h3>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px;">
                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 12px; color: #666;">Final Value</div>
                    <div id="finalValue" style="font-size: 24px; font-weight: bold; color: #28a745;">-</div>
                </div>

                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 12px; color: #666;">Return %</div>
                    <div id="returnPct" style="font-size: 24px; font-weight: bold;">-</div>
                </div>

                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 12px; color: #666;">Max Drawdown</div>
                    <div id="maxDrawdown" style="font-size: 24px; font-weight: bold; color: #dc3545;">-</div>
                </div>

                <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 12px; color: #666;">Win Rate</div>
                    <div id="winRate" style="font-size: 24px; font-weight: bold;">-</div>
                </div>
            </div>

            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <canvas id="backtestChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        let backtestChart = null;

        async function runBacktest() {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            const initialCapital = parseInt(document.getElementById('initialCapital').value);
            const interval = document.getElementById('interval').value;

            const coins = Array.from(document.querySelectorAll('input[type=checkbox]:checked'))
                .map(cb => cb.value);

            if (coins.length === 0) {
                alert('Please select at least one coin');
                return;
            }

            document.getElementById('results').style.display = 'none';
            alert('Running backtest... This may take a few minutes.');

            try {
                const response = await fetch('/api/backtest/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        start_date: startDate,
                        end_date: endDate,
                        coins: coins,
                        interval: interval,
                        initial_capital: initialCapital
                    })
                });

                const report = await response.json();

                if (report.error) {
                    alert('Error: ' + report.error);
                    return;
                }

                displayResults(report);

            } catch (error) {
                alert('Error running backtest: ' + error);
            }
        }

        function displayResults(report) {
            const summary = report.summary;

            document.getElementById('finalValue').textContent = '$' + summary.final_value.toFixed(2);
            document.getElementById('returnPct').textContent = summary.return_percentage.toFixed(2) + '%';
            document.getElementById('maxDrawdown').textContent = summary.max_drawdown.toFixed(2) + '%';
            document.getElementById('winRate').textContent = summary.win_rate.toFixed(2) + '%';

            // 显示结果区域
            document.getElementById('results').style.display = 'block';

            // 绘制账户价值图表
            const timestamps = report.account_values.map(v =>
                new Date(v.timestamp * 1000).toLocaleDateString()
            );
            const values = report.account_values.map(v => v.value);

            if (backtestChart) {
                backtestChart.destroy();
            }

            const ctx = document.getElementById('backtestChart').getContext('2d');
            backtestChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: timestamps,
                    datasets: [{
                        label: 'Account Value',
                        data: values,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Account Value Over Time'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>
```

---

## 8. Implementation Plan (实施计划)

### 8.1 Phase 1: 数据库和动态币种管理 (Week 1-2)

#### Week 1: 数据库设计和迁移

**任务**:
1. 创建新表 (`coins`, `coin_groups`, `coin_group_members`, `model_coin_pools`, `market_data_cache`)
2. 编写数据迁移脚本
3. 测试迁移脚本
4. 执行数据迁移

**交付物**:
- `database_migration.py` 脚本
- 更新的 `database.py` 模块
- 迁移文档

#### Week 2: 币种管理 API 和 UI

**任务**:
1. 实现币种管理 API (`/api/coins/*`)
2. 实现模型币种池 API (`/api/models/<id>/coins`)
3. 创建币种管理 UI (`coin_management.html`)
4. 创建模型币种选择 UI (`model_coins.html`)
5. 集成测试

**交付物**:
- 完整的币种管理系统
- API 文档
- UI 界面

### 8.2 Phase 2: 多数据源集成 (Week 3-4)

#### Week 3: Binance 和 OKX API 集成

**任务**:
1. 安装 SDK (`python-binance`, `python-okx`)
2. 实现 `BinanceDataFetcher` 类
3. 实现 `OKXDataFetcher` 类
4. 实现速率限制器
5. 单元测试

**交付物**:
- `binance_fetcher.py`
- `okx_fetcher.py`
- `rate_limiter.py`
- 测试用例

#### Week 4: 数据聚合器和缓存

**任务**:
1. 实现 `MultiSourceDataAggregator` 类
2. 实现数据缓存层 (`DataCache`)
3. 更新 `TradingEngine` 使用新聚合器
4. 集成测试和性能测试

**交付物**:
- `data_aggregator.py`
- `data_cache.py`
- 性能测试报告

### 8.3 Phase 3: 数据可视化 (Week 5-6)

#### Week 5: TradingView Lightweight Charts 集成

**任务**:
1. 创建 K 线数据 API (`/api/klines/<coin>`)
2. 实现 `charts.html` 页面
3. 集成交易信号标记
4. 多时间周期切换
5. 响应式设计

**交付物**:
- 完整的图表系统
- K 线数据 API
- 用户文档

#### Week 6: 仪表板增强

**任务**:
1. 实现增强的仪表板 (`dashboard_enhanced.html`)
2. 集成 Chart.js 图表
3. 实时数据更新
4. 性能优化

**交付物**:
- 增强的仪表板
- 实时更新机制

### 8.4 Phase 4: 回测系统 (Week 7-8)

#### Week 7: 回测引擎

**任务**:
1. 实现 `BacktestEngine` 类
2. 历史数据加载
3. 模拟交易执行
4. 性能指标计算

**交付物**:
- `backtesting.py`
- 回测引擎文档

#### Week 8: 回测 UI 和集成测试

**任务**:
1. 实现回测 API (`/api/backtest/run`)
2. 创建回测 UI (`backtest.html`)
3. 结果可视化
4. 完整系统集成测试
5. 性能优化

**交付物**:
- 完整的回测系统
- 用户指南
- 系统测试报告

### 8.5 Phase 5: 测试和部署 (Week 9)

**任务**:
1. 完整的端到端测试
2. 性能测试和优化
3. 文档完善
4. 用户培训
5. 生产环境部署

**交付物**:
- 测试报告
- 部署文档
- 用户手册

---

## 9. Risk Assessment and Mitigation (风险评估与缓解)

### 9.1 技术风险

#### 风险 1: API 速率限制导致数据获取失败

**影响**: 高
**概率**: 中

**缓解措施**:
1. 实现智能速率限制器
2. 多数据源故障转移
3. 数据缓存策略
4. WebSocket 优先策略

#### 风险 2: 数据一致性问题

**影响**: 高
**概率**: 中

**缓解措施**:
1. 数据验证和清洗
2. 多源数据交叉验证
3. 异常数据检测和告警
4. 详细的日志记录

#### 风险 3: 性能瓶颈

**影响**: 中
**概率**: 中

**缓解措施**:
1. 数据库索引优化
2. 缓存策略
3. 异步处理
4. 负载测试和优化

### 9.2 业务风险

#### 风险 4: 数据迁移失败

**影响**: 高
**概率**: 低

**缓解措施**:
1. 完整的数据备份
2. 分步迁移
3. 回滚计划
4. 迁移前测试

#### 风险 5: 用户学习曲线

**影响**: 中
**概率**: 中

**缓解措施**:
1. 直观的 UI 设计
2. 详细的文档和教程
3. 渐进式功能发布
4. 用户反馈收集

### 9.3 运维风险

#### 风险 6: 第三方 API 服务中断

**影响**: 高
**概率**: 低

**缓解措施**:
1. 多数据源冗余
2. 降级策略
3. 服务监控和告警
4. 应急响应计划

---

## 10. Code Examples and Prototypes (代码示例)

### 10.1 完整的启动流程

```python
# main.py - 系统启动入口

from flask import Flask
from database import Database
from data_aggregator import MultiSourceDataAggregator, DataCache
from binance_fetcher import BinanceDataFetcher
from okx_fetcher import OKXDataFetcher
from market_data import MarketDataFetcher
from trading_engine import TradingEngine
from ai_trader_enhanced import EnhancedAITrader

# 初始化 Flask
app = Flask(__name__)

# 初始化数据库
db = Database()

# 初始化数据获取器
binance_fetcher = BinanceDataFetcher()
okx_fetcher = OKXDataFetcher()
coingecko_fetcher = MarketDataFetcher()

# 初始化缓存
cache = DataCache(db)

# 初始化数据聚合器
data_aggregator = MultiSourceDataAggregator(
    db=db,
    binance=binance_fetcher,
    okx=okx_fetcher,
    coingecko=coingecko_fetcher,
    cache=cache
)

# 创建交易引擎（示例）
def create_trading_engine(model_id: int):
    model = db.get_model(model_id)
    provider = db.get_provider(model['provider_id'])

    ai_trader = EnhancedAITrader(
        api_key=provider['api_key'],
        api_url=provider['api_url'],
        model_name=model['model_name']
    )

    return TradingEngine(
        model_id=model_id,
        db=db,
        data_aggregator=data_aggregator,
        ai_trader=ai_trader,
        trade_fee_rate=0.001
    )

# 启动 Flask
if __name__ == '__main__':
    print("\\n===== AI Trading System Enhanced =====")
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 10.2 配置文件

```python
# config.py - 系统配置

class Config:
    # 数据库配置
    DATABASE_PATH = 'trading_bot.db'

    # API 配置
    BINANCE_API_KEY = ''  # 可选，公开数据不需要
    BINANCE_API_SECRET = ''

    OKX_API_KEY = ''  # 可选
    OKX_API_SECRET = ''
    OKX_PASSPHRASE = ''

    # 缓存配置
    CACHE_ENABLED = True
    CACHE_PRICE_TTL = 10  # 价格缓存 10 秒
    CACHE_KLINE_TTL = 60  # K 线缓存 60 秒

    # 速率限制
    BINANCE_RATE_LIMIT = 6000  # weight/minute
    OKX_RATE_LIMIT = 3  # requests/second

    # 交易配置
    DEFAULT_TRADE_FEE_RATE = 0.001  # 0.1%

    # 数据源优先级
    DATA_SOURCE_PRIORITY = {
        'price': ['binance', 'okx', 'coingecko'],
        'klines': ['binance', 'okx'],
        'depth': ['binance', 'okx']
    }
```

---

## 11. Conclusion (结论)

本技术设计文档详细规划了 AI 交易系统的全面增强方案，涵盖：

1. **动态币种管理**: 从 6 个硬编码币种扩展到支持 100+ 币种的灵活系统
2. **多数据源集成**: 集成 Binance、OKX、CoinGecko，提供高质量、高可用的市场数据
3. **数据可视化**: 使用 TradingView Lightweight Charts 提供专业级图表
4. **回测系统**: 完整的策略回测框架，支持历史数据测试

### 关键优势:

- **可扩展性**: 架构设计支持未来扩展更多数据源和功能
- **可靠性**: 多源冗余和故障转移机制
- **易用性**: 直观的 UI 和完整的文档
- **性能**: 多层缓存和优化策略

### 后续步骤:

1. 评审本设计文档
2. 确认技术栈和依赖
3. 按照实施计划逐步开发
4. 持续测试和优化

---

**文档结束**
