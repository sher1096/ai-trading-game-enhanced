"""
Add dropdown menu JavaScript to app.js
"""

# Read the file
with open('static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# JavaScript code to add
menu_js = """

// ============================================
// Settings Menu Dropdown
// ============================================
const settingsMenuBtn = document.getElementById('settingsMenuBtn');
const settingsDropdown = document.getElementById('settingsDropdown');

if (settingsMenuBtn && settingsDropdown) {
    // Toggle dropdown on button click
    settingsMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isVisible = settingsDropdown.style.display !== 'none';
        settingsDropdown.style.display = isVisible ? 'none' : 'block';
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!settingsMenuBtn.contains(e.target) && !settingsDropdown.contains(e.target)) {
            settingsDropdown.style.display = 'none';
        }
    });

    // Close dropdown when clicking a menu item
    const menuItems = settingsDropdown.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            settingsDropdown.style.display = 'none';
        });
    });
}

// ============================================
// Navigation Active State
// ============================================
const navLinks = document.querySelectorAll('.nav-link');
const currentPath = window.location.pathname;

navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href && (href === currentPath || (href !== '/' && currentPath.startsWith(href)))) {
        // Remove active from all links
        navLinks.forEach(l => l.classList.remove('active'));
        // Add active to current link
        link.classList.add('active');
    }
});
"""

# Add the menu JavaScript at the end of the file
if '// Settings Menu Dropdown' not in content:
    content += menu_js
    print("[OK] Menu JavaScript added successfully")

    # Write back
    with open('static/app.js', 'w', encoding='utf-8') as f:
        f.write(content)

    print("[OK] app.js updated")
    print("\nAdded features:")
    print("  - Settings dropdown toggle")
    print("  - Click outside to close dropdown")
    print("  - Navigation active state management")
else:
    print("[INFO] Menu JavaScript already exists")
