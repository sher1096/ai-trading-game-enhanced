# 交易告警系统集成指南

本指南介绍如何配置 Slack、Discord 和邮件告警，实时接收交易系统的重要通知。

## 📋 目录

1. [Slack 告警配置](#slack-告警配置)
2. [Discord 告警配置](#discord-告警配置)
3. [邮件告警配置](#邮件告警配置)
4. [告警代码集成](#告警代码集成)
5. [告警规则配置](#告警规则配置)
6. [告警最佳实践](#告警最佳实践)

---

## Slack 告警配置

### 方式 1：使用 Slack MCP（推荐）

#### 步骤 1：创建 Slack App

1. 访问 [Slack API Apps](https://api.slack.com/apps)
2. 点击 **"Create New App"** → **"From scratch"**
3. 输入应用名称（如 "AI Trading Alerts"）
4. 选择工作区

#### 步骤 2：配置权限

在 "OAuth & Permissions" 页面添加以下权限：
- `chat:write` - 发送消息
- `chat:write.public` - 发送到公共频道
- `channels:read` - 读取频道列表
- `users:read` - 读取用户信息

点击 **"Install to Workspace"** 安装应用。

#### 步骤 3：获取 Token

安装完成后，复制 **"Bot User OAuth Token"**（格式：`xoxb-...`）

#### 步骤 4：配置 Claude Desktop MCP

编辑 `%APPDATA%\Claude\claude_desktop_config.json`:

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
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token-here",
        "SLACK_TEAM_ID": "T1234567890"
      }
    }
  }
}
```

#### 步骤 5：获取 Team ID

```bash
# 使用 Slack API 测试工具
curl -H "Authorization: Bearer xoxb-your-token" \
  https://slack.com/api/team.info

# 或在浏览器访问你的 Slack workspace，URL 中包含 Team ID
# https://app.slack.com/client/T1234567890/...
```

#### 步骤 6：重启 Claude Desktop

配置完成后，重启 Claude Desktop。

#### 步骤 7：测试 Slack MCP

重启后，你可以要求 Claude：
- "发送测试消息到 Slack #trading-alerts 频道"
- "在交易失败时通知我"
- "每天早上 9 点发送交易报告"

---

### 方式 2：直接使用 Slack Webhook

如果不使用 MCP，可以直接用 Webhook。

#### 创建 Incoming Webhook

1. 访问 [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
2. 点击 **"Create your Slack app"**
3. 启用 "Incoming Webhooks"
4. 点击 **"Add New Webhook to Workspace"**
5. 选择频道（如 #trading-alerts）
6. 复制 Webhook URL（格式：`https://hooks.slack.com/services/T.../B.../...`）

#### 测试 Webhook

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Hello from AI Trading Game! 🤖"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## Discord 告警配置

### 方式 1：使用 Discord Webhook（最简单）

#### 步骤 1：创建 Webhook

1. 打开 Discord，进入你的服务器
2. 右键点击频道 → **编辑频道**
3. 左侧菜单选择 **整合** → **Webhook**
4. 点击 **"新建 Webhook"**
5. 设置名称（如 "Trading Alerts"）和头像
6. 复制 Webhook URL（格式：`https://discord.com/api/webhooks/...`）
7. 保存更改

#### 步骤 2：测试 Webhook

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from AI Trading Game! 🚀"}' \
  https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

#### 步骤 3：发送嵌入消息（更美观）

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "embeds": [{
      "title": "🔴 交易告警",
      "description": "BTC 价格突破 $50,000!",
      "color": 16711680,
      "fields": [
        {"name": "模型", "value": "Conservative AI", "inline": true},
        {"name": "操作", "value": "买入", "inline": true},
        {"name": "数量", "value": "0.1 BTC", "inline": true}
      ],
      "timestamp": "2023-11-20T10:30:00.000Z"
    }]
  }' \
  https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

---

### 方式 2：使用 Discord Bot

更高级的功能（交互按钮、斜杠命令等）。

#### 步骤 1：创建 Discord Bot

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击 **"New Application"**
3. 输入名称（如 "AI Trading Bot"）
4. 在 **"Bot"** 页面点击 **"Add Bot"**
5. 复制 **Token**（格式：`MTAy...`）

#### 步骤 2：邀请 Bot 到服务器

1. 在 **"OAuth2"** → **"URL Generator"**
2. 勾选 **"bot"** scope
3. 权限勾选：
   - Send Messages
   - Embed Links
   - Attach Files
4. 复制生成的 URL 并在浏览器打开
5. 选择服务器并授权

#### 步骤 3：配置环境变量

在 `.env` 文件中添加:

```bash
# Discord
DISCORD_BOT_TOKEN=MTAy...your-bot-token
DISCORD_CHANNEL_ID=1234567890  # 频道 ID（右键频道 → 复制 ID）
```

---

## 邮件告警配置

### 使用 Gmail SMTP

#### 步骤 1：启用 Gmail App Password

1. 访问 [Google Account Security](https://myaccount.google.com/security)
2. 启用 **"两步验证"**
3. 访问 [App Passwords](https://myaccount.google.com/apppasswords)
4. 生成应用专用密码（选择 "Mail" 和 "Other"）
5. 复制 16 位密码（如 `abcd efgh ijkl mnop`）

#### 步骤 2：配置环境变量

在 `.env` 文件中添加:

```bash
# 邮件告警
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # 应用专用密码
ALERT_EMAIL=your-email@gmail.com    # 接收告警的邮箱
```

#### 步骤 3：测试邮件发送

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_test_email():
    msg = MIMEMultipart()
    msg['From'] = 'your-email@gmail.com'
    msg['To'] = 'your-email@gmail.com'
    msg['Subject'] = 'AI Trading Game - 测试告警'

    body = '''
    这是一封测试邮件！

    如果你收到这封邮件，说明告警系统配置成功。
    '''
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-app-password')
    server.send_message(msg)
    server.quit()

    print('✅ 测试邮件已发送！')

send_test_email()
```

---

## 告警代码集成

### 创建告警管理器

创建 `alert_manager.py`:

```python
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any

class AlertManager:
    """统一的告警管理器，支持 Slack、Discord 和邮件"""

    def __init__(self):
        # Slack 配置
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')

        # Discord 配置
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')

        # 邮件配置
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.alert_email = os.getenv('ALERT_EMAIL')

    def send_alert(self, alert_type: str, message: str, data: Dict[str, Any] = None):
        """发送告警到所有配置的渠道"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 发送到 Slack
        if self.slack_webhook:
            self._send_slack(alert_type, message, data, timestamp)

        # 发送到 Discord
        if self.discord_webhook:
            self._send_discord(alert_type, message, data, timestamp)

        # 发送邮件
        if self.smtp_server and self.alert_email:
            self._send_email(alert_type, message, data, timestamp)

    def _send_slack(self, alert_type: str, message: str, data: Dict, timestamp: str):
        """发送 Slack 消息"""
        emoji = self._get_emoji(alert_type)
        color = self._get_color(alert_type)

        payload = {
            "attachments": [{
                "color": color,
                "title": f"{emoji} {alert_type.upper()}",
                "text": message,
                "fields": self._format_fields(data),
                "footer": "AI Trading Game",
                "ts": int(datetime.now().timestamp())
            }]
        }

        try:
            response = requests.post(self.slack_webhook, json=payload)
            response.raise_for_status()
            print(f"✅ Slack 告警已发送: {alert_type}")
        except Exception as e:
            print(f"❌ Slack 告警发送失败: {e}")

    def _send_discord(self, alert_type: str, message: str, data: Dict, timestamp: str):
        """发送 Discord 消息"""
        emoji = self._get_emoji(alert_type)
        color = int(self._get_color(alert_type).replace('#', ''), 16)

        payload = {
            "embeds": [{
                "title": f"{emoji} {alert_type.upper()}",
                "description": message,
                "color": color,
                "fields": [
                    {"name": k, "value": str(v), "inline": True}
                    for k, v in (data or {}).items()
                ],
                "footer": {"text": "AI Trading Game"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }

        try:
            response = requests.post(self.discord_webhook, json=payload)
            response.raise_for_status()
            print(f"✅ Discord 告警已发送: {alert_type}")
        except Exception as e:
            print(f"❌ Discord 告警发送失败: {e}")

    def _send_email(self, alert_type: str, message: str, data: Dict, timestamp: str):
        """发送邮件告警"""
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = self.alert_email
        msg['Subject'] = f'[AI Trading] {alert_type.upper()} - {timestamp}'

        body = f"""
        <html>
          <body>
            <h2>{self._get_emoji(alert_type)} {alert_type.upper()}</h2>
            <p>{message}</p>
            <hr>
            <table border="1" cellpadding="5">
              <tr style="background-color: #f2f2f2">
                <th>属性</th>
                <th>值</th>
              </tr>
              {''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in (data or {}).items())}
            </table>
            <hr>
            <p style="color: gray;">时间: {timestamp}</p>
          </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            print(f"✅ 邮件告警已发送: {alert_type}")
        except Exception as e:
            print(f"❌ 邮件告警发送失败: {e}")

    @staticmethod
    def _get_emoji(alert_type: str) -> str:
        """根据告警类型返回 emoji"""
        emojis = {
            'trade': '💰',
            'profit': '📈',
            'loss': '📉',
            'error': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️',
            'stop_loss': '🔻',
            'take_profit': '🎯',
            'daily_report': '📊'
        }
        return emojis.get(alert_type.lower(), '🔔')

    @staticmethod
    def _get_color(alert_type: str) -> str:
        """根据告警类型返回颜色"""
        colors = {
            'trade': '#36a64f',      # 绿色
            'profit': '#2ecc71',     # 亮绿色
            'loss': '#e74c3c',       # 红色
            'error': '#c0392b',      # 深红色
            'warning': '#f39c12',    # 橙色
            'info': '#3498db',       # 蓝色
            'stop_loss': '#e67e22',  # 橙红色
            'take_profit': '#27ae60' # 深绿色
        }
        return colors.get(alert_type.lower(), '#95a5a6')

    @staticmethod
    def _format_fields(data: Dict) -> list:
        """格式化为 Slack fields"""
        if not data:
            return []
        return [
            {"title": k, "value": str(v), "short": True}
            for k, v in data.items()
        ]


# 全局单例
alert_manager = AlertManager()
```

---

## 告警规则配置

### 在交易引擎中集成告警

修改 `trading_engine.py`，添加告警:

```python
from alert_manager import alert_manager

class TradingEngine:
    def execute_trade(self, model, decision):
        # ... 执行交易逻辑 ...

        # 🔔 发送交易告警
        alert_manager.send_alert(
            alert_type='trade',
            message=f"模型 {model.name} 执行了 {decision['action']} 操作",
            data={
                '模型': model.name,
                '操作': decision['action'],
                '币种': decision['symbol'],
                '数量': decision['amount'],
                '价格': current_price,
                'AI 理由': decision['reasoning'][:100]
            }
        )

    def check_stop_loss(self, model, position):
        current_pnl = self.calculate_pnl(position)

        if current_pnl < -model.stop_loss_threshold:
            # 🚨 触发止损告警
            alert_manager.send_alert(
                alert_type='stop_loss',
                message=f"⚠️ 模型 {model.name} 触发止损！",
                data={
                    '模型': model.name,
                    '币种': position.symbol,
                    '当前亏损': f'{current_pnl:.2f}%',
                    '止损阈值': f'{model.stop_loss_threshold}%',
                    '建议': '立即平仓'
                }
            )

            # 执行止损...

    def handle_error(self, error, context):
        # 🚨 发送错误告警
        alert_manager.send_alert(
            alert_type='error',
            message=f"系统错误: {str(error)}",
            data={
                '错误类型': type(error).__name__,
                '错误信息': str(error),
                '上下文': context,
                '时间': datetime.now().isoformat()
            }
        )
```

### 每日报告定时任务

在 `app.py` 中添加定时任务:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from alert_manager import alert_manager

def send_daily_report():
    """生成并发送每日交易报告"""
    # 查询今日交易数据
    today_trades = TradeHistory.query.filter(
        TradeHistory.timestamp >= datetime.now().date()
    ).all()

    total_pnl = sum(trade.pnl for trade in today_trades)
    win_rate = len([t for t in today_trades if t.pnl > 0]) / len(today_trades) * 100 if today_trades else 0

    # 发送报告
    alert_manager.send_alert(
        alert_type='daily_report',
        message=f"今日交易报告 - {datetime.now().date()}",
        data={
            '总交易次数': len(today_trades),
            '盈利次数': len([t for t in today_trades if t.pnl > 0]),
            '亏损次数': len([t for t in today_trades if t.pnl < 0]),
            '胜率': f'{win_rate:.2f}%',
            '总盈亏': f'${total_pnl:.2f}',
            '最佳模型': get_best_model_today(),
            '最差模型': get_worst_model_today()
        }
    )

# 启动定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_report, 'cron', hour=20, minute=0)  # 每天晚上8点
scheduler.start()
```

---

## 告警规则示例

### 重要盈亏告警

```python
def check_significant_pnl(model, pnl_percent):
    """检查重要的盈亏变化"""
    if abs(pnl_percent) >= 5:  # 超过 5% 告警
        alert_type = 'profit' if pnl_percent > 0 else 'loss'
        alert_manager.send_alert(
            alert_type=alert_type,
            message=f"{'📈 大幅盈利' if pnl_percent > 0 else '📉 显著亏损'}！",
            data={
                '模型': model.name,
                '盈亏比例': f'{pnl_percent:+.2f}%',
                '当前资金': f'${model.current_capital:.2f}',
                '初始资金': f'${model.initial_capital:.2f}'
            }
        )
```

### 异常活动告警

```python
def check_abnormal_activity(model):
    """检测异常交易活动"""
    recent_trades = get_recent_trades(model, hours=1)

    if len(recent_trades) > 10:  # 1小时内超过10次交易
        alert_manager.send_alert(
            alert_type='warning',
            message=f"⚠️ 检测到异常高频交易！",
            data={
                '模型': model.name,
                '1小时内交易次数': len(recent_trades),
                '建议': '检查策略逻辑或暂停交易'
            }
        )
```

### 余额不足告警

```python
def check_balance(model):
    """检查账户余额"""
    if model.current_capital < model.initial_capital * 0.5:
        alert_manager.send_alert(
            alert_type='warning',
            message=f"⚠️ 账户余额已低于初始资金的 50%！",
            data={
                '模型': model.name,
                '当前余额': f'${model.current_capital:.2f}',
                '初始资金': f'${model.initial_capital:.2f}',
                '亏损比例': f'{((model.current_capital / model.initial_capital - 1) * 100):.2f}%'
            }
        )
```

---

## 告警最佳实践

### 1. 避免告警疲劳

❌ **不好**：每次交易都发送告警
```python
# 这会导致大量无用告警
if trade.execute():
    alert_manager.send_alert(...)  # 太频繁！
```

✅ **好**：仅重要事件告警
```python
# 仅在重要情况下告警
if trade.pnl_percent > 5 or trade.pnl_percent < -3:
    alert_manager.send_alert(...)
```

### 2. 告警优先级

```python
ALERT_PRIORITIES = {
    'critical': ['error', 'stop_loss'],
    'high': ['loss', 'warning'],
    'medium': ['trade', 'profit'],
    'low': ['info', 'daily_report']
}

# 根据优先级设置不同的通知渠道
def send_alert_by_priority(alert_type, message, data):
    priority = get_priority(alert_type)

    if priority == 'critical':
        # 发送到所有渠道 + 短信
        alert_manager.send_alert(alert_type, message, data)
        send_sms(message)
    elif priority == 'high':
        # 发送到 Slack 和邮件
        alert_manager._send_slack(...)
        alert_manager._send_email(...)
    else:
        # 仅发送到 Slack
        alert_manager._send_slack(...)
```

### 3. 告警去重

```python
from datetime import timedelta

class AlertManager:
    def __init__(self):
        self.alert_cache = {}

    def send_alert(self, alert_type, message, data):
        # 生成唯一键
        cache_key = f"{alert_type}:{message[:50]}"

        # 检查是否在5分钟内发送过相同告警
        if cache_key in self.alert_cache:
            last_sent = self.alert_cache[cache_key]
            if datetime.now() - last_sent < timedelta(minutes=5):
                print(f"⏭️ 跳过重复告警: {alert_type}")
                return

        # 发送告警
        self._send_slack(...)
        self._send_discord(...)
        self._send_email(...)

        # 更新缓存
        self.alert_cache[cache_key] = datetime.now()
```

### 4. 告警聚合

```python
# 每小时聚合一次小额交易告警
small_trades_buffer = []

def aggregate_small_trades():
    if len(small_trades_buffer) > 0:
        alert_manager.send_alert(
            alert_type='info',
            message=f"过去1小时内执行了 {len(small_trades_buffer)} 笔小额交易",
            data={
                '总交易数': len(small_trades_buffer),
                '总盈亏': sum(t.pnl for t in small_trades_buffer),
                '详情': '查看交易历史'
            }
        )
        small_trades_buffer.clear()

# 定时执行聚合
scheduler.add_job(aggregate_small_trades, 'interval', hours=1)
```

---

## 完整配置检查清单

### 环境变量配置

在 `.env` 文件中添加:

```bash
# ==================== 告警配置 ====================

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# 邮件
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=your-email@gmail.com

# 告警规则
ALERT_MIN_PNL_PERCENT=5         # 最小盈亏百分比才告警
ALERT_DEDUP_MINUTES=5           # 去重时间（分钟）
ALERT_DAILY_REPORT_TIME=20:00   # 每日报告时间
```

### 测试告警系统

创建 `test_alerts.py`:

```python
from alert_manager import alert_manager

def test_all_alerts():
    """测试所有告警渠道"""

    # 测试交易告警
    alert_manager.send_alert(
        alert_type='trade',
        message='测试交易告警',
        data={'测试': 'OK'}
    )

    # 测试盈利告警
    alert_manager.send_alert(
        alert_type='profit',
        message='测试盈利告警',
        data={'盈利': '+10%'}
    )

    # 测试错误告警
    alert_manager.send_alert(
        alert_type='error',
        message='测试错误告警',
        data={'错误': '这是一个测试'}
    )

    print("✅ 所有告警已发送，请检查 Slack/Discord/邮箱")

if __name__ == '__main__':
    test_all_alerts()
```

运行测试:
```bash
python test_alerts.py
```

---

## 相关资源

- [Slack API 文档](https://api.slack.com/messaging/webhooks)
- [Discord Webhooks 文档](https://discord.com/developers/docs/resources/webhook)
- [Python smtplib 文档](https://docs.python.org/3/library/smtplib.html)
- [APScheduler 文档](https://apscheduler.readthedocs.io/)

---

**需要帮助？** 在 [GitHub Issues](https://github.com/sher1096/ai-trading-game-enhanced/issues) 提问
