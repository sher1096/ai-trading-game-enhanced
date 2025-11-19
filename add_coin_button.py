"""
Add coin management button to index.html header
"""

# Read the file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the insertion point (after line 43 which contains "API提供方")
new_button = """                    <button class="btn-secondary" onclick="window.location.href='/coins-management'" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                        <i class="bi bi-coin"></i>
                        币种管理
                    </button>
"""

# Insert after line 43 (index 43 in zero-indexed array)
lines.insert(44, new_button)

# Write back
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("[OK] Successfully added coin management button to index.html")
print("     Button inserted between 'API提供方' and '实盘交易' buttons")
