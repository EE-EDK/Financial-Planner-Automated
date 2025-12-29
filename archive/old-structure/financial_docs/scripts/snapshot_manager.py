#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snapshot Manager
Unified script for managing financial snapshots and trend tracking.

Consolidates:
- track_monthly_snapshot.py (tracking trends over time)
- save_monthly_snapshot.py (archiving monthly state)

Usage:
    python3 snapshot_manager.py record      # Record current financial state
    python3 snapshot_manager.py archive     # Archive to snapshots/YYYY-MM/
    python3 snapshot_manager.py trends      # Generate trend report
    python3 snapshot_manager.py all         # Do all three actions
"""

import sys
import json
import csv
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import shared utilities
from financial_utils import (
    setup_windows_encoding,
    load_config,
    load_budget,
    calculate_financial_snapshot,
    save_json,
    save_report,
    ARCHIVE_DIR,
    PROCESSED_DIR,
    SNAPSHOTS_DIR,
    DASHBOARD_DATA_FILE
)

# Setup encoding
setup_windows_encoding()

# Data files
HISTORY_FILE = ARCHIVE_DIR / "processed" / "financial_history.json"


def load_history() -> List[Dict[str, Any]]:
    """Load existing financial history."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def record_snapshot() -> Dict[str, Any]:
    """
    Record current financial state to history.

    Returns:
        The snapshot entry that was recorded
    """
    print("📊 Recording Monthly Snapshot")
    print("=" * 70)
    print()

    # Load current data
    config = load_config()
    snapshot_data = calculate_financial_snapshot(config)

    # Get monthly spending from config if available
    monthly_spending = snapshot_data.get('monthly_recurring', 0)

    # Create snapshot entry
    snapshot = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'month': datetime.now().strftime('%Y-%m'),
        'data': {
            'net_worth': snapshot_data['net_worth'],
            'liquid_cash': snapshot_data['liquid_cash'],
            'credit_card_debt': snapshot_data['consumer_debt'],  # Approximation
            'total_debt': snapshot_data['total_debt'],
            'monthly_income': snapshot_data['monthly_income'],
            'monthly_spending': monthly_spending,
            'discretionary_spending': 0,  # Would need to calculate from transactions
        },
        'calculated': {
            'debt_to_income': (monthly_spending * 12) / (snapshot_data['monthly_income'] * 12) if snapshot_data['monthly_income'] > 0 else 0,
            'emergency_months': snapshot_data['liquid_cash'] / monthly_spending if monthly_spending > 0 else 0,
            'discretionary_pct': 0,
            'cash_flow': snapshot_data['monthly_income'] - monthly_spending
        }
    }

    # Load existing history
    history = load_history()

    # Check if this month already exists
    current_month = snapshot['month']
    history = [h for h in history if h['month'] != current_month]
    history.append(snapshot)

    # Sort by date
    history = sorted(history, key=lambda x: x['date'])

    # Save history
    save_json(history, HISTORY_FILE, update_metadata=False)

    print(f"✅ Snapshot recorded for {snapshot['month']}")
    print()
    print("📈 Key Metrics:")
    print(f"   Net Worth:   ${snapshot['data']['net_worth']:,.0f}")
    print(f"   Liquid Cash: ${snapshot['data']['liquid_cash']:,.0f}")
    print(f"   Total Debt:  ${snapshot['data']['total_debt']:,.0f}")
    print(f"   Cash Flow:   ${snapshot['calculated']['cash_flow']:+,.0f}/month")
    print()
    print(f"📊 Total months tracked: {len(history)}")
    print()

    return snapshot


def archive_snapshot() -> bool:
    """
    Archive current financial state to snapshots/YYYY-MM/ directory.

    Returns:
        True if successful, False otherwise
    """
    print("📸 Archiving Monthly Snapshot")
    print("=" * 70)
    print()

    # Get snapshot directory for current month
    snapshot_month = datetime.now().strftime('%Y-%m')
    snapshot_dir = SNAPSHOTS_DIR / snapshot_month
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    print(f"Snapshot directory: {snapshot_dir}")
    print()

    files_saved = []
    files_failed = []

    print("Saving snapshot files...")

    # Copy JSON files from processed directory
    json_files = ['dashboard_data.json', 'financial_config.json', 'budget.json']
    for filename in json_files:
        source = PROCESSED_DIR / filename
        dest = snapshot_dir / filename

        if source.exists():
            shutil.copy2(source, dest)
            files_saved.append(filename)
            print(f"  ✅ {filename}")
        else:
            files_failed.append(filename)
            print(f"  ⚠️  {filename} (not found)")

    # Save current month transactions to snapshot
    from financial_utils import TRANSACTIONS_FILE

    if TRANSACTIONS_FILE.exists():
        current_month = datetime.now().strftime('%Y-%m')
        dest = snapshot_dir / "transactions_monthly.csv"

        try:
            with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f_in:
                reader = csv.DictReader(f_in)
                fieldnames = reader.fieldnames

                # Filter to current month only
                monthly_transactions = [row for row in reader if row.get('Date', '').startswith(current_month)]

                # Write to snapshot
                if monthly_transactions and fieldnames:
                    with open(dest, 'w', encoding='utf-8', newline='') as f_out:
                        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(monthly_transactions)
                    files_saved.append('transactions_monthly.csv')
                    print(f"  ✅ transactions_monthly.csv ({len(monthly_transactions)} transactions)")
                else:
                    files_failed.append('transactions_monthly.csv')
                    print(f"  ⚠️  transactions_monthly.csv (no transactions for current month)")
        except Exception as e:
            files_failed.append('transactions_monthly.csv')
            print(f"  ⚠️  transactions_monthly.csv (error: {e})")
    else:
        files_failed.append('transactions_monthly.csv')
        print(f"  ⚠️  transactions_monthly.csv (source not found)")

    print()

    # Create snapshot summary
    print("Creating snapshot summary...")
    create_snapshot_summary(snapshot_dir)
    print("  ✅ snapshot_summary.json")
    print()

    # Results
    print("=" * 70)
    print("✅ SNAPSHOT ARCHIVED")
    print("=" * 70)
    print()
    print(f"Location: {snapshot_dir}")
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
        print(f"  Alerts:         {summary['alerts_count']}")
        print()

    return len(files_failed) == 0


def create_snapshot_summary(snapshot_dir: Path):
    """Create a summary of the archived snapshot."""
    dashboard_data_file = snapshot_dir / "dashboard_data.json"

    if not dashboard_data_file.exists():
        # Create minimal summary without dashboard data
        config = load_config()
        snapshot_data = calculate_financial_snapshot(config)

        summary = {
            'snapshot_date': datetime.now().isoformat(),
            'snapshot_month': snapshot_dir.name,
            'financial_snapshot': snapshot_data,
            'budget_summary': {},
            'emergency_fund': {},
            'credit_card_debt': snapshot_data['consumer_debt'],
            'alerts_count': 0
        }
    else:
        # Use dashboard data for detailed summary
        with open(dashboard_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        summary = {
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

    # Save summary
    summary_file = snapshot_dir / "snapshot_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


def generate_trends_report() -> str:
    """
    Generate trends analysis report from historical snapshots.

    Returns:
        Markdown report content
    """
    print("📈 Generating Trends Report")
    print("=" * 70)
    print()

    history = load_history()

    if len(history) < 2:
        report = "# FINANCIAL TRENDS\n\nNot enough data yet. Track for at least 2 months.\n"
        print("⚠️  Need at least 2 months of data for trend analysis")
        return report

    report = f"""# FINANCIAL TRENDS REPORT
**Generated:** {datetime.now().strftime('%B %d, %Y')}
**Months Tracked:** {len(history)}

---

## 📈 TREND OVERVIEW

### Net Worth Trend

| Month | Net Worth | Change | % Change |
|-------|-----------|--------|----------|
"""

    # Net worth trend
    for i, entry in enumerate(history):
        nw = entry['data']['net_worth']
        if i > 0:
            prev_nw = history[i-1]['data']['net_worth']
            change = nw - prev_nw
            pct = (change / prev_nw * 100) if prev_nw != 0 else 0
            report += f"| {entry['month']} | ${nw:,.0f} | ${change:+,.0f} | {pct:+.1f}% |\n"
        else:
            report += f"| {entry['month']} | ${nw:,.0f} | - | - |\n"

    report += "\n### Credit Card Debt Trend\n\n"
    report += "| Month | Balance | Paid | Progress |\n"
    report += "|-------|---------|------|----------|\n"

    for i, entry in enumerate(history):
        cc = entry['data'].get('credit_card_debt', 0)
        if i > 0:
            prev_cc = history[i-1]['data'].get('credit_card_debt', 0)
            paid = prev_cc - cc
            report += f"| {entry['month']} | ${cc:,.0f} | ${paid:,.0f} | "
            if paid > 0:
                report += "✅ Improved |\n"
            elif paid < 0:
                report += "🔴 Worse |\n"
            else:
                report += "→ Same |\n"
        else:
            report += f"| {entry['month']} | ${cc:,.0f} | - | - |\n"

    report += "\n### Emergency Fund Trend\n\n"
    report += "| Month | Balance | Change | Months Coverage |\n"
    report += "|-------|---------|--------|----------------|\n"

    for i, entry in enumerate(history):
        cash = entry['data']['liquid_cash']
        months_cov = entry['calculated'].get('emergency_months', 0)
        if i > 0:
            prev_cash = history[i-1]['data']['liquid_cash']
            change = cash - prev_cash
            report += f"| {entry['month']} | ${cash:,.0f} | ${change:+,.0f} | {months_cov:.1f} months |\n"
        else:
            report += f"| {entry['month']} | ${cash:,.0f} | - | {months_cov:.1f} months |\n"

    report += "\n### Spending Trend\n\n"
    report += "| Month | Income | Spending | Cash Flow | Discretionary |\n"
    report += "|-------|--------|----------|-----------|---------------|\n"

    for entry in history:
        income = entry['data'].get('monthly_income', 0)
        spending = entry['data'].get('monthly_spending', 0)
        flow = entry['calculated'].get('cash_flow', 0)
        disc = entry['data'].get('discretionary_spending', 0)
        report += f"| {entry['month']} | ${income:,.0f} | ${spending:,.0f} | ${flow:+,.0f} | ${disc:,.0f} |\n"

    report += f"""

---

## 💡 INSIGHTS

### Progress Summary

**Total Months Tracked:** {len(history)}

**Latest Snapshot:**
- Net Worth: ${history[-1]['data']['net_worth']:,.0f}
- Liquid Cash: ${history[-1]['data']['liquid_cash']:,.0f}
- Total Debt: ${history[-1]['data']['total_debt']:,.0f}
- Cash Flow: ${history[-1]['calculated']['cash_flow']:+,.0f}/month

**Overall Trends:**
"""

    # Calculate overall trends
    if len(history) >= 2:
        first = history[0]
        last = history[-1]

        nw_change = last['data']['net_worth'] - first['data']['net_worth']
        cash_change = last['data']['liquid_cash'] - first['data']['liquid_cash']
        debt_change = last['data']['total_debt'] - first['data']['total_debt']

        report += f"- Net Worth: ${nw_change:+,.0f} ({'+' if nw_change > 0 else ''}{(nw_change/first['data']['net_worth']*100):.1f}%)\n"
        report += f"- Liquid Cash: ${cash_change:+,.0f} ({'+' if cash_change > 0 else ''}{(cash_change/first['data']['liquid_cash']*100 if first['data']['liquid_cash'] else 0):.1f}%)\n"
        report += f"- Total Debt: ${debt_change:+,.0f} ({'+' if debt_change > 0 else ''}{(debt_change/first['data']['total_debt']*100 if first['data']['total_debt'] else 0):.1f}%)\n"

    report += f"""

---

**Generated by:** snapshot_manager.py
**Data File:** financial_history.json
**Next Update:** Monthly
"""

    # Save report
    save_report(report, "FINANCIAL_TRENDS.md")
    print(f"✅ Trend report generated: FINANCIAL_TRENDS.md")
    print()

    return report


def main():
    """Main entry point with subcommands."""
    parser = argparse.ArgumentParser(
        description='Manage financial snapshots and trend tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  record    Record current financial state to history
  archive   Archive current state to snapshots/YYYY-MM/ directory
  trends    Generate trend analysis report
  all       Execute all three commands in sequence

Examples:
  %(prog)s record
  %(prog)s archive
  %(prog)s trends
  %(prog)s all
        """
    )

    parser.add_argument(
        'command',
        choices=['record', 'archive', 'trends', 'all'],
        help='Command to execute'
    )

    args = parser.parse_args()

    print()

    if args.command == 'all':
        # Execute all commands in sequence
        record_snapshot()
        archive_snapshot()
        generate_trends_report()

        print("=" * 70)
        print("✅ ALL SNAPSHOT OPERATIONS COMPLETE")
        print("=" * 70)
        print()

    elif args.command == 'record':
        record_snapshot()

    elif args.command == 'archive':
        archive_snapshot()

    elif args.command == 'trends':
        generate_trends_report()

    return 0


if __name__ == '__main__':
    sys.exit(main())
