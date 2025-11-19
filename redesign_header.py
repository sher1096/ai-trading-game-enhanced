"""
Redesign the header of index.html with better organization
"""

# Read the file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old header-right structure (lines 27-56)
old_header_right = """                <div class="header-right">
                    <div class="update-indicator" id="updateIndicator" style="display: none;">
                        <button class="btn-icon update-btn" id="checkUpdateBtn" title="检查更新">
                            <i class="bi bi-arrow-up-circle"></i>
                        </button>
                    </div>
                    <button class="btn-icon" id="refreshBtn" title="刷新">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                    <button class="btn-secondary" id="settingsBtn">
                        <i class="bi bi-gear"></i>
                        设置
                    </button>
                    <button class="btn-secondary" id="addApiProviderBtn">
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
                    </button>
                    <button class="btn-primary" id="addModelBtn">
                        <i class="bi bi-plus-lg"></i>
                        添加模型
                    </button>
                </div>"""

# Define the new header-right structure with better organization
new_header_right = """                <div class="header-right">
                    <!-- Quick Actions -->
                    <div class="header-actions-group">
                        <div class="update-indicator" id="updateIndicator" style="display: none;">
                            <button class="btn-icon update-btn" id="checkUpdateBtn" title="检查更新">
                                <i class="bi bi-arrow-up-circle"></i>
                            </button>
                        </div>
                        <button class="btn-icon" id="refreshBtn" title="刷新">
                            <i class="bi bi-arrow-clockwise"></i>
                        </button>
                    </div>

                    <div class="header-divider"></div>

                    <!-- Main Navigation -->
                    <nav class="header-nav">
                        <a href="/" class="nav-link active">
                            <i class="bi bi-speedometer2"></i>
                            <span>仪表盘</span>
                        </a>
                        <a href="/coins-management" class="nav-link">
                            <i class="bi bi-coin"></i>
                            <span>币种管理</span>
                        </a>
                        <a href="#" class="nav-link" id="liveTradingBtn">
                            <i class="bi bi-rocket-takeoff"></i>
                            <span>实盘交易</span>
                        </a>
                    </nav>

                    <div class="header-divider"></div>

                    <!-- Primary Action -->
                    <button class="btn-primary" id="addModelBtn">
                        <i class="bi bi-plus-lg"></i>
                        添加模型
                    </button>

                    <div class="header-divider"></div>

                    <!-- Settings Menu -->
                    <div class="header-menu">
                        <button class="btn-icon" id="settingsMenuBtn" title="设置">
                            <i class="bi bi-three-dots-vertical"></i>
                        </button>
                        <div class="menu-dropdown" id="settingsDropdown" style="display: none;">
                            <button class="menu-item" id="addApiProviderBtn">
                                <i class="bi bi-cloud-plus"></i>
                                <span>API提供方</span>
                            </button>
                            <button class="menu-item" id="settingsBtn">
                                <i class="bi bi-gear"></i>
                                <span>系统设置</span>
                            </button>
                        </div>
                    </div>
                </div>"""

# Replace the old with the new
if old_header_right in content:
    content = content.replace(old_header_right, new_header_right)
    print("[OK] Header redesigned successfully")

    # Write back
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("[OK] File updated")
    print("\nChanges:")
    print("  - Organized header into functional groups")
    print("  - Added navigation-style links (仪表盘, 币种管理, 实盘交易)")
    print("  - Moved settings and API provider to dropdown menu")
    print("  - Added visual dividers between groups")
else:
    print("[ERROR] Could not find header structure to replace")
    print("The file may have been modified")
