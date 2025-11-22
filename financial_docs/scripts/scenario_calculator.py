#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scenario Calculator (TEMPLATE)
Model different financial scenarios and their impacts

⚠️  THIS IS A TEMPLATE FILE ⚠️
Update the values in each scenario function below to match your personal
financial situation before running this script.

Usage:
    python3 financial_docs/scripts/scenario_calculator.py

Output:
    - Generates SCENARIO_ANALYSIS.md in Archive/reports/
"""

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

# ============================================================================
# UPDATE THESE VALUES TO MATCH YOUR SITUATION
# ============================================================================

CURRENT_INCOME = 7500  # Your monthly income
CURRENT_SPENDING = 6000  # Your monthly spending
CURRENT_DEBT = 20000  # Total consumer debt
EMERGENCY_FUND = 15000  # Current emergency fund

# ============================================================================

def calculate_scenario_extra_income():
    """Scenario: Side income or raise"""
    extra_income = 1000  # Update: How much extra income per month?
    new_income = CURRENT_INCOME + extra_income
    surplus = new_income - CURRENT_SPENDING
    annual_surplus = surplus * 12

    return {
        'name': 'Extra Income Scenario',
        'monthly_surplus': surplus,
        'annual_impact': annual_surplus
    }

def calculate_scenario_job_loss():
    """Scenario: Job loss emergency"""
    unemployment = 2000  # Estimated unemployment benefits
    new_income = unemployment
    deficit = new_income - CURRENT_SPENDING
    months_covered = EMERGENCY_FUND / abs(deficit) if deficit < 0 else 999

    return {
        'name': 'Job Loss Emergency',
        'deficit': deficit,
        'months_covered': months_covered
    }

def generate_report():
    """Generate basic scenario report"""
    
    scenario1 = calculate_scenario_extra_income()
    scenario2 = calculate_scenario_job_loss()

    report = f"""# FINANCIAL SCENARIO ANALYSIS (TEMPLATE)
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

⚠️  **TEMPLATE FILE** - Update values in scenario_calculator.py before using

---

## Scenario 1: {scenario1['name']}
- Monthly surplus: ${scenario1['monthly_surplus']:,.0f}
- Annual impact: ${scenario1['annual_impact']:,.0f}

## Scenario 2: {scenario2['name']}
- Monthly deficit: ${scenario2['deficit']:,.0f}
- Months covered: {scenario2['months_covered']:.1f}

---

**To customize:** Edit scenario_calculator.py with your personal values
"""
    return report

def main():
    print("🎯 Scenario Calculator (Template)")
    print("=" * 70)
    print()
    print("⚠️  UPDATE VALUES IN scenario_calculator.py FIRST")
    print()

    report = generate_report()
    reports_dir = ARCHIVE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_file = reports_dir / "SCENARIO_ANALYSIS.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Template scenario saved: {output_file}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
