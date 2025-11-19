# Web UI 自动化测试指南

本指南介绍如何使用 Puppeteer 和 Puppeteer MCP 进行 Web UI 自动化测试。

## 📋 目录

1. [Puppeteer MCP 配置](#puppeteer-mcp-配置)
2. [手动测试脚本](#手动测试脚本)
3. [测试用例示例](#测试用例示例)
4. [截图对比测试](#截图对比测试)
5. [性能测试](#性能测试)
6. [CI/CD 集成](#cicd-集成)

---

## Puppeteer MCP 配置

### 步骤 1：配置 Claude Desktop

编辑 `%APPDATA%\Claude\claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

### 步骤 2：重启 Claude Desktop

完全关闭并重启。

### 步骤 3：测试 Puppeteer MCP

重启后，你可以要求 Claude：

- **基本操作**:
  - "访问 http://localhost:5000 并截图"
  - "检查页面标题是否包含 'AI Trading Game'"
  - "查找页面中的所有按钮"

- **交互测试**:
  - "点击'添加 AI 提供方'按钮"
  - "填写表单并提交"
  - "测试登录流程"

- **截图和对比**:
  - "截取整个页面的屏幕截图"
  - "对比当前页面与上次截图的差异"

---

## 手动测试脚本

如果不使用 MCP，可以直接运行测试脚本。

### 安装依赖

```bash
# 安装 Node.js 和 npm (如果还没有)
# Windows: 下载 https://nodejs.org/

# 安装 Puppeteer
npm install puppeteer

# 或使用 Python 版本
pip install pyppeteer
```

### 基础测试脚本（Node.js）

创建 `tests/ui_test.js`:

```javascript
const puppeteer = require('puppeteer');

(async () => {
  // 启动浏览器
  const browser = await puppeteer.launch({
    headless: false,  // 显示浏览器窗口
    slowMo: 50        // 减慢操作速度，便于观察
  });

  const page = await browser.newPage();

  try {
    console.log('📍 访问应用首页...');
    await page.goto('http://localhost:5000', {
      waitUntil: 'networkidle2'
    });

    console.log('📸 截取首页截图...');
    await page.screenshot({ path: 'screenshots/homepage.png', fullPage: true });

    console.log('✅ 检查页面标题...');
    const title = await page.title();
    console.log(`页面标题: ${title}`);

    console.log('🔍 查找关键元素...');
    const elements = {
      addProviderBtn: await page.$('button:contains("添加 AI 提供方")') !== null,
      addModelBtn: await page.$('button:contains("添加模型")') !== null,
      dashboard: await page.$('.dashboard') !== null
    };
    console.log('页面元素检查:', elements);

    console.log('✅ 测试通过！');
  } catch (error) {
    console.error('❌ 测试失败:', error);
  } finally {
    await browser.close();
  }
})();
```

运行测试:
```bash
node tests/ui_test.js
```

### 基础测试脚本（Python）

创建 `tests/ui_test.py`:

```python
import asyncio
from pyppeteer import launch

async def test_homepage():
    # 启动浏览器
    browser = await launch({
        'headless': False,  # 显示浏览器
        'slowMo': 50
    })

    page = await browser.newPage()

    try:
        print('📍 访问应用首页...')
        await page.goto('http://localhost:5000', {
            'waitUntil': 'networkidle2'
        })

        print('📸 截取首页截图...')
        await page.screenshot({'path': 'screenshots/homepage.png', 'fullPage': True})

        print('✅ 检查页面标题...')
        title = await page.title()
        print(f'页面标题: {title}')

        print('🔍 查找关键元素...')
        add_provider_btn = await page.querySelector('button')
        print(f'找到按钮: {add_provider_btn is not None}')

        print('✅ 测试通过！')
    except Exception as e:
        print(f'❌ 测试失败: {e}')
    finally:
        await browser.close()

# 运行测试
asyncio.get_event_loop().run_until_complete(test_homepage())
```

运行测试:
```bash
python tests/ui_test.py
```

---

## 测试用例示例

### 测试 1：添加 AI 提供方

```javascript
async function testAddProvider() {
  const page = await browser.newPage();
  await page.goto('http://localhost:5000');

  // 点击"添加 AI 提供方"按钮
  await page.click('button:contains("添加 AI 提供方")');

  // 等待模态框出现
  await page.waitForSelector('#providerModal');

  // 填写表单
  await page.type('#providerName', 'TestProvider');
  await page.type('#providerApiKey', 'sk-test-key-123');
  await page.type('#providerBaseUrl', 'https://api.example.com/v1');

  // 提交表单
  await page.click('#submitProvider');

  // 等待成功消息
  await page.waitForSelector('.success-message');

  // 截图
  await page.screenshot({ path: 'screenshots/provider-added.png' });

  console.log('✅ 添加提供方测试通过');
}
```

### 测试 2：添加交易模型

```javascript
async function testAddModel() {
  const page = await browser.newPage();
  await page.goto('http://localhost:5000');

  // 点击"添加模型"
  await page.click('button:contains("添加模型")');

  // 填写模型信息
  await page.select('#providerSelect', '1');  // 选择提供方
  await page.type('#modelName', 'Test Model');
  await page.type('#initialCapital', '10000');

  // 填写策略提示词
  const prompt = `You are a conservative crypto trader.
  - Only trade BTC and ETH
  - Maximum 10% position per trade
  - Stop loss at 3%`;
  await page.type('#strategyPrompt', prompt);

  // 选择知识模块
  await page.click('input[value="risk_management"]');
  await page.click('input[value="technical_theory"]');

  // 提交
  await page.click('#submitModel');

  // 验证
  await page.waitForSelector('.model-card:contains("Test Model")');

  console.log('✅ 添加模型测试通过');
}
```

### 测试 3：查看交易历史

```javascript
async function testTradeHistory() {
  const page = await browser.newPage();
  await page.goto('http://localhost:5000');

  // 等待数据加载
  await page.waitForSelector('.model-card');

  // 点击某个模型查看详情
  await page.click('.model-card:first-child');

  // 等待交易历史加载
  await page.waitForSelector('#tradeHistoryChart');

  // 检查是否有数据
  const hasData = await page.evaluate(() => {
    const chart = document.querySelector('#tradeHistoryChart');
    return chart && chart.offsetHeight > 0;
  });

  console.log(`图表数据: ${hasData ? '有' : '无'}`);

  // 截图
  await page.screenshot({
    path: 'screenshots/trade-history.png',
    fullPage: true
  });

  console.log('✅ 交易历史测试通过');
}
```

### 完整测试套件

创建 `tests/full_test_suite.js`:

```javascript
const puppeteer = require('puppeteer');

async function runAllTests() {
  const browser = await puppeteer.launch({
    headless: false,
    slowMo: 50
  });

  const tests = [
    { name: '首页加载', fn: testHomepage },
    { name: '添加提供方', fn: testAddProvider },
    { name: '添加模型', fn: testAddModel },
    { name: '交易历史', fn: testTradeHistory },
    { name: '币种管理', fn: testCoinManagement },
    { name: '响应式设计', fn: testResponsive }
  ];

  const results = [];

  for (const test of tests) {
    try {
      console.log(`\n🧪 运行测试: ${test.name}`);
      await test.fn(browser);
      results.push({ name: test.name, status: 'PASS' });
      console.log(`✅ ${test.name} - 通过`);
    } catch (error) {
      results.push({ name: test.name, status: 'FAIL', error: error.message });
      console.error(`❌ ${test.name} - 失败:`, error);
    }
  }

  // 生成测试报告
  console.log('\n📊 测试报告:');
  console.table(results);

  await browser.close();
}

runAllTests();
```

---

## 截图对比测试

### 视觉回归测试

使用 `pixelmatch` 进行截图对比:

```bash
npm install pixelmatch pngjs
```

```javascript
const fs = require('fs');
const pixelmatch = require('pixelmatch');
const { PNG } = require('pngjs');

async function visualRegressionTest(page, name) {
  const screenshotPath = `screenshots/${name}.png`;
  const baselinePath = `screenshots/baseline/${name}.png`;
  const diffPath = `screenshots/diff/${name}.png`;

  // 截取当前页面
  await page.screenshot({ path: screenshotPath, fullPage: true });

  if (!fs.existsSync(baselinePath)) {
    // 第一次运行，保存为基准
    fs.copyFileSync(screenshotPath, baselinePath);
    console.log(`📸 保存基准截图: ${baselinePath}`);
    return { match: true, isBaseline: true };
  }

  // 加载图片
  const img1 = PNG.sync.read(fs.readFileSync(baselinePath));
  const img2 = PNG.sync.read(fs.readFileSync(screenshotPath));

  const { width, height } = img1;
  const diff = new PNG({ width, height });

  // 对比图片
  const numDiffPixels = pixelmatch(
    img1.data, img2.data, diff.data,
    width, height,
    { threshold: 0.1 }
  );

  // 保存差异图
  fs.writeFileSync(diffPath, PNG.sync.write(diff));

  const diffPercent = (numDiffPixels / (width * height) * 100).toFixed(2);

  console.log(`📊 像素差异: ${numDiffPixels} (${diffPercent}%)`);

  if (diffPercent > 1) {
    console.warn(`⚠️ 视觉差异超过阈值！查看: ${diffPath}`);
    return { match: false, diffPercent, diffPath };
  }

  return { match: true, diffPercent };
}
```

---

## 性能测试

### 页面加载性能

```javascript
async function performanceTest(page) {
  await page.goto('http://localhost:5000');

  const metrics = await page.metrics();
  const performance = await page.evaluate(() => {
    const timing = performance.timing;
    return {
      loadTime: timing.loadEventEnd - timing.navigationStart,
      domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
      firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
    };
  });

  console.log('📈 性能指标:');
  console.log(`  - 页面加载时间: ${performance.loadTime}ms`);
  console.log(`  - DOM 就绪时间: ${performance.domReady}ms`);
  console.log(`  - 首次绘制: ${performance.firstPaint}ms`);
  console.log(`  - JS 堆大小: ${(metrics.JSHeapUsedSize / 1024 / 1024).toFixed(2)}MB`);

  // 断言性能要求
  if (performance.loadTime > 3000) {
    console.warn('⚠️ 页面加载时间过长！');
  }

  return performance;
}
```

### Lighthouse 审计

```javascript
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');

async function runLighthouse() {
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });

  const options = {
    logLevel: 'info',
    output: 'html',
    port: chrome.port
  };

  const runnerResult = await lighthouse('http://localhost:5000', options);

  // 保存报告
  const reportHtml = runnerResult.report;
  fs.writeFileSync('lighthouse-report.html', reportHtml);

  // 输出分数
  const scores = runnerResult.lhr.categories;
  console.log('📊 Lighthouse 分数:');
  console.log(`  - 性能: ${scores.performance.score * 100}`);
  console.log(`  - 可访问性: ${scores.accessibility.score * 100}`);
  console.log(`  - 最佳实践: ${scores['best-practices'].score * 100}`);
  console.log(`  - SEO: ${scores.seo.score * 100}`);

  await chrome.kill();
}
```

---

## CI/CD 集成

### GitHub Actions 配置

创建 `.github/workflows/ui-tests.yml`:

```yaml
name: UI Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: |
        npm install puppeteer pixelmatch pngjs

    - name: Start application
      run: |
        docker-compose up -d
        sleep 10  # 等待应用启动

    - name: Run UI tests
      run: |
        node tests/full_test_suite.js

    - name: Upload screenshots
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: screenshots
        path: screenshots/

    - name: Stop application
      if: always()
      run: docker-compose down
```

### 测试报告生成

使用 `mochawesome` 生成美观的 HTML 报告:

```bash
npm install mocha mochawesome

# package.json
{
  "scripts": {
    "test": "mocha tests/**/*.test.js --reporter mochawesome"
  }
}
```

---

## 最佳实践

### 1. 稳定的选择器

```javascript
// ❌ 不好：依赖脆弱的选择器
await page.click('.btn-primary');

// ✅ 好：使用 data 属性
await page.click('[data-testid="add-provider-btn"]');

// ✅ 好：使用语义化选择器
await page.click('button[aria-label="添加 AI 提供方"]');
```

在 HTML 中添加 test IDs:
```html
<button data-testid="add-provider-btn" class="btn btn-primary">
  添加 AI 提供方
</button>
```

### 2. 等待策略

```javascript
// ❌ 不好：硬编码延迟
await page.waitFor(3000);

// ✅ 好：等待特定元素
await page.waitForSelector('#providerModal');

// ✅ 好：等待网络空闲
await page.goto(url, { waitUntil: 'networkidle2' });

// ✅ 好：等待自定义条件
await page.waitForFunction(() => {
  return document.querySelector('.loading') === null;
});
```

### 3. 错误处理

```javascript
async function robustTest(page) {
  try {
    await page.goto('http://localhost:5000', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });
  } catch (error) {
    // 截图保存错误状态
    await page.screenshot({ path: 'screenshots/error.png' });
    console.error('导航失败:', error);
    throw error;
  }
}
```

### 4. 清理和隔离

```javascript
describe('AI Trading Game Tests', () => {
  let browser, page;

  beforeEach(async () => {
    browser = await puppeteer.launch();
    page = await browser.newPage();
    // 清理 cookies 和 localStorage
    await page.evaluateOnNewDocument(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  afterEach(async () => {
    await browser.close();
  });

  it('should load homepage', async () => {
    await page.goto('http://localhost:5000');
    const title = await page.title();
    expect(title).toContain('AI Trading Game');
  });
});
```

---

## 调试技巧

### 1. 慢速模式

```javascript
const browser = await puppeteer.launch({
  headless: false,
  slowMo: 250  // 每个操作延迟 250ms
});
```

### 2. 截图调试

```javascript
await page.screenshot({ path: 'debug.png', fullPage: true });
```

### 3. 控制台日志

```javascript
page.on('console', msg => console.log('浏览器日志:', msg.text()));
page.on('pageerror', error => console.error('页面错误:', error));
```

### 4. DevTools 协议

```javascript
const client = await page.target().createCDPSession();
await client.send('Network.enable');
client.on('Network.responseReceived', ({ response }) => {
  console.log(`响应: ${response.url} - ${response.status}`);
});
```

---

## 相关资源

- [Puppeteer 官方文档](https://pptr.dev/)
- [Puppeteer 示例](https://github.com/puppeteer/puppeteer/tree/main/examples)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [Visual Regression Testing](https://github.com/garris/BackstopJS)

---

**需要帮助？** 在 [GitHub Issues](https://github.com/sher1096/ai-trading-game-enhanced/issues) 提问
