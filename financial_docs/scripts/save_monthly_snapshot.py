#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monthly Snapshot Archiver
Saves current financial state to monthly snapshot folder

This script creates a snapshot of the current financial state including:
- dashboard_data.json
- financial_config.json
- budget.json
- AllTransactions.csv (current month only)

Saved to: Archive/snapshots/YYYY-MM/
"""

import json
import csv
import shutil
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "Archive" / "processed"
EXPORTS_DIR = BASE_DIR / "Archive" / "raw" / "exports"
SNAPSHOTS_DIR = BASE_DIR / "Archive" / "snapshots"

def get_snapshot_dir(month_override=None):
    """Get the snapshot directory for the current month"""
    if month_override:
        snapshot_month = month_override
    else:
        snapshot_month = datetime.now().strftime('%Y-%m')

    snapshot_dir = SNAPSHOTS_DIR / snapshot_month
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    return snapshot_dir

def save_json_snapshot(filename, snapshot_dir):
    """Copy JSON file to snapshot directory"""
    source = PROCESSED_DIR / filename
    dest = snapshot_dir / filename

    if source.exists():
        shutil.copy2(source, dest)
        return True
    return False

def save_current_month_transactions(snapshot_dir):
    """Save only current month's transactions to snapshot"""
    source = EXPORTS_DIR / "AllTransactions.csv"

    if not source.exists():
        return False

    current_month = datetime.now().strftime('%Y-%m')
    dest = snapshot_dir / "transactions_monthly.csv"

    with open(source, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)

        # Filter to current month only
        monthly_transactions = []
        for row in reader:
            if row.get('Date', '').startswith(current_month):
                monthly_transactions.append(row)

        # Write to snapshot
        if monthly_transactions:
            with open(dest, 'w', encoding='utf-8', newline='') as f_out:
                writer = csv.DictWriter(f_out, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(monthly_transactions)
            return True

    return False

def create_snapshot_summary(snapshot_dir):
    """Create a summary of the snapshot"""
    dashboard_data_file = snapshot_dir / "dashboard_data.json"

    if not dashboard_data_file.exists():
        return

    with open(dashboard_data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    snapshot_summary = {
        'snapshot_date': datetime.now().isoformat(),
        'snapshot_month': snapshot_dir.name,
        'financial_snapshot': data.get('snapshot', {}),
        'budget_summary': {
            'total_budgeted': data.get('budget_vs_actual', {}).get('total_budgeted', 0),
            'total_spent': data.get('budget_vs_actual', {}).get('total_spent', 0),
            'over_budget_categories': len(data.get('budget_vs_actual', {}).get('over_budget_items', []))
        },
        'emergency_fund': data.get('emergency_fund', {}),
        'credit_card_debt': data.get('credit_card_payoff', {}).get('total_balance', 0),
        'alerts_count': len(data.get('alerts', []))
    }

    summary_file = snapshot_dir / "snapshot_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot_summary, f, indent=2, ensure_ascii=False)

def main():
    """Create monthly snapshot"""

    print()
    print("=" * 70)
    print("📸 MONTHLY SNAPSHOT ARCHIVER")
    print("=" * 70)
    print()

    # Get snapshot directory
    snapshot_dir = get_snapshot_dir()
    print(f"Snapshot directory: {snapshot_dir}")
    print()

    # Save files
    files_saved = []
    files_failed = []

    print("Saving snapshot files...")

    # JSON files
    json_files = ['dashboard_data.json', 'financial_config.json', 'budget.json']
    for filename in json_files:
        if save_json_snapshot(filename, snapshot_dir):
            files_saved.append(filename)
            print(f"  ✅ {filename}")
        else:
            files_failed.append(filename)
            print(f"  ⚠️  {filename} (not found)")

    # Current month transactions
    if save_current_month_transactions(snapshot_dir):
        files_saved.append('transactions_monthly.csv')
        print(f"  ✅ transactions_monthly.csv (current month only)")
    else:
        files_failed.append('transactions_monthly.csv')
        print(f"  ⚠️  transactions_monthly.csv (failed)")

    print()

    # Create summary
    print("Creating snapshot summary...")
    create_snapshot_summary(snapshot_dir)
    print("  ✅ snapshot_summary.json")
    print()

    # Results
    print("=" * 70)
    print("✅ SNAPSHOT COMPLETE")
    print("=" * 70)
    print()
    print(f"Snapshot saved to: {snapshot_dir}")
    print(f"Files saved: {len(files_saved)}")
    if files_failed:
        print(f"Files failed: {len(files_failed)} ({', '.join(files_failed)})")
    print()

    # Show summary
    summary_file = snapshot_dir / "snapshot_summary.json"
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)

        print("📊 Snapshot Summary:")
        print(f"  Month:          {summary['snapshot_month']}")
        print(f"  Liquid Cash:    ${summary['financial_snapshot']['liquid_cash']:,.2f}")
        print(f"  Total Debt:     ${summary['financial_snapshot']['total_debt']:,.2f}")
        print(f"  Net Worth:      ${summary['financial_snapshot']['net_worth']:,.2f}")
        print(f"  CC Debt:        ${summary['credit_card_debt']:,.2f}")
        print(f"  Alerts:         {summary['alerts_count']}")
        print()

if __name__ == '__main__':
    main()
