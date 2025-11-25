#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Category Trends Analyzer for Category-Based Excel Format
Analyzes spending trends across categories over time
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

def analyze_category_trends():
    """Analyze category spending trends over time"""

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

    # Analyze by category
    category_totals = defaultdict(Decimal)
    category_monthly = defaultdict(lambda: defaultdict(Decimal))

    for txn in transactions:
        try:
            date = txn.get('Date', '')
            amount = Decimal(str(txn.get('Amount', 0)))
            category = txn.get('Category', 'Uncategorized')

            # Total by category
            category_totals[category] += abs(amount)

            # Monthly by category
            if date:
                month = date[:7]  # YYYY-MM
                category_monthly[category][month] += abs(amount)
        except:
            continue

    # Generate report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_file = REPORTS_DIR / "CATEGORY_TRENDS.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📊 Category Spending Trends\n\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n")
        f.write("---\n\n")

        f.write("## Overall Category Breakdown\n\n")

        # Sort categories by total spending
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

        total_spending = sum(category_totals.values())

        f.write("| Rank | Category | Total | % of Total |\n")
        f.write("|------|----------|-------|------------|\n")

        for idx, (category, amount) in enumerate(sorted_categories, 1):
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            f.write(f"| {idx} | {category} | ${amount:,.2f} | {percentage:.1f}% |\n")

        f.write(f"\n**Total Activity:** ${total_spending:,.2f}\n\n")

        f.write("---\n\n")
        f.write("## Top 5 Categories - Monthly Trends\n\n")

        # Show trends for top 5 categories
        top_5_categories = [cat for cat, _ in sorted_categories[:5]]

        for category in top_5_categories:
            f.write(f"### {category}\n\n")

            monthly_data = category_monthly[category]
            sorted_months = sorted(monthly_data.keys())

            if sorted_months:
                f.write("| Month | Amount | Trend |\n")
                f.write("|-------|--------|-------|\n")

                prev_amount = None
                for month in sorted_months:
                    amount = monthly_data[month]
                    trend = ""
                    if prev_amount is not None:
                        if amount > prev_amount:
                            trend = "📈 Up"
                        elif amount < prev_amount:
                            trend = "📉 Down"
                        else:
                            trend = "➡️ Stable"

                    f.write(f"| {month} | ${amount:,.2f} | {trend} |\n")
                    prev_amount = amount

                # Calculate average
                avg_amount = sum(monthly_data.values()) / len(monthly_data)
                f.write(f"\n**Monthly Average:** ${avg_amount:,.2f}\n\n")
            else:
                f.write("No monthly data available\n\n")

        f.write("---\n\n")
        f.write("## Category Growth Analysis\n\n")

        f.write("Categories with increasing spend over time:\n\n")

        # Analyze growth trends
        for category in top_5_categories:
            monthly_data = category_monthly[category]
            sorted_months = sorted(monthly_data.keys())

            if len(sorted_months) >= 2:
                first_month_avg = sum(monthly_data[m] for m in sorted_months[:3]) / min(3, len(sorted_months[:3]))
                last_month_avg = sum(monthly_data[m] for m in sorted_months[-3:]) / min(3, len(sorted_months[-3:]))

                change = ((last_month_avg - first_month_avg) / first_month_avg * 100) if first_month_avg > 0 else 0

                if abs(change) > 5:  # Significant change
                    direction = "📈 Increased" if change > 0 else "📉 Decreased"
                    f.write(f"- **{category}**: {direction} by {abs(change):.1f}%\n")

        f.write("\n---\n\n")
        f.write("*This report analyzes spending patterns across categories over time*\n")

    print(f"✅ Category trends report generated: {output_file}")
    return True

def main():
    return 0 if analyze_category_trends() else 1

if __name__ == '__main__':
    sys.exit(main())
