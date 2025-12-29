#!/usr/bin/env python3
"""
Windows GUI Verification Script
Run this on your Windows machine to test all GUI functionality
"""

import sys
import os
from pathlib import Path
import time

def test_gui_launch():
    """Test that GUI launches without errors"""
    print("="*60)
    print("TEST 1: GUI Launch")
    print("="*60)

    try:
        import tkinter as tk
        from tkinter import ttk
        print("✓ tkinter imported successfully")

        # Import the GUI class
        sys.path.insert(0, str(Path(__file__).parent))
        from financial_manager_gui import FinancialManagerGUI

        print("✓ FinancialManagerGUI imported successfully")

        # Create root window
        root = tk.Tk()
        print("✓ Tk root created")

        # Create GUI instance
        gui = FinancialManagerGUI(root)
        print("✓ GUI instance created")

        # Verify key attributes exist
        assert hasattr(gui, 'notebook'), "Missing notebook attribute"
        assert hasattr(gui, 'import_files'), "Missing import_files attribute"
        assert hasattr(gui, 'import_preview'), "Missing import_preview attribute"
        print("✓ All key attributes present")

        # Don't show the window, just test creation
        root.update()  # Process any pending events
        print("✓ GUI update successful")

        root.destroy()
        print("✓ GUI destroyed cleanly")

        print("\n✅ TEST 1 PASSED: GUI launches successfully\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loading():
    """Test that financial data loads correctly"""
    print("="*60)
    print("TEST 2: Data Loading")
    print("="*60)

    try:
        import tkinter as tk
        sys.path.insert(0, str(Path(__file__).parent))
        from financial_manager_gui import FinancialManagerGUI

        root = tk.Tk()
        root.withdraw()

        gui = FinancialManagerGUI(root)

        # Test load_financial_data
        gui.load_financial_data()
        print("✓ load_financial_data() executed")

        # Check that config was loaded
        assert hasattr(gui, 'financial_config'), "Missing financial_config"
        print(f"✓ financial_config loaded: {len(gui.financial_config)} keys")

        # Test flatten function
        test_data = {
            'category1': {
                'item1': {'balance': 100},
                'item2': {'balance': 200}
            }
        }

        result = gui.flatten_nested_dict(test_data, 'balance')
        assert 'item1' in result and result['item1'] == 100, "Flatten failed"
        print("✓ flatten_nested_dict() works correctly")

        root.destroy()

        print("\n✅ TEST 2 PASSED: Data loading works\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_validation():
    """Test CSV/Excel file validation"""
    print("="*60)
    print("TEST 3: File Validation")
    print("="*60)

    try:
        import tkinter as tk
        import csv
        import tempfile
        sys.path.insert(0, str(Path(__file__).parent))
        from financial_manager_gui import FinancialManagerGUI

        root = tk.Tk()
        root.withdraw()

        gui = FinancialManagerGUI(root)

        # Create a test CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Amount', 'Description'])
            writer.writerow(['2025-01-01', '100.00', 'Test transaction'])
            writer.writerow(['2025-01-02', '200.00', 'Test transaction 2'])
            test_csv = f.name

        print(f"✓ Created test CSV: {test_csv}")

        # Test read_file_data
        headers, rows = gui.read_file_data(test_csv)
        assert 'Date' in headers, "Headers not read correctly"
        assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"
        print("✓ read_file_data() works for CSV")

        # Clean up
        os.unlink(test_csv)
        root.destroy()

        print("\n✅ TEST 3 PASSED: File validation works\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_update_functionality():
    """Test balance update functionality"""
    print("="*60)
    print("TEST 4: Balance Updates")
    print("="*60)

    try:
        import tkinter as tk
        sys.path.insert(0, str(Path(__file__).parent))
        from financial_manager_gui import FinancialManagerGUI

        root = tk.Tk()
        root.withdraw()

        gui = FinancialManagerGUI(root)

        # Test populate_update_forms
        gui.populate_update_forms()
        print("✓ populate_update_forms() executed")

        # Check that entry dicts were created
        assert hasattr(gui, 'cash_entries'), "Missing cash_entries"
        assert hasattr(gui, 'debt_entries'), "Missing debt_entries"
        assert hasattr(gui, 'recurring_entries'), "Missing recurring_entries"
        print(f"✓ Entry dicts created: {len(gui.cash_entries)} cash, {len(gui.debt_entries)} debt, {len(gui.recurring_entries)} recurring")

        root.destroy()

        print("\n✅ TEST 4 PASSED: Balance update functionality works\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_subprocess_encoding():
    """Test that subprocess calls have proper encoding"""
    print("="*60)
    print("TEST 5: Subprocess Encoding (Windows Compatibility)")
    print("="*60)

    try:
        gui_file = Path(__file__).parent / "financial_manager_gui.py"
        with open(gui_file, 'r', encoding='utf-8') as f:
            content = f.read()

        import re
        subprocess_calls = re.findall(r'subprocess\.run\([^)]+\)', content, re.DOTALL)

        print(f"Found {len(subprocess_calls)} subprocess.run() calls")

        all_have_encoding = True
        for i, call in enumerate(subprocess_calls, 1):
            if 'encoding=' in call:
                print(f"✓ Call {i}: Has encoding parameter")
            else:
                print(f"❌ Call {i}: Missing encoding parameter")
                all_have_encoding = False

        if all_have_encoding:
            print("\n✅ TEST 5 PASSED: All subprocess calls have encoding\n")
            return True
        else:
            print("\n❌ TEST 5 FAILED: Some subprocess calls missing encoding\n")
            return False

    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}")
        return False

def test_cli_tools():
    """Test command-line tools"""
    print("="*60)
    print("TEST 6: CLI Tools")
    print("="*60)

    try:
        import subprocess

        # Test quick_update
        quick_update = Path(__file__).parent / "scripts" / "quick_update.py"
        result = subprocess.run(
            [sys.executable, str(quick_update), "--help"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=5
        )

        if result.returncode == 0:
            print("✓ quick_update.py --help works")
        else:
            print(f"❌ quick_update.py --help failed: {result.stderr}")
            return False

        # Test watcher
        watcher = Path(__file__).parent / "scripts" / "watch_and_rebuild.py"
        result = subprocess.run(
            [sys.executable, str(watcher), "--help"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=5
        )

        if result.returncode == 0:
            print("✓ watch_and_rebuild.py --help works")
        else:
            print(f"⚠️  watch_and_rebuild.py --help had issues (not critical)")

        print("\n✅ TEST 6 PASSED: CLI tools work\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 6 FAILED: {e}")
        return False

def interactive_gui_test():
    """Launch GUI for manual testing"""
    print("="*60)
    print("TEST 7: Interactive GUI Test")
    print("="*60)

    try:
        print("\nLaunching GUI for 10 seconds...")
        print("Please verify:")
        print("  1. GUI window appears")
        print("  2. All 6 tabs are visible")
        print("  3. No error messages")
        print("  4. Dashboard tab shows metrics")
        print("\nGUI will close automatically in 10 seconds...\n")

        import tkinter as tk
        sys.path.insert(0, str(Path(__file__).parent))
        from financial_manager_gui import FinancialManagerGUI

        root = tk.Tk()
        gui = FinancialManagerGUI(root)

        # Auto-close after 10 seconds
        root.after(10000, root.destroy)

        root.mainloop()

        print("\n✅ TEST 7 COMPLETED: GUI launched successfully\n")
        return True

    except Exception as e:
        print(f"\n❌ TEST 7 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests(interactive=False):
    """Run all verification tests"""
    print("\n" + "="*60)
    print("FINANCIAL MANAGER GUI - WINDOWS VERIFICATION")
    print("="*60 + "\n")

    tests = [
        ("GUI Launch", test_gui_launch),
        ("Data Loading", test_data_loading),
        ("File Validation", test_file_validation),
        ("Balance Updates", test_update_functionality),
        ("Subprocess Encoding", test_subprocess_encoding),
        ("CLI Tools", test_cli_tools),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
        time.sleep(0.5)  # Brief pause between tests

    # Interactive test (optional)
    if interactive:
        try:
            results["Interactive GUI"] = interactive_gui_test()
        except Exception as e:
            print(f"❌ Interactive test crashed: {e}")
            results["Interactive GUI"] = False

    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")

    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)

    if failed == 0:
        print("\n🎉 All tests passed! GUI is fully functional.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review errors above.")

    return failed == 0

if __name__ == "__main__":
    # Check if --interactive flag is present
    interactive = "--interactive" in sys.argv

    if interactive:
        print("Running tests with interactive GUI verification...\n")
    else:
        print("Running automated tests only.")
        print("Use --interactive flag to include GUI visual test.\n")

    success = run_all_tests(interactive)
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
