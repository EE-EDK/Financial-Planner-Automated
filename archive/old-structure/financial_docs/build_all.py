#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIFIED FINANCIAL HUB BUILDER
Runs all analysis scripts and builds the complete financial hub in one command.

Usage:
    python3 financial_docs/build_all.py

What it does:
1. Analyzes transactions → TRANSACTION_ANALYSIS_REPORT.md
2. Compares budget vs actual → BUDGET_VS_ACTUAL.md
3. Calculates financial health score → FINANCIAL_HEALTH_SCORE.md
4. Tracks monthly snapshot → FINANCIAL_TRENDS.md
5. Runs scenario analysis → SCENARIO_ANALYSIS.md
6. Builds financial_hub.html with all documents

One script to rule them all! 🎯
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

# All the analysis scripts
SCRIPTS = [
    {
        'name': 'Transaction Analysis',
        'script': 'scripts/analyze_transactions.py',
        'output': 'TRANSACTION_ANALYSIS_REPORT.md',
        'icon': '💳',
        'required': True,
        'requires_csv': True
    },
    {
        'name': 'Budget vs Actual',
        'script': 'scripts/budget_vs_actual.py',
        'output': 'BUDGET_VS_ACTUAL.md',
        'icon': '📊',
        'required': False,
        'requires_csv': True,
        'args': ['1']  # Default: 1 month, can be overridden via --months
    },
    {
        'name': 'Financial Health Score',
        'script': 'scripts/calculate_health_score.py',
        'output': 'FINANCIAL_HEALTH_SCORE.md',
        'icon': '🏆',
        'required': True,
        'requires_csv': False
    },
    {
        'name': 'Monthly Snapshot',
        'script': 'scripts/snapshot_manager.py',
        'output': 'FINANCIAL_TRENDS.md',
        'icon': '📈',
        'required': False,
        'requires_csv': False,
        'args': ['trends']  # Use the 'trends' command
    },
    {
        'name': 'Scenario Analysis',
        'script': 'scripts/scenario_calculator.py',
        'output': 'SCENARIO_ANALYSIS.md',
        'icon': '🎯',
        'required': True,
        'requires_csv': False
    },
    {
        'name': 'Dashboard Data',
        'script': 'scripts/generate_dashboard_data.py',
        'output': 'dashboard_data.json',
        'icon': '📊',
        'required': True,
        'requires_csv': False
    },
    {
        'name': 'Account Balance History',
        'script': 'scripts/track_account_balances.py',
        'output': 'account_balance_history.json',
        'icon': '💰',
        'required': False,
        'requires_csv': False
    },
    {
        'name': 'Goal Progress Tracking',
        'script': 'scripts/track_goals.py',
        'output': 'goal_progress.txt',  # This script outputs to console
        'icon': '🎯',
        'required': False,
        'requires_csv': False
    }
]


def print_header():
    """Print fancy header"""
    print()
    print("=" * 80)
    print("💰 UNIFIED FINANCIAL HUB BUILDER")
    print("=" * 80)
    print(f"Build Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("=" * 80)
    print()


def check_prerequisites():
    """Check if required files exist"""
    print("🔍 Checking prerequisites...")
    print()

    issues = []

    # Check Archive directory
    archive_dir = BASE_DIR / "Archive"
    if not archive_dir.exists():
        issues.append("❌ Archive/ directory not found")
    else:
        print("✅ Archive/ directory exists")

    # Check for CSV file (needed by some scripts) - check both root and data/ subdirectory
    csv_file = archive_dir / "AllTransactions.csv"
    csv_file_data = archive_dir / "data" / "AllTransactions.csv"

    if csv_file.exists():
        print("✅ AllTransactions.csv found")
    elif csv_file_data.exists():
        print("✅ AllTransactions.csv found (in data/)")
    else:
        issues.append("⚠️  AllTransactions.csv not found (some scripts will skip)")
        print("⚠️  AllTransactions.csv not found - transaction-based analysis will be limited")

    print()

    if "❌" in str(issues):
        for issue in issues:
            print(issue)
        return False

    return True


def run_script(script_info):
    """Run a single analysis script"""
    script_name = script_info['name']
    script_file = BASE_DIR / script_info['script']
    icon = script_info['icon']

    print(f"{icon} Running {script_name}...")
    print(f"   Script: {script_info['script']}")

    if not script_file.exists():
        print(f"   ❌ Script not found: {script_file}")
        return False

    # Check if CSV is required but missing
    if script_info.get('requires_csv'):
        csv_file = BASE_DIR / "Archive" / "raw" / "exports" / "AllTransactions.csv"
        if not csv_file.exists():
            print(f"   ⚠️  Skipped (requires AllTransactions.csv)")
            return True  # Not a failure, just skipped

    try:
        # Build command with optional arguments
        cmd = [sys.executable, str(script_file)]
        if script_info.get('args'):
            cmd.extend(script_info['args'])

        # Run the script with UTF-8 encoding
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace undecodable chars instead of crashing
            timeout=30
        )

        # Check if output was created (more reliable than exit code)
        # Check multiple possible output locations based on file type
        output_name = script_info['output']
        if output_name.endswith('.json'):
            output_file = BASE_DIR / "Archive" / "processed" / output_name
        elif output_name.endswith('.md'):
            output_file = BASE_DIR / "Archive" / "reports" / output_name
        else:
            output_file = BASE_DIR / "Archive" / output_name

        if output_file.exists() and output_file.stat().st_size > 0:
            size = output_file.stat().st_size / 1024  # KB
            print(f"   ✅ Success → {script_info['output']} ({size:.1f} KB)")
            return True
        elif result.returncode == 0:
            print(f"   ⚠️  Script ran but output not found: {script_info['output']}")
            return True  # Script ran, might not have generated output
        else:
            print(f"   ❌ Failed with exit code {result.returncode}")
            if result.stderr:
                # Show full error on Windows
                error_msg = result.stderr.strip()
                if error_msg:
                    print(f"   Error: {error_msg[:500]}")
            if result.stdout:
                # Sometimes error details are in stdout
                stdout_msg = result.stdout.strip()
                if stdout_msg and 'Error' in stdout_msg or 'Traceback' in stdout_msg:
                    print(f"   Output: {stdout_msg[:500]}")
            return not script_info['required']  # Only fail if required

    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout (>30s)")
        return not script_info['required']
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return not script_info['required']


def build_financial_hub():
    """Build the final financial_hub.html"""
    print()
    print("🌐 Building financial_hub.html...")
    print()

    build_script = BASE_DIR / "scripts" / "build_financial_docs.py"

    if not build_script.exists():
        print(f"   ❌ build_financial_docs.py not found")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(build_script)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # Replace undecodable chars instead of crashing
            timeout=30
        )

        # Check if HTML was created (more reliable than exit code)
        output_file = BASE_DIR / "financial_hub.html"

        if output_file.exists() and output_file.stat().st_size > 0:
            size = output_file.stat().st_size / 1024  # KB
            print(f"✅ financial_hub.html generated ({size:.1f} KB)")
            print()
            return True
        else:
            print(f"   ❌ Build failed with exit code {result.returncode}")
            if result.stderr:
                error_msg = result.stderr.strip()
                if error_msg:
                    print(f"   Error: {error_msg[:500]}")
            if result.stdout:
                stdout_msg = result.stdout.strip()
                if stdout_msg and ('Error' in stdout_msg or 'Traceback' in stdout_msg):
                    print(f"   Output: {stdout_msg[:500]}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return False


def print_summary():
    """Print summary of generated files"""
    print("=" * 80)
    print("📦 BUILD SUMMARY")
    print("=" * 80)
    print()

    archive_dir = BASE_DIR / "Archive"

    # Count files
    md_files = list(archive_dir.glob("*.md"))
    pdf_files = list(archive_dir.glob("*.pdf"))
    csv_files = list(archive_dir.glob("*.csv"))
    img_files = list(archive_dir.glob("*.jpg")) + list(archive_dir.glob("*.png"))

    print(f"📄 Markdown documents: {len(md_files)}")
    print(f"📋 PDF documents: {len(pdf_files)}")
    print(f"💳 CSV files: {len(csv_files)}")
    print(f"📸 Images: {len(img_files)}")
    print(f"📦 Total files: {len(md_files) + len(pdf_files) + len(csv_files) + len(img_files)}")
    print()

    # Check HTML
    html_file = BASE_DIR / "financial_hub.html"
    if html_file.exists():
        size = html_file.stat().st_size / 1024  # KB
        print(f"🌐 financial_hub.html: {size:.1f} KB")
    else:
        print("❌ financial_hub.html: NOT FOUND")
    print()


def print_next_steps():
    """Print next steps"""
    print("=" * 80)
    print("🎯 NEXT STEPS")
    print("=" * 80)
    print()

    html_file = BASE_DIR / "financial_hub.html"

    if html_file.exists():
        print("✅ Build complete! Your financial hub is ready.")
        print()
        print("To view your financial hub:")
        print(f"   1. Open: {html_file}")
        print(f"   2. Or run: open {html_file}")
        print()
        print("To rebuild after changes:")
        print(f"   python3 {Path(__file__).name}")
    else:
        print("❌ Build incomplete. Check errors above.")
    print()
    print("=" * 80)
    print()


def parse_args():
    """Parse command-line arguments"""
    months = 1
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--months' and i + 2 <= len(sys.argv[1:]):
            try:
                months = int(sys.argv[i + 2])
            except ValueError:
                pass
        elif arg.startswith('--months='):
            try:
                months = int(arg.split('=')[1])
            except ValueError:
                pass
    return {'months': months}


def main():
    """Main build process"""
    args = parse_args()

    # Update budget_vs_actual args with months
    for script in SCRIPTS:
        if script['name'] == 'Budget vs Actual':
            script['args'] = [str(args['months'])]

    print_header()

    # Check prerequisites
    if not check_prerequisites():
        print()
        print("❌ Prerequisites not met. Please fix issues above.")
        return 1

    print("=" * 80)
    print("🔧 RUNNING ANALYSIS SCRIPTS")
    print("=" * 80)
    print()

    # Track success
    success = True
    skipped = []
    failed = []
    succeeded = []

    # Run all analysis scripts
    for script in SCRIPTS:
        result = run_script(script)
        print()

        if result:
            succeeded.append(script['name'])
        elif not script['required']:
            skipped.append(script['name'])
        else:
            failed.append(script['name'])
            success = False

    # Build HTML
    print("=" * 80)
    print("🌐 BUILDING FINAL HTML")
    print("=" * 80)
    print()

    if not build_financial_hub():
        failed.append("HTML Build")
        success = False
    else:
        succeeded.append("HTML Build")

    print()

    # Print summary
    print_summary()

    # Results summary
    print("=" * 80)
    print("📊 BUILD RESULTS")
    print("=" * 80)
    print()
    print(f"✅ Succeeded: {len(succeeded)}")
    for item in succeeded:
        print(f"   • {item}")

    if skipped:
        print()
        print(f"⚠️  Skipped: {len(skipped)}")
        for item in skipped:
            print(f"   • {item}")

    if failed:
        print()
        print(f"❌ Failed: {len(failed)}")
        for item in failed:
            print(f"   • {item}")

    print()

    # Next steps
    print_next_steps()

    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
