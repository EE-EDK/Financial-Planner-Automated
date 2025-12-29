#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transaction Analyzer
Automatically analyze AllTransactions.csv and generate spending reports

Usage:
    python3 financial_docs/analyze_transactions.py

Output:
    - Generates TRANSACTION_ANALYSIS_REPORT.md in Archive/
    - Shows top spending categories
    - Identifies top merchants
    - Monthly trends
    - Waste identification
"""

import csv
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from financial_utils import (
    setup_windows_encoding,
    save_report,
    EXPORTS_DIR,
    TRANSACTIONS_FILE,
    REPORTS_DIR
)

# Setup encoding for cross-platform support
setup_windows_encoding()

CSV_FILE = TRANSACTIONS_FILE

def load_transactions():
    """Load transactions from CSV file"""
    if not CSV_FILE.exists():
        print(f"❌ Error: {CSV_FILE} not found")
        return []

    transactions = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            # Try to detect CSV format
            sample = f.read(1024)
            f.seek(0)

            # Common CSV headers we might encounter
            reader = csv.DictReader(f)

            for row in reader:
                transactions.append(row)

        print(f"✅ Loaded {len(transactions)} transactions")
        return transactions

    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return []

def analyze_by_category(transactions):
    """Analyze spending by category"""
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)

    for trans in transactions:
        # Adapt to your CSV column names
        category = trans.get('Category', trans.get('category', 'Unknown'))
        amount = trans.get('Amount', trans.get('amount', '0'))

        # Clean amount (remove $, commas, etc.)
        try:
            amount_float = float(str(amount).replace('$', '').replace(',', ''))
            # Only count expenses (negative or explicitly marked)
            if amount_float != 0:
                category_totals[category] += abs(amount_float)
                category_counts[category] += 1
        except ValueError:
            continue

    # Sort by total spending
    sorted_categories = sorted(
        category_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_categories, category_counts

def analyze_by_merchant(transactions):
    """Analyze spending by merchant"""
    merchant_totals = defaultdict(float)
    merchant_counts = defaultdict(int)

    for trans in transactions:
        merchant = trans.get('Merchant', trans.get('merchant', trans.get('Description', 'Unknown')))
        amount = trans.get('Amount', trans.get('amount', '0'))

        try:
            amount_float = float(str(amount).replace('$', '').replace(',', ''))
            if amount_float != 0:
                merchant_totals[merchant] += abs(amount_float)
                merchant_counts[merchant] += 1
        except ValueError:
            continue

    # Sort by total spending
    sorted_merchants = sorted(
        merchant_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_merchants[:20], merchant_counts  # Top 20

def analyze_monthly_trends(transactions):
    """Analyze spending trends by month"""
    monthly_totals = defaultdict(float)
    monthly_by_category = defaultdict(lambda: defaultdict(float))

    for trans in transactions:
        # Try to parse date
        date_str = trans.get('Date', trans.get('date', ''))
        amount = trans.get('Amount', trans.get('amount', '0'))
        category = trans.get('Category', trans.get('category', 'Unknown'))

        try:
            # Parse various date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d']:
                try:
                    date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                continue  # Skip if no format matched

            month_key = date.strftime('%Y-%m')
            amount_float = float(str(amount).replace('$', '').replace(',', ''))

            if amount_float != 0:
                monthly_totals[month_key] += abs(amount_float)
                monthly_by_category[month_key][category] += abs(amount_float)

        except Exception:
            continue

    # Sort by month
    sorted_months = sorted(monthly_totals.items())

    return sorted_months, monthly_by_category

def identify_waste(transactions):
    """Identify potential waste in spending"""
    waste_categories = {
        'Amazon': [],
        'Dining': [],
        'Fast Food': [],
        'Subscription': [],
        'Impulse': []
    }

    # Keywords for waste identification
    amazon_keywords = ['AMAZON', 'AMZ', 'AMZN']
    dining_keywords = ['RESTAURANT', 'CAFE', 'PIZZA', 'GRILL', 'DINER', 'BISTRO']
    fastfood_keywords = ['MCDONALDS', 'TACO BELL', 'BURGER', 'WENDYS', 'SUBWAY', 'CHIPOTLE', 'DOORDASH', 'UBER EATS']
    subscription_keywords = ['SUBSCRIPTION', 'MONTHLY', 'STREAMING', 'NETFLIX', 'SPOTIFY', 'HULU']

    for trans in transactions:
        merchant = trans.get('Merchant', trans.get('merchant', trans.get('Description', ''))).upper()
        amount = trans.get('Amount', trans.get('amount', '0'))

        try:
            amount_float = abs(float(str(amount).replace('$', '').replace(',', '')))

            if amount_float > 0:
                # Check each waste category
                if any(kw in merchant for kw in amazon_keywords):
                    waste_categories['Amazon'].append((merchant, amount_float))
                elif any(kw in merchant for kw in fastfood_keywords):
                    waste_categories['Fast Food'].append((merchant, amount_float))
                elif any(kw in merchant for kw in dining_keywords):
                    waste_categories['Dining'].append((merchant, amount_float))
                elif any(kw in merchant for kw in subscription_keywords):
                    waste_categories['Subscription'].append((merchant, amount_float))

        except ValueError:
            continue

    # Calculate totals
    waste_totals = {
        category: sum(amt for _, amt in items)
        for category, items in waste_categories.items()
    }

    return waste_totals, waste_categories

def generate_report(transactions):
    """Generate comprehensive analysis report"""

    print("\n📊 Analyzing transactions...")

    # Run analyses
    categories, cat_counts = analyze_by_category(transactions)
    merchants, merch_counts = analyze_by_merchant(transactions)
    monthly_trends, monthly_cats = analyze_monthly_trends(transactions)
    waste_totals, waste_details = identify_waste(transactions)

    # Calculate date range
    dates = []
    for trans in transactions:
        date_str = trans.get('Date', trans.get('date', ''))
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d']:
            try:
                dates.append(datetime.strptime(date_str, fmt))
                break
            except ValueError:
                continue

    if dates:
        start_date = min(dates)
        end_date = max(dates)
        months_analyzed = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
    else:
        start_date = datetime.now()
        end_date = datetime.now()
        months_analyzed = 0

    # Generate markdown report
    report = f"""# TRANSACTION ANALYSIS REPORT
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Data Source:** AllTransactions.csv
**Period:** {start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}
**Months Analyzed:** {months_analyzed}
**Total Transactions:** {len(transactions):,}

---

## 📊 EXECUTIVE SUMMARY

### Total Spending by Period

**Overall:**
- Total transactions: {len(transactions):,}
- Period: {months_analyzed} months
- Average per month: ${sum(cat[1] for cat in categories) / max(months_analyzed, 1):,.2f}

---

## 💳 TOP SPENDING CATEGORIES

### Top 15 Categories

| Rank | Category | Total Spent | Transactions | Avg per Transaction |
|------|----------|-------------|--------------|-------------------|
"""

    # Add categories
    for i, (category, total) in enumerate(categories[:15], 1):
        count = cat_counts[category]
        avg = total / count if count > 0 else 0
        report += f"| {i} | **{category}** | ${total:,.2f} | {count:,} | ${avg:.2f} |\n"

    report += f"""

---

## 🏪 TOP MERCHANTS

### Top 20 Merchants by Total Spending

| Rank | Merchant | Total Spent | Transactions |
|------|----------|-------------|--------------|
"""

    # Add merchants
    for i, (merchant, total) in enumerate(merchants, 1):
        count = merch_counts[merchant]
        report += f"| {i} | {merchant[:50]} | ${total:,.2f} | {count:,} |\n"

    report += f"""

---

## 📈 MONTHLY SPENDING TRENDS

### Last 12 Months (or available data)

| Month | Total Spending | Change from Previous |
|-------|---------------|---------------------|
"""

    # Add monthly trends
    prev_total = None
    for month, total in monthly_trends[-12:]:  # Last 12 months
        if prev_total:
            change = total - prev_total
            change_pct = (change / prev_total * 100) if prev_total > 0 else 0
            change_str = f"${change:+,.2f} ({change_pct:+.1f}%)"
        else:
            change_str = "-"

        report += f"| {month} | ${total:,.2f} | {change_str} |\n"
        prev_total = total

    report += f"""

---

## 🚨 WASTE IDENTIFICATION

### Potential Waste by Category

| Category | Total | Monthly Average | % of Total Spending |
|----------|-------|-----------------|---------------------|
"""

    total_spending = sum(cat[1] for cat in categories)

    for category, total in sorted(waste_totals.items(), key=lambda x: x[1], reverse=True):
        if total > 0:
            monthly_avg = total / max(months_analyzed, 1)
            pct = (total / total_spending * 100) if total_spending > 0 else 0
            report += f"| **{category}** | ${total:,.2f} | ${monthly_avg:,.2f} | {pct:.1f}% |\n"

    report += f"""

### Waste Analysis Details

**Amazon Spending:**
- Total: ${waste_totals.get('Amazon', 0):,.2f}
- Monthly Average: ${waste_totals.get('Amazon', 0) / max(months_analyzed, 1):,.2f}
- Recommendation: Target $200/month (84% reduction if current >$1,000/mo)

**Dining Out:**
- Total: ${waste_totals.get('Dining', 0):,.2f}
- Monthly Average: ${waste_totals.get('Dining', 0) / max(months_analyzed, 1):,.2f}
- Recommendation: Target $200/month (80% reduction if current >$1,000/mo)

**Fast Food:**
- Total: ${waste_totals.get('Fast Food', 0):,.2f}
- Monthly Average: ${waste_totals.get('Fast Food', 0) / max(months_analyzed, 1):,.2f}
- Recommendation: Eliminate (pack lunches, meal prep)

**Total Identified Waste:** ${sum(waste_totals.values()):,.2f}
**Monthly Waste Average:** ${sum(waste_totals.values()) / max(months_analyzed, 1):,.2f}

---

## 💡 INSIGHTS & RECOMMENDATIONS

### Spending Patterns

**High Spending Categories:**
"""

    # Top 3 categories
    for i, (category, total) in enumerate(categories[:3], 1):
        monthly_avg = total / max(months_analyzed, 1)
        report += f"{i}. **{category}**: ${monthly_avg:,.2f}/month average\n"

    report += f"""

**Opportunities for Savings:**

1. **Reduce Discretionary Spending**
   - Current waste: ${sum(waste_totals.values()) / max(months_analyzed, 1):,.2f}/month
   - Target: $450/month total discretionary
   - Potential savings: ${(sum(waste_totals.values()) / max(months_analyzed, 1)) - 450:,.2f}/month

2. **Eliminate Fast Food**
   - Current: ${waste_totals.get('Fast Food', 0) / max(months_analyzed, 1):,.2f}/month
   - Target: $0/month
   - Savings: ${waste_totals.get('Fast Food', 0) / max(months_analyzed, 1):,.2f}/month

3. **Control Amazon Spending**
   - Current: ${waste_totals.get('Amazon', 0) / max(months_analyzed, 1):,.2f}/month
   - Target: $200/month
   - Savings: ${max(0, (waste_totals.get('Amazon', 0) / max(months_analyzed, 1)) - 200):,.2f}/month

---

## 🎯 ACTION ITEMS

### Immediate Actions

- [ ] Review all Amazon purchases for necessities vs wants
- [ ] Delete food delivery apps
- [ ] Implement 30-day rule for all purchases >$25
- [ ] Set up spending alerts in Rocket Money
- [ ] Cancel unused subscriptions

### Monthly Habits

- [ ] Track every transaction immediately
- [ ] Weekly budget review (Sundays)
- [ ] Meal planning to avoid dining out
- [ ] Pack lunch 5 days/week

### Behavior Changes

- **Stop:** Impulse purchases, convenience dining, Amazon browsing
- **Start:** Meal prep, 30-day rule, cash-only for discretionary
- **Continue:** Tracking all expenses, monthly reviews

---

## 📊 DATA QUALITY NOTES

**Transaction Coverage:**
- Transactions analyzed: {len(transactions):,}
- Date range: {months_analyzed} months
- Average transactions per month: {len(transactions) / max(months_analyzed, 1):.0f}

**Limitations:**
- Analysis based on categorization in CSV
- Some merchants may be miscategorized
- Cash transactions may not be included
- Shared expenses may not be split

---

## 🔗 RELATED DOCUMENTS

- **[SPENDING_ANALYSIS.md](SPENDING_ANALYSIS.md)** - Detailed waste analysis
- **[DASHBOARD.md](DASHBOARD.md)** - Real-time metrics
- **[BUDGET_GUIDELINES.md](BUDGET_GUIDELINES.md)** - Budget targets
- **[MONTHLY_REVIEW_TEMPLATE.md](MONTHLY_REVIEW_TEMPLATE.md)** - Monthly tracking

---

**Next Steps:**
1. Review this report with family
2. Identify specific areas to cut
3. Update budget in Rocket Money
4. Set up automatic alerts
5. Re-run this analysis monthly to track progress

---

**Generated by:** analyze_transactions.py
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Data File:** AllTransactions.csv
"""

    return report

def main():
    print("💳 Transaction Analyzer")
    print("=" * 70)

    # Load transactions
    transactions = load_transactions()

    if not transactions:
        print("❌ No transactions to analyze")
        return 1

    # Generate report
    report = generate_report(transactions)

    # Save report using shared utility
    save_report(report, "TRANSACTION_ANALYSIS_REPORT.md")

    print(f"\n✅ Report generated: {REPORTS_DIR / 'TRANSACTION_ANALYSIS_REPORT.md'}")
    print(f"📊 Report size: {len(report)} characters")
    print()
    print("💡 To view:")
    print(f"   1. Rebuild docs: python3 financial_docs/build_financial_docs.py")
    print(f"   2. Open: financial_docs/financial_hub.html")
    print()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
