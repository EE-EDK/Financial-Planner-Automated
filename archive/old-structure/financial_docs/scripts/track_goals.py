#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Goals Tracker
Tracks progress toward financial goals

Reads:
- financial_goals.json (goal definitions)
- dashboard_data.json (current metrics)
- account_balance_history.json (historical data)

Updates:
- financial_goals.json (progress updates)

Displays:
- Goal progress
- Days remaining
- On-track status
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "Archive" / "processed"
GOALS_FILE = PROCESSED_DIR / "financial_goals.json"
DASHBOARD_FILE = PROCESSED_DIR / "dashboard_data.json"

def load_goals():
    """Load financial goals"""
    if GOALS_FILE.exists():
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'goals': {}, 'metadata': {}}

def load_dashboard_data():
    """Load dashboard data"""
    if DASHBOARD_FILE.exists():
        with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def calculate_goal_progress(goal, dashboard_data):
    """Calculate progress for a specific goal"""

    goal_type = goal.get('type')
    target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
    days_remaining = (target_date - datetime.now()).days

    progress = {
        'days_remaining': days_remaining,
        'on_track': None,
        'current_value': None,
        'target_value': goal.get('target_amount'),
        'percent_complete': 0,
        'status_message': ''
    }

    if goal_type == 'savings':
        # Emergency fund or savings goal
        emergency_fund = dashboard_data.get('emergency_fund', {})
        current_balance = emergency_fund.get('current_balance', 0)
        target = goal['target_amount']

        progress['current_value'] = current_balance
        progress['percent_complete'] = min((current_balance / target * 100), 100) if target > 0 else 0
        progress['on_track'] = current_balance >= target * 0.5 if days_remaining > 180 else current_balance >= target * 0.8
        progress['status_message'] = f"${current_balance:,.2f} / ${target:,.2f}"

    elif goal_type == 'debt_payoff':
        # Credit card or debt payoff
        cc_payoff = dashboard_data.get('credit_card_payoff', {})
        current_balance = goal.get('current_balance', 0)

        # Update current balance from dashboard
        for card in cc_payoff.get('cards', []):
            if goal['name'].lower() in card['name'].lower():
                current_balance = card['balance']
                break

        target = 0  # Goal is to pay off completely
        paid_off = goal.get('current_balance', current_balance) - current_balance

        progress['current_value'] = current_balance
        progress['percent_complete'] = (paid_off / goal.get('current_balance', 1) * 100)
        progress['on_track'] = current_balance <= goal.get('current_balance', 0) * 0.5
        progress['status_message'] = f"${current_balance:,.2f} remaining (${paid_off:,.2f} paid)"

    elif goal_type == 'spending_reduction':
        # Spending reduction goal
        category = goal.get('category')
        target = goal['target_amount']

        # Get current month spending for category
        budget_vs_actual = dashboard_data.get('budget_vs_actual', {})
        category_data = budget_vs_actual.get('categories', {}).get(category, {})
        current_spending = category_data.get('actual', 0)

        progress['current_value'] = current_spending
        progress['target_value'] = target
        progress['on_track'] = current_spending <= target
        progress['percent_complete'] = min((target / current_spending * 100), 100) if current_spending > 0 else 100
        progress['status_message'] = f"${current_spending:,.2f} / ${target:,.2f} budget"

    elif goal_type == 'savings_rate':
        # Monthly savings rate goal
        snapshot = dashboard_data.get('snapshot', {})
        # This would need historical data to calculate actual savings rate
        # For now, just show target
        target = goal['target_amount']

        progress['target_value'] = target
        progress['status_message'] = f"Target: ${target:,.2f}/month"
        progress['on_track'] = None  # Unknown without historical data

    return progress

def main():
    """Track financial goals"""

    print()
    print("=" * 70)
    print("🎯 FINANCIAL GOALS TRACKER")
    print("=" * 70)
    print()

    # Load data
    goals_data = load_goals()
    dashboard_data = load_dashboard_data()

    goals = goals_data.get('goals', {})

    if not goals:
        print("⚠️  No goals defined. Edit Archive/processed/financial_goals.json to add goals.")
        print()
        return

    print(f"Tracking {len(goals)} goals...")
    print()

    # Track each goal
    for goal_id, goal in goals.items():
        if goal.get('status') == 'completed':
            continue

        progress = calculate_goal_progress(goal, dashboard_data)

        # Display
        priority_icon = '🔴' if goal['priority'] == 'high' else '🟡' if goal['priority'] == 'medium' else '🟢'
        status_icon = '✅' if progress['on_track'] else '⚠️' if progress['on_track'] is not None else '❓'

        print(f"{priority_icon} {status_icon} {goal['name']}")
        print(f"   {goal['description']}")
        print(f"   Progress: {progress['status_message']}")
        print(f"   {progress['percent_complete']:.1f}% complete • {progress['days_remaining']} days remaining")

        if progress['on_track'] is True:
            print(f"   🎯 On track!")
        elif progress['on_track'] is False:
            print(f"   ⚠️  Behind target")

        print()

    print("=" * 70)
    print("💡 TIP: Update goals in Archive/processed/financial_goals.json")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
