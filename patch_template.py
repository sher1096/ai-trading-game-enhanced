"""
Patch index.html to add strategy selection
"""

# 读取文件
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 在初始资金字段后添加策略选择和自定义提示词字段
old_html = '''                <div class="form-group">
                    <label>初始资金</label>
                    <input type="number" id="initialCapital" value="100000" class="form-input">
                </div>
            </div>
            <div class="modal-footer">'''

new_html = '''                <div class="form-group">
                    <label>初始资金</label>
                    <input type="number" id="initialCapital" value="100000" class="form-input">
                </div>
                <div class="form-group">
                    <label>技术指标策略（可选）</label>
                    <select id="strategyName" class="form-input">
                        <option value="None">None - 纯AI决策</option>
                        <option value="MovingAverage">MovingAverage - 移动平均线</option>
                        <option value="RSI">RSI - 相对强弱指标</option>
                        <option value="MACD">MACD - 平滑异同移动平均线</option>
                        <option value="Combined">Combined - 组合策略</option>
                    </select>
                    <small class="form-help">选择技术指标策略作为AI决策参考</small>
                </div>
                <div class="form-group">
                    <label>自定义提示词（可选）</label>
                    <textarea id="customPrompt" class="form-input" rows="4" placeholder="输入自定义交易策略描述，AI将根据这个描述做决策..."></textarea>
                    <small class="form-help">留空使用默认提示词</small>
                </div>
            </div>
            <div class="modal-footer">'''

content = content.replace(old_html, new_html)

# 修改提交模型的JavaScript代码
old_js = '''        // Submit model
        document.getElementById('submitBtn').addEventListener('click', () => {
            const providerId = document.getElementById('modelProvider').value;
            const modelIdentifier = document.getElementById('modelIdentifier').value;
            const modelName = document.getElementById('modelName').value;
            const initialCapital = document.getElementById('initialCapital').value;

            if (!providerId || !modelIdentifier || !modelName) {
                alert('请填写所有必填项');
                return;
            }

            const payload = {
                provider_id: parseInt(providerId),
                model_name: modelIdentifier,
                name: modelName,
                initial_capital: parseFloat(initialCapital)
            };'''

new_js = '''        // Submit model
        document.getElementById('submitBtn').addEventListener('click', () => {
            const providerId = document.getElementById('modelProvider').value;
            const modelIdentifier = document.getElementById('modelIdentifier').value;
            const modelName = document.getElementById('modelName').value;
            const initialCapital = document.getElementById('initialCapital').value;
            const strategyName = document.getElementById('strategyName').value;
            const customPrompt = document.getElementById('customPrompt').value;

            if (!providerId || !modelIdentifier || !modelName) {
                alert('请填写所有必填项');
                return;
            }

            const payload = {
                provider_id: parseInt(providerId),
                model_name: modelIdentifier,
                name: modelName,
                initial_capital: parseFloat(initialCapital),
                strategy_name: strategyName || 'None',
                custom_prompt: customPrompt || null
            };'''

content = content.replace(old_js, new_js)

# 写回文件
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] index.html has been patched!")
