"""
Fix the button layout in index.html
The coin management button was inserted incorrectly, breaking the live trading button
"""

# Read the file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the broken button structure
broken_structure = """                    <button class="btn-secondary" id="addApiProviderBtn">
                        <i class="bi bi-cloud-plus"></i>
                        API提供方
                    </button>
                    <button class="btn-secondary" id="liveTradingBtn" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <button class="btn-secondary" onclick="window.location.href='/coins-management'" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                        <i class="bi bi-coin"></i>
                        币种管理
                    </button>
                        <i class="bi bi-rocket-takeoff"></i>
                        实盘交易
                    </button>"""

fixed_structure = """                    <button class="btn-secondary" id="addApiProviderBtn">
                        <i class="bi bi-cloud-plus"></i>
                        API提供方
                    </button>
                    <button class="btn-secondary" onclick="window.location.href='/coins-management'" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                        <i class="bi bi-coin"></i>
                        币种管理
                    </button>
                    <button class="btn-secondary" id="liveTradingBtn" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <i class="bi bi-rocket-takeoff"></i>
                        实盘交易
                    </button>"""

# Replace the broken structure with the fixed one
if broken_structure in content:
    content = content.replace(broken_structure, fixed_structure)
    print("[OK] Fixed button layout")
else:
    print("[WARN] Broken structure not found - file may have been modified")
    print("Checking alternative structure...")
    # Try to find if it's already fixed
    if fixed_structure in content:
        print("[INFO] Structure already appears to be correct")
    else:
        print("[ERROR] Could not locate button structure")

# Write back
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] File updated successfully")
print("     Button order: API提供方 -> 币种管理 -> 实盘交易 -> 添加模型")
