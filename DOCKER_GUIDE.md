# Docker 部署指南

本指南介绍如何使用 Docker 和 Docker Compose 部署 AI Trading Game Enhanced。

## 📋 目录

1. [前置要求](#前置要求)
2. [快速开始](#快速开始)
3. [Docker MCP 配置](#docker-mcp-配置)
4. [常用命令](#常用命令)
5. [故障排除](#故障排除)
6. [生产部署](#生产部署)

---

## 前置要求

### 安装 Docker

**Windows**:
- 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
- 确保启用 WSL 2 后端

**检查安装**:
```bash
docker --version
docker-compose --version
```

---

## 快速开始

### 方式 1：Docker Compose（推荐）

```bash
# 1. 进入项目目录
cd E:\code\nof1_enhanced

# 2. 创建 .env 文件（如果还没有）
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 访问应用
浏览器打开: http://localhost:5000
```

**服务说明**:
- `postgres`: PostgreSQL 数据库（端口 5432）
- `app`: Flask 应用（端口 5000，仅容器内）
- `nginx`: Nginx 反向代理（端口 80/443）

### 方式 2：仅运行 Flask 应用

```bash
# 构建镜像
docker build -t aitradegame:latest .

# 运行容器
docker run -d \
  --name aitradegame_app \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  -e OPENAI_API_KEY=sk-your-key \
  aitradegame:latest

# 查看日志
docker logs -f aitradegame_app

# 访问应用
浏览器打开: http://localhost:5000
```

---

## Docker MCP 配置

### 步骤 1：安装 Docker MCP

Docker MCP 通过 npx 自动安装，无需手动安装。

### 步骤 2：配置 Claude Desktop

编辑配置文件：`%APPDATA%\Claude\claude_desktop_config.json`

添加 Docker MCP:

```json
{
  "mcpServers": {
    "docker": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-docker"]
    }
  }
}
```

### 步骤 3：重启 Claude Desktop

完全关闭并重启 Claude Desktop。

### 步骤 4：测试 MCP

重启后，你可以要求 Claude 执行：
- "列出所有 Docker 容器"
- "显示 aitradegame_app 容器的日志"
- "重启 PostgreSQL 容器"
- "检查容器健康状态"
- "查看 Docker 镜像列表"

---

## 常用命令

### 容器管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器 + 卷（谨慎使用，会删除数据）
docker-compose down -v

# 查看服务状态
docker-compose ps

# 查看特定服务日志
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f nginx

# 进入容器
docker-compose exec app bash
docker-compose exec postgres psql -U postgres -d aitradegame
```

### 镜像管理

```bash
# 构建镜像
docker-compose build

# 强制重新构建（不使用缓存）
docker-compose build --no-cache

# 拉取最新镜像
docker-compose pull

# 查看镜像
docker images | grep aitradegame

# 删除旧镜像
docker image prune -a
```

### 日志和监控

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看最后100行日志
docker-compose logs --tail=100 app

# 查看容器资源使用
docker stats

# 查看特定容器的详细信息
docker inspect aitradegame_app

# 查看容器内进程
docker-compose exec app ps aux
```

### 数据备份

```bash
# 备份PostgreSQL数据
docker-compose exec postgres pg_dump -U postgres aitradegame > backup_$(date +%Y%m%d).sql

# 备份数据卷
docker run --rm \
  -v nof1_enhanced_postgres_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz /data

# 恢复数据
docker-compose exec -T postgres psql -U postgres -d aitradegame < backup_20231120.sql
```

---

## 健康检查

### 检查应用健康状态

```bash
# 使用 healthcheck API
curl http://localhost:5000/api/health

# 期望输出
{
  "status": "healthy",
  "timestamp": "2023-11-20T10:30:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

### 检查容器健康

```bash
# 查看健康检查状态
docker-compose ps

# 输出示例
NAME                     STATUS
aitradegame_app          Up 2 hours (healthy)
aitradegame_postgres     Up 2 hours (healthy)
aitradegame_nginx        Up 2 hours
```

---

## 环境变量管理

### 生产环境 .env 示例

创建 `.env` 文件:

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=False

# 数据库
DATABASE_URL=postgresql://postgres:strong_password@postgres:5432/aitradegame
POSTGRES_DB=aitradegame
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_password_here

# AI API
OPENAI_API_KEY=sk-your-real-api-key
DEEPSEEK_API_KEY=sk-your-deepseek-key

# 交易所API（如果使用实盘）
BINANCE_API_KEY=your_binance_key
BINANCE_API_SECRET=your_binance_secret
BINANCE_TESTNET=False  # 生产环境使用主网
```

---

## 性能优化

### 1. 调整 Docker 资源限制

在 `docker-compose.yml` 中添加:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 512M
```

### 2. 使用多阶段构建优化镜像大小

`Dockerfile` 已采用 Python slim 镜像，进一步优化：

```dockerfile
# 多阶段构建示例
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

### 3. 启用 Nginx 缓存

在 `nginx.conf` 中配置:

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=100m;

location /static/ {
    proxy_cache my_cache;
    proxy_cache_valid 200 1d;
}
```

---

## 故障排除

### 问题 1：容器无法启动

**症状**: `docker-compose up` 失败

**解决方案**:
```bash
# 1. 查看详细日志
docker-compose logs app

# 2. 检查端口占用
netstat -ano | findstr :5000
netstat -ano | findstr :5432

# 3. 强制重建
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 4. 检查 .env 文件
cat .env  # 确保所有必需的变量都已设置
```

### 问题 2：PostgreSQL 连接失败

**症状**: `OperationalError: could not connect to server`

**解决方案**:
```bash
# 1. 检查 PostgreSQL 容器状态
docker-compose ps postgres

# 2. 查看 PostgreSQL 日志
docker-compose logs postgres

# 3. 测试连接
docker-compose exec postgres pg_isready -U postgres

# 4. 手动连接测试
docker-compose exec postgres psql -U postgres -d aitradegame
```

### 问题 3：内存不足

**症状**: 容器频繁重启或 OOM killed

**解决方案**:
```bash
# 1. 增加 Docker Desktop 内存限制
# Docker Desktop -> Settings -> Resources -> Memory -> 提高到 4GB+

# 2. 限制单个容器内存
docker-compose.yml 中添加:
    mem_limit: 1g

# 3. 查看内存使用
docker stats
```

### 问题 4：磁盘空间不足

**症状**: `no space left on device`

**解决方案**:
```bash
# 1. 清理未使用的镜像
docker image prune -a

# 2. 清理未使用的容器
docker container prune

# 3. 清理未使用的卷
docker volume prune

# 4. 清理所有未使用资源
docker system prune -a --volumes
```

---

## 生产部署

### 1. 使用 HTTPS

安装 Let's Encrypt 证书:

```bash
# 使用 certbot
sudo apt-get install certbot
sudo certbot certonly --standalone -d yourdomain.com

# 更新 nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    # ...
}
```

### 2. 配置域名

更新 `docker-compose.yml`:

```yaml
nginx:
  environment:
    - VIRTUAL_HOST=yourdomain.com
    - LETSENCRYPT_HOST=yourdomain.com
    - LETSENCRYPT_EMAIL=your@email.com
```

### 3. 启用防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 阻止直接访问 5432（PostgreSQL）
# 仅允许容器内访问
```

### 4. 配置自动备份

创建 cron 任务:

```bash
# 编辑 crontab
crontab -e

# 添加每日备份任务（凌晨 2 点）
0 2 * * * cd /path/to/nof1_enhanced && docker-compose exec -T postgres pg_dump -U postgres aitradegame > /backups/db_$(date +\%Y\%m\%d).sql

# 清理 30 天前的备份
0 3 * * * find /backups -name "db_*.sql" -mtime +30 -delete
```

### 5. 日志轮转

配置 Docker 日志限制:

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 6. 监控和告警

使用 Prometheus + Grafana:

```bash
# 添加 Prometheus 导出器
docker-compose.yml:
  prometheus:
    image: prom/prometheus
    # ...

  grafana:
    image: grafana/grafana
    # ...
```

---

## 升级和维护

### 拉取最新代码并重新部署

```bash
# 1. 停止服务
docker-compose down

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建
docker-compose build

# 4. 启动服务
docker-compose up -d

# 5. 验证
docker-compose ps
curl http://localhost:5000/api/health
```

### 数据库迁移

```bash
# 运行迁移脚本
docker-compose exec app python upgrade_database.py

# 或进入容器手动迁移
docker-compose exec app bash
python database_migration.py
```

---

## 相关资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Dockerfile 最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [项目 Deployment Guide](DEPLOYMENT_GUIDE.md)

---

**需要帮助？** 在 [GitHub Issues](https://github.com/sher1096/ai-trading-game-enhanced/issues) 提问
