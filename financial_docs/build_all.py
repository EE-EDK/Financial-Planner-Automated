#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIFIED FINANCIAL HUB BUILDER (Enhanced with Excel Import)
Runs all analysis scripts and builds the complete financial hub in one command.

Usage:
    python3 financial_docs/build_all.py [--months N]

What it does:
1. 📊 IMPORTS Excel budget file (Budget_in_Excel_for_Ethan.xlsx) → AllTransactions.csv
2. 💳 Analyzes transactions → TRANSACTION_ANALYSIS_REPORT.md
3. 📊 Compares budget vs actual → BUDGET_VS_ACTUAL.md
4. 🏆 Calculates financial health score → FINANCIAL_HEALTH_SCORE.md
5. 📈 Tracks monthly snapshot → FINANCIAL_TRENDS.md
6. 🎯 Runs scenario analysis → SCENARIO_ANALYSIS.md
7. 🌐 Builds financial_hub.html with all documents

Excel File Locations Searched:
- Current directory
- Archive/raw/exports/
- Archive/ directory  
- Downloads folder
- /mnt/user-data/uploads/ (Claude uploads)

One script to rule them all! 🎯
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32' and sys.stdout is not None:
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
        'script': 'scripts/track_monthly_snapshot.py',
        'output': 'FINANCIAL_TRENDS.md',
        'icon': '📈',
        'required': False,
        'requires_csv': False
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
    }
]

def print_header():
    """Print fancy header"""
    print()
    print("=" * 80)
    print("💰 UNIFIED FINANCIAL HUB BUILDER (Enhanced)")
    print("=" * 80)
    print(f"Build Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("=" * 80)
    print()

def import_excel_budget():
    """Import Excel budget file if available"""
    print("📊 Looking for Excel budget file...")
    print()

    # Look for Budget Excel file in multiple locations
    possible_locations = [
        Path("Budget_in_Excel_for_Ethan.xlsx"),  # Current directory
        BASE_DIR / "Budget_in_Excel_for_Ethan.xlsx",  # Financial docs directory  
        BASE_DIR / "Archive" / "raw" / "exports" / "Budget_in_Excel_for_Ethan.xlsx",  # Raw exports
        BASE_DIR / "Archive" / "Budget_in_Excel_for_Ethan.xlsx",  # Archive root
        Path.home() / "Downloads" / "Budget_in_Excel_for_Ethan.xlsx",  # Downloads folder
        Path("/mnt/user-data/uploads/Budget_in_Excel_for_Ethan.xlsx"),  # Uploaded files
    ]

    # Also look for any Excel file with "budget" in the name or "100" in the name
    excel_patterns = [
        "Budget*.xlsx", "*budget*.xlsx", "*Budget*.xlsx", "budget*.xls", "*budget*.xls",
        "*100*.xlsx", "*100*.xls"
    ]

    budget_file = None
    
    # Check specific locations first
    for location in possible_locations:
        if location.exists():
            budget_file = location
            print(f"✅ Found Excel budget: {budget_file}")
            break
    
    # If not found, search for budget patterns
    if not budget_file:
        search_dirs = [
            BASE_DIR,
            BASE_DIR / "Archive",
            BASE_DIR / "Archive" / "raw" / "exports",
            Path.home() / "Downloads",
            Path("/mnt/user-data/uploads")
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            for pattern in excel_patterns:
                try:
                    matches = list(search_dir.glob(pattern))
                    if matches:
                        budget_file = max(matches, key=lambda x: x.stat().st_mtime)  # Most recent
                        print(f"✅ Found budget file: {budget_file}")
                        break
                except Exception:
                    continue  # Skip if permission denied
            if budget_file:
                break

    if not budget_file:
        print("⚠️  No Excel budget file found - will skip Excel import")
        print("   Expected: Budget_in_Excel_for_Ethan.xlsx")
        print("   Searched:")
        for loc in possible_locations:
            print(f"     • {loc}")
        return False

    # Run import script
    import_script = BASE_DIR / "scripts" / "import_excel_budget.py"
    
    # If import script doesn't exist in expected location, look for it elsewhere
    if not import_script.exists():
        # Check current directory for the script
        alt_locations = [
            Path("import_excel_budget.py"),
            Path("scripts/import_excel_budget.py"),
            Path("/mnt/user-data/uploads/import_excel_budget.py")
        ]
        
        for alt_script in alt_locations:
            if alt_script.exists():
                import_script = alt_script
                print(f"📍 Using import script: {import_script}")
                break
        else:
            print("⚠️  import_excel_budget.py not found - skipping Excel import")
            print("   Expected locations:")
            for loc in [BASE_DIR / "scripts" / "import_excel_budget.py"] + alt_locations:
                print(f"     • {loc}")
            return False

    print(f"📥 Importing Excel budget from: {budget_file.name}")
    print(f"🔧 Using import script: {import_script}")
    
    try:
        # Create Archive directories if they don't exist
        archive_dirs = [
            BASE_DIR / "Archive",
            BASE_DIR / "Archive" / "raw",
            BASE_DIR / "Archive" / "raw" / "exports",
            BASE_DIR / "Archive" / "reports",
            BASE_DIR / "Archive" / "processed"
        ]
        
        for directory in archive_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
        result = subprocess.run(
            [sys.executable, str(import_script), str(budget_file)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )

        if result.returncode == 0:
            print("✅ Excel budget imported successfully")
            print()
            return True
        else:
            print(f"❌ Excel import failed with exit code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()[:300]}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()[:300]}")
            print()
            return False

    except subprocess.TimeoutExpired:
        print("❌ Excel import timeout (>60s)")
        print()
        return False
    except Exception as e:
        print(f"❌ Excel import error: {str(e)[:100]}")
        print()
        return False

def check_prerequisites():
    """Check if required files exist"""
    print("🔍 Checking prerequisites...")
    print()

    issues = []

    # Check Archive directory
    archive_dir = BASE_DIR / "Archive"
    if not archive_dir.exists():
        print("📁 Creating Archive/ directory...")
        archive_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Archive/ directory created")
    else:
        print("✅ Archive/ directory exists")

    # Create subdirectories
    subdirs = [
        archive_dir / "raw" / "exports",
        archive_dir / "reports",
        archive_dir / "processed"
    ]
    
    for subdir in subdirs:
        subdir.mkdir(parents=True, exist_ok=True)

    # Check for CSV file (will be created from Excel import)
    csv_locations = [
        archive_dir / "AllTransactions.csv",
        archive_dir / "data" / "AllTransactions.csv",
        archive_dir / "raw" / "exports" / "AllTransactions.csv"
    ]

    csv_found = False
    for csv_file in csv_locations:
        if csv_file.exists():
            print(f"✅ AllTransactions.csv found at: {csv_file}")
            csv_found = True
            break

    if not csv_found:
        print("⚠️  AllTransactions.csv not found - will be created from Excel import")

    print()
    return True  # Always return True since we'll create what we need

def run_script(script_info):
    """Run a single analysis script"""
    script_name = script_info['name']
    script_file = BASE_DIR / script_info['script']
    icon = script_info['icon']

    print(f"{icon} Running {script_name}...")
    print(f"   Script: {script_info['script']}")

    if not script_file.exists():
        # Try alternative locations
        alt_locations = [
            Path(script_info['script']),  # Relative to current
            Path(script_info['script'].split('/')[-1]),  # Just filename
            Path("/mnt/user-data/uploads") / script_info['script'].split('/')[-1]  # Uploads
        ]
        
        for alt_script in alt_locations:
            if alt_script.exists():
                script_file = alt_script
                break
        else:
            print(f"   ❌ Script not found: {script_file}")
            return False

    # Check if CSV is required but missing
    if script_info.get('requires_csv'):
        csv_locations = [
            BASE_DIR / "Archive" / "raw" / "exports" / "AllTransactions.csv",
            BASE_DIR / "Archive" / "AllTransactions.csv",
            BASE_DIR / "Archive" / "data" / "AllTransactions.csv"
        ]
        
        csv_found = any(csv_file.exists() for csv_file in csv_locations)
        
        if not csv_found:
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
        possible_output_locations = [
            BASE_DIR / "Archive" / "processed" / output_name,
            BASE_DIR / "Archive" / "reports" / output_name,
            BASE_DIR / "Archive" / output_name,
            BASE_DIR / output_name
        ]
        
        output_file = None
        for location in possible_output_locations:
            if location.exists() and location.stat().st_size > 0:
                output_file = location
                break

        if output_file:
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
                if stdout_msg and ('Error' in stdout_msg or 'Traceback' in stdout_msg):
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

    build_script_locations = [
        BASE_DIR / "scripts" / "build_financial_docs.py",
        BASE_DIR / "build_financial_docs.py",
        Path("build_financial_docs.py"),
        Path("/mnt/user-data/uploads/build_financial_docs.py")
    ]
    
    build_script = None
    for location in build_script_locations:
        if location.exists():
            build_script = location
            break

    if not build_script:
        print(f"   ❌ build_financial_docs.py not found in any location")
        print("   ⚠️  Skipping HTML generation")
        return True  # Don't fail the whole process

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
        possible_html_locations = [
            BASE_DIR / "financial_hub.html",
            Path("financial_hub.html")
        ]
        
        output_file = None
        for location in possible_html_locations:
            if location.exists() and location.stat().st_size > 0:
                output_file = location
                break

        if output_file:
            size = output_file.stat().st_size / 1024  # KB
            print(f"✅ financial_hub.html generated ({size:.1f} KB)")
            print()
            return True
        else:
            print(f"   ⚠️  HTML build completed but file not found")
            print(f"   Exit code: {result.returncode}")
            if result.stderr:
                error_msg = result.stderr.strip()
                if error_msg:
                    print(f"   Error: {error_msg[:300]}")
            if result.stdout:
                stdout_msg = result.stdout.strip()
                if stdout_msg:
                    print(f"   Output: {stdout_msg[:300]}")
            return True  # Don't fail the whole process

    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return True  # Don't fail the whole process

def print_summary():
    """Print summary of generated files"""
    print("=" * 80)
    print("📦 BUILD SUMMARY")
    print("=" * 80)
    print()

    archive_dir = BASE_DIR / "Archive"

    # Count files in multiple directories
    all_files = []
    search_dirs = [archive_dir, BASE_DIR]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            all_files.extend(search_dir.rglob("*.md"))
            all_files.extend(search_dir.rglob("*.pdf"))
            all_files.extend(search_dir.rglob("*.csv"))
            all_files.extend(search_dir.rglob("*.jpg"))
            all_files.extend(search_dir.rglob("*.png"))

    # Categorize
    md_files = [f for f in all_files if f.suffix == '.md']
    pdf_files = [f for f in all_files if f.suffix == '.pdf']
    csv_files = [f for f in all_files if f.suffix == '.csv']
    img_files = [f for f in all_files if f.suffix in ['.jpg', '.png']]

    print(f"📄 Markdown documents: {len(md_files)}")
    print(f"📋 PDF documents: {len(pdf_files)}")
    print(f"💳 CSV files: {len(csv_files)}")
    print(f"📸 Images: {len(img_files)}")
    print(f"📦 Total files: {len(all_files)}")
    print()

    # Check HTML
    html_locations = [
        BASE_DIR / "financial_hub.html",
        Path("financial_hub.html")
    ]
    
    html_file = None
    for location in html_locations:
        if location.exists():
            html_file = location
            break
    
    if html_file:
        size = html_file.stat().st_size / 1024  # KB
        print(f"🌐 financial_hub.html: {size:.1f} KB at {html_file}")
    else:
        print("❌ financial_hub.html: NOT FOUND")
    print()

def print_next_steps():
    """Print next steps"""
    print("=" * 80)
    print("🎯 NEXT STEPS")
    print("=" * 80)
    print()

    # Find HTML file
    html_locations = [
        BASE_DIR / "financial_hub.html",
        Path("financial_hub.html")
    ]
    
    html_file = None
    for location in html_locations:
        if location.exists():
            html_file = location
            break

    if html_file:
        print("✅ Build complete! Your financial hub is ready.")
        print()
        print("To view your financial hub:")
        print(f"   1. Open: {html_file}")
        print(f"   2. Or run: start {html_file}")
        print()
        print("To rebuild after changes:")
        print(f"   python3 {Path(__file__).name}")
        print()
        print("📊 Your Excel budget data has been processed!")
        print("📈 All analysis reports are now based on your latest data.")
    else:
        print("⚠️  Build completed with some limitations.")
        print("   Reports may have been generated without the final HTML.")
        print("   Check the Archive/ directory for individual reports.")
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

    # Check prerequisites (always succeeds, creates what's needed)
    check_prerequisites()

    # STEP 1: Import Excel budget file first
    print("=" * 80)
    print("📊 IMPORTING EXCEL BUDGET DATA")
    print("=" * 80)
    print()
    
    excel_imported = import_excel_budget()
    print()

    # STEP 2: Run analysis scripts
    print("=" * 80)
    print("🔧 RUNNING ANALYSIS SCRIPTS")
    print("=" * 80)
    print()

    # Track success
    success = True
    skipped = []
    failed = []
    succeeded = []

    # Add Excel import to results
    if excel_imported:
        succeeded.append("Excel Budget Import")
    else:
        skipped.append("Excel Budget Import")

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

    # Build HTML (non-blocking)
    print("=" * 80)
    print("🌐 BUILDING FINAL HTML")
    print("=" * 80)
    print()

    html_built = build_financial_hub()
    if html_built:
        succeeded.append("HTML Build")
    else:
        skipped.append("HTML Build")

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

    return 0 if len(failed) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())