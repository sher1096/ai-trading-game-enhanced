"""
数据库迁移脚本 - 添加动态币种管理支持
从硬编码的 6 个币种迁移到灵活的数据库驱动系统
"""

import sqlite3
import os
from datetime import datetime

class DatabaseMigration:
    def __init__(self, db_path='trading_bot.db'):
        self.db_path = db_path
        self.backup_path = f'trading_bot_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

    def backup_database(self):
        """备份当前数据库"""
        if os.path.exists(self.db_path):
            print(f"\n[1/6] 备份数据库...")
            import shutil
            shutil.copy2(self.db_path, self.backup_path)
            print(f"[OK] 数据库已备份到: {self.backup_path}")
        else:
            print(f"\n[1/6] 数据库文件不存在，跳过备份")

    def create_new_tables(self):
        """创建新的表结构"""
        print(f"\n[2/6] 创建新表...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. coins 表
        print("  - 创建 coins 表")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol VARCHAR(20) NOT NULL UNIQUE,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50),
                is_active BOOLEAN DEFAULT 1,
                binance_symbol VARCHAR(20),
                okx_symbol VARCHAR(20),
                coingecko_id VARCHAR(50),
                market_cap_rank INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_coins_symbol ON coins(symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_coins_category ON coins(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_coins_is_active ON coins(is_active)")

        # 2. coin_groups 表
        print("  - 创建 coin_groups 表")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coin_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. coin_group_members 表
        print("  - 创建 coin_group_members 表")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coin_group_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                coin_id INTEGER NOT NULL,
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (group_id) REFERENCES coin_groups(id) ON DELETE CASCADE,
                FOREIGN KEY (coin_id) REFERENCES coins(id) ON DELETE CASCADE,
                UNIQUE(group_id, coin_id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cgm_group ON coin_group_members(group_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cgm_coin ON coin_group_members(coin_id)")

        # 4. model_coin_pools 表
        print("  - 创建 model_coin_pools 表")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_coin_pools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER NOT NULL,
                coin_id INTEGER NOT NULL,
                is_enabled BOOLEAN DEFAULT 1,
                weight REAL DEFAULT 1.0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
                FOREIGN KEY (coin_id) REFERENCES coins(id) ON DELETE CASCADE,
                UNIQUE(model_id, coin_id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mcp_model ON model_coin_pools(model_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mcp_coin ON model_coin_pools(coin_id)")

        # 5. market_data_cache 表
        print("  - 创建 market_data_cache 表")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id INTEGER NOT NULL,
                data_type VARCHAR(50) NOT NULL,
                data_source VARCHAR(50) NOT NULL,
                data_json TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (coin_id) REFERENCES coins(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdc_coin_type ON market_data_cache(coin_id, data_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdc_expires ON market_data_cache(expires_at)")

        conn.commit()
        conn.close()
        print("[OK] 所有新表创建完成")

    def insert_initial_coins(self):
        """插入初始币种数据（现有的 6 个币种）"""
        print(f"\n[3/6] 插入初始币种数据...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 现有的 6 个硬编码币种
        initial_coins = [
            ('BTC', 'Bitcoin', 'Layer1', 'BTCUSDT', 'BTC-USDT', 'bitcoin', 1),
            ('ETH', 'Ethereum', 'Layer1', 'ETHUSDT', 'ETH-USDT', 'ethereum', 2),
            ('SOL', 'Solana', 'Layer1', 'SOLUSDT', 'SOL-USDT', 'solana', 5),
            ('BNB', 'BNB', 'Exchange', 'BNBUSDT', 'BNB-USDT', 'binancecoin', 4),
            ('XRP', 'Ripple', 'Payment', 'XRPUSDT', 'XRP-USDT', 'ripple', 6),
            ('DOGE', 'Dogecoin', 'Meme', 'DOGEUSDT', 'DOGE-USDT', 'dogecoin', 10)
        ]

        for coin in initial_coins:
            cursor.execute("""
                INSERT OR IGNORE INTO coins
                (symbol, name, category, binance_symbol, okx_symbol, coingecko_id, market_cap_rank, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, coin)
            print(f"  - 插入币种: {coin[0]} ({coin[1]})")

        conn.commit()
        conn.close()
        print("[OK] 初始币种数据插入完成")

    def create_coin_groups(self):
        """创建币种分组"""
        print(f"\n[4/6] 创建币种分组...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        groups = [
            ('Top10', '市值前 10 的主流币种'),
            ('DeFi', 'DeFi 生态币种'),
            ('Layer1', 'Layer1 公链'),
            ('Layer2', 'Layer2 扩容方案'),
            ('Meme', 'Meme 币种'),
            ('Exchange', '交易所代币'),
            ('Payment', '支付类币种')
        ]

        for group in groups:
            cursor.execute("""
                INSERT OR IGNORE INTO coin_groups (name, description)
                VALUES (?, ?)
            """, group)
            print(f"  - 创建分组: {group[0]}")

        conn.commit()

        # 将币种分配到对应的分组
        print("\n  分配币种到分组...")

        # Top10 分组（BTC, ETH, SOL, BNB, XRP）
        cursor.execute("SELECT id FROM coin_groups WHERE name = 'Top10'")
        top10_id = cursor.fetchone()[0]

        for symbol in ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']:
            cursor.execute("SELECT id FROM coins WHERE symbol = ?", (symbol,))
            coin_result = cursor.fetchone()
            if coin_result:
                coin_id = coin_result[0]
                cursor.execute("""
                    INSERT OR IGNORE INTO coin_group_members (group_id, coin_id, sort_order)
                    VALUES (?, ?, ?)
                """, (top10_id, coin_id, 0))

        # Layer1 分组
        cursor.execute("SELECT id FROM coin_groups WHERE name = 'Layer1'")
        layer1_id = cursor.fetchone()[0]

        for symbol in ['BTC', 'ETH', 'SOL']:
            cursor.execute("SELECT id FROM coins WHERE symbol = ?", (symbol,))
            coin_result = cursor.fetchone()
            if coin_result:
                coin_id = coin_result[0]
                cursor.execute("""
                    INSERT OR IGNORE INTO coin_group_members (group_id, coin_id, sort_order)
                    VALUES (?, ?, ?)
                """, (layer1_id, coin_id, 0))

        # Meme 分组
        cursor.execute("SELECT id FROM coin_groups WHERE name = 'Meme'")
        meme_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM coins WHERE symbol = 'DOGE'")
        coin_result = cursor.fetchone()
        if coin_result:
            doge_id = coin_result[0]
            cursor.execute("""
                INSERT OR IGNORE INTO coin_group_members (group_id, coin_id, sort_order)
                VALUES (?, ?, ?)
            """, (meme_id, doge_id, 0))

        # Exchange 分组
        cursor.execute("SELECT id FROM coin_groups WHERE name = 'Exchange'")
        exchange_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM coins WHERE symbol = 'BNB'")
        coin_result = cursor.fetchone()
        if coin_result:
            bnb_id = coin_result[0]
            cursor.execute("""
                INSERT OR IGNORE INTO coin_group_members (group_id, coin_id, sort_order)
                VALUES (?, ?, ?)
            """, (exchange_id, bnb_id, 0))

        # Payment 分组
        cursor.execute("SELECT id FROM coin_groups WHERE name = 'Payment'")
        payment_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM coins WHERE symbol = 'XRP'")
        coin_result = cursor.fetchone()
        if coin_result:
            xrp_id = coin_result[0]
            cursor.execute("""
                INSERT OR IGNORE INTO coin_group_members (group_id, coin_id, sort_order)
                VALUES (?, ?, ?)
            """, (payment_id, xrp_id, 0))

        conn.commit()
        conn.close()
        print("[OK] 币种分组创建完成")

    def migrate_model_coins(self):
        """为所有现有模型分配币种池"""
        print(f"\n[5/6] 迁移模型币种池...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 检查 models 表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='models'
        """)
        if not cursor.fetchone():
            print("  - models 表不存在，跳过模型币种池迁移")
            print("  - 提示：首次运行系统时需要先创建模型")
            conn.close()
            return

        # 获取所有模型
        cursor.execute("SELECT id, name FROM models")
        models = cursor.fetchall()

        if not models:
            print("  - 没有找到模型，跳过")
            conn.close()
            return

        # 获取所有币种 ID
        cursor.execute("SELECT id, symbol FROM coins WHERE is_active = 1")
        coins = cursor.fetchall()

        # 为每个模型分配所有币种
        for model_id, model_name in models:
            print(f"  - 为模型 {model_id} ({model_name}) 分配币种池")
            for coin_id, coin_symbol in coins:
                cursor.execute("""
                    INSERT OR IGNORE INTO model_coin_pools (model_id, coin_id, is_enabled, weight)
                    VALUES (?, ?, 1, 1.0)
                """, (model_id, coin_id))
                print(f"    * {coin_symbol}")

        conn.commit()
        conn.close()
        print("[OK] 模型币种池迁移完成")

    def verify_migration(self):
        """验证迁移结果"""
        print(f"\n[6/6] 验证迁移结果...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 验证币种数量
        cursor.execute("SELECT COUNT(*) FROM coins")
        coin_count = cursor.fetchone()[0]
        print(f"  - 币种总数: {coin_count}")

        # 验证分组数量
        cursor.execute("SELECT COUNT(*) FROM coin_groups")
        group_count = cursor.fetchone()[0]
        print(f"  - 分组总数: {group_count}")

        # 验证模型币种池（检查 models 表是否存在）
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='models'
        """)
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(DISTINCT model_id) FROM model_coin_pools")
            model_count = cursor.fetchone()[0]
            print(f"  - 已配置币种池的模型数: {model_count}")

            # 显示每个模型的币种数量
            cursor.execute("""
                SELECT m.id, m.name, COUNT(mcp.coin_id) as coin_count
                FROM models m
                LEFT JOIN model_coin_pools mcp ON m.id = mcp.model_id
                GROUP BY m.id
            """)
            model_coins = cursor.fetchall()

            for model_id, model_name, coin_count in model_coins:
                print(f"  - 模型 {model_id} ({model_name}): {coin_count} 个币种")
        else:
            print("  - models 表不存在，跳过模型验证")

        conn.close()
        print("\n[OK] 迁移验证完成")

    def run(self):
        """执行完整的迁移流程"""
        print("\n" + "="*60)
        print("数据库迁移: 动态币种管理系统")
        print("="*60)

        try:
            self.backup_database()
            self.create_new_tables()
            self.insert_initial_coins()
            self.create_coin_groups()
            self.migrate_model_coins()
            self.verify_migration()

            print("\n" + "="*60)
            print("[OK] 迁移成功完成！")
            print("="*60)
            print(f"\n备份文件: {self.backup_path}")
            print(f"数据库文件: {self.db_path}")

        except Exception as e:
            print(f"\n[ERROR] 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            print(f"\n如需回滚，请将备份文件恢复: {self.backup_path}")

if __name__ == '__main__':
    migration = DatabaseMigration()
    migration.run()
