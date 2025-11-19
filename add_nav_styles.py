"""
Add new navigation styles to style.css
"""

# Read the file
with open('static/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the position after .header-right { ... }
marker = """.header-right {
    display: flex;
    gap: 12px;
}"""

# Define the new styles to add
new_styles = """
/* Header组织 */
.header-actions-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.header-divider {
    width: 1px;
    height: 24px;
    background: var(--border-1);
}

/* Header导航 */
.header-nav {
    display: flex;
    align-items: center;
    gap: 4px;
}

.nav-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: var(--radius);
    color: var(--text-2);
    text-decoration: none;
    font-size: 14px;
    transition: all 0.2s;
    position: relative;
    border-bottom: 2px solid transparent;
}

.nav-link:hover {
    background: var(--bg-2);
    color: var(--text-1);
}

.nav-link.active {
    color: var(--primary);
    background: #e8f4ff;
}

.nav-link.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--primary);
}

/* Header菜单 */
.header-menu {
    position: relative;
}

.menu-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    min-width: 200px;
    background: var(--bg-1);
    border: 1px solid var(--border-1);
    border-radius: var(--radius);
    box-shadow: var(--shadow-3);
    padding: 8px;
    z-index: 1000;
}

.menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 6px;
    background: transparent;
    border: none;
    color: var(--text-2);
    font-size: 14px;
    width: 100%;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
}

.menu-item:hover {
    background: var(--bg-2);
    color: var(--text-1);
}

.menu-item i {
    font-size: 16px;
    width: 20px;
    text-align: center;
}
"""

# Add the new styles after .header-right
if marker in content:
    content = content.replace(marker, marker + new_styles)
    print("[OK] Navigation styles added successfully")

    # Write back
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(content)

    print("[OK] CSS file updated")
    print("\nAdded styles for:")
    print("  - header-actions-group")
    print("  - header-divider")
    print("  - header-nav and nav-link")
    print("  - header-menu and menu-dropdown")
else:
    print("[ERROR] Could not find marker in CSS file")
