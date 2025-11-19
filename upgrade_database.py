"""
Database upgrade script - Add strategy and custom_prompt fields
数据库升级脚本 - 添加策略和自定义提示词字段
"""
import sqlite3


def upgrade_database(db_path='AITradeGame.db'):
    """升级数据库，添加新字段"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查是否已经有strategy_name字段
        cursor.execute("PRAGMA table_info(models)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'strategy_name' not in columns:
            print("[INFO] Adding strategy_name column to models table...")
            cursor.execute('''
                ALTER TABLE models ADD COLUMN strategy_name TEXT DEFAULT 'None'
            ''')
            print("[SUCCESS] strategy_name column added")

        if 'custom_prompt' not in columns:
            print("[INFO] Adding custom_prompt column to models table...")
            cursor.execute('''
                ALTER TABLE models ADD COLUMN custom_prompt TEXT
            ''')
            print("[SUCCESS] custom_prompt column added")

        conn.commit()
        print("[SUCCESS] Database upgrade completed!")

    except Exception as e:
        print(f"[ERROR] Database upgrade failed: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    upgrade_database()
