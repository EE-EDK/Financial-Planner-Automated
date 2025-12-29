#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Health Score Calculator
Calculates overall financial health score (0-100) based on multiple factors

Usage:
    python3 financial_docs/calculate_health_score.py

Output:
    - Displays financial health score
    - Generates FINANCIAL_HEALTH_SCORE.md in Archive/
    - Shows breakdown by category
    - Provides recommendations
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Import shared utilities
from financial_utils import (
    setup_windows_encoding,
    load_config,
    load_budget,
    load_transactions,
    calculate_financial_snapshot,
    categorize_spending,
    save_report,
    ARCHIVE_DIR,
    PROCESSED_DIR,
    REPORTS_DIR
)

# Setup encoding
setup_windows_encoding()


def get_financial_data():
    """
    Load and calculate all financial data from config files.

    Returns:
        Dictionary with all financial metrics needed for health score calculation
    """
    config = load_config()
    budget = load_budget()
    snapshot = calculate_financial_snapshot(config)

    # Get recent transactions for spending calculation (last 1 month)
    transactions = load_transactions(months=1)
    spending_by_category = categorize_spending(transactions)

    # Calculate monthly spending
    monthly_spending = sum(spending_by_category.values())

    # Calculate emergency fund target (6 months of spending)
    emergency_fund_target = snapshot['monthly_recurring'] * 6

    # Calculate annual income
    annual_income = snapshot['monthly_income'] * 12

    # Get savings info from config
    retirement_401k = config.get('retirement', {}).get('monthly_contribution', 0)
    employer_match = config.get('retirement', {}).get('employer_match', 0)
    hsa_contribution = config.get('savings', {}).get('hsa_monthly', 0)
    monthly_savings = retirement_401k + hsa_contribution

    # Get credit card specific data
    credit_cards = config.get('credit_cards', {})
    total_cc_debt = sum(card.get('balance', 0) for card in credit_cards.values() if isinstance(card, dict))

    # Calculate weighted average credit card rate
    cc_rate = 0.22  # Default
    if total_cc_debt > 0:
        weighted_rate_sum = 0
        for card in credit_cards.values():
            if isinstance(card, dict):
                balance = card.get('balance', 0)
                apr = card.get('apr', 0) or 0  # Handle None values
                if balance > 0 and apr > 0:
                    weighted_rate_sum += (balance * apr / 100)
        cc_rate = weighted_rate_sum / total_cc_debt if weighted_rate_sum > 0 else 0.22

    # Calculate mortgage average rate
    mortgage_debt = snapshot['mortgage_debt']
    mortgage_rate_avg = 0.0244  # Default

    debt_balances = config.get('debt_balances', {})
    if mortgage_debt > 0:
        weighted_mortgage_rate = 0
        for section_name, section in debt_balances.items():
            if 'mortgage' in section_name.lower():
                for item in section.values():
                    if isinstance(item, dict):
                        balance = item.get('balance', 0)
                        rate = item.get('interest_rate', 0) or 0  # Handle None values
                        if balance > 0 and rate > 0:
                            weighted_mortgage_rate += (balance * rate)
        mortgage_rate_avg = weighted_mortgage_rate / mortgage_debt if weighted_mortgage_rate > 0 else 0.0244

    return {
        'net_worth': snapshot['net_worth'],
        'liquid_cash': snapshot['liquid_cash'],
        'emergency_fund_target': emergency_fund_target,
        'annual_income': annual_income,
        'total_debt': snapshot['total_debt'],
        'consumer_debt': snapshot['consumer_debt'],
        'monthly_income': snapshot['monthly_income'],
        'monthly_spending': monthly_spending if monthly_spending > 0 else snapshot['monthly_recurring'],
        'monthly_savings': monthly_savings,
        'employer_match': employer_match,
        'credit_card_debt': total_cc_debt,
        'credit_card_rate': cc_rate,
        'mortgage_debt': mortgage_debt,
        'mortgage_rate_avg': mortgage_rate_avg,
    }

def calculate_emergency_fund_score(financial_data):
    """
    Calculate emergency fund score (0-25 points)
    Based on months of expenses covered
    """
    liquid = financial_data['liquid_cash']
    target = financial_data['emergency_fund_target']
    monthly_expenses = financial_data['monthly_spending']

    # Calculate months of coverage
    months_coverage = liquid / monthly_expenses

    # Scoring:
    # 0 months: 0 points
    # 1 month: 5 points
    # 3 months: 15 points
    # 6+ months: 25 points

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
        'target_months': 6,
        'status': get_status(score, 25)
    }

def calculate_debt_management_score(financial_data):
    """
    Calculate debt management score (0-25 points)
    Based on debt-to-income ratio and debt types
    """
    annual_income = financial_data['annual_income']
    total_debt = financial_data['total_debt']
    consumer_debt = financial_data['consumer_debt']
    mortgage_debt = financial_data['mortgage_debt']

    # Debt-to-income ratio (total annual debt payments / annual income)
    monthly_debt_payments = 4141 + 1900  # Fixed + target CC payment
    annual_debt_payments = monthly_debt_payments * 12
    dti = annual_debt_payments / annual_income if annual_income > 0 else 0

    # DTI Scoring (0-15 points):
    # < 0.20: 15 points (excellent)
    # 0.20-0.28: 12 points (good)
    # 0.28-0.36: 9 points (fair)
    # 0.36-0.43: 6 points (concerning)
    # > 0.43: 3 points (danger)

    if dti < 0.20:
        dti_score = 15
    elif dti < 0.28:
        dti_score = 12
    elif dti < 0.36:
        dti_score = 9
    elif dti < 0.43:
        dti_score = 6
    else:
        dti_score = 3

    # High-interest debt penalty (0-10 points)
    cc_debt = financial_data['credit_card_debt']
    annual_cc_interest = cc_debt * financial_data['credit_card_rate']

    if cc_debt == 0:
        hi_debt_score = 10
    elif cc_debt < 5000:
        hi_debt_score = 8
    elif cc_debt < 15000:
        hi_debt_score = 6
    elif cc_debt < 30000:
        hi_debt_score = 4
    else:
        hi_debt_score = 2

    total_score = dti_score + hi_debt_score

    return {
        'score': round(total_score, 1),
        'max_score': 25,
        'dti': round(dti, 3),
        'dti_score': dti_score,
        'high_interest_debt': cc_debt,
        'hi_debt_score': hi_debt_score,
        'status': get_status(total_score, 25)
    }

def calculate_savings_rate_score(financial_data):
    """
    Calculate savings rate score (0-25 points)
    Based on percentage of income saved
    """
    monthly_income = financial_data['monthly_income']
    monthly_savings = financial_data['monthly_savings']
    employer_match = financial_data['employer_match']

    # Total savings including match
    total_monthly_savings = monthly_savings + employer_match

    # Savings rate
    savings_rate = total_monthly_savings / monthly_income if monthly_income > 0 else 0

    # Scoring:
    # < 5%: 0-5 points
    # 5-10%: 5-10 points
    # 10-15%: 10-15 points
    # 15-20%: 15-20 points
    # 20%+: 20-25 points

    if savings_rate >= 0.20:
        score = 20 + (min(savings_rate - 0.20, 0.10) * 50)  # Up to 25 for 30%+
    elif savings_rate >= 0.15:
        score = 15 + ((savings_rate - 0.15) / 0.05) * 5
    elif savings_rate >= 0.10:
        score = 10 + ((savings_rate - 0.10) / 0.05) * 5
    elif savings_rate >= 0.05:
        score = 5 + ((savings_rate - 0.05) / 0.05) * 5
    else:
        score = savings_rate * 100

    return {
        'score': round(min(score, 25), 1),
        'max_score': 25,
        'savings_rate': round(savings_rate, 3),
        'monthly_savings': total_monthly_savings,
        'target_rate': 0.20,
        'status': get_status(score, 25)
    }

def calculate_cash_flow_score(financial_data):
    """
    Calculate cash flow score (0-25 points)
    Based on monthly surplus/deficit
    """
    monthly_income = financial_data['monthly_income']
    monthly_spending = financial_data['monthly_spending']

    # Cash flow (positive or negative)
    monthly_cash_flow = monthly_income - monthly_spending

    # Cash flow as percentage of income
    cash_flow_pct = monthly_cash_flow / monthly_income if monthly_income > 0 else 0

    # Scoring:
    # +20% or more: 25 points
    # +10% to +20%: 20 points
    # +5% to +10%: 15 points
    # 0% to +5%: 10 points
    # -5% to 0%: 5 points
    # Below -5%: 0 points

    if cash_flow_pct >= 0.20:
        score = 25
    elif cash_flow_pct >= 0.10:
        score = 20
    elif cash_flow_pct >= 0.05:
        score = 15
    elif cash_flow_pct >= 0:
        score = 10
    elif cash_flow_pct >= -0.05:
        score = 5
    else:
        score = max(0, 5 + (cash_flow_pct + 0.05) * 100)

    return {
        'score': round(score, 1),
        'max_score': 25,
        'monthly_cash_flow': monthly_cash_flow,
        'cash_flow_pct': round(cash_flow_pct, 3),
        'status': get_status(score, 25)
    }

def get_status(score, max_score):
    """Get status based on score percentage"""
    pct = (score / max_score) * 100

    if pct >= 90:
        return '🟢 Excellent'
    elif pct >= 75:
        return '🟡 Good'
    elif pct >= 60:
        return '🟠 Fair'
    else:
        return '🔴 Poor'

def get_grade(total_score):
    """Get letter grade based on total score"""
    if total_score >= 90:
        return 'A'
    elif total_score >= 80:
        return 'B'
    elif total_score >= 70:
        return 'C'
    elif total_score >= 60:
        return 'D'
    else:
        return 'F'

def get_grade_description(grade):
    """Get description for grade"""
    descriptions = {
        'A': 'Excellent financial health. Keep up the great work!',
        'B': 'Good financial health. Minor improvements needed.',
        'C': 'Fair financial health. Significant improvements needed.',
        'D': 'Poor financial health. Urgent action required.',
        'F': 'Financial crisis. Immediate intervention needed.'
    }
    return descriptions.get(grade, 'Unknown')

def generate_recommendations(scores, total_score, grade):
    """Generate personalized recommendations"""
    recommendations = []

    # Emergency fund recommendations
    ef_score = scores['emergency_fund']
    if ef_score['score'] < 15:
        recommendations.append({
            'priority': 'CRITICAL',
            'category': 'Emergency Fund',
            'issue': f"Only {ef_score['months_coverage']} months of expenses saved",
            'action': 'Build emergency fund to 3-6 months of expenses ASAP',
            'target': '$25,000 minimum, $52,596 optimal',
            'timeline': 'Next 6-12 months'
        })

    # Debt management recommendations
    debt_score = scores['debt_management']
    if debt_score['high_interest_debt'] > 0:
        recommendations.append({
            'priority': 'CRITICAL',
            'category': 'High-Interest Debt',
            'issue': f"${debt_score['high_interest_debt']:,.0f} in credit card debt",
            'action': 'Pay off or transfer to HELOC before 0% APR expires',
            'target': '$0 credit card debt',
            'timeline': 'April 2026 (143 days)'
        })

    # Cash flow recommendations
    cf_score = scores['cash_flow']
    if cf_score['monthly_cash_flow'] < 0:
        recommendations.append({
            'priority': 'CRITICAL',
            'category': 'Cash Flow',
            'issue': f"Negative cash flow of ${abs(cf_score['monthly_cash_flow']):,.0f}/month",
            'action': 'Cut discretionary spending from $5,393 to $450/month',
            'target': '+$2,051/month surplus',
            'timeline': 'Immediately'
        })

    # Savings rate recommendations
    sr_score = scores['savings_rate']
    if sr_score['savings_rate'] < 0.15:
        recommendations.append({
            'priority': 'IMPORTANT',
            'category': 'Savings Rate',
            'issue': f"Savings rate below 15% target",
            'action': 'Continue current 401k (22% including match) but add emergency fund savings',
            'target': '20% total savings rate',
            'timeline': 'After debt payoff'
        })

    return recommendations

def generate_report(scores, total_score, grade, recommendations, financial_data):
    """Generate detailed report markdown"""

    report = f"""# FINANCIAL HEALTH SCORE REPORT
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Assessment Date:** {datetime.now().strftime('%Y-%m-%d')}

---

## 🏆 OVERALL SCORE: {total_score}/100

### Grade: {grade}

**{get_grade_description(grade)}**

```
Score: {total_score}/100  [{'▓' * int(total_score/5)}{'░' * (20-int(total_score/5))}]
```

---

## 📊 SCORE BREAKDOWN

### Category Scores

| Category | Score | Max | Status | Performance |
|----------|-------|-----|--------|-------------|
| **Emergency Fund** | {scores['emergency_fund']['score']} | {scores['emergency_fund']['max_score']} | {scores['emergency_fund']['status']} | {'▓' * int(scores['emergency_fund']['score']/5)}{'░' * (5-int(scores['emergency_fund']['score']/5))} |
| **Debt Management** | {scores['debt_management']['score']} | {scores['debt_management']['max_score']} | {scores['debt_management']['status']} | {'▓' * int(scores['debt_management']['score']/5)}{'░' * (5-int(scores['debt_management']['score']/5))} |
| **Savings Rate** | {scores['savings_rate']['score']} | {scores['savings_rate']['max_score']} | {scores['savings_rate']['status']} | {'▓' * int(scores['savings_rate']['score']/5)}{'░' * (5-int(scores['savings_rate']['score']/5))} |
| **Cash Flow** | {scores['cash_flow']['score']} | {scores['cash_flow']['max_score']} | {scores['cash_flow']['status']} | {'▓' * int(scores['cash_flow']['score']/5)}{'░' * (5-int(scores['cash_flow']['score']/5))} |
| **TOTAL** | **{total_score}** | **100** | **Grade {grade}** | {'▓' * int(total_score/5)}{'░' * (20-int(total_score/5))} |

---

## 🔍 DETAILED ANALYSIS

### 1. Emergency Fund: {scores['emergency_fund']['score']}/25 points

**Current Status:**
- Liquid cash: ${financial_data['liquid_cash']:,.0f}
- Target: ${financial_data['emergency_fund_target']:,.0f}
- Coverage: {scores['emergency_fund']['months_coverage']} months of expenses
- Target coverage: {scores['emergency_fund']['target_months']} months

**Scoring:**
- 🔴 0-1 months: Critical (0-5 points)
- 🟠 1-3 months: Poor (5-15 points)
- 🟡 3-6 months: Fair (15-20 points)
- 🟢 6+ months: Excellent (20-25 points)

**Your Score:** {scores['emergency_fund']['status']}

---

### 2. Debt Management: {scores['debt_management']['score']}/25 points

**Current Status:**
- Total debt: ${financial_data['total_debt']:,.0f}
- Consumer debt: ${financial_data['consumer_debt']:,.0f}
- Debt-to-income ratio: {scores['debt_management']['dti']:.1%}
- High-interest debt: ${scores['debt_management']['high_interest_debt']:,.0f}

**Scoring Breakdown:**
- DTI Score: {scores['debt_management']['dti_score']}/15 points
  - 🟢 < 20%: Excellent (15 pts)
  - 🟡 20-28%: Good (12 pts)
  - 🟡 28-36%: Fair (9 pts) ← **You are here**
  - 🟠 36-43%: Concerning (6 pts)
  - 🔴 > 43%: Danger (3 pts)

- High-Interest Debt: {scores['debt_management']['hi_debt_score']}/10 points
  - 🟢 $0: 10 points
  - 🟡 < $5k: 8 points
  - 🟠 < $15k: 6 points
  - 🔴 < $30k: 4 points ← **You are here**
  - 🔴 $30k+: 2 points

**Your Score:** {scores['debt_management']['status']}

---

### 3. Savings Rate: {scores['savings_rate']['score']}/25 points

**Current Status:**
- Monthly savings: ${scores['savings_rate']['monthly_savings']:,.0f}
- Savings rate: {scores['savings_rate']['savings_rate']:.1%}
- Target rate: {scores['savings_rate']['target_rate']:.1%}

**Scoring:**
- 🔴 < 5%: Poor (0-5 points)
- 🟠 5-10%: Fair (5-10 points)
- 🟡 10-15%: Good (10-15 points)
- 🟡 15-20%: Very Good (15-20 points)
- 🟢 20%+: Excellent (20-25 points) ← **You are here**

**Your Score:** {scores['savings_rate']['status']}

**Note:** Your 22% savings rate (including employer match) is excellent! This is your strongest category.

---

### 4. Cash Flow: {scores['cash_flow']['score']}/25 points

**Current Status:**
- Monthly income: ${financial_data['monthly_income']:,.0f}
- Monthly spending: ${financial_data['monthly_spending']:,.0f}
- Monthly cash flow: ${scores['cash_flow']['monthly_cash_flow']:,.0f}
- Cash flow %: {scores['cash_flow']['cash_flow_pct']:.1%}

**Scoring:**
- 🟢 +20% or more: Excellent (25 pts)
- 🟢 +10% to +20%: Very Good (20 pts)
- 🟡 +5% to +10%: Good (15 pts)
- 🟡 0% to +5%: Fair (10 pts)
- 🔴 -5% to 0%: Poor (5 pts) ← **You are here**
- 🔴 Below -5%: Critical (0 pts)

**Your Score:** {scores['cash_flow']['status']}

---

## ⚠️ PRIORITY RECOMMENDATIONS

"""

    # Add recommendations
    for i, rec in enumerate(recommendations, 1):
        priority_emoji = '🚨' if rec['priority'] == 'CRITICAL' else '⚠️'
        report += f"""
### {priority_emoji} {i}. {rec['category']} - {rec['priority']}

**Issue:** {rec['issue']}

**Action Required:** {rec['action']}

**Target:** {rec['target']}

**Timeline:** {rec['timeline']}

---
"""

    report += f"""

## 💡 IMPROVEMENT OPPORTUNITIES

### Quick Wins (30 Days)

1. **Cut Discretionary Spending**
   - Current: $5,393/month
   - Target: $450/month
   - **Savings: $4,943/month**
   - Actions: Delete apps, 30-day rule, meal prep

2. **Increase Credit Card Payment**
   - Current: $500/month
   - Target: $1,900/month
   - **Additional: $1,375/month**
   - Source: Discretionary spending cuts

3. **Start Emergency Fund**
   - Current: $7,462
   - Target: $15,000 minimum
   - **Need: $7,538 more**
   - Timeline: From spending cuts

### Medium-Term Goals (3-6 Months)

1. **Pay Off Credit Card**
   - Balance: $30,000
   - Deadline: April 2026
   - Strategy: $1,900/month + $8k tax refund

2. **Build Emergency Fund to $25,000**
   - Current: $7,462
   - Target: $25,000
   - Strategy: Sell rental property

3. **Eliminate Negative Cash Flow**
   - Current: -$597/month
   - Target: +$2,051/month
   - Strategy: Execute spending cuts

### Long-Term Vision (1-3 Years)

1. **Debt Freedom by May 2028**
   - Pay off all consumer debt
   - Only keep mortgages (2.25% and 2.75%)

2. **Full Emergency Fund by 2029**
   - Build to $52,596 (6 months)

3. **Increase Savings Rate to 25%+**
   - Continue 401k + employer match
   - Add additional investments

---

## 📈 SCORE PROJECTIONS

### If You Execute the Plan

**In 6 Months (May 2026):**
- Emergency Fund: 4 → 18 points (+14)
- Debt Management: 18 → 22 points (+4)
- Cash Flow: 8 → 20 points (+12)
- **Total: 52 → 82 (Grade B)**

**In 1 Year (November 2026):**
- Emergency Fund: 4 → 22 points (+18)
- Debt Management: 18 → 23 points (+5)
- Cash Flow: 8 → 25 points (+17)
- **Total: 52 → 92 (Grade A)**

**In 3 Years (May 2028 - Debt Free):**
- Emergency Fund: 4 → 25 points (+21)
- Debt Management: 18 → 25 points (+7)
- Savings Rate: 22 → 25 points (+3)
- Cash Flow: 8 → 25 points (+17)
- **Total: 52 → 100 (Grade A+)**

---

## 🎯 TRACKING YOUR PROGRESS

### Score by Month

| Month | Score | Grade | Change | Status |
|-------|-------|-------|--------|--------|
| Nov 2025 | {total_score} | {grade} | - | Baseline |
| Dec 2025 | TBD | TBD | TBD | Track |
| Jan 2026 | TBD | TBD | TBD | Track |

**Update this report monthly** by running:
```bash
python3 financial_docs/calculate_health_score.py
```

---

## 💪 YOUR STRENGTHS

"""

    strengths = []
    if scores['savings_rate']['score'] >= 20:
        strengths.append(f"✅ **Excellent Savings Rate** ({scores['savings_rate']['savings_rate']:.1%} including match)")
    if scores['debt_management']['dti'] < 0.36:
        strengths.append(f"✅ **Manageable Debt-to-Income** ({scores['debt_management']['dti']:.1%} DTI)")
    if financial_data['mortgage_rate_avg'] < 0.03:
        strengths.append(f"✅ **Low Mortgage Rates** ({financial_data['mortgage_rate_avg']:.2%} average)")
    if financial_data['net_worth'] > 400000:
        strengths.append(f"✅ **Strong Net Worth** (${financial_data['net_worth']:,.0f})")

    for strength in strengths:
        report += f"- {strength}\n"

    report += """

---

## 🚨 YOUR WEAKNESSES

"""

    weaknesses = []
    if scores['emergency_fund']['score'] < 10:
        weaknesses.append("🔴 **Critical Emergency Fund** (Only 0.5 months)")
    if scores['cash_flow']['monthly_cash_flow'] < 0:
        weaknesses.append("🔴 **Negative Cash Flow** (Spending more than earning)")
    if scores['debt_management']['high_interest_debt'] > 20000:
        weaknesses.append("🔴 **High Credit Card Debt** ($30,000 @ 22% pending)")

    for weakness in weaknesses:
        report += f"- {weakness}\n"

    report += f"""

---

## 🔗 RELATED DOCUMENTS

- **[DASHBOARD.md](DASHBOARD.md)** - Real-time financial metrics
- **[FINANCIAL_ACTION_PLAN.md](FINANCIAL_ACTION_PLAN.md)** - Complete action plan
- **[CURRENT_FINANCIAL_STATUS.md](CURRENT_FINANCIAL_STATUS.md)** - Full financial snapshot
- **[BUDGET_GUIDELINES.md](BUDGET_GUIDELINES.md)** - Budget configuration

---

## 📊 METHODOLOGY

### Scoring System

**Emergency Fund (0-25 points):**
- Measures months of expenses covered
- Targets 6+ months for full points

**Debt Management (0-25 points):**
- Debt-to-income ratio (0-15 pts)
- High-interest debt burden (0-10 pts)

**Savings Rate (0-25 points):**
- Percentage of income saved
- Includes employer match
- Targets 20%+ for full points

**Cash Flow (0-25 points):**
- Monthly surplus/deficit
- As percentage of income
- Targets +20% for full points

**Grade Scale:**
- A (90-100): Excellent
- B (80-89): Good
- C (70-79): Fair
- D (60-69): Poor
- F (0-59): Crisis

---

**Next Assessment:** {(datetime.now()).replace(day=1).replace(month=((datetime.now().month % 12) + 1)).strftime('%B %Y')} (Monthly)
**Generated by:** calculate_health_score.py
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**Remember:** Your score is a snapshot, not a judgment. Every point of improvement brings you closer to financial freedom!
"""

    return report

def main():
    print("🏆 Financial Health Score Calculator")
    print("=" * 70)
    print()

    # Load financial data from config files
    print("📥 Loading financial data...")
    financial_data = get_financial_data()
    print("   ✅ Financial data loaded")
    print()

    # Calculate scores
    print("📊 Calculating scores...")

    ef_score = calculate_emergency_fund_score(financial_data)
    debt_score = calculate_debt_management_score(financial_data)
    sr_score = calculate_savings_rate_score(financial_data)
    cf_score = calculate_cash_flow_score(financial_data)

    scores = {
        'emergency_fund': ef_score,
        'debt_management': debt_score,
        'savings_rate': sr_score,
        'cash_flow': cf_score
    }

    total_score = round(sum(s['score'] for s in scores.values()), 1)
    grade = get_grade(total_score)

    # Display results
    print()
    print(f"{'=' * 70}")
    print(f"  FINANCIAL HEALTH SCORE: {total_score}/100 (Grade: {grade})")
    print(f"{'=' * 70}")
    print()
    print("Category Breakdown:")
    print(f"  Emergency Fund:   {ef_score['score']:>5.1f}/25  {ef_score['status']}")
    print(f"  Debt Management:  {debt_score['score']:>5.1f}/25  {debt_score['status']}")
    print(f"  Savings Rate:     {sr_score['score']:>5.1f}/25  {sr_score['status']}")
    print(f"  Cash Flow:        {cf_score['score']:>5.1f}/25  {cf_score['status']}")
    print()

    # Generate recommendations
    recommendations = generate_recommendations(scores, total_score, grade)

    print(f"🎯 Priority Recommendations: {len(recommendations)}")
    for rec in recommendations:
        print(f"  {rec['priority']}: {rec['category']}")
    print()

    # Generate report
    print("📝 Generating detailed report...")
    report = generate_report(scores, total_score, grade, recommendations, financial_data)

    # Save report
    output_file = REPORTS_DIR / "FINANCIAL_HEALTH_SCORE.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Report saved: {output_file}")
    print()
    print("💡 To view:")
    print("   1. Rebuild docs: python3 financial_docs/build_financial_docs.py")
    print("   2. Open: financial_docs/financial_hub.html")
    print()

    # Save score history
    history_file = PROCESSED_DIR / "financial_health_history.json"
    history_entry = {
        'date': datetime.now().isoformat(),
        'score': total_score,
        'grade': grade,
        'breakdown': {k: v['score'] for k, v in scores.items()}
    }

    # Append to history
    history = []
    if history_file.exists():
        with open(history_file, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    history.append(history_entry)

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

    print(f"📊 Score history updated: {history_file}")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
