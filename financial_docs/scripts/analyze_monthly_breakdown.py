#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monthly Breakdown Analyzer for Category-Based Excel Format
Creates detailed month-by-month spending breakdowns
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

def analyze_monthly_breakdown():
    """Create detailed monthly breakdown by category"""

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

    # Organize by month and category
    monthly_categories = defaultdict(lambda: defaultdict(Decimal))
    monthly_totals = defaultdict(Decimal)
    all_categories = set()

    for txn in transactions:
        try:
            date = txn.get('Date', '')
            if not date:
                continue

            month = date[:7]  # YYYY-MM
            amount = Decimal(str(txn.get('Amount', 0)))
            category = txn.get('Category', 'Uncategorized')

            monthly_categories[month][category] += abs(amount)
            monthly_totals[month] += abs(amount)
            all_categories.add(category)
        except:
            continue

    # Generate report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = REPORTS_DIR / "MONTHLY_BREAKDOWN.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📅 Monthly Breakdown by Category\n\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Months Analyzed:** {len(monthly_totals)}\n")
        f.write(f"- **Categories Tracked:** {len(all_categories)}\n")
        f.write(f"- **Total Transactions:** {len(transactions)}\n\n")

        # Sort months
        sorted_months = sorted(monthly_totals.keys(), reverse=True)

        f.write("## Monthly Totals\n\n")
        f.write("| Month | Total Activity |\n")
        f.write("|-------|---------------|\n")

        for month in sorted_months:
            f.write(f"| {month} | ${monthly_totals[month]:,.2f} |\n")

        f.write("\n---\n\n")

        # Detailed breakdown for each month
        f.write("## Detailed Monthly Breakdowns\n\n")

        for month in sorted_months[:6]:  # Show last 6 months in detail
            f.write(f"### {month}\n\n")

            categories = monthly_categories[month]
            sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)

            f.write("| Category | Amount | % of Month |\n")
            f.write("|----------|--------|------------|\n")

            month_total = monthly_totals[month]

            for category, amount in sorted_cats:
                percentage = (amount / month_total * 100) if month_total > 0 else 0
                f.write(f"| {category} | ${amount:,.2f} | {percentage:.1f}% |\n")

            f.write(f"\n**Month Total:** ${month_total:,.2f}\n\n")

        f.write("---\n\n")

        # Category comparison across months
        f.write("## Category Comparison Across Months\n\n")

        # Get top 5 categories overall
        overall_categories = defaultdict(Decimal)
        for month_cats in monthly_categories.values():
            for cat, amount in month_cats.items():
                overall_categories[cat] += amount

        top_categories = sorted(overall_categories.items(), key=lambda x: x[1], reverse=True)[:5]

        for category, _ in top_categories:
            f.write(f"### {category}\n\n")
            f.write("| Month | Amount |\n")
            f.write("|-------|--------|\n")

            for month in sorted_months:
                amount = monthly_categories[month].get(category, Decimal(0))
                if amount > 0:
                    f.write(f"| {month} | ${amount:,.2f} |\n")

            f.write("\n")

        f.write("---\n\n")
        f.write("*This report provides detailed month-by-month spending breakdown*\n")

    print(f"✅ Monthly breakdown report generated: {output_file}")
    return True

def main():
    return 0 if analyze_monthly_breakdown() else 1

if __name__ == '__main__':
    sys.exit(main())
