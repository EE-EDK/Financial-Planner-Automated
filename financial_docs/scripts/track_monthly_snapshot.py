#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monthly Snapshot Tracker (TEMPLATE)
Track financial metrics over time for trend analysis

⚠️  THIS IS A TEMPLATE - Update CURRENT_DATA below with your values

Usage:
    python3 financial_docs/scripts/track_monthly_snapshot.py
"""

import json
from pathlib import Path
from datetime import datetime
import sys
import io

# Fix Windows console encoding for emoji support
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
ARCHIVE_DIR = BASE_DIR / "Archive"
HISTORY_FILE = ARCHIVE_DIR / "financial_history.json"

# ============================================================================
# UPDATE THESE VALUES MONTHLY
# ============================================================================

CURRENT_DATA = {
    'net_worth': 40000,  # Total assets - total liabilities
    'liquid_cash': 15000,  # Checking + savings + brokerage
    'total_debt': 265000,  # All debt (mortgage + car + credit cards)
    'monthly_income': 7500,  # Monthly income
    'monthly_spending': 6000,  # Average monthly spending
    'emergency_fund_target': 18000,  # 3 months of expenses target
    'retirement_balance': 50000,  # 401k/IRA balances
    'discretionary_spending': 1500,  # Non-essential spending
}

# ============================================================================

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

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

    return snapshot

def main():
    print("📸 Monthly Snapshot Tracker")
    print("=" * 70)
    print()
    print("⚠️  UPDATE CURRENT_DATA values in this script first!")
    print()

    snapshot = save_snapshot(CURRENT_DATA)

    print(f"✅ Snapshot saved for {snapshot['month']}")
    print()
    print(f"   Net Worth: ${snapshot['data']['net_worth']:,}")
    print(f"   Liquid Cash: ${snapshot['data']['liquid_cash']:,}")
    print(f"   Emergency Months: {snapshot['calculated']['emergency_months']:.1f}")
    print(f"   Cash Flow: ${snapshot['calculated']['cash_flow']:,}/month")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
