#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Runner for Financial Scripts
Runs all tests with coverage reporting.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --coverage   # Run with coverage report
    python run_tests.py --html       # Generate HTML coverage report
    python run_tests.py --quick      # Run only fast unit tests
    python run_tests.py --verbose    # Extra verbose output
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import pytest
        print(f"  pytest: {pytest.__version__}")
    except ImportError:
        print("  pytest: NOT INSTALLED")
        print("    Install with: pip install pytest")
        return False

    try:
        import coverage
        print(f"  coverage: {coverage.__version__}")
    except ImportError:
        print("  coverage: NOT INSTALLED (optional)")
        print("    Install with: pip install coverage pytest-cov")

    return True


def run_tests(args):
    """Run pytest with given arguments."""
    cmd = [sys.executable, "-m", "pytest"]

    if "--coverage" in args or "--html" in args:
        cmd.extend(["--cov=scripts", "--cov-report=term-missing"])

        if "--html" in args:
            cmd.append("--cov-report=html:tests/coverage_html")

    if "--quick" in args:
        cmd.extend(["-m", "not slow and not integration"])

    if "--verbose" in args:
        cmd.append("-vv")
    else:
        cmd.append("-v")

    # Add test directory
    cmd.append("tests/")

    print(f"\nRunning: {' '.join(cmd)}\n")
    print("=" * 70)

    result = subprocess.run(cmd, cwd=BASE_DIR)
    return result.returncode


def main():
    print("=" * 70)
    print("  FINANCIAL SCRIPTS TEST RUNNER")
    print("=" * 70)
    print()

    print("Checking dependencies...")
    if not check_dependencies():
        print("\nPlease install required dependencies first.")
        return 1

    print()

    args = sys.argv[1:]
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
