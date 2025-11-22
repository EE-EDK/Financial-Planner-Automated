#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Health Score Calculator
Calculates overall financial health score (0-100) based on multiple factors

Reads from: Archive/processed/financial_config.json
            Archive/processed/budget.json

Usage:
    python3 financial_docs/scripts/calculate_health_score.py

Output:
    - Generates FINANCIAL_HEALTH_SCORE.md in Archive/reports/
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
CONFIG_FILE = ARCHIVE_DIR / "processed" / "financial_config.json"
BUDGET_FILE = ARCHIVE_DIR / "processed" / "budget.json"

def load_config():
    """Load financial configuration"""
    if not CONFIG_FILE.exists():
        print(f"❌ Config file not found: {CONFIG_FILE}")
        print("   Create this file with your financial data first.")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def load_budget():
    """Load budget configuration"""
    if not BUDGET_FILE.exists():
        print(f"❌ Budget file not found: {BUDGET_FILE}")
        sys.exit(1)
    
    with open(BUDGET_FILE, 'r') as f:
        return json.load(f)

def calculate_totals(config):
    """Calculate financial totals from config"""
    # Sum cash accounts
    liquid_cash = sum(
        account['balance'] 
        for account in config.get('cash_accounts', {}).values()
        if account.get('liquid', True)
    )
    
    # Sum all debt
    total_debt = 0
    for debt_type in config.get('debt_balances', {}).values():
        for debt in debt_type.values():
            total_debt += debt.get('balance', 0)
    
    # Add credit card debt
    for cc in config.get('credit_cards', {}).values():
        total_debt += cc.get('balance', 0)
    
    # Sum recurring expenses
    monthly_recurring = 0
    for expense_type in config.get('recurring_expenses', {}).values():
        for expense in expense_type.values():
            if expense.get('status') != 'cancelled':
                monthly_recurring += expense.get('amount', 0)
    
    return {
        'liquid_cash': liquid_cash,
        'total_debt': total_debt,
        'monthly_recurring': monthly_recurring
    }

def get_status(score, max_score):
    """Get status based on score percentage"""
    pct = (score / max_score) * 100
    if pct >= 80:
        return "✅ Excellent"
    elif pct >= 60:
        return "🟢 Good"
    elif pct >= 40:
        return "🟡 Fair"
    else:
        return "🔴 Needs Improvement"

def calculate_emergency_fund_score(totals, budget):
    """Calculate emergency fund score (0-25 points)"""
    liquid = totals['liquid_cash']
    monthly_budget = budget.get('metadata', {}).get('total_spending_budget', 5000)
    months_coverage = liquid / monthly_budget if monthly_budget > 0 else 0

    # Scoring: 0 mo = 0pts, 1 mo = 5pts, 3 mo = 15pts, 6+ mo = 25pts
    if months_coverage >= 6:
        score = 25
    elif months_coverage >= 3:
        score = 15 + ((months_coverage - 3) / 3) * 10
    elif months_coverage >= 1:
        score = 5 + ((months_coverage - 1) / 2) * 10
    else:
        score = months_coverage * 5

    return {
        'score': round(score, 1),
        'max_score': 25,
        'months_coverage': round(months_coverage, 1),
        'status': get_status(score, 25)
    }

def calculate_debt_score(totals, budget):
    """Calculate debt management score (0-25 points)"""
    monthly_income = budget.get('monthly_income', {}).get('earnings', 0)
    total_debt = totals['total_debt']
    
    if monthly_income == 0:
        return {'score': 0, 'max_score': 25, 'status': '🔴 No income data'}
    
    # Simple debt-to-income check (total debt / annual income)
    annual_income = monthly_income * 12
    dti_ratio = total_debt / annual_income if annual_income > 0 else 0
    
    # Score: < 2x income = 25pts, 2-4x = 15pts, > 4x = 5pts
    if dti_ratio < 2:
        score = 25
    elif dti_ratio < 4:
        score = 15
    else:
        score = max(5, 25 - (dti_ratio - 2) * 5)
    
    return {
        'score': round(score, 1),
        'max_score': 25,
        'dti_ratio': round(dti_ratio, 2),
        'status': get_status(score, 25)
    }

def calculate_cash_flow_score(totals, budget):
    """Calculate cash flow score (0-25 points)"""
    monthly_income = budget.get('monthly_income', {}).get('earnings', 0)
    monthly_spending = budget.get('metadata', {}).get('total_spending_budget', 0)
    surplus = monthly_income - monthly_spending
    
    if monthly_income == 0:
        return {'score': 0, 'max_score': 25, 'status': '🔴 No income data'}
    
    surplus_pct = (surplus / monthly_income) * 100 if monthly_income > 0 else 0
    
    # Score: > 20% = 25pts, 10-20% = 15pts, 0-10% = 10pts, negative = 0pts
    if surplus_pct >= 20:
        score = 25
    elif surplus_pct >= 10:
        score = 15
    elif surplus_pct >= 0:
        score = 10
    else:
        score = 0
    
    return {
        'score': round(score, 1),
        'max_score': 25,
        'surplus': surplus,
        'surplus_pct': round(surplus_pct, 1),
        'status': get_status(score, 25)
    }

def calculate_overall_score(config, budget):
    """Calculate overall financial health score"""
    totals = calculate_totals(config)
    
    emergency = calculate_emergency_fund_score(totals, budget)
    debt = calculate_debt_score(totals, budget)
    cash_flow = calculate_cash_flow_score(totals, budget)
    
    total_score = emergency['score'] + debt['score'] + cash_flow['score']
    max_score = 75  # 25 + 25 + 25
    
    return {
        'total_score': round(total_score, 1),
        'max_score': max_score,
        'grade': get_grade(total_score, max_score),
        'emergency': emergency,
        'debt': debt,
        'cash_flow': cash_flow,
        'totals': totals
    }

def get_grade(score, max_score):
    """Convert score to letter grade"""
    pct = (score / max_score) * 100
    if pct >= 90:
        return "A+"
    elif pct >= 80:
        return "A"
    elif pct >= 70:
        return "B"
    elif pct >= 60:
        return "C"
    elif pct >= 50:
        return "D"
    else:
        return "F"

def generate_report(result):
    """Generate health score report"""
    
    report = f"""# FINANCIAL HEALTH SCORE
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## 🎯 OVERALL SCORE

### {result['total_score']:.0f} / {result['max_score']} (Grade: {result['grade']})

---

## 📊 COMPONENT SCORES

### 1. Emergency Fund: {result['emergency']['score']:.1f} / {result['emergency']['max_score']}
**Status:** {result['emergency']['status']}
- Coverage: {result['emergency']['months_coverage']:.1f} months of expenses
- Target: 6 months

### 2. Debt Management: {result['debt']['score']:.1f} / {result['debt']['max_score']}
**Status:** {result['debt']['status']}
- Total Debt: ${result['totals']['total_debt']:,.0f}

### 3. Cash Flow: {result['cash_flow']['score']:.1f} / {result['cash_flow']['max_score']}
**Status:** {result['cash_flow']['status']}
- Monthly Surplus: ${result['cash_flow']['surplus']:,.0f}
- Surplus Rate: {result['cash_flow']['surplus_pct']:.1f}%

---

## 💰 FINANCIAL SNAPSHOT

- **Liquid Cash:** ${result['totals']['liquid_cash']:,.0f}
- **Total Debt:** ${result['totals']['total_debt']:,.0f}
- **Monthly Recurring:** ${result['totals']['monthly_recurring']:,.0f}

---

**Generated by:** calculate_health_score.py
**Data from:** financial_config.json, budget.json
"""
    
    return report

def main():
    print("🏆 Financial Health Score Calculator")
    print("=" * 70)
    print()

    config = load_config()
    budget = load_budget()
    
    result = calculate_overall_score(config, budget)
    
    print(f"Overall Score: {result['total_score']:.0f} / {result['max_score']} (Grade: {result['grade']})")
    print()
    
    report = generate_report(result)
    
    reports_dir = ARCHIVE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_file = reports_dir / "FINANCIAL_HEALTH_SCORE.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Health score saved: {output_file}")
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
