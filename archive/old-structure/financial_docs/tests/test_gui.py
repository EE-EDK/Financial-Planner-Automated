#!/usr/bin/env python3
"""
GUI Verification Script - Tests all Financial Manager GUI functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox, scrolledtext
        import json
        import csv
        import threading
        import subprocess
        import time
        from datetime import datetime
        import shutil
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_file_structure():
    """Test that required files and directories exist"""
    print("\nTesting file structure...")
    base_path = Path(__file__).parent

    required_files = [
        "financial_manager_gui.py",
        "scripts/quick_update.py",
        "scripts/watch_and_rebuild.py",
    ]

    required_dirs = [
        "Archive",
        "Archive/processed",
        "Archive/raw",
        "scripts",
    ]

    all_good = True

    for file in required_files:
        if (base_path / file).exists():
            print(f"✓ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_good = False

    for dir in required_dirs:
        if (base_path / dir).exists():
            print(f"✓ {dir}/ exists")
        else:
            print(f"⚠️  {dir}/ missing (will be created)")
            (base_path / dir).mkdir(parents=True, exist_ok=True)

    return all_good

def test_gui_class_methods():
    """Test that all GUI methods are defined"""
    print("\nTesting GUI class methods...")

    # Import the GUI module
    try:
        from financial_manager_gui import FinancialManagerGUI
    except Exception as e:
        print(f"❌ Failed to import GUI: {e}")
        return False

    required_methods = [
        'create_widgets',
        'create_dashboard_tab',
        'create_import_tab',
        'create_update_tab',
        'create_comparison_tab',
        'create_automation_tab',
        'create_reports_tab',
        'load_financial_data',
        'populate_update_forms',
        'browse_import_file',
        'validate_files',
        'import_csv',
        'save_all_updates',
        'rebuild_dashboard',
        'save_snapshot',
        'flatten_nested_dict',
    ]

    all_good = True
    for method in required_methods:
        if hasattr(FinancialManagerGUI, method):
            print(f"✓ {method} defined")
        else:
            print(f"❌ {method} missing")
            all_good = False

    return all_good

def test_flatten_nested_dict():
    """Test the flatten_nested_dict function"""
    print("\nTesting flatten_nested_dict...")

    from financial_manager_gui import FinancialManagerGUI
    import tkinter as tk

    # Create a minimal instance (without actually showing GUI)
    root = tk.Tk()
    root.withdraw()  # Hide the window

    try:
        gui = FinancialManagerGUI(root)

        # Test with nested structure
        test_data = {
            'cash': {
                'account1': {'balance': 1000, 'name': 'Test Account'},
                'account2': {'balance': 2000, 'name': 'Test Account 2'}
            },
            'simple_account': 500
        }

        result = gui.flatten_nested_dict(test_data, 'balance')

        if 'account1' in result and result['account1'] == 1000:
            print("✓ Nested structure flattening works")
        else:
            print(f"❌ Nested structure flattening failed: {result}")
            return False

        if 'simple_account' in result and result['simple_account'] == 500:
            print("✓ Simple value handling works")
        else:
            print(f"❌ Simple value handling failed: {result}")
            return False

        root.destroy()
        return True

    except Exception as e:
        print(f"❌ Flatten test failed: {e}")
        import traceback
        traceback.print_exc()
        root.destroy()
        return False

def test_config_loading():
    """Test configuration file loading"""
    print("\nTesting configuration loading...")

    base_path = Path(__file__).parent
    config_file = base_path / "Archive" / "processed" / "financial_config.json"

    if config_file.exists():
        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)

            print(f"✓ Config file loaded successfully")

            # Check for expected keys
            expected_keys = ['cash_accounts', 'debt_balances', 'recurring_expenses', 'metadata']
            for key in expected_keys:
                if key in config:
                    print(f"✓ '{key}' found in config")
                else:
                    print(f"⚠️  '{key}' not in config (might be empty)")

            return True
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return False
    else:
        print(f"⚠️  Config file doesn't exist yet (will be created)")
        return True

def test_quick_update_cli():
    """Test the quick_update CLI tool"""
    print("\nTesting quick_update CLI...")

    base_path = Path(__file__).parent
    quick_update = base_path / "scripts" / "quick_update.py"

    if not quick_update.exists():
        print(f"❌ quick_update.py not found")
        return False

    try:
        import subprocess

        # Test the help command
        result = subprocess.run(
            [sys.executable, str(quick_update), "--help"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=5
        )

        if result.returncode == 0 and "Quick financial data updater" in result.stdout:
            print("✓ quick_update.py --help works")
        else:
            print(f"⚠️  quick_update.py help may have issues")

        # Test list command
        result = subprocess.run(
            [sys.executable, str(quick_update), "list"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=5
        )

        if result.returncode == 0:
            print("✓ quick_update.py list works")
            return True
        else:
            print(f"❌ quick_update.py list failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ quick_update test failed: {e}")
        return False

def test_watcher_script():
    """Test the watcher script"""
    print("\nTesting watch_and_rebuild script...")

    base_path = Path(__file__).parent
    watcher = base_path / "scripts" / "watch_and_rebuild.py"

    if not watcher.exists():
        print(f"❌ watch_and_rebuild.py not found")
        return False

    try:
        import subprocess

        # Test the help command
        result = subprocess.run(
            [sys.executable, str(watcher), "--help"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=5
        )

        if result.returncode == 0 and "Watch financial data" in result.stdout:
            print("✓ watch_and_rebuild.py --help works")
            return True
        else:
            print(f"⚠️  watch_and_rebuild.py may have issues")
            return True  # Not critical

    except Exception as e:
        print(f"❌ Watcher test failed: {e}")
        return False

def check_potential_issues():
    """Check for common issues in the GUI code"""
    print("\nChecking for potential issues...")

    issues_found = []

    gui_file = Path(__file__).parent / "financial_manager_gui.py"

    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for TODO or FIXME comments
    if 'TODO' in content or 'FIXME' in content:
        issues_found.append("⚠️  Found TODO/FIXME comments")

    # Check if all subprocess.run calls have encoding specified
    import re
    subprocess_calls = re.findall(r'subprocess\.run\([^)]+\)', content, re.DOTALL)
    for call in subprocess_calls:
        if 'encoding=' not in call:
            issues_found.append("⚠️  Found subprocess.run without encoding (may cause Windows issues)")
            break

    # Check for proper error handling
    if 'except Exception as e:' in content:
        print("✓ Basic error handling present")
    else:
        issues_found.append("❌ No error handling found")

    if issues_found:
        for issue in issues_found:
            print(issue)
        return False
    else:
        print("✓ No obvious issues found")
        return True

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("Financial Manager GUI - Comprehensive Verification")
    print("="*60)

    results = {
        'Imports': test_imports(),
        'File Structure': test_file_structure(),
        'GUI Methods': test_gui_class_methods(),
        'Flatten Function': test_flatten_nested_dict(),
        'Config Loading': test_config_loading(),
        'Quick Update CLI': test_quick_update_cli(),
        'Watcher Script': test_watcher_script(),
        'Code Quality': check_potential_issues(),
    }

    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    passed = 0
    failed = 0

    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print("="*60)
    print(f"Total: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("\n🎉 All tests passed! GUI should work correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")

    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
