#!/usr/bin/env python3
"""
Quick fix to embed dashboard_data.json directly into the HTML
This modifies build_financial_docs.py to embed the dashboard data
"""

from pathlib import Path
import json

# Read the current build script
script_path = Path(__file__).parent / 'build_financial_docs.py'
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the loadDashboardData function
old_function = '''        // Load and render dashboard data
        function loadDashboardData() {
            fetch('Archive/processed/dashboard_data.json')
                .then(response => {
                    if (!response.ok) {
                        console.warn('⚠️  dashboard_data.json not found, showing placeholder');
                        return null;
                    }
                    return response.json();
                })
                .then(data => {
                    if (data) {
                        renderDashboard(data);
                    } else {
                        showPlaceholderDashboard();
                    }
                })
                .catch(error => {
                    console.error('Error loading dashboard data:', error);
                    showPlaceholderDashboard();
                });
        }'''

new_function = '''        // EMBEDDED_DASHBOARD_DATA will be replaced at build time
        
        // Load and render dashboard data (uses embedded data)
        function loadDashboardData() {
            try {
                if (typeof EMBEDDED_DASHBOARD_DATA !== 'undefined' && EMBEDDED_DASHBOARD_DATA) {
                    renderDashboard(EMBEDDED_DASHBOARD_DATA);
                } else {
                    console.warn('⚠️  Dashboard data not embedded, showing placeholder');
                    showPlaceholderDashboard();
                }
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                showPlaceholoardDashboard();
            }
        }'''

# Replace the function
if old_function in content:
    content = content.replace(old_function, new_function)
    print("✅ Replaced loadDashboardData() function")
else:
    print("⚠️  Could not find exact match for loadDashboardData(). Searching for alternative...")
    # Try a more flexible search
    if 'function loadDashboardData()' in content:
        print("Found function, but pattern doesn't match exactly. Manual fix needed.")
    else:
        print("❌ Function not found at all!")

# Now add the dashboard data loading logic to generate_html()
# Find the line where embedded_js is created and add dashboard loading after it

# Look for the generate_html function definition
html_func_start = content.find('def generate_html(embedded_data, structure):')
if html_func_start == -1:
    print("❌ Could not find generate_html function!")
else:
    # Find where embedded_js is defined
    embedded_js_line = content.find('embedded_js = "const embeddedContent = "', html_func_start)
    if embedded_js_line == -1:
        print("❌ Could not find embedded_js definition!")
    else:
        # Find the end of that statement (next newline after the assignment)
        next_newline = content.find('\n', embedded_js_line)
        
        # Insert dashboard data loading code right after
        dashboard_code = '''
    # Load dashboard data if it exists
    dashboard_data_path = BASE_DIR / 'Archive' / 'processed' / 'dashboard_data.json'
    dashboard_js = ""
    if dashboard_data_path.exists():
        try:
            with open(dashboard_data_path, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
            dashboard_js = "\\nconst EMBEDDED_DASHBOARD_DATA = " + json.dumps(dashboard_data, ensure_ascii=True) + ";\\n"
            print("   📊 Dashboard data embedded successfully")
        except Exception as e:
            print(f"   ⚠️  Could not load dashboard data: {e}")
            dashboard_js = "\\nconst EMBEDDED_DASHBOARD_DATA = null;\\n"
    else:
        print("   ⚠️  Dashboard data not found, will show placeholder")
        dashboard_js = "\\nconst EMBEDDED_DASHBOARD_DATA = null;\\n"
'''
        
        content = content[:next_newline+1] + dashboard_code + content[next_newline+1:]
        print("✅ Added dashboard data loading to generate_html()")
        
        # Now find where the script tag starts and inject the dashboard_js
        # Look for the <script> tag after the embedded_js
        script_tag_search_start = content.find('<script>', next_newline)
        if script_tag_search_start != -1:
            # Find where embeddedContent is inserted
            embedded_insert = content.find('''' + embedded_js + '''', script_tag_search_start)
            if embedded_insert != -1:
                # Replace it to include dashboard_js
                content = content.replace(
                    '''' + embedded_js + '''',
                    '''' + embedded_js + dashboard_js + ''''
                )
                print("✅ Configured HTML template to include dashboard data")

# Write the modified script
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ build_financial_docs.py has been updated!")
print("Now run: python scripts/build_financial_docs.py")
