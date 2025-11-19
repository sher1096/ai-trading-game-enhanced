# AI Trading Game - Enhanced Version

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

🤖 **AI-Powered Cryptocurrency Trading System** with Multi-Model Support, Advanced Technical Analysis, and Live Trading Capabilities.

## ✨ Key Features

- 🧠 **Multi-AI Support**: OpenAI GPT-4, DeepSeek, Claude, Ollama (Qwen)
- 💰 **Dynamic Coin Management**: 100+ cryptocurrencies with database-driven configuration
- 📚 **11 Trading Knowledge Modules**: Risk management, technical analysis, candlestick patterns
- 📊 **28 Candlestick Pattern Recognition**: Automated technical analysis
- 🔴 **Live Trading**: Binance, OKX exchange integration
- 🎨 **Modern Web UI**: Real-time charts with ECharts
- 🐳 **Docker Ready**: Production deployment with Nginx + Gunicorn
- 🧪 **Comprehensive Testing**: Integration tests and unit tests

## 🚀 Quick Start

### Option 1: Direct Run (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/sher1096/ai-trading-game-enhanced.git
cd ai-trading-game-enhanced

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python app.py

# 4. Open browser
http://localhost:5000
```

### Option 2: Docker Deployment (Recommended for Production)

```bash
# 1. Using Docker Compose
docker-compose up -d

# 2. Access application
http://localhost:5000
```

## 📖 Documentation

- [English README](README.md)
- [中文文档](README_ZH.md)
- [Technical Design](TECHNICAL_DESIGN.md)
- [Trading Knowledge Guide](TRADING_KNOWLEDGE_GUIDE.md)
- [Live Trading Setup](README_LIVE_TRADING.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [AI Models Guide 2025](AI_MODELS_2025_LATEST.md)

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Flask 3.0, SQLAlchemy |
| **AI Integration** | OpenAI API, Anthropic Claude, DeepSeek |
| **Trading** | CCXT (Binance, OKX), Pandas, NumPy |
| **Deployment** | Docker, Nginx, Gunicorn |
| **Database** | SQLite (dev), PostgreSQL (production) |
| **Frontend** | HTML5, JavaScript, ECharts |

## 📊 System Architecture

```
┌─────────────────────────────────────────────────┐
│           Web UI (Flask + ECharts)              │
├─────────────────────────────────────────────────┤
│  AI Trading Engine                              │
│  ├─ Multi-Model Support                         │
│  ├─ 11 Knowledge Modules                        │
│  └─ Decision Analysis                           │
├─────────────────────────────────────────────────┤
│  Trading Engine                                 │
│  ├─ Dynamic Coin Management                     │
│  ├─ Advanced Indicators                         │
│  └─ Candlestick Pattern Recognition             │
├─────────────────────────────────────────────────┤
│  Exchange Connectors                            │
│  ├─ Binance API                                 │
│  ├─ OKX API                                     │
│  └─ Market Data Aggregation                     │
└─────────────────────────────────────────────────┘
```

## 🎯 Use Cases

### 1️⃣ AI Model Comparison
- Test different AI models with same strategy
- Compare decision-making patterns
- Analyze performance metrics

### 2️⃣ Strategy Development
- Natural language strategy definition
- Knowledge module injection
- Backtesting and optimization

### 3️⃣ Live Trading
- Automated 24/7 trading
- Risk management
- Real-time alerts

### 4️⃣ Learning & Research
- Study AI trading behavior
- Understand technical analysis
- Experiment with different approaches

## 🔐 Security & Risk Warning

⚠️ **IMPORTANT DISCLAIMERS**:

1. **Trading Risk**: Cryptocurrency trading involves substantial risk of loss. Never invest more than you can afford to lose.

2. **AI Limitations**: AI models can make mistakes. Always monitor trading activity and use proper risk management.

3. **API Security**:
   - Never commit `.env` files with API keys
   - Use API keys with restricted permissions
   - Enable IP whitelisting on exchanges

4. **Start Small**: Always test with small amounts first in simulation mode before live trading.

## 🧪 Testing

```bash
# Run integration tests
python integration_test.py

# Run specific test suite
python test_trading_engine.py
python test_knowledge_modules.py

# Check database schema
python check_schema.py
```

## 📈 Performance Metrics

The system tracks comprehensive metrics:
- Win Rate & Profit/Loss Ratio
- Sharpe Ratio & Maximum Drawdown
- Total Trades & Success Rate
- Account Value History

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- OpenAI, Anthropic, DeepSeek for AI APIs
- CCXT for unified exchange API
- Flask and Python community

## 📞 Support

- 📖 [Documentation](TECHNICAL_DESIGN.md)
- 🐛 [Issue Tracker](https://github.com/sher1096/ai-trading-game-enhanced/issues)
- 💬 [Discussions](https://github.com/sher1096/ai-trading-game-enhanced/discussions)

---

**⭐ Star this repo if you find it useful!**

Made with ❤️ by AI Trading Community
