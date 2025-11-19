# MCP 完整配置指南

本文档提供了所有 MCP（Model Context Protocol）服务器的完整配置，帮助你一次性配置所有功能。

## 📋 目录

1. [什么是 MCP](#什么是-mcp)
2. [完整配置文件](#完整配置文件)
3. [配置步骤](#配置步骤)
4. [各 MCP 功能说明](#各-mcp-功能说明)
5. [获取必需的 Tokens](#获取必需的-tokens)
6. [验证配置](#验证配置)
7. [故障排除](#故障排除)

---

## 什么是 MCP

MCP（Model Context Protocol）是 Anthropic 推出的协议，允许 Claude Desktop 与外部工具和服务集成，扩展 Claude 的能力。

通过配置 MCP 服务器，Claude 可以：
- 🐙 管理 GitHub 仓库（创建、推送、PR）
- 🗄️ 查询 PostgreSQL 数据库
- 🐳 控制 Docker 容器
- 🌐 自动化 Web UI 测试
- 💬 发送 Slack/Discord 告警

---

## 完整配置文件

### 配置文件位置

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**完整路径**: `C:\Users\你的用户名\AppData\Roaming\Claude\claude_desktop_config.json`

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Linux**: `~/.config/Claude/claude_desktop_config.json`

### 完整配置内容

将以下内容复制到配置文件中（替换你的实际 token 和密码）：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_github_token_here"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION": "postgresql://postgres:changeme123@localhost:5432/aitradegame"
      }
    },
    "docker": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-docker"]
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-slack-bot-token",
        "SLACK_TEAM_ID": "T1234567890"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "E:\\code\\nof1_enhanced"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

---

## 配置步骤

### 步骤 1：创建配置文件

如果配置文件不存在，创建一个新文件：

**Windows (PowerShell)**:
```powershell
$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"
New-Item -ItemType Directory -Force -Path (Split-Path $configPath)
New-Item -ItemType File -Force -Path $configPath
```

**macOS/Linux**:
```bash
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 步骤 2：填入配置

将上面的完整配置复制到文件中。

### 步骤 3：替换 Tokens

根据下面的指南获取并替换各项 token。

### 步骤 4：保存文件

确保 JSON 格式正确（可以用 [JSONLint](https://jsonlint.com/) 验证）。

### 步骤 5：重启 Claude Desktop

**重要**：配置完成后必须**完全关闭并重启** Claude Desktop，MCP 才会生效。

**Windows**:
- 右键任务栏 Claude 图标 → 退出
- 重新打开 Claude Desktop

**macOS**:
- Cmd+Q 完全退出
- 重新打开

---

## 各 MCP 功能说明

### 1️⃣ GitHub MCP

**功能**：
- ✅ 创建和管理 GitHub 仓库
- ✅ 推送代码和创建提交
- ✅ 创建 Issues 和 Pull Requests
- ✅ 查看仓库状态和分支

**需要**：GitHub Personal Access Token

**使用示例**：
- "创建一个新的 GitHub Issue 标题为 'Bug: 交易失败'"
- "推送本地更改到 GitHub"
- "查看最近的 Pull Requests"

**详细文档**: [项目 README → GitHub 集成](#)

---

### 2️⃣ PostgreSQL MCP

**功能**：
- ✅ 查询数据库表和数据
- ✅ 执行 SQL 查询
- ✅ 查看数据库架构
- ✅ 分析数据库性能

**需要**：PostgreSQL 连接字符串

**使用示例**：
- "查询数据库中的所有 AI 模型"
- "显示最近 10 条交易记录"
- "分析数据库表大小"

**详细文档**: [POSTGRESQL_GUIDE.md](POSTGRESQL_GUIDE.md)

---

### 3️⃣ Docker MCP

**功能**：
- ✅ 列出和管理 Docker 容器
- ✅ 查看容器日志
- ✅ 启动/停止/重启容器
- ✅ 检查容器健康状态

**需要**：无（自动检测本地 Docker）

**使用示例**：
- "列出所有运行中的 Docker 容器"
- "查看 aitradegame_app 容器的日志"
- "重启 PostgreSQL 容器"

**详细文档**: [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

---

### 4️⃣ Puppeteer MCP

**功能**：
- ✅ 自动化 Web UI 测试
- ✅ 网页截图
- ✅ 模拟用户交互
- ✅ 性能测试

**需要**：无（自动安装）

**使用示例**：
- "访问 http://localhost:5000 并截图"
- "测试添加 AI 模型的流程"
- "检查页面加载性能"

**详细文档**: [WEB_TESTING_GUIDE.md](WEB_TESTING_GUIDE.md)

---

### 5️⃣ Slack MCP

**功能**：
- ✅ 发送消息到 Slack 频道
- ✅ 创建交易告警
- ✅ 发送每日报告
- ✅ 格式化消息（附件、字段）

**需要**：Slack Bot Token 和 Team ID

**使用示例**：
- "发送测试消息到 Slack #trading-alerts 频道"
- "在交易失败时通知 Slack"
- "发送每日交易报告"

**详细文档**: [ALERTS_GUIDE.md](ALERTS_GUIDE.md)

---

### 6️⃣ Filesystem MCP（可选）

**功能**：
- ✅ 高级文件操作
- ✅ 批量文件处理
- ✅ 文件监控

**需要**：指定允许访问的目录

**使用示例**：
- "批量重命名 Python 文件"
- "监控日志文件变化"

---

### 7️⃣ Memory MCP（可选）

**功能**：
- ✅ 长期记忆存储
- ✅ 追踪项目演进
- ✅ 记住重要决策

**需要**：无

**使用示例**：
- "记住这次重构的原因"
- "回忆上次讨论的架构方案"

---

## 获取必需的 Tokens

### GitHub Personal Access Token

1. 访问 [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. 点击 **"Generate new token (classic)"**
3. 设置权限：
   - ✅ `repo` - 完整仓库访问
   - ✅ `workflow` - 工作流访问
4. 点击 **"Generate token"**
5. 复制 token（格式：`ghp_xxxxxxxxxxxx`）

⚠️ **重要**：立即保存，离开页面后无法再查看！

---

### PostgreSQL 连接字符串

**格式**：`postgresql://用户名:密码@主机:端口/数据库名`

**Docker 部署**（默认）：
```
postgresql://postgres:changeme123@localhost:5432/aitradegame
```

**自定义配置**：
```
postgresql://myuser:mypassword@localhost:5432/mydb
```

**云数据库**（AWS RDS 示例）：
```
postgresql://admin:password@mydb.xxxxx.us-east-1.rds.amazonaws.com:5432/aitradegame
```

---

### Slack Bot Token

**方式 1：Slack App（推荐）**

1. 访问 [Slack API Apps](https://api.slack.com/apps)
2. 点击 **"Create New App"** → **"From scratch"**
3. 输入应用名称，选择工作区
4. 在 **"OAuth & Permissions"** 添加权限：
   - `chat:write`
   - `chat:write.public`
   - `channels:read`
5. 点击 **"Install to Workspace"**
6. 复制 **"Bot User OAuth Token"**（格式：`xoxb-...`）

**方式 2：Webhook（简化版）**

如果只需要发送消息，可以用 Webhook 替代：
1. 访问 [Incoming Webhooks](https://api.slack.com/messaging/webhooks)
2. 创建 Webhook
3. 复制 Webhook URL
4. 在应用中使用 Webhook 而非 MCP

---

### Slack Team ID

**方法 1**：从 Slack URL 获取
```
https://app.slack.com/client/T1234567890/...
                          ^^^^^^^^^^^^
                          这就是 Team ID
```

**方法 2**：使用 API
```bash
curl -H "Authorization: Bearer xoxb-your-token" \
  https://slack.com/api/team.info
```

---

## 验证配置

### 检查配置文件

```bash
# Windows (PowerShell)
Get-Content $env:APPDATA\Claude\claude_desktop_config.json | ConvertFrom-Json

# macOS/Linux
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq
```

### 验证 JSON 格式

在线验证：[JSONLint](https://jsonlint.com/)

### 测试各 MCP

重启 Claude Desktop 后，测试各项功能：

**GitHub**:
```
你: 查看我的 GitHub 仓库列表
```

**PostgreSQL**:
```
你: 查询数据库中的所有表
```

**Docker**:
```
你: 列出所有 Docker 容器
```

**Puppeteer**:
```
你: 访问 http://localhost:5000 并截图
```

**Slack**:
```
你: 发送测试消息到 Slack
```

---

## 故障排除

### 问题 1：MCP 服务器未启动

**症状**：Claude 提示 "MCP 服务器不可用"

**解决方案**：
1. 检查配置文件路径是否正确
2. 检查 JSON 格式是否有效
3. 确保已完全重启 Claude Desktop
4. 查看 Claude Desktop 日志（Help → View Logs）

---

### 问题 2：GitHub MCP 认证失败

**症状**：`Authentication failed`

**解决方案**：
1. 检查 token 是否正确复制（无额外空格）
2. 确认 token 权限包含 `repo`
3. 测试 token：
```bash
curl -H "Authorization: token ghp_your_token" \
  https://api.github.com/user
```

---

### 问题 3：PostgreSQL MCP 连接失败

**症状**：`could not connect to server`

**解决方案**：
1. 检查 PostgreSQL 是否运行：
```bash
docker ps | grep postgres
```

2. 测试连接字符串：
```bash
psql "postgresql://postgres:changeme123@localhost:5432/aitradegame"
```

3. 检查端口 5432 是否开放：
```bash
netstat -an | grep 5432
```

---

### 问题 4：npx 命令未找到

**症状**：`npx: command not found`

**解决方案**：
1. 安装 Node.js：[nodejs.org](https://nodejs.org/)
2. 验证安装：
```bash
node --version
npm --version
npx --version
```

---

### 问题 5：Slack MCP 无法发送消息

**症状**：消息未出现在 Slack

**解决方案**：
1. 确认 Bot 已加入频道：
   - 在 Slack 频道输入 `/invite @YourBotName`
2. 检查 Bot 权限
3. 测试 token：
```bash
curl -X POST -H "Authorization: Bearer xoxb-your-token" \
  -H "Content-Type: application/json" \
  -d '{"channel":"C1234567890","text":"Test"}' \
  https://slack.com/api/chat.postMessage
```

---

## 最小配置（仅核心功能）

如果只需要核心功能，可以使用简化配置：

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
    "docker": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-docker"]
    }
  }
}
```

这样只配置 GitHub 和 Docker MCP，其他功能可以后续添加。

---

## 安全建议

### 1. 保护配置文件

```bash
# Windows (PowerShell)
icacls "$env:APPDATA\Claude\claude_desktop_config.json" /grant:r "$($env:USERNAME):(R,W)"

# macOS/Linux
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 2. 使用环境变量（高级）

对于更安全的配置，可以使用环境变量：

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

然后在系统环境变量中设置 `GITHUB_TOKEN`。

### 3. 定期轮换 Tokens

建议每 90 天轮换一次 API tokens。

### 4. 限制权限

只授予必需的最小权限：
- GitHub token：仅 `repo` 权限
- Slack Bot：仅 `chat:write` 权限
- PostgreSQL：只读用户（如果只需查询）

---

## 相关资源

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [Claude Desktop 文档](https://claude.ai/docs)
- [MCP 服务器列表](https://github.com/modelcontextprotocol/servers)

---

## 总结

配置完成后，你将拥有以下能力：

| MCP | 状态 | 功能 |
|-----|------|------|
| ✅ GitHub | 必需 | 代码管理 |
| ✅ PostgreSQL | 推荐 | 数据库管理 |
| ✅ Docker | 推荐 | 容器管理 |
| ✅ Puppeteer | 推荐 | UI 测试 |
| 🔔 Slack | 可选 | 告警通知 |
| 📁 Filesystem | 可选 | 文件操作 |
| 🧠 Memory | 可选 | 长期记忆 |

**下一步**：配置完成后，开始使用这些功能提升开发效率！

---

**需要帮助？** 在 [GitHub Issues](https://github.com/sher1096/ai-trading-game-enhanced/issues) 提问
