#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monthly Snapshot Tracker
Track financial metrics over time for trend analysis

Usage:
    python3 financial_docs/track_monthly_snapshot.py

Creates monthly snapshots in financial_history.json
"""

import json
from pathlib import Path
from datetime import datetime
import sys
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent  # Go up from scripts/ to financial_docs/
ARCHIVE_DIR = BASE_DIR / "Archive"
HISTORY_FILE = ARCHIVE_DIR / "financial_history.json"

# Update these values monthly
CURRENT_DATA = {
    'net_worth': 456000,
    'liquid_cash': 7462,
    'credit_card_debt': 30000,
    'total_debt': 483301,
    'monthly_income': 15334,
    'monthly_spending': 15931,
    'emergency_fund_target': 52596,
    'retirement_balance': 192042,
    'primary_mortgage': 256506,
    'rental_mortgage': 138226,
    'honda_loan': 28686,
    'discretionary_spending': 5393,
}

def load_history():
    """Load existing history"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_snapshot(data):
    """Save monthly snapshot"""
    history = load_history()

    snapshot = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'month': datetime.now().strftime('%Y-%m'),
        'data': data,
        'calculated': {
            'debt_to_income': (data['monthly_spending'] * 12) / (data['monthly_income'] * 12),
            'emergency_months': data['liquid_cash'] / data['monthly_spending'],
            'discretionary_pct': data['discretionary_spending'] / data['monthly_income'],
            'cash_flow': data['monthly_income'] - data['monthly_spending']
        }
    }

    # Check if this month already exists
    current_month = snapshot['month']
    history = [h for h in history if h['month'] != current_month]
    history.append(snapshot)

    # Sort by date
    history = sorted(history, key=lambda x: x['date'])

    # Ensure parent directory exists
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

    return snapshot

def generate_trend_report(history):
    """Generate trend analysis report"""

    if len(history) < 2:
        return "# FINANCIAL TRENDS\n\nNot enough data yet. Track for at least 2 months.\n"

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
            pct = (change / prev_nw * 100) if prev_nw > 0 else 0
            report += f"| {entry['month']} | ${nw:,.0f} | ${change:+,.0f} | {pct:+.1f}% |\n"
        else:
            report += f"| {entry['month']} | ${nw:,.0f} | - | - |\n"

    report += "\n### Credit Card Debt Trend\n\n"
    report += "| Month | Balance | Paid | Progress |\n"
    report += "|-------|---------|------|----------|\n"

    for i, entry in enumerate(history):
        cc = entry['data']['credit_card_debt']
        if i > 0:
            prev_cc = history[i-1]['data']['credit_card_debt']
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
        months_cov = entry['calculated']['emergency_months']
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
        income = entry['data']['monthly_income']
        spending = entry['data']['monthly_spending']
        flow = entry['calculated']['cash_flow']
        disc = entry['data']['discretionary_spending']
        report += f"| {entry['month']} | ${income:,.0f} | ${spending:,.0f} | ${flow:+,.0f} | ${disc:,.0f} |\n"

    report += f"""

---

## 💡 INSIGHTS

### Progress Summary

**Best Month:**
- [Calculate from data]

**Areas of Improvement:**
- [Calculate from data]

**Areas Needing Attention:**
- [Calculate from data]

---

**Generated by:** track_monthly_snapshot.py
**Data File:** financial_history.json
**Next Update:** Monthly
"""

    return report

def main():
    print("📊 Monthly Snapshot Tracker")
    print("=" * 70)
    print()

    # Save current snapshot
    print("💾 Saving current snapshot...")
    snapshot = save_snapshot(CURRENT_DATA)

    print(f"✅ Snapshot saved for {snapshot['month']}")
    print()
    print("📈 Key Metrics:")
    print(f"   Net Worth: ${snapshot['data']['net_worth']:,.0f}")
    print(f"   Liquid Cash: ${snapshot['data']['liquid_cash']:,.0f}")
    print(f"   Credit Card: ${snapshot['data']['credit_card_debt']:,.0f}")
    print(f"   Cash Flow: ${snapshot['calculated']['cash_flow']:+,.0f}/month")
    print()

    # Load full history
    history = load_history()
    print(f"📊 Total months tracked: {len(history)}")
    print()

    # Generate trend report
    if len(history) >= 2:
        print("📈 Generating trend report...")
        report = generate_trend_report(history)

        output_file = ARCHIVE_DIR / "FINANCIAL_TRENDS.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ Trend report saved: {output_file}")
    else:
        print("ℹ️  Need at least 2 months of data for trend analysis")

    print()
    print("💡 Next steps:")
    print("   1. Update CURRENT_DATA in this script monthly")
    print("   2. Run script on the same day each month")
    print("   3. Rebuild docs to see trends")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
