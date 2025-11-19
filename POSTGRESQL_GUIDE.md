# PostgreSQL 数据库配置指南

本指南介绍如何使用 PostgreSQL 数据库替代 SQLite，以获得更好的性能和并发支持。

## 📋 目录

1. [为什么使用 PostgreSQL](#为什么使用-postgresql)
2. [Docker 方式部署](#docker-方式部署推荐)
3. [PostgreSQL MCP 配置](#postgresql-mcp-配置)
4. [数据迁移](#数据迁移从-sqlite-到-postgresql)
5. [常用操作](#常用操作)
6. [故障排除](#故障排除)

---

## 为什么使用 PostgreSQL

### SQLite vs PostgreSQL

| 特性 | SQLite | PostgreSQL |
|------|--------|------------|
| **并发写入** | ❌ 单写入 | ✅ 多写入 |
| **性能** | 小数据量快 | 大数据量优秀 |
| **数据完整性** | 基础 | 高级（外键、事务） |
| **扩展性** | ❌ 有限 | ✅ 优秀 |
| **部署** | ✅ 零配置 | 需要服务器 |
| **适用场景** | 开发、小项目 | 生产、多用户 |

**推荐**：开发用 SQLite，生产用 PostgreSQL

---

## Docker 方式部署（推荐）

### 方式 1：使用 docker-compose（最简单）

项目已配置好 PostgreSQL 服务，直接启动：

```bash
# 1. 启动所有服务（包括 PostgreSQL）
cd E:\code\nof1_enhanced
docker-compose up -d

# 2. 查看PostgreSQL日志
docker-compose logs postgres

# 3. 验证PostgreSQL运行状态
docker-compose ps
```

**默认配置**：
- 主机: `postgres`（容器内）或 `localhost:5432`（主机）
- 数据库: `aitradegame`
- 用户: `postgres`
- 密码: `changeme123`（⚠️ 生产环境务必修改）

### 方式 2：单独运行 PostgreSQL 容器

```bash
# 启动PostgreSQL容器
docker run -d \
  --name aitradegame_postgres \
  -e POSTGRES_DB=aitradegame \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=changeme123 \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# 查看日志
docker logs aitradegame_postgres

# 连接到PostgreSQL
docker exec -it aitradegame_postgres psql -U postgres -d aitradegame
```

---

## PostgreSQL MCP 配置

### 步骤 1：配置 Claude Desktop

编辑 Claude Desktop 配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加 PostgreSQL MCP 配置：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION": "postgresql://postgres:changeme123@localhost:5432/aitradegame"
      }
    }
  }
}
```

### 步骤 2：重启 Claude Desktop

配置后需要**完全关闭并重启 Claude Desktop**。

### 步骤 3：验证 MCP 连接

重启后，你可以要求 Claude 执行 PostgreSQL 操作：
- "查询数据库中的所有表"
- "显示 ai_models 表的结构"
- "查询最近的交易记录"

---

## 数据迁移（从 SQLite 到 PostgreSQL）

### 方式 1：使用 Python 脚本迁移

创建迁移脚本 `migrate_to_postgres.py`：

```python
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch

# SQLite 源数据库
sqlite_conn = sqlite3.connect('AITradeGame.db')
sqlite_cursor = sqlite_conn.cursor()

# PostgreSQL 目标数据库
pg_conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='aitradegame',
    user='postgres',
    password='changeme123'
)
pg_cursor = pg_conn.cursor()

# 获取所有表名
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = sqlite_cursor.fetchall()

for (table_name,) in tables:
    if table_name == 'sqlite_sequence':
        continue

    print(f"迁移表: {table_name}")

    # 读取SQLite数据
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()

    if rows:
        # 获取列名
        columns = [description[0] for description in sqlite_cursor.description]
        placeholders = ','.join(['%s'] * len(columns))

        # 插入PostgreSQL
        insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        execute_batch(pg_cursor, insert_sql, rows)
        pg_conn.commit()
        print(f"✅ {len(rows)} 条记录已迁移")

print("🎉 迁移完成！")
sqlite_conn.close()
pg_conn.close()
```

运行迁移：
```bash
python migrate_to_postgres.py
```

### 方式 2：导出/导入（适合小数据量）

```bash
# 1. 从 SQLite 导出
sqlite3 AITradeGame.db .dump > backup.sql

# 2. 手动编辑 backup.sql，将 SQLite 语法转换为 PostgreSQL

# 3. 导入 PostgreSQL
docker exec -i aitradegame_postgres psql -U postgres -d aitradegame < backup.sql
```

---

## 常用操作

### 连接 PostgreSQL

```bash
# 使用 docker exec
docker exec -it aitradegame_postgres psql -U postgres -d aitradegame

# 使用 psql 客户端（需要安装）
psql -h localhost -p 5432 -U postgres -d aitradegame
```

### 常用 SQL 命令

```sql
-- 查看所有表
\dt

-- 查看表结构
\d ai_providers
\d trading_models
\d trade_history

-- 查看数据库大小
SELECT pg_size_pretty(pg_database_size('aitradegame'));

-- 查看表数据量
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查询最近的交易
SELECT * FROM trade_history ORDER BY timestamp DESC LIMIT 10;

-- 查询活跃的模型
SELECT * FROM trading_models WHERE is_active = true;

-- 清空表（谨慎使用）
TRUNCATE TABLE trade_history CASCADE;
```

### 备份与恢复

```bash
# 备份数据库
docker exec aitradegame_postgres pg_dump -U postgres aitradegame > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i aitradegame_postgres psql -U postgres -d aitradegame < backup_20231120.sql

# 导出为自定义格式（压缩）
docker exec aitradegame_postgres pg_dump -U postgres -F c aitradegame > backup.dump

# 恢复自定义格式
docker exec -i aitradegame_postgres pg_restore -U postgres -d aitradegame < backup.dump
```

---

## 性能优化

### 1. 创建索引

```sql
-- 为常用查询创建索引
CREATE INDEX idx_trade_history_timestamp ON trade_history(timestamp);
CREATE INDEX idx_trade_history_model_id ON trade_history(model_id);
CREATE INDEX idx_trading_models_active ON trading_models(is_active);

-- 查看现有索引
\di
```

### 2. 定期维护

```sql
-- 分析表（更新统计信息）
ANALYZE;

-- 清理死元组
VACUUM;

-- 完整清理（需要更多时间）
VACUUM FULL;
```

### 3. 连接池配置

在应用中使用连接池：

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

---

## 监控与调优

### 查看活动连接

```sql
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'aitradegame';
```

### 查看慢查询

```sql
-- 启用慢查询日志（postgresql.conf）
-- log_min_duration_statement = 1000  # 记录超过1秒的查询

-- 查看最耗时的查询
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

---

## 故障排除

### 问题 1：无法连接到 PostgreSQL

**症状**：`psycopg2.OperationalError: could not connect to server`

**解决方案**：
```bash
# 1. 检查容器是否运行
docker ps | grep postgres

# 2. 检查端口是否开放
netstat -an | grep 5432

# 3. 查看 PostgreSQL 日志
docker logs aitradegame_postgres

# 4. 测试连接
telnet localhost 5432
```

### 问题 2：密码认证失败

**症状**：`FATAL: password authentication failed`

**解决方案**：
```bash
# 1. 确认环境变量
docker exec aitradegame_postgres env | grep POSTGRES

# 2. 重置密码
docker exec -it aitradegame_postgres psql -U postgres
ALTER USER postgres WITH PASSWORD 'new_password';
```

### 问题 3：磁盘空间不足

**症状**：`ERROR: could not extend file`

**解决方案**：
```bash
# 1. 查看磁盘使用
df -h

# 2. 清理旧数据
docker exec -it aitradegame_postgres psql -U postgres -d aitradegame
DELETE FROM trade_history WHERE timestamp < NOW() - INTERVAL '30 days';
VACUUM FULL;

# 3. 清理 Docker 卷
docker system prune -a --volumes
```

### 问题 4：数据库锁死

**症状**：查询一直等待

**解决方案**：
```sql
-- 查看锁
SELECT * FROM pg_locks WHERE NOT granted;

-- 终止阻塞的查询
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND state_change < current_timestamp - INTERVAL '10 minutes';
```

---

## 安全建议

### 1. 修改默认密码

```bash
# 生产环境务必修改密码
docker exec -it aitradegame_postgres psql -U postgres
ALTER USER postgres WITH PASSWORD 'strong_random_password_here';
```

### 2. 限制访问

在 `docker-compose.yml` 中不暴露 5432 端口（仅容器内访问）：

```yaml
postgres:
  ports:
    # - "5432:5432"  # 注释掉这行
  # 容器内仍可通过 postgres:5432 访问
```

### 3. 定期备份

设置自动备份 cron 任务：

```bash
# 每天凌晨2点备份
0 2 * * * docker exec aitradegame_postgres pg_dump -U postgres aitradegame > /backups/aitradegame_$(date +\%Y\%m\%d).sql
```

### 4. 启用 SSL 连接

```python
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"
```

---

## 生产环境最佳实践

1. **使用独立的数据库服务器**（或云数据库如 AWS RDS）
2. **启用自动备份**（每日备份 + WAL归档）
3. **配置监控告警**（磁盘、连接数、慢查询）
4. **定期更新 PostgreSQL**（安全补丁）
5. **使用强密码和证书认证**
6. **限制数据库访问 IP 白名单**
7. **配置主从复制**（高可用）

---

## 相关资源

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [SQLAlchemy PostgreSQL 方言](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
- [psycopg2 文档](https://www.psycopg.org/docs/)
- [Docker PostgreSQL 镜像](https://hub.docker.com/_/postgres)

---

**需要帮助？** 在 [GitHub Issues](https://github.com/sher1096/ai-trading-game-enhanced/issues) 提问
