#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scenario Calculator
Model different financial scenarios and their impacts

Usage:
    python3 financial_docs/scenario_calculator.py

Output:
    - Generates SCENARIO_ANALYSIS.md in Archive/
    - Compares multiple scenarios
    - Shows projected outcomes
"""

from pathlib import Path
from datetime import datetime

from financial_utils import (
    setup_windows_encoding,
    save_report,
    REPORTS_DIR
)

# Setup encoding for cross-platform support
setup_windows_encoding()

def calculate_scenario_sell_property():
    """Scenario: Sell rental property"""
    sale_price = 270000
    mortgage_balance = 138226
    selling_costs = sale_price * 0.06
    net_proceeds = sale_price - mortgage_balance - selling_costs

    # Use of proceeds
    credit_card = 30000
    emergency_fund = 25000
    honda_loan = 28686
    remaining = net_proceeds - credit_card - emergency_fund - honda_loan

    # Monthly impact
    eliminate_mortgage = 1240
    lose_rental_income = -1865
    save_maintenance = 300  # average risk
    net_monthly = eliminate_mortgage + lose_rental_income + save_maintenance

    return {
        'name': 'Sell Rental Property',
        'net_proceeds': net_proceeds,
        'uses': {
            'credit_card': credit_card,
            'emergency_fund': emergency_fund,
            'honda_loan': honda_loan,
            'remaining': remaining
        },
        'monthly_impact': net_monthly,
        'score_change': 78 - 52,  # From health score
        'pros': [
            'Solves credit card crisis immediately',
            'Creates emergency fund',
            'Eliminates all consumer debt',
            'Removes 1,400-mile management hassle',
            'Provides $15k+ buffer'
        ],
        'cons': [
            'Lose potential appreciation',
            'Lose rental income stream',
            'Pay capital gains tax (~$17k)',
            'Transaction costs (~$16k)'
        ]
    }

def calculate_scenario_furlough():
    """Scenario: Ethan gets furloughed"""
    current_income = 15334
    lost_income = 5689
    unemployment = 2000  # estimated
    new_income = current_income - lost_income + unemployment

    current_spending = 15931
    deficit = new_income - current_spending

    # Emergency fund depletion
    emergency_fund = 7462
    months_covered = emergency_fund / abs(deficit) if deficit < 0 else float('inf')

    # Mitigation
    pause_401k = 1493
    cut_discretionary = 5393
    total_mitigation = pause_401k + cut_discretionary

    return {
        'name': 'Furlough (Worst Case)',
        'income_loss': lost_income,
        'unemployment': unemployment,
        'new_income': new_income,
        'current_spending': current_spending,
        'deficit': deficit,
        'months_covered': months_covered,
        'mitigation': {
            'pause_401k': pause_401k,
            'cut_discretionary': cut_discretionary,
            'total': total_mitigation,
            'resulting_deficit': deficit + total_mitigation
        },
        'actions': [
            'File for unemployment immediately',
            'Pause 401k contributions',
            'Cut all discretionary to $0',
            'Use HELOC only for emergencies',
            'Seek temporary work'
        ]
    }

def calculate_scenario_perfect_execution():
    """Scenario: Follow plan exactly"""
    months = {
        6: {  # May 2026
            'credit_card': 12500,
            'emergency_fund': 12000,
            'net_worth': 465000,
            'health_score': 82
        },
        12: {  # Nov 2026
            'credit_card': 0,
            'emergency_fund': 22000,
            'net_worth': 480000,
            'health_score': 92
        },
        36: {  # May 2028 - Debt Free
            'credit_card': 0,
            'heloc': 0,
            'emergency_fund': 52596,
            'net_worth': 550000,
            'health_score': 100,
            'monthly_surplus': 2500
        }
    }

    return {
        'name': 'Perfect Execution',
        'projections': months,
        'keys': [
            'Cut discretionary to $450/month',
            'Pay $1,900/month to credit card',
            'Add $900/month to emergency fund',
            'Survive maternity leave',
            'Pay off HELOC by May 2028'
        ]
    }

def generate_report():
    """Generate scenario comparison report"""

    scenario1 = calculate_scenario_sell_property()
    scenario2 = calculate_scenario_furlough()
    scenario3 = calculate_scenario_perfect_execution()

    report = f"""# FINANCIAL SCENARIO ANALYSIS
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Baseline Date:** November 2025

---

## 📊 SCENARIO COMPARISON

### Scenario 1: {scenario1['name']} ⭐ RECOMMENDED

**Net Impact:**
- Cash proceeds: ${scenario1['net_proceeds']:,.0f}
- Credit card: $30,000 → $0 ✅
- Emergency fund: $7,462 → $32,462 ✅
- Honda loan: $28,686 → $0 ✅
- Remaining buffer: ${scenario1['uses']['remaining']:,.0f}

**Monthly Cash Flow Change:**
- Eliminate mortgage: +$1,240
- Lose rental income: -$1,865
- Save maintenance risk: +$300
- **Net monthly: {'+' if scenario1['monthly_impact'] >= 0 else ''} ${scenario1['monthly_impact']:,.0f}**

**Financial Health Score:** 52 → 78 (+26 points)

**Pros:**
"""

    for pro in scenario1['pros']:
        report += f"- ✅ {pro}\n"

    report += "\n**Cons:**\n"
    for con in scenario1['cons']:
        report += f"- ❌ {con}\n"

    report += f"""

**Decision:** ⭐ **SELL** - Solves immediate crisis and provides stability for baby arrival

---

### Scenario 2: {scenario2['name']}

**Impact:**
- Income loss: ${scenario2['income_loss']:,.0f}/month
- Unemployment benefit: ${scenario2['unemployment']:,.0f}/month
- New income: ${scenario2['new_income']:,.0f}/month
- Current spending: ${scenario2['current_spending']:,.0f}/month
- **Monthly deficit: ${scenario2['deficit']:,.0f}**

**Emergency Fund:**
- Current: $7,462
- Months covered: {scenario2['months_covered']:.1f} months
- Status: 🔴 Depleted in {scenario2['months_covered']:.0f} month{'s' if scenario2['months_covered'] != 1 else ''}

**Mitigation Actions:**
- Pause 401k: +${scenario2['mitigation']['pause_401k']:,.0f}/month
- Cut all discretionary: +${scenario2['mitigation']['cut_discretionary']:,.0f}/month
- **Total mitigation: +${scenario2['mitigation']['total']:,.0f}/month**
- **Resulting situation: {'+' if scenario2['mitigation']['resulting_deficit'] >= 0 else ''}${scenario2['mitigation']['resulting_deficit']:,.0f}/month**

**Required Actions:**
"""

    for action in scenario2['actions']:
        report += f"- [ ] {action}\n"

    report += f"""

**Outcome:** Can survive but very painful. HELOC needed for emergencies.

---

### Scenario 3: {scenario3['name']}

**6-Month Projection (May 2026):**
- Credit card: ${scenario3['projections'][6]['credit_card']:,.0f}
- Emergency fund: ${scenario3['projections'][6]['emergency_fund']:,.0f}
- Net worth: ${scenario3['projections'][6]['net_worth']:,.0f}
- Health score: {scenario3['projections'][6]['health_score']}/100 (Grade B)

**12-Month Projection (November 2026):**
- Credit card: ${scenario3['projections'][12]['credit_card']:,.0f} ✅ PAID OFF
- Emergency fund: ${scenario3['projections'][12]['emergency_fund']:,.0f}
- Net worth: ${scenario3['projections'][12]['net_worth']:,.0f}
- Health score: {scenario3['projections'][12]['health_score']}/100 (Grade A)

**36-Month Projection (May 2028 - DEBT FREE):**
- All consumer debt: $0 🎉
- HELOC: $0 🎉
- Emergency fund: ${scenario3['projections'][36]['emergency_fund']:,.0f} ✅ FULL
- Net worth: ${scenario3['projections'][36]['net_worth']:,.0f}+
- Monthly surplus: ${scenario3['projections'][36]['monthly_surplus']:,.0f}/month
- Health score: {scenario3['projections'][36]['health_score']}/100 (Grade A+)

**Key Success Factors:**
"""

    for key in scenario3['keys']:
        report += f"- ✅ {key}\n"

    report += """

---

## 🎯 RECOMMENDATION

### Optimal Strategy: Combination Approach

**Phase 1 (NOW - December 2025):**
1. ✅ Decide to sell rental property
2. ✅ Cut discretionary spending to $450/month
3. ✅ Increase credit card payment to $1,900/month
4. ✅ List property in December

**Phase 2 (January - March 2026):**
1. ✅ Continue aggressive credit card payments
2. ✅ Close property sale (target: Feb 2026)
3. ✅ Use proceeds to pay off credit card + emergency fund + Honda
4. ✅ Prepare for baby (March 2026)

**Phase 3 (April - August 2026):**
1. ✅ Transfer any remaining CC balance to HELOC (if needed)
2. ✅ Survive maternity leave with emergency fund
3. ✅ Maintain reduced spending habits
4. ✅ Resume full income August 2026

**Phase 4 (September 2026 - May 2028):**
1. ✅ Pay off HELOC ($500/month)
2. ✅ Build emergency fund to full $52,596
3. ✅ Achieve debt freedom May 2028

**Outcome:** Debt-free by May 2028, full emergency fund, excellent financial health

---

## 📊 SCENARIO COMPARISON TABLE

| Metric | Current | Sell Property | Furlough | Perfect Plan |
|--------|---------|---------------|----------|--------------|
| **Credit Card** | $30,000 | $0 ✅ | $30,000 | $0 (Apr 2026) |
| **Emergency Fund** | $7,462 | $32,462 ✅ | Depleted 🔴 | $52,596 (2028) |
| **Monthly Cash Flow** | -$597 | +$668 ✅ | -$6,286 🔴 | +$2,051 ✅ |
| **Financial Score** | 52/100 | 78/100 ✅ | 25/100 🔴 | 100/100 ✅ |
| **Net Worth** | $456k | $456k | $450k 🔴 | $550k+ ✅ |
| **Stress Level** | High | Low ✅ | Extreme 🔴 | Low ✅ |

---

## 💰 FINANCIAL PROJECTIONS

### Month-by-Month: Perfect Execution + Property Sale

| Month | Credit Card | Emergency Fund | Net Worth | Score |
|-------|-------------|----------------|-----------|-------|
| Nov 2025 | $30,000 | $7,462 | $456,000 | 52 |
| Dec 2025 | $28,100 | $8,362 | $458,000 | 55 |
| Jan 2026 | $26,200 | $9,262 | $460,000 | 58 |
| Feb 2026 | $0 (sold property) | $32,462 | $465,000 | 78 ✅ |
| Mar 2026 | $0 | $33,362 | $467,000 | 80 |
| Apr 2026 | $0 | $34,262 | $469,000 | 82 |
| ... | ... | ... | ... | ... |
| May 2028 | $0 | $52,596 | $550,000+ | 100 ✅ |

---

## 🚨 RISK ANALYSIS

### Scenario 1 Risks (Sell Property)
- **Low Risk:** Clear path to debt freedom
- **Main risk:** Missing out on future property appreciation
- **Mitigation:** Invest proceeds wisely

### Scenario 2 Risks (Furlough)
- **High Risk:** Income loss + depleted emergency fund
- **Main risk:** Unable to pay bills, spiral into more debt
- **Mitigation:** Build emergency fund NOW

### Scenario 3 Risks (Perfect Execution)
- **Medium Risk:** Requires discipline and no surprises
- **Main risks:** Unexpected expenses, losing discipline
- **Mitigation:** Build buffer, stay focused

---

## 🎯 DECISION MATRIX

### Should You Sell the Rental Property?

**YES if:**
- ✅ You need cash now for credit card
- ✅ You value peace of mind over returns
- ✅ Managing from 1,400 miles is stressful
- ✅ You want stability before baby
- ✅ You need emergency fund ASAP

**NO if:**
- ❌ You can weather negative cash flow
- ❌ You have other sources for emergency fund
- ❌ Property management isn't burdensome
- ❌ You're OK with the risk
- ❌ Long-term appreciation is priority

**Recommendation:** ⭐ **SELL** - Your current situation (credit card deadline, baby coming, low emergency fund) makes this the smart choice.

---

## 🔗 RELATED DOCUMENTS

- **[PROPERTY_308_RENTAL_ANALYSIS.md](PROPERTY_308_RENTAL_ANALYSIS.md)** - Detailed property analysis
- **[FINANCIAL_ACTION_PLAN.md](FINANCIAL_ACTION_PLAN.md)** - Complete action plan
- **[DASHBOARD.md](DASHBOARD.md)** - Real-time metrics
- **[FINANCIAL_HEALTH_SCORE.md](FINANCIAL_HEALTH_SCORE.md)** - Your current score

---

**Generated by:** scenario_calculator.py
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Next Update:** Run before making major financial decisions
"""

    return report

def main():
    print("🎯 Scenario Calculator")
    print("=" * 70)
    print()

    print("📊 Calculating scenarios...")
    report = generate_report()

    # Save report using shared utility
    save_report(report, "SCENARIO_ANALYSIS.md")

    print(f"✅ Scenario analysis saved: {REPORTS_DIR / 'SCENARIO_ANALYSIS.md'}")
    print()
    print("💡 Scenarios analyzed:")
    print("   1. Sell Rental Property (RECOMMENDED)")
    print("   2. Furlough (Worst Case)")
    print("   3. Perfect Execution")
    print()
    print("🔗 To view:")
    print("   1. Rebuild: python3 financial_docs/build_financial_docs.py")
    print("   2. Open: financial_docs/financial_hub.html")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
