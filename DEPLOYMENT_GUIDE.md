# AITradeGame 服务器部署指南

## 概述

本指南将帮助您将AITradeGame部署到云服务器，实现24/7自动AI交易运行。

## 部署架构

```
[客户端浏览器]
       ↓
[Nginx反向代理] :80/443
       ↓
[Gunicorn WSGI服务器] :8000
       ↓
[Flask应用 + APScheduler定时任务]
       ↓
[SQLite/PostgreSQL数据库]
```

## 方案选择

### 方案1: Docker部署（推荐）
- **优点**: 环境隔离、易于迁移、快速部署
- **适合**: 所有云服务器（AWS、阿里云、腾讯云等）

### 方案2: 传统部署
- **优点**: 更多控制、资源占用小
- **适合**: VPS、独立服务器

## 前置要求

### 服务器配置建议
- **最低**: 1核CPU、1GB内存、10GB硬盘
- **推荐**: 2核CPU、2GB内存、20GB硬盘
- **操作系统**: Ubuntu 20.04/22.04 或 CentOS 7/8

### 需要的服务
- Python 3.8+
- Nginx（反向代理）
- Supervisor/Systemd（进程管理）
- SSL证书（可选，推荐使用Let's Encrypt）

## 快速开始

### Docker部署（5分钟）

1. 安装Docker和Docker Compose
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. 克隆项目
```bash
git clone <your-repo-url>
cd nof1_enhanced
```

3. 配置环境变量
```bash
cp .env.example .env
nano .env  # 编辑配置
```

4. 启动服务
```bash
docker-compose up -d
```

5. 访问应用
```
http://your-server-ip:5000
```

### 传统部署（15分钟）

详见下文完整步骤。

## 安全配置

### 1. 环境变量管理
不要在代码中硬编码API密钥，使用环境变量：

```bash
# .env文件
FLASK_ENV=production
SECRET_KEY=your-random-secret-key
DATABASE_URL=sqlite:///AITradeGame.db
# 或使用PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/aitradegame

# API密钥通过环境变量管理
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
```

### 2. 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 3. 限制访问
- 使用Nginx基本认证
- 配置IP白名单
- 启用HTTPS

## 性能优化

### 1. 使用PostgreSQL代替SQLite
```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb aitradegame
sudo -u postgres createuser aitrader
sudo -u postgres psql -c "ALTER USER aitrader WITH PASSWORD 'your-password';"
```

### 2. Nginx缓存配置
```nginx
# 缓存静态文件
location /static {
    alias /path/to/nof1_enhanced/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 3. Gunicorn工作进程
```bash
# 根据CPU核心数调整
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

## 监控和日志

### 查看应用日志
```bash
# Docker部署
docker-compose logs -f app

# 传统部署
tail -f /var/log/aitradegame/app.log
```

### 监控定时任务
应用内置了任务监控，访问:
```
http://your-domain/api/scheduler/status
```

## 备份策略

### 自动备份数据库
```bash
# 创建备份脚本
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/backups
mkdir -p $BACKUP_DIR

# 备份数据库
cp /path/to/AITradeGame.db $BACKUP_DIR/db_$DATE.db

# 保留最近7天的备份
find $BACKUP_DIR -name "db_*.db" -mtime +7 -delete
EOF

chmod +x /opt/backup.sh

# 添加到crontab（每天凌晨2点备份）
echo "0 2 * * * /opt/backup.sh" | crontab -
```

## 故障排查

### 常见问题

**1. 服务无法启动**
```bash
# 检查端口占用
sudo netstat -tlnp | grep :5000

# 查看错误日志
journalctl -u aitradegame -n 50
```

**2. 定时任务不执行**
- 检查APScheduler日志
- 确认时区配置正确
- 验证数据库连接

**3. 性能问题**
```bash
# 查看资源占用
htop
# 或
docker stats
```

## 更新部署

### Docker部署更新
```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### 传统部署更新
```bash
git pull
pip install -r requirements.txt
sudo systemctl restart aitradegame
```

## 成本估算

### 云服务器选择

**1. 阿里云轻量服务器**
- 配置: 2核2G
- 价格: ¥60-80/月
- 适合: 个人使用

**2. 腾讯云服务器**
- 配置: 2核4G
- 价格: ¥80-120/月
- 适合: 小团队

**3. AWS EC2 t2.small**
- 配置: 1核2G
- 价格: ~$15/月
- 适合: 国际部署

## 下一步

完成部署后:
1. ✅ 配置域名和SSL证书
2. ✅ 设置监控告警
3. ✅ 配置自动备份
4. ✅ 测试AI交易逻辑
5. ✅ 设置资金限额保护

## 技术支持

如有问题，请查看:
- [完整文档](./docs/)
- [常见问题](./FAQ.md)
- [GitHub Issues](https://github.com/your-repo/issues)
