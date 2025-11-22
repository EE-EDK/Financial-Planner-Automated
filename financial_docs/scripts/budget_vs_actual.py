#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Budget vs Actual Tracker
Compare budgeted amounts vs actual spending by category

Usage:
    python3 financial_docs/budget_vs_actual.py

Requires: AllTransactions.csv in Archive/
"""

from pathlib import Path
from datetime import datetime
import csv
import json
from collections import defaultdict
import sys
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent  # Go up from scripts/ to financial_docs/
ARCHIVE_DIR = BASE_DIR / "Archive"
PROCESSED_DIR = ARCHIVE_DIR / "processed"
EXPORTS_DIR = ARCHIVE_DIR / "raw" / "exports"
CSV_FILE = EXPORTS_DIR / "AllTransactions.csv"
BUDGET_FILE = PROCESSED_DIR / "budget.json"


def load_budget():
    """Load budget from JSON config"""
    if BUDGET_FILE.exists():
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Combine category_budgets and fixed_expenses
            budget = data.get('category_budgets', {})
            budget.update(data.get('fixed_expenses', {}))
            return budget
    # Fallback defaults
    return {
        'Dining & Drinks': 250,
        'Groceries': 1000,
        'Shopping': 100,
        'Entertainment & Rec.': 100,
    }

def load_recent_transactions(months=1):
    """Load transactions from last N months"""
    if not CSV_FILE.exists():
        return []

    transactions = []
    cutoff_date = datetime.now()

    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Try to parse date
                date_str = row.get('Date', row.get('date', ''))
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y']:
                    try:
                        trans_date = datetime.strptime(date_str, fmt)
                        # Check if within last N months
                        months_diff = (cutoff_date.year - trans_date.year) * 12 + cutoff_date.month - trans_date.month
                        if months_diff <= months:
                            transactions.append(row)
                        break
                    except ValueError:
                        continue

    except Exception as e:
        print(f"Error loading CSV: {e}")

    return transactions

def categorize_spending(transactions):
    """Categorize spending from transactions"""
    spending = defaultdict(float)

    for trans in transactions:
        category = trans.get('Category', 'Unknown')
        amount = trans.get('Amount', '0')

        try:
            amount_float = abs(float(str(amount).replace('$', '').replace(',', '')))
            spending[category] += amount_float
        except ValueError:
            continue

    return dict(spending)

def generate_report(budget, actual, months=1):
    """Generate budget vs actual report"""

    report = f"""# BUDGET VS ACTUAL REPORT
**Generated:** {datetime.now().strftime('%B %d, %Y')}
**Period:** Last {months} month{'s' if months > 1 else ''}

---

## 📊 COMPARISON SUMMARY

### Budget Performance

| Category | Budget | Actual | Variance | % of Budget | Status |
|----------|--------|--------|----------|-------------|--------|
"""

    total_budget = 0
    total_actual = 0
    total_variance = 0

    # Compare each category
    all_categories = set(list(budget.keys()) + list(actual.keys()))

    for category in sorted(all_categories):
        # Scale monthly budget by number of months analyzed
        budgeted = budget.get(category, 0) * months
        spent = actual.get(category, 0)
        variance = spent - budgeted
        pct = (spent / budgeted * 100) if budgeted > 0 else 0

        # Status emoji
        if variance <= 0:
            status = '🟢 Under'
        elif variance <= budgeted * 0.1:
            status = '🟡 Close'
        else:
            status = '🔴 Over'

        if budgeted > 0 or spent > 0:  # Only show relevant categories
            report += f"| **{category}** | ${budgeted:,.0f} | ${spent:,.0f} | ${variance:+,.0f} | {pct:.0f}% | {status} |\n"

            total_budget += budgeted
            total_actual += spent
            total_variance += variance

    # Totals
    total_pct = (total_actual / total_budget * 100) if total_budget > 0 else 0
    overall_status = '🟢 Under Budget' if total_variance <= 0 else '🔴 Over Budget'

    report += f"| **TOTAL** | **${total_budget:,.0f}** | **${total_actual:,.0f}** | **${total_variance:+,.0f}** | **{total_pct:.0f}%** | **{overall_status}** |\n"

    report += f"""

---

## 🎯 PERFORMANCE BY CATEGORY

### Top Performers (Under Budget)

"""

    under_budget = [(cat, budget.get(cat, 0) - actual.get(cat, 0))
                    for cat in all_categories
                    if budget.get(cat, 0) - actual.get(cat, 0) > 0]
    under_budget.sort(key=lambda x: x[1], reverse=True)

    if under_budget:
        for cat, savings in under_budget[:5]:
            report += f"- ✅ **{cat}**: Saved ${savings:,.0f}\n"
    else:
        report += "- No categories under budget\n"

    report += "\n### Problem Areas (Over Budget)\n\n"

    over_budget = [(cat, actual.get(cat, 0) - budget.get(cat, 0))
                   for cat in all_categories
                   if actual.get(cat, 0) - budget.get(cat, 0) > 0]
    over_budget.sort(key=lambda x: x[1], reverse=True)

    if over_budget:
        for cat, overage in over_budget[:5]:
            report += f"- 🔴 **{cat}**: Over by ${overage:,.0f}\n"
    else:
        report += "- ✅ All categories within budget!\n"

    report += f"""

---

## 💡 RECOMMENDATIONS

"""

    if total_variance > 0:
        report += f"""
### Immediate Actions

1. **Cut Overspending:** Focus on {over_budget[0][0] if over_budget else 'discretionary'} category
2. **Review Transactions:** Identify unnecessary purchases
3. **Adjust Habits:** Implement spending controls

### Monthly Adjustments

"""
        for cat, overage in over_budget[:3]:
            report += f"- Reduce **{cat}** by ${overage:,.0f}/month\n"
    else:
        report += """
### Great Job! 🎉

You're under budget! Keep up the good work.

**Suggestions:**
- Allocate savings to emergency fund
- Apply extra to debt payoff
- Build investment buffer
"""

    report += f"""

---

## 📈 TRENDS

**Overall Budget Adherence:** {100.0 if total_variance <= 0 else (total_budget / total_actual * 100) if total_actual > 0 else 100.0:.1f}%

**Categories On Track:** {len([c for c in all_categories if actual.get(c, 0) <= budget.get(c, 0) * months])} / {len(all_categories)}

---

## 🔗 RELATED DOCUMENTS

- **[BUDGET_GUIDELINES.md](BUDGET_GUIDELINES.md)** - Budget targets
- **[DASHBOARD.md](DASHBOARD.md)** - Real-time metrics
- **[MONTHLY_REVIEW_TEMPLATE.md](MONTHLY_REVIEW_TEMPLATE.md)** - Monthly review

---

**Generated by:** budget_vs_actual.py
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Next Update:** Run monthly after reviewing transactions
"""

    return report

def main():
    print("📊 Budget vs Actual Tracker")
    print("=" * 70)
    print()

    # Parse command-line argument for months
    months = 1
    if len(sys.argv) > 1:
        try:
            months = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  Invalid months argument: {sys.argv[1]}, using 1")
            months = 1

    # Load budget from JSON
    print("📥 Loading budget from config...")
    budget = load_budget()
    print(f"   Loaded {len(budget)} budget categories")

    # Load transactions
    print(f"📥 Loading transactions (last {months} month{'s' if months > 1 else ''})...")
    transactions = load_recent_transactions(months=months)
    print(f"   Found {len(transactions)} transactions")
    print()

    if not transactions:
        print("⚠️  No recent transactions found")
        print("   Make sure AllTransactions.csv is in Archive/raw/exports/")
        return 1

    # Categorize spending
    print("📊 Analyzing spending by category...")
    actual_spending = categorize_spending(transactions)
    print(f"   Categories found: {len(actual_spending)}")
    print()

    # Generate report
    print("📝 Generating report...")
    report = generate_report(budget, actual_spending, months=months)

    # Save report with UTF-8 encoding
    output_file = ARCHIVE_DIR / "reports" / "BUDGET_VS_ACTUAL.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Report saved: {output_file}")
    print()

    # Quick summary
    total_budget = sum(budget.values()) * months
    total_actual = sum(actual_spending.values())
    variance = total_actual - total_budget

    print("📊 Quick Summary:")
    print(f"   Budget: ${total_budget:,.0f}")
    print(f"   Actual: ${total_actual:,.0f}")
    print(f"   Variance: ${variance:+,.0f}")
    print(f"   Status: {'🟢 Under Budget' if variance <= 0 else '🔴 Over Budget'}")
    print()

    print("💡 To view:")
    print("   1. Rebuild: python3 financial_docs/build_financial_docs.py")
    print("   2. Open: financial_docs/financial_hub.html")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
