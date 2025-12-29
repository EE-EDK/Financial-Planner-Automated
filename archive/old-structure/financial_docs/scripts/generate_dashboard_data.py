#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Data Generator
Processes all financial data and generates dashboard metrics

Reads:
- financial_config.json (balances, recurring expenses, debt)
- budget.json (category budgets)
- AllTransactions.csv (spending history)

Outputs:
- dashboard_data.json (all metrics for dashboard display)
"""

import csv
import json
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "Archive" / "processed"
EXPORTS_DIR = BASE_DIR / "Archive" / "raw" / "exports"
CONFIG_FILE = PROCESSED_DIR / "financial_config.json"
BUDGET_FILE = PROCESSED_DIR / "budget.json"
TRANSACTIONS_FILE = EXPORTS_DIR / "AllTransactions.csv"
OUTPUT_FILE = PROCESSED_DIR / "dashboard_data.json"

def load_config():
    """Load financial configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_budget():
    """Load budget data"""
    if BUDGET_FILE.exists():
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_transactions():
    """Load transaction history"""
    transactions = []

    if not TRANSACTIONS_FILE.exists():
        return transactions

    with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip credit card payments and ignored transactions
            if row.get('Ignored From') or row.get('Category') == 'Credit Card Payment':
                continue

            try:
                amount = float(row.get('Amount', 0))
                transactions.append({
                    'date': row.get('Date', ''),
                    'name': row.get('Custom Name') or row.get('Name', ''),
                    'amount': amount,
                    'category': row.get('Category', ''),
                    'account': row.get('Account Name', ''),
                    'description': row.get('Description', '')
                })
            except (ValueError, TypeError):
                continue

    return transactions

def calculate_snapshot(config):
    """Calculate current financial snapshot"""

    # Liquid cash
    cash_accounts = config.get('cash_accounts', {})
    total_cash = sum(acct['balance'] for acct in cash_accounts.values())

    # Total debt
    total_debt = 0

    for section in config.get('debt_balances', {}).values():
        for item in section.values():
            total_debt += item['balance']

    for card in config.get('credit_cards', {}).values():
        total_debt += card['balance']

    # Net worth (simplified: cash - debt, not including home equity)
    net_worth = total_cash - total_debt

    # Monthly recurring expenses
    recurring_expenses = 0
    for section in config.get('recurring_expenses', {}).values():
        for item in section.values():
            if item.get('status') != 'cancelled':
                recurring_expenses += item['amount']

    return {
        'liquid_cash': round(total_cash, 2),
        'total_debt': round(total_debt, 2),
        'net_worth': round(net_worth, 2),
        'monthly_recurring': round(recurring_expenses, 2)
    }

def analyze_spending_trends(transactions, months=6):
    """Analyze spending trends for key categories"""

    # Get date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    # Track by category and month
    category_by_month = defaultdict(lambda: defaultdict(float))
    merchant_totals = defaultdict(float)

    # Problem categories to track
    problem_categories = {
        'Amazon': [],
        'Dining & Drinks': [],
        'Groceries': [],
        'Shopping': [],
        'Entertainment & Rec.': []
    }

    for txn in transactions:
        try:
            txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')

            if txn_date < start_date:
                continue

            if txn['amount'] <= 0:  # Skip income/refunds
                continue

            month_key = txn_date.strftime('%Y-%m')
            category = txn['category']

            # Track by category and month
            category_by_month[category][month_key] += txn['amount']

            # Track merchants
            merchant_totals[txn['name']] += txn['amount']

            # Track problem categories
            if 'amazon' in txn['name'].lower() or category == 'Amazon':
                problem_categories['Amazon'].append({
                    'date': txn['date'],
                    'amount': txn['amount'],
                    'name': txn['name']
                })

            if category in problem_categories:
                problem_categories[category].append({
                    'date': txn['date'],
                    'amount': txn['amount'],
                    'name': txn['name']
                })

        except (ValueError, KeyError):
            continue

    # Calculate trends
    trends = {}

    for category, monthly_data in category_by_month.items():
        months_list = sorted(monthly_data.keys())[-6:]  # Last 6 months

        if len(months_list) >= 2:
            amounts = [monthly_data[m] for m in months_list]
            avg_amount = sum(amounts) / len(amounts)

            trends[category] = {
                'months': months_list,
                'amounts': [round(a, 2) for a in amounts],
                'average': round(avg_amount, 2),
                'total': round(sum(amounts), 2)
            }

    # Top merchants
    top_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:10]

    # Problem category details
    problem_details = {}
    for cat, txns in problem_categories.items():
        if txns:
            total = sum(t['amount'] for t in txns)
            problem_details[cat] = {
                'total': round(total, 2),
                'count': len(txns),
                'average': round(total / len(txns), 2) if txns else 0
            }

    return {
        'trends': trends,
        'top_merchants': [{'name': m[0], 'total': round(m[1], 2)} for m in top_merchants],
        'problem_categories': problem_details
    }

def calculate_budget_vs_actual(transactions, budget):
    """Calculate budget vs actual spending"""

    # Get current month
    now = datetime.now()
    current_month = now.strftime('%Y-%m')

    # Calculate spending by category for current month
    category_spending = defaultdict(float)

    for txn in transactions:
        try:
            if not txn['date'].startswith(current_month):
                continue

            if txn['amount'] <= 0:  # Skip income/refunds
                continue

            category = txn['category']

            # Map Amazon transactions
            if 'amazon' in txn['name'].lower():
                category = 'Amazon'

            category_spending[category] += txn['amount']

        except (ValueError, KeyError):
            continue

    # Compare to budget
    budget_categories = budget.get('category_budgets', {})

    comparisons = {}
    over_budget = []

    for category, budget_amount in budget_categories.items():
        actual = category_spending.get(category, 0)
        remaining = budget_amount - actual
        percent = (actual / budget_amount * 100) if budget_amount > 0 else 0

        comparisons[category] = {
            'budget': budget_amount,
            'actual': round(actual, 2),
            'remaining': round(remaining, 2),
            'percent': round(percent, 1),
            'over_budget': remaining < 0
        }

        if remaining < 0:
            over_budget.append({
                'category': category,
                'budget': budget_amount,
                'actual': round(actual, 2),
                'overage': round(abs(remaining), 2)
            })

    # Calculate totals
    total_budgeted = sum(budget_categories.values())
    total_spent = sum(category_spending.values())

    # Days remaining in month
    next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
    last_day_of_month = next_month - timedelta(days=1)
    days_remaining = (last_day_of_month - now).days

    return {
        'categories': comparisons,
        'over_budget_items': sorted(over_budget, key=lambda x: x['overage'], reverse=True),
        'total_budgeted': total_budgeted,
        'total_spent': round(total_spent, 2),
        'total_remaining': round(total_budgeted - total_spent, 2),
        'days_in_month': now.day,
        'days_remaining': days_remaining
    }

def generate_alerts(snapshot, budget_vs_actual, trends):
    """Generate financial alerts"""

    alerts = []

    # Low cash alert
    if snapshot['liquid_cash'] < 5000:
        alerts.append({
            'type': 'critical',
            'category': 'Cash',
            'message': f"Liquid cash is low: ${snapshot['liquid_cash']:,.2f}",
            'action': 'Build emergency fund to 3-6 months expenses'
        })

    # Over budget alerts
    for item in budget_vs_actual['over_budget_items']:
        alerts.append({
            'type': 'warning',
            'category': item['category'],
            'message': f"{item['category']} over budget by ${item['overage']:.2f}",
            'action': f"Reduce {item['category']} spending"
        })

    # High Amazon spending
    amazon_trend = trends['problem_categories'].get('Amazon', {})
    if amazon_trend.get('total', 0) > 500:
        alerts.append({
            'type': 'warning',
            'category': 'Amazon',
            'message': f"Amazon spending: ${amazon_trend['total']:.2f} ({amazon_trend['count']} transactions)",
            'action': 'Review Amazon purchases, consider removing app'
        })

    # High dining spending
    dining_trend = trends['problem_categories'].get('Dining & Drinks', {})
    if dining_trend.get('total', 0) > 250:
        alerts.append({
            'type': 'warning',
            'category': 'Dining & Drinks',
            'message': f"Dining spending: ${dining_trend['total']:.2f}",
            'action': 'Reduce restaurant spending'
        })

    return alerts

def detect_spending_anomalies(transactions, trends):
    """Detect unusual spending patterns"""

    anomalies = []

    # Get current month spending by category
    now = datetime.now()
    current_month = now.strftime('%Y-%m')

    category_spending_current = defaultdict(float)

    for txn in transactions:
        try:
            if not txn['date'].startswith(current_month):
                continue

            if txn['amount'] <= 0:
                continue

            category_spending_current[txn['category']] += txn['amount']

        except (ValueError, KeyError):
            continue

    # Compare to 6-month averages
    for category, trend_data in trends['trends'].items():
        current_spending = category_spending_current.get(category, 0)
        average_spending = trend_data.get('average', 0)

        if average_spending == 0:
            continue

        # Calculate percent change
        percent_change = ((current_spending - average_spending) / average_spending) * 100

        # Anomaly if > 50% increase
        if percent_change > 50:
            anomalies.append({
                'category': category,
                'type': 'high_spending',
                'current': round(current_spending, 2),
                'average': round(average_spending, 2),
                'percent_change': round(percent_change, 1),
                'message': f"{category}: ${current_spending:,.2f} this month vs ${average_spending:,.2f} average ({percent_change:+.1f}%)"
            })

        # Anomaly if > 50% decrease (could indicate missing data)
        elif percent_change < -50:
            anomalies.append({
                'category': category,
                'type': 'low_spending',
                'current': round(current_spending, 2),
                'average': round(average_spending, 2),
                'percent_change': round(percent_change, 1),
                'message': f"{category}: ${current_spending:,.2f} this month vs ${average_spending:,.2f} average ({percent_change:+.1f}%)"
            })

    # Detect unusual single transactions (> $500)
    large_transactions = []
    for txn in transactions:
        try:
            if not txn['date'].startswith(current_month):
                continue

            if txn['amount'] > 500:
                large_transactions.append({
                    'date': txn['date'],
                    'name': txn['name'],
                    'amount': txn['amount'],
                    'category': txn['category']
                })

        except (ValueError, KeyError):
            continue

    # Sort by amount
    large_transactions.sort(key=lambda x: x['amount'], reverse=True)

    return {
        'category_anomalies': anomalies,
        'large_transactions': large_transactions[:10],  # Top 10
        'anomaly_count': len(anomalies)
    }

def calculate_credit_card_payoff(config):
    """Calculate credit card payoff timeline"""

    credit_cards = config.get('credit_cards', {})

    # Get all credit cards with balances
    cards_with_debt = []
    total_cc_debt = 0

    for card_id, card in credit_cards.items():
        balance = card.get('balance', 0)
        if balance > 0:
            apr = card.get('apr', 0) or 0
            cards_with_debt.append({
                'name': card['name'],
                'balance': balance,
                'apr': apr,
                'monthly_interest_rate': apr / 100 / 12 if apr > 0 else 0
            })
            total_cc_debt += balance

    # Sort by APR (highest first - avalanche method)
    cards_with_debt.sort(key=lambda x: x['apr'], reverse=True)

    # Calculate payoff scenarios
    # Assumption: Pay minimum $176 (from Venture minimum) + extra
    monthly_payment_scenarios = [200, 500, 1000, 1500]

    payoff_scenarios = {}

    for monthly_payment in monthly_payment_scenarios:
        months_to_payoff = 0
        total_interest = 0
        remaining_debt = total_cc_debt

        # Simple calculation (not accounting for multiple cards, just total)
        if total_cc_debt > 0:
            # Weighted average APR
            weighted_apr = sum(c['balance'] * c['apr'] for c in cards_with_debt) / total_cc_debt
            monthly_rate = weighted_apr / 100 / 12

            # Calculate payoff time
            temp_balance = total_cc_debt
            months = 0

            while temp_balance > 0 and months < 360:  # Max 30 years
                interest_charge = temp_balance * monthly_rate
                principal_payment = monthly_payment - interest_charge

                if principal_payment <= 0:
                    months = 999  # Can't pay off
                    break

                temp_balance -= principal_payment
                total_interest += interest_charge
                months += 1

            payoff_scenarios[f"${monthly_payment}/mo"] = {
                'monthly_payment': monthly_payment,
                'months': months if months < 999 else None,
                'years': round(months / 12, 1) if months < 999 else None,
                'total_interest': round(total_interest, 2),
                'total_paid': round(total_cc_debt + total_interest, 2)
            }

    # Calculate minimum payment timeline
    # For each card individually
    card_details = []
    for card in cards_with_debt:
        # Minimum payment typically 2% of balance or $25, whichever is greater
        min_payment = max(card['balance'] * 0.02, 25)

        months = 0
        temp_balance = card['balance']
        total_interest = 0

        while temp_balance > 0 and months < 360:
            interest_charge = temp_balance * card['monthly_interest_rate']
            principal = min_payment - interest_charge

            if principal <= 0:
                months = 999
                break

            temp_balance -= principal
            total_interest += interest_charge
            months += 1

        card_details.append({
            'name': card['name'],
            'balance': card['balance'],
            'apr': card['apr'],
            'min_payment': round(min_payment, 2),
            'months_to_payoff': months if months < 999 else None,
            'total_interest': round(total_interest, 2)
        })

    # Current payment (Venture minimum = $176)
    current_monthly = 176

    return {
        'total_balance': round(total_cc_debt, 2),
        'cards': card_details,
        'current_payment': current_monthly,
        'scenarios': payoff_scenarios,
        'recommendation': {
            'method': 'avalanche',
            'description': 'Pay highest APR first',
            'target_payment': 500,
            'payoff_months': payoff_scenarios.get('$500/mo', {}).get('months', 0)
        }
    }

def calculate_emergency_fund(config):
    """Calculate emergency fund progress"""

    # Get monthly recurring expenses
    monthly_expenses = 0
    for section in config.get('recurring_expenses', {}).values():
        for item in section.values():
            if item.get('status') != 'cancelled':
                monthly_expenses += item['amount']

    # Get liquid cash
    cash_accounts = config.get('cash_accounts', {})
    liquid_cash = sum(acct['balance'] for acct in cash_accounts.values() if acct.get('liquid', False))

    # Calculate targets
    target_3_months = monthly_expenses * 3
    target_6_months = monthly_expenses * 6

    # Progress
    months_covered = liquid_cash / monthly_expenses if monthly_expenses > 0 else 0
    days_covered = months_covered * 30

    # Percent to goals
    percent_to_3mo = (liquid_cash / target_3_months * 100) if target_3_months > 0 else 0
    percent_to_6mo = (liquid_cash / target_6_months * 100) if target_6_months > 0 else 0

    # Status
    if months_covered >= 6:
        status = 'excellent'
        message = '✅ Excellent - You have 6+ months covered'
    elif months_covered >= 3:
        status = 'good'
        message = '✅ Good - You have 3-6 months covered'
    elif months_covered >= 1:
        status = 'fair'
        message = '⚠️  Fair - You have 1-3 months covered'
    else:
        status = 'critical'
        message = '🔴 Critical - Less than 1 month covered'

    return {
        'current_balance': round(liquid_cash, 2),
        'monthly_expenses': round(monthly_expenses, 2),
        'months_covered': round(months_covered, 2),
        'days_covered': round(days_covered, 0),
        'targets': {
            'three_months': round(target_3_months, 2),
            'six_months': round(target_6_months, 2)
        },
        'progress': {
            'to_3_months': {
                'percent': round(percent_to_3mo, 1),
                'remaining': round(max(0, target_3_months - liquid_cash), 2)
            },
            'to_6_months': {
                'percent': round(percent_to_6mo, 1),
                'remaining': round(max(0, target_6_months - liquid_cash), 2)
            }
        },
        'status': status,
        'message': message
    }

def main():
    """Generate dashboard data"""

    print()
    print("=" * 70)
    print("📊 DASHBOARD DATA GENERATOR")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    config = load_config()
    budget = load_budget()
    transactions = load_transactions()

    print(f"  ✅ Config loaded")
    print(f"  ✅ Budget loaded")
    print(f"  ✅ {len(transactions)} transactions loaded")
    print()

    # Calculate metrics
    print("Calculating metrics...")

    snapshot = calculate_snapshot(config)
    print(f"  ✅ Financial snapshot")

    trends = analyze_spending_trends(transactions)
    print(f"  ✅ Spending trends")

    budget_vs_actual = calculate_budget_vs_actual(transactions, budget)
    print(f"  ✅ Budget vs actual")

    credit_card_payoff = calculate_credit_card_payoff(config)
    print(f"  ✅ Credit card payoff analysis")

    emergency_fund = calculate_emergency_fund(config)
    print(f"  ✅ Emergency fund progress")

    anomalies = detect_spending_anomalies(transactions, trends)
    print(f"  ✅ Spending anomalies detected ({anomalies['anomaly_count']} found)")

    alerts = generate_alerts(snapshot, budget_vs_actual, trends)
    print(f"  ✅ Alerts generated")
    print()

    # Build dashboard data
    dashboard_data = {
        'generated_at': datetime.now().isoformat(),
        'snapshot': snapshot,
        'trends': trends,
        'budget_vs_actual': budget_vs_actual,
        'credit_card_payoff': credit_card_payoff,
        'emergency_fund': emergency_fund,
        'anomalies': anomalies,
        'alerts': alerts,
        'config': {
            'recurring_expenses': config.get('recurring_expenses', {}),
            'debt_balances': config.get('debt_balances', {}),
            'credit_cards': config.get('credit_cards', {}),
            'cash_accounts': config.get('cash_accounts', {})
        }
    }

    # Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print("✅ DASHBOARD DATA GENERATED")
    print("=" * 70)
    print()
    print(f"Output: {OUTPUT_FILE}")
    print()

    # Summary
    print("📊 Summary:")
    print(f"  Liquid Cash:    ${snapshot['liquid_cash']:>10,.2f}")
    print(f"  Total Debt:     ${snapshot['total_debt']:>10,.2f}")
    print(f"  Net Worth:      ${snapshot['net_worth']:>10,.2f}")
    print()
    print(f"  Budget:         ${budget_vs_actual['total_budgeted']:>10,.2f}")
    print(f"  Spent:          ${budget_vs_actual['total_spent']:>10,.2f}")
    print(f"  Remaining:      ${budget_vs_actual['total_remaining']:>10,.2f}")
    print()
    print(f"  Alerts:         {len(alerts)}")
    print()

    # Show alerts
    if alerts:
        print("⚠️  Alerts:")
        for alert in alerts:
            icon = "🔴" if alert['type'] == 'critical' else "⚠️ "
            print(f"  {icon} {alert['message']}")
        print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
