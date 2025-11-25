#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Balance Timeline Analyzer for Category-Based Excel Format
Tracks balance progression over time from transaction data
"""

import sys
import csv
import io
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

# Fix Windows console encoding
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
ARCHIVE_DIR = BASE_DIR / "Archive"
REPORTS_DIR = ARCHIVE_DIR / "reports"
EXPORTS_DIR = ARCHIVE_DIR / "raw" / "exports"

def analyze_balance_timeline():
    """Analyze balance progression over time"""

    csv_file = EXPORTS_DIR / "AllTransactions.csv"

    if not csv_file.exists():
        print("❌ AllTransactions.csv not found")
        return False

    # Read transactions
    transactions = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append(row)

    # Sort by date
    transactions.sort(key=lambda x: x.get('Date', ''))

    # Track daily totals
    daily_activity = defaultdict(lambda: {'income': Decimal(0), 'expenses': Decimal(0), 'net': Decimal(0)})

    for txn in transactions:
        try:
            date = txn.get('Date', '')
            if not date:
                continue

            amount = Decimal(str(txn.get('Amount', 0)))

            if amount > 0:
                daily_activity[date]['income'] += amount
            else:
                daily_activity[date]['expenses'] += abs(amount)

            daily_activity[date]['net'] += amount
        except:
            continue

    # Generate report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = REPORTS_DIR / "BALANCE_TIMELINE.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📈 Balance Timeline Analysis\n\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total Days with Activity:** {len(daily_activity)}\n")
        f.write(f"- **Total Transactions:** {len(transactions)}\n\n")

        # Calculate totals
        total_income = sum(day['income'] for day in daily_activity.values())
        total_expenses = sum(day['expenses'] for day in daily_activity.values())
        net_change = total_income - total_expenses

        f.write(f"- **Total Income:** ${total_income:,.2f}\n")
        f.write(f"- **Total Expenses:** ${total_expenses:,.2f}\n")
        f.write(f"- **Net Change:** ${net_change:,.2f}\n\n")

        f.write("---\n\n")
        f.write("## Daily Activity Timeline\n\n")

        # Show last 30 days of activity
        sorted_dates = sorted(daily_activity.keys(), reverse=True)[:30]

        f.write("### Recent Activity (Last 30 Days)\n\n")
        f.write("| Date | Income | Expenses | Net Change |\n")
        f.write("|------|--------|----------|------------|\n")

        for date in sorted_dates:
            activity = daily_activity[date]
            f.write(f"| {date} | ${activity['income']:,.2f} | ${activity['expenses']:,.2f} | ${activity['net']:,.2f} |\n")

        f.write("\n---\n\n")
        f.write("## Monthly Summary\n\n")

        # Group by month
        monthly_activity = defaultdict(lambda: {'income': Decimal(0), 'expenses': Decimal(0), 'net': Decimal(0)})

        for date, activity in daily_activity.items():
            month = date[:7]  # YYYY-MM
            monthly_activity[month]['income'] += activity['income']
            monthly_activity[month]['expenses'] += activity['expenses']
            monthly_activity[month]['net'] += activity['net']

        f.write("| Month | Income | Expenses | Net | Savings Rate |\n")
        f.write("|-------|--------|----------|-----|-------------|\n")

        for month in sorted(monthly_activity.keys(), reverse=True):
            activity = monthly_activity[month]
            savings_rate = (activity['net'] / activity['income'] * 100) if activity['income'] > 0 else 0
            f.write(f"| {month} | ${activity['income']:,.2f} | ${activity['expenses']:,.2f} | ${activity['net']:,.2f} | {savings_rate:.1f}% |\n")

        f.write("\n---\n\n")
        f.write("*This report tracks your balance changes over time based on transaction data*\n")

    print(f"✅ Balance timeline report generated: {output_file}")
    return True

def main():
    return 0 if analyze_balance_timeline() else 1

if __name__ == '__main__':
    sys.exit(main())
