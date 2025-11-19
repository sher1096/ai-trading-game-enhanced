# AITradeGame 快速部署指南

5分钟内将AI交易系统部署到云服务器，实现24/7自动交易。

## 快速开始

### 方法1: 一键部署（推荐）

在云服务器上执行以下命令：

```bash
# 克隆项目
git clone <your-repo-url>
cd nof1_enhanced

# 运行部署脚本
bash deploy.sh
```

脚本会自动完成：
- 安装Docker和Docker Compose
- 创建配置文件
- 构建并启动服务
- 健康检查

### 方法2: 手动部署

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑.env填入API密钥
nano .env

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

## 访问应用

部署完成后，在浏览器访问：

```
http://your-server-ip:80
```

## 必填配置项

编辑 `.env` 文件，至少配置以下一项：

```bash
# AI API密钥（至少配置一个）
OPENAI_API_KEY=sk-your-api-key
# 或
DEEPSEEK_API_KEY=sk-your-api-key

# SECRET_KEY会自动生成，无需修改
```

## 常用命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新应用
git pull
docker-compose up -d --build

# 查看运行状态
docker-compose ps

# 检查健康状态
curl http://localhost/api/health
```

## 服务器要求

**最低配置：**
- 1核CPU
- 1GB内存
- 10GB硬盘

**推荐配置：**
- 2核CPU
- 2GB内存
- 20GB硬盘

**支持的系统：**
- Ubuntu 20.04/22.04
- CentOS 7/8
- Debian 10/11

## 端口配置

默认端口：
- HTTP: 80
- HTTPS: 443（需配置SSL证书）

修改端口：编辑 `docker-compose.yml`

```yaml
nginx:
  ports:
    - "8080:80"  # 改为8080端口
```

## 数据持久化

数据存储位置：
- 数据库: `./data/AITradeGame.db`
- 日志: `./logs/`

备份数据：

```bash
# 手动备份
cp -r data/ data_backup_$(date +%Y%m%d)

# 自动备份（添加到crontab）
0 2 * * * cd /path/to/nof1_enhanced && cp -r data/ data_backup_$(date +\%Y\%m\%d)
```

## 防火墙配置

开放必要端口：

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 监控和维护

### 查看资源占用

```bash
# Docker容器资源使用
docker stats

# 系统资源
htop
```

### 查看应用日志

```bash
# 应用日志
docker-compose logs -f app

# Nginx日志
docker-compose logs -f nginx

# 只看最近100行
docker-compose logs --tail=100 app
```

### 健康检查

访问健康检查端点：

```bash
curl http://localhost/api/health
```

返回示例：

```json
{
  "status": "healthy",
  "database": "connected",
  "scheduler": "running",
  "timestamp": "2025-01-18T10:30:00"
}
```

## 故障排查

### 问题1: 无法访问服务

```bash
# 检查容器状态
docker-compose ps

# 查看容器日志
docker-compose logs

# 检查端口占用
netstat -tlnp | grep :80
```

### 问题2: API密钥错误

编辑 `.env` 文件，确保API密钥正确：

```bash
nano .env
docker-compose restart
```

### 问题3: 数据库问题

```bash
# 重建数据库（警告：会清空数据）
docker-compose down
rm -rf data/
docker-compose up -d
```

## 安全建议

1. **修改默认密钥**
   - 确保 `.env` 中的 `SECRET_KEY` 是随机生成的

2. **使用HTTPS**
   - 参考 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 配置SSL证书

3. **限制访问**
   - 配置防火墙规则
   - 使用Nginx基本认证

4. **定期更新**
   - 及时更新依赖包
   - 关注安全公告

## 性能优化

### 使用PostgreSQL（可选）

编辑 `.env`:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/aitradegame
```

### 调整Gunicorn worker数量

编辑 `Dockerfile`:

```dockerfile
# 根据CPU核心数调整 workers
CMD ["gunicorn", "--workers", "8", ...]
```

### 启用Nginx缓存

已在 `nginx.conf` 中预配置静态文件缓存。

## 下一步

- 📖 完整部署文档: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- 🔧 应用配置说明: [.env.example](./.env.example)
- 📝 使用说明: [README.md](./README.md)

## 获取帮助

遇到问题？

1. 查看 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. 检查日志: `docker-compose logs -f`
3. 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)

---

**祝您部署顺利！开始您的AI交易之旅。**
