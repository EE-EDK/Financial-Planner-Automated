#!/usr/bin/env python3
"""
Kunz Family Finance Manager
Simplified all-in-one financial analysis and reporting tool

Usage:
    python finance.py import           # Import/update transactions from data/transactions.csv
    python finance.py analyze          # Analyze transactions and spending patterns
    python finance.py report           # Generate financial summary report
    python finance.py process-inputs   # Process files dropped in data/inputs/
    python finance.py all              # Run everything (import → analyze → report)

Configuration:
    - Edit tools/config.json for budget categories, accounts, and debts
    - Drop transaction CSV in data/transactions.csv
    - Drop other files in data/inputs/ for Claude to process
    - Use budget_editor.html to create/edit config files
"""

import csv
import json
import sys
import argparse
import os
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal

try:
    import openpyxl
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False

# Directories - Simple hybrid path detection
if getattr(sys, 'frozen', False):
    # Running as executable - use exe location as base
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script in tools/ - use parent directory as base
    BASE_DIR = Path(__file__).parent.parent

TOOLS_DIR = BASE_DIR / "tools"
DATA_DIR = BASE_DIR / "data"
INPUTS_DIR = DATA_DIR / "inputs"
ARCHIVE_DIR = BASE_DIR / "archive"
CONFIG_FILE = TOOLS_DIR / "config.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
INPUTS_DIR.mkdir(exist_ok=True)
ARCHIVE_DIR.mkdir(exist_ok=True)


class FinanceManager:
    def __init__(self):
        self.config = self.load_config()
        self.transactions = []
        self.analysis = {}

    def load_config(self):
        """Load configuration from config.json"""
        if not CONFIG_FILE.exists():
            print(f"❌ Error: {CONFIG_FILE} not found")
            print("Please create config.json with your budget and financial information")
            sys.exit(1)

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_config(self):
        """Save configuration to config.json"""
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def load_transactions(self):
        """Load transactions from CSV file (last 12 months only)"""
        if not TRANSACTIONS_FILE.exists():
            print(f"❌ Error: {TRANSACTIONS_FILE} not found")
            print(f"Please export transactions from Rocket Money and save as: {TRANSACTIONS_FILE}")
            return []

        print(f"📥 Loading transactions from {TRANSACTIONS_FILE.name}...")

        # Calculate 12 months ago date
        twelve_months_ago = datetime.now() - timedelta(days=365)

        transactions = []
        total_count = 0
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                total_count += 1

                # Parse date
                try:
                    trans_date = datetime.strptime(row['Date'], '%Y-%m-%d')
                except:
                    continue

                # Only keep last 12 months
                if trans_date < twelve_months_ago:
                    continue

                # Skip credit card payments and ignored transactions
                if row.get('Ignored From') or row.get('Category') == 'Credit Card Payment':
                    continue

                # Parse amount
                try:
                    amount = float(row['Amount']) if row.get('Amount') else 0.0
                except:
                    amount = 0.0

                transactions.append({
                    'date': row['Date'],
                    'name': row.get('Custom Name') or row.get('Name', 'Unknown'),
                    'amount': amount,
                    'category': row.get('Category', 'Uncategorized'),
                    'account': row.get('Account Name', 'Unknown'),
                    'description': row.get('Description', '')
                })

        self.transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        print(f"✅ Loaded {len(self.transactions)} transactions from last 12 months (filtered from {total_count} total)")
        return self.transactions

    def analyze_spending(self):
        """Analyze spending patterns"""
        print("\n📊 Analyzing spending patterns...")

        category_spending = defaultdict(float)
        current_month_spending = defaultdict(float)  # NEW: Track current month separately
        merchant_spending = defaultdict(lambda: {'total': 0, 'count': 0})
        monthly_spending = defaultdict(float)

        current_month = datetime.now().strftime('%Y-%m')  # e.g., "2025-12"

        for trans in self.transactions:
            amount = trans['amount']
            if amount <= 0:  # Skip refunds/income
                continue

            category = trans['category']
            merchant = trans['name']
            month = trans['date'][:7]  # YYYY-MM

            category_spending[category] += amount
            merchant_spending[merchant]['total'] += amount
            merchant_spending[merchant]['count'] += 1
            monthly_spending[month] += amount

        # Calculate budget vs actual for CURRENT MONTH
        current_month = datetime.now().strftime('%Y-%m')
        current_month_spending = defaultdict(float)

        # Get current month's spending by category
        for trans in self.transactions:
            if trans['date'][:7] == current_month and trans['amount'] > 0:
                current_month_spending[trans['category']] += trans['amount']

        budget_comparison = {}
        total_budgeted = 0
        total_spent = 0

        for category, budgeted in self.config.get('budget', {}).items():
            spent_this_month = current_month_spending.get(category, 0)
            remaining = budgeted - spent_this_month
            budget_comparison[category] = {
                'budgeted': budgeted,
                'spent': spent_this_month,
                'remaining': remaining,
                'percent': (spent_this_month / budgeted * 100) if budgeted > 0 else 0
            }
            total_budgeted += budgeted
            total_spent += spent_this_month

        self.analysis = {
            'category_spending': dict(category_spending),
            'merchant_spending': dict(merchant_spending),
            'monthly_spending': dict(monthly_spending),
            'budget_comparison': budget_comparison,
            'total_budgeted': total_budgeted,
            'total_spent': total_spent,
            'total_remaining': total_budgeted - total_spent
        }

        print(f"✅ Analysis complete")
        print(f"   Budget for {current_month}: ${total_budgeted:,.2f}")
        print(f"   Spent in {current_month}: ${total_spent:,.2f}")
        print(f"   Remaining this month: ${total_budgeted - total_spent:,.2f}")

        return self.analysis

    def calculate_financial_health(self):
        """Calculate financial health score"""
        score = 100
        warnings = []

        # Calculate totals
        total_liquid = sum(
            sum(accounts.values())
            for accounts in self.config.get('accounts', {}).values()
        )

        total_debt = 0
        for debt_category in self.config.get('debts', {}).values():
            if isinstance(debt_category, list):
                total_debt += sum(d.get('balance', 0) for d in debt_category)

        monthly_income = self.config.get('income', {}).get('monthly_earnings', 0)
        total_budgeted = sum(self.config.get('budget', {}).values())

        # Scoring factors
        # 1. Emergency fund (0-25 points)
        emergency_fund_target = self.config.get('goals', {}).get('emergency_fund_target', 25000)
        emergency_fund_ratio = min(1.0, total_liquid / emergency_fund_target)
        emergency_score = emergency_fund_ratio * 25

        if total_liquid < 5000:
            warnings.append(f"⚠️ CRITICAL: Liquid cash only ${total_liquid:,.2f} - extremely low")
            score -= 20
        elif total_liquid < emergency_fund_target * 0.5:
            warnings.append(f"⚠️ Emergency fund below 50% of target (${total_liquid:,.2f} / ${emergency_fund_target:,.2f})")
            score -= 10

        # 2. Budget adherence (0-25 points)
        if monthly_income > 0:
            budget_ratio = total_budgeted / monthly_income
            if budget_ratio > 1.0:
                warnings.append(f"⚠️ Spending exceeds income by ${(total_budgeted - monthly_income):,.2f}/month")
                score -= 15
            elif budget_ratio > 0.95:
                warnings.append(f"⚠️ Budget very tight - only ${(monthly_income - total_budgeted):,.2f}/month left")
                score -= 5

        # 3. High-interest debt (0-25 points)
        high_interest_debt = 0
        for debt_list in self.config.get('debts', {}).values():
            if isinstance(debt_list, list):
                for debt in debt_list:
                    rate = debt.get('apr', debt.get('rate', 0))
                    if rate >= 10:
                        high_interest_debt += debt.get('balance', 0)

        if high_interest_debt > 0:
            warnings.append(f"⚠️ High-interest debt: ${high_interest_debt:,.2f}")
            if high_interest_debt > 20000:
                score -= 20
            elif high_interest_debt > 10000:
                score -= 10
            else:
                score -= 5

        # 4. Debt-to-income ratio (0-25 points)
        if monthly_income > 0:
            annual_income = monthly_income * 12
            debt_to_income = total_debt / annual_income if annual_income > 0 else 0
            if debt_to_income > 4:
                score -= 15
            elif debt_to_income > 3:
                score -= 10

        return {
            'score': max(0, min(100, score)),
            'total_liquid': total_liquid,
            'total_debt': total_debt,
            'high_interest_debt': high_interest_debt,
            'monthly_income': monthly_income,
            'warnings': warnings
        }

    def generate_report(self):
        """Generate comprehensive financial report"""
        print("\n📄 Generating financial report...")

        if not self.transactions:
            self.load_transactions()

        if not self.analysis:
            self.analyze_spending()

        health = self.calculate_financial_health()

        # Generate HTML report
        html = self._generate_html_report(health)

        # Save report
        report_file = BASE_DIR / "financial_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Report saved to: {report_file}")
        print(f"   Open in browser to view")

        # Also save JSON data for programmatic access
        data_file = BASE_DIR / "financial_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'generated': datetime.now().isoformat(),
                'health_score': health,
                'analysis': self.analysis,
                'config': self.config
            }, f, indent=2)

        return report_file

    def _generate_html_report(self, health):
        """Generate HTML report content"""

        # Get current month spending
        current_month = datetime.now().strftime('%Y-%m')
        current_spending = self.analysis.get('monthly_spending', {}).get(current_month, 0)

        # Top categories
        category_spending = sorted(
            self.analysis.get('category_spending', {}).items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        # Top merchants
        merchant_spending = sorted(
            self.analysis.get('merchant_spending', {}).items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:10]

        # Monthly trend (last 6 months)
        monthly = sorted(
            self.analysis.get('monthly_spending', {}).items(),
            reverse=True
        )[:6]

        # Budget categories with overspending
        budget_items = sorted(
            self.analysis.get('budget_comparison', {}).items(),
            key=lambda x: x[1]['spent'],
            reverse=True
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Report - Kunz Family</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        :root {{
            --navy: #0F1626;
            --leather: #AB987A;
            --coral: #FF533D;
            --eggshell: #F5F5F5;
            --white: #FFFFFF;
            --dark-text: #1a1a1a;
            --light-text: #6b7280;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--eggshell);
            min-height: 100vh;
            color: var(--dark-text);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: var(--white);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }}

        .header {{
            background: var(--navy);
            color: var(--white);
            padding: 60px 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 42px;
            font-weight: 300;
            letter-spacing: 8px;
            margin-bottom: 15px;
            text-transform: uppercase;
        }}

        .header p {{
            opacity: 0.7;
            font-size: 14px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}

        .health-score {{
            background: {'#2dd4bf' if health['score'] >= 70 else '#AB987A' if health['score'] >= 50 else '#FF533D'};
            color: var(--white);
            padding: 40px;
            text-align: center;
        }}

        .score-circle {{
            width: 140px;
            height: 140px;
            border-radius: 50%;
            background: rgba(255,255,255,0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            border: 3px solid rgba(255,255,255,0.3);
            backdrop-filter: blur(10px);
        }}

        .score-value {{
            font-size: 56px;
            font-weight: 300;
            letter-spacing: -2px;
        }}

        .score-label {{
            font-size: 16px;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 10px;
            opacity: 0.9;
        }}

        .content {{
            padding: 60px 40px;
            background: var(--white);
        }}

        .section {{
            margin-bottom: 60px;
        }}

        .section-title {{
            font-size: 24px;
            font-weight: 300;
            letter-spacing: 3px;
            margin-bottom: 30px;
            color: var(--navy);
            text-transform: uppercase;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--leather);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}

        .stat-card {{
            background: var(--eggshell);
            padding: 30px;
            border-radius: 4px;
            border-left: 4px solid var(--leather);
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        .stat-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--light-text);
            margin-bottom: 10px;
            font-weight: 600;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: 300;
            color: var(--navy);
            letter-spacing: -1px;
        }}

        .warnings {{
            background: #fff3e0;
            border-left: 4px solid var(--coral);
            padding: 30px;
            border-radius: 4px;
            margin-bottom: 40px;
        }}

        .warnings h3 {{
            color: var(--navy);
            font-weight: 300;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 20px;
            font-size: 16px;
        }}

        .warnings ul {{ margin-left: 20px; }}
        .warnings li {{
            margin: 12px 0;
            color: #d84315;
            line-height: 1.6;
        }}

        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 20px 0;
            background: var(--white);
        }}

        th, td {{
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid var(--eggshell);
        }}

        th {{
            background: var(--navy);
            color: var(--white);
            font-weight: 400;
            font-size: 11px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }}

        th:first-child {{
            border-radius: 4px 0 0 0;
        }}

        th:last-child {{
            border-radius: 0 4px 0 0;
        }}

        tr:hover {{
            background: var(--eggshell);
        }}

        td strong {{
            color: var(--navy);
            font-weight: 500;
        }}

        .progress-bar {{
            width: 100%;
            height: 6px;
            background: var(--eggshell);
            border-radius: 3px;
            overflow: hidden;
            margin-top: 8px;
        }}

        .progress-fill {{
            height: 100%;
            background: var(--leather);
            transition: width 0.3s ease;
        }}

        .over-budget {{
            background: var(--coral);
        }}

        .footer {{
            text-align: center;
            padding: 40px;
            color: var(--light-text);
            background: var(--navy);
            color: rgba(255,255,255,0.6);
        }}

        .footer a {{
            color: var(--leather);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s;
        }}

        .footer a:hover {{
            border-bottom-color: var(--leather);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Kunz Family</h1>
            <p>Financial Report — {datetime.now().strftime('%B %d, %Y')}</p>
        </div>

        <div class="health-score">
            <div class="score-circle">
                <div class="score-value">{health['score']:.0f}</div>
            </div>
            <div class="score-label">Financial Health</div>
        </div>

        <div class="content">
            <div class="section">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Monthly Income</div>
                        <div class="stat-value">${health['monthly_income']:,.0f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Liquid Cash</div>
                        <div class="stat-value">${health['total_liquid']:,.0f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Total Debt</div>
                        <div class="stat-value">${health['total_debt']:,.0f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">This Month Spending</div>
                        <div class="stat-value">${current_spending:,.0f}</div>
                    </div>
                </div>
            </div>

            {f'''<div class="warnings">
                <h3>Attention Needed</h3>
                <ul>
                    {''.join(f'<li>{w}</li>' for w in health['warnings'])}
                </ul>
            </div>''' if health['warnings'] else ''}

            <div class="section">
                <h2 class="section-title">Budget vs Actual — {datetime.now().strftime('%B %Y')}</h2>
                <p style="color: var(--light-text); margin-bottom: 25px; font-size: 12px; letter-spacing: 1px; text-transform: uppercase;">
                    Current month spending compared to monthly budget
                </p>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Budgeted</th>
                            <th>Spent</th>
                            <th>Remaining</th>
                            <th>Progress</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'''<tr>
                            <td><strong>{cat}</strong></td>
                            <td>${data['budgeted']:,.2f}</td>
                            <td>${data['spent']:,.2f}</td>
                            <td style="color: {'#f87171' if data['remaining'] < 0 else '#4ade80'}">${data['remaining']:,.2f}</td>
                            <td>
                                <div class="progress-bar">
                                    <div class="progress-fill {'over-budget' if data['percent'] > 100 else ''}"
                                         style="width: {min(100, data['percent']):.0f}%"></div>
                                </div>
                                {data['percent']:.0f}%
                            </td>
                        </tr>''' for cat, data in budget_items)}
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2 class="section-title">Top Spending Categories (Last 12 Months)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Total Spent</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'<tr><td>{cat}</td><td>${amount:,.2f}</td></tr>' for cat, amount in category_spending)}
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2 class="section-title">Top Merchants (Last 12 Months)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Merchant</th>
                            <th>Total</th>
                            <th>Transactions</th>
                            <th>Average</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'''<tr>
                            <td>{merchant}</td>
                            <td>${data['total']:,.2f}</td>
                            <td>{data['count']}</td>
                            <td>${data['total']/data['count']:,.2f}</td>
                        </tr>''' for merchant, data in merchant_spending)}
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2 class="section-title">Monthly Spending Trend</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Total Spending</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'<tr><td>{month}</td><td>${amount:,.2f}</td></tr>' for month, amount in monthly)}
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2 class="section-title">Accounts & Balances</h2>
                <div class="stats-grid">
                    {self._generate_account_cards()}
                </div>
            </div>

            <div class="section">
                <h2 class="section-title">Financial Goals</h2>
                <ul style="line-height: 2;">
                    {''.join(f'<li>{note}</li>' for note in self.config.get('goals', {}).get('notes', []))}
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>Data from last 12 months of transactions • Generated by finance.py</p>
            <p style="margin-top: 10px; font-size: 12px;">
                Edit budget: <a href="budget_editor.html">budget_editor.html</a>
            </p>
        </div>
    </div>
</body>
</html>"""
        return html

    def _generate_account_cards(self):
        """Generate HTML for account balance cards"""
        cards = []
        for account_type, accounts in self.config.get('accounts', {}).items():
            for name, balance in accounts.items():
                cards.append(f'''<div class="stat-card">
                    <div class="stat-label">{name}</div>
                    <div class="stat-value">${balance:,.2f}</div>
                </div>''')
        return '\n'.join(cards)

    def process_excel_budget(self, excel_file):
        """Process Excel budget file and auto-generate config and transactions"""
        if not EXCEL_SUPPORT:
            print("❌ Excel support not available. Install openpyxl: pip install openpyxl")
            return False

        print(f"\n📊 Processing Excel budget: {excel_file.name}")

        try:
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active

            # Read header row to get categories
            header_row = list(ws.iter_rows(min_row=1, max_row=1, values_only=True))[0]

            # Find category columns (skip Date and Description columns)
            categories = {}
            for col_idx, header in enumerate(header_row):
                if header and header not in ['Date', None] and col_idx >= 2:
                    # Remove trailing spaces from category names
                    category_name = str(header).strip()
                    if category_name and category_name not in ['Deposit', 'Balance']:
                        categories[col_idx] = category_name

            print(f"✅ Found {len(categories)} budget categories")

            # Extract transactions from data rows
            transactions = []
            category_totals = defaultdict(float)

            for row in ws.iter_rows(min_row=2, values_only=True):
                # Skip empty rows and total rows
                if not row[0] or str(row[0]).lower() in ['totals', 'total']:
                    continue

                # Get date
                try:
                    if isinstance(row[0], datetime):
                        trans_date = row[0].strftime('%Y-%m-%d')
                    else:
                        trans_date = str(row[0])
                except:
                    continue

                # Get description
                description = str(row[1]) if len(row) > 1 and row[1] else "Transaction"

                # Process each category column
                for col_idx, category_name in categories.items():
                    if col_idx < len(row) and row[col_idx]:
                        try:
                            amount = float(row[col_idx])
                            if amount != 0:  # Skip zero amounts
                                transactions.append({
                                    'date': trans_date,
                                    'name': description,
                                    'amount': abs(amount),  # Use absolute value
                                    'category': category_name,
                                    'account': 'Excel Import',
                                    'description': description
                                })
                                category_totals[category_name] += abs(amount)
                        except (ValueError, TypeError):
                            continue

            print(f"✅ Extracted {len(transactions)} transactions")

            # Auto-generate config.json with discovered categories
            # Use category totals as initial budget estimates (monthly average)
            num_months = 1  # Could be improved to detect actual date range
            auto_budget = {}
            for category, total in category_totals.items():
                monthly_avg = total / max(num_months, 1)
                auto_budget[category] = round(monthly_avg, 2)

            # Create new config
            new_config = {
                "last_updated": datetime.now().strftime('%Y-%m-%d'),
                "income": {
                    "monthly_earnings": sum(auto_budget.values())  # Estimate based on spending
                },
                "budget": auto_budget,
                "accounts": {
                    "checking": {"Checking Account": 0},
                    "savings": {"Savings Account": 0}
                },
                "debts": {
                    "mortgages": [],
                    "auto": [],
                    "credit_cards": []
                },
                "recurring_expenses": {
                    "subscriptions": [],
                    "utilities": []
                },
                "goals": {
                    "emergency_fund_target": 10000,
                    "notes": [
                        "Auto-generated from Excel import",
                        "Review and adjust budget amounts as needed"
                    ]
                }
            }

            # Save config
            print(f"💾 Generating config.json with {len(auto_budget)} categories...")
            self.config = new_config
            self.save_config()

            # Save transactions to CSV
            print(f"💾 Saving {len(transactions)} transactions to CSV...")
            with open(TRANSACTIONS_FILE, 'w', newline='', encoding='utf-8') as f:
                if transactions:
                    writer = csv.DictWriter(f, fieldnames=['date', 'name', 'amount', 'category', 'account', 'description'])
                    writer.writeheader()
                    writer.writerows(transactions)

            print(f"✅ Excel import complete!")
            print(f"   Categories: {', '.join(sorted(auto_budget.keys()))}")

            return True

        except Exception as e:
            print(f"❌ Error processing Excel file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_inputs(self):
        """Process files in data/inputs/ directory"""
        print("\n📂 Processing input files...")

        input_files = list(INPUTS_DIR.glob('*'))
        if not input_files:
            print("No files found in data/inputs/")
            return False

        print(f"Found {len(input_files)} files:")
        for file in input_files:
            print(f"  - {file.name}")

        # Look for Excel files
        excel_files = [f for f in input_files if f.suffix.lower() in ['.xlsx', '.xls']]

        if excel_files:
            print(f"\n✨ Found {len(excel_files)} Excel file(s) - auto-processing...")
            for excel_file in excel_files:
                if self.process_excel_budget(excel_file):
                    return True
            return False
        else:
            print("\nℹ️  No Excel files found.")
            print("    Drop an Excel budget file here to auto-generate report!")
            return False

    def archive_monthly(self):
        """Archive current month's data"""
        current_month = datetime.now().strftime('%Y-%m')
        archive_month_dir = ARCHIVE_DIR / current_month
        archive_month_dir.mkdir(exist_ok=True)

        # Copy current config
        import shutil
        shutil.copy(CONFIG_FILE, archive_month_dir / "config.json")

        # Save current analysis if available
        if self.analysis:
            with open(archive_month_dir / "analysis.json", 'w') as f:
                json.dump(self.analysis, f, indent=2)

        print(f"✅ Archived to: {archive_month_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Kunz Family Finance Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python finance.py all              Run full analysis and generate report
  python finance.py import           Import transactions from data/transactions.csv
  python finance.py analyze          Analyze spending patterns
  python finance.py report           Generate HTML report
  python finance.py process-inputs   List files in data/inputs/ for processing
        """
    )

    parser.add_argument(
        'command',
        choices=['import', 'analyze', 'report', 'process-inputs', 'all'],
        help='Command to run'
    )

    args = parser.parse_args()

    # Initialize manager
    fm = FinanceManager()

    # Run requested command
    if args.command == 'import':
        fm.load_transactions()

    elif args.command == 'analyze':
        fm.load_transactions()
        fm.analyze_spending()

    elif args.command == 'report':
        fm.load_transactions()
        fm.analyze_spending()
        fm.generate_report()

    elif args.command == 'process-inputs':
        fm.process_inputs()

    elif args.command == 'all':
        print("=" * 70)
        print("🚀 RUNNING FULL FINANCIAL ANALYSIS")
        print("=" * 70)

        # Check for Excel files in inputs first
        excel_files = list(INPUTS_DIR.glob('*.xlsx')) + list(INPUTS_DIR.glob('*.xls'))
        if excel_files:
            print(f"\n✨ Detected Excel file(s) in data/inputs/")
            print(f"   Auto-importing from Excel...")
            if fm.process_inputs():
                print("\n📊 Excel import successful! Continuing with analysis...")

        fm.load_transactions()
        fm.analyze_spending()
        report_file = fm.generate_report()
        fm.archive_monthly()
        print("\n" + "=" * 70)
        print("✅ COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Open your report: {report_file}")
        print(f"💰 Edit budget: budget_editor.html\n")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Kunz Family Finance Manager\n")
        print("Usage: python finance.py <command>\n")
        print("Commands:")
        print("  all              Run everything (import → analyze → report)")
        print("  import           Import transactions from data/transactions.csv")
        print("  analyze          Analyze spending patterns")
        print("  report           Generate financial report")
        print("  process-inputs   Process files in data/inputs/\n")
        print("Quick start: python finance.py all")
        sys.exit(0)

    main()
