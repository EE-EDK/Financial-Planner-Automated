# 💰 Personal Financial Hub

**One unified system for all your financial documents, analysis, and reports.**

---

## 🚀 Quick Start

### Build Everything (Recommended)

Run ONE command to generate all reports and build the financial hub:

```bash
python3 financial_docs/build_all.py
```

Then open the generated HTML:

```bash
open financial_docs/financial_hub.html
```

That's it! 🎉

---

## 📦 What Gets Generated

When you run `build_all.py`, it automatically:

1. **💳 Analyzes Transactions** → `TRANSACTION_ANALYSIS_REPORT.md`
2. **📊 Budget vs Actual** → `BUDGET_VS_ACTUAL.md`
3. **🏆 Financial Health Score** → `FINANCIAL_HEALTH_SCORE.md`
4. **📈 Monthly Snapshot** → `FINANCIAL_TRENDS.md`
5. **🎯 Scenario Analysis** → `SCENARIO_ANALYSIS.md`
6. **🌐 Financial Hub HTML** → `financial_hub.html` (all documents in one view)

---

## 🎨 Features

### Dashboard
- 💰 **Real-Time Snapshot Cards** - Liquid cash, total debt, net worth, monthly recurring
- ⚠️  **Automated Alerts** - Low cash warnings, over-budget alerts, high spending
- 🎯 **Budget vs Actual** - Progress bars for all budget categories
- 📊 **6-Month Spending Trends** - Visual charts by category

### Goal Tracking
- 🎯 **Emergency Fund Progress** - Track progress to 3-month and 6-month goals
- 💳 **Credit Card Payoff Scenarios** - Compare different payment strategies
- 📈 **Financial Goals** - Define and track custom goals (debt payoff, savings, spending reduction)

### Data Management
- 📸 **Monthly Snapshots** - Archive financial state month-over-month
- 📊 **Account Balance History** - Track how balances change over time
- 🔔 **Spending Anomaly Detection** - Identify unusual spending patterns
- 🔍 **Search** - Find anything across all documents

### Design
- 📱 **Responsive Design** - Works on all devices
- 🌙 **Dark Theme** with modern styling
- 💾 **Self-Contained** - No internet required
- ⚡ **Dynamic Data** - Updates automatically from JSON files

---

## 📂 Project Structure

```
financial_docs/
├── build_all.py                    # 🎯 RUN THIS ONE SCRIPT
├── financial_hub.html              # 🌐 OPEN THIS TO VIEW
├── README.md                       # Documentation
├── QUICK_START.md                  # Quick reference
├── scripts/                        # Analysis scripts (auto-run by build_all.py)
│   ├── analyze_transactions.py
│   ├── budget_vs_actual.py
│   ├── calculate_health_score.py
│   ├── generate_dashboard_data.py
│   ├── import_rocket_money.py
│   ├── save_monthly_snapshot.py
│   ├── track_account_balances.py
│   ├── track_goals.py
│   └── build_financial_docs.py
└── Archive/                        # Your financial documents
    ├── raw/                        # Original source files
    │   ├── tax/                    # Tax documents (W2s, 1099s, 1098s)
    │   ├── property/               # Property-related documents
    │   ├── screenshots/            # Budget screenshots
    │   └── exports/                # Transaction CSV exports (AllTransactions.csv)
    ├── processed/                  # Generated JSON data files
    │   ├── dashboard_data.json     # Dashboard metrics
    │   ├── financial_config.json   # Account balances and recurring expenses
    │   ├── budget.json             # Budget categories
    │   └── financial_goals.json    # Goal definitions
    ├── reports/                    # Generated markdown reports
    └── snapshots/                  # Monthly financial snapshots
        └── YYYY-MM/                # Archived state per month
```

---

## 🔄 Monthly Workflow

**Step 1: Export from Your Budgeting App**
1. Export transactions CSV from Rocket Money, Mint, YNAB, or your bank
2. Save to `Archive/raw/exports/` folder

**Step 2: Import Transactions**
```bash
python scripts/import_rocket_money.py
```
This will:
- Import new transactions into AllTransactions.csv
- Show spending summary by category
- Identify potential recurring expenses

**Step 3: Update Balances (Monthly)**
```bash
python scripts/update_config.py
```
Interactive menu to update:
- Recurring expenses (mortgages, subscriptions, utilities)
- Debt balances (mortgages, loans, credit cards)
- Cash accounts (checking, savings, brokerage)

**Step 4: Generate Reports**
```bash
python build_all.py
```
Generates all financial reports and HTML dashboard

**Step 5: Review**
Open `financial_hub.html` in your browser 📊

---

## 🛠️ Utility Scripts

### Monthly Snapshot
Save current financial state for historical tracking:
```bash
python scripts/save_monthly_snapshot.py
```
Saves to `Archive/snapshots/YYYY-MM/`

### Track Account Balances
Record balance history over time:
```bash
python scripts/track_account_balances.py
```
Updates `Archive/processed/account_balance_history.json`

### Track Financial Goals
View progress toward your financial goals:
```bash
python scripts/track_goals.py
```
Reads `Archive/processed/financial_goals.json`

### View Dashboard Data
See what metrics are being calculated:
```bash
python scripts/generate_dashboard_data.py
```
Generates `Archive/processed/dashboard_data.json`

---

## 📁 Adding New Documents

Simply add files to the appropriate Archive subdirectory:
- Tax forms → `Archive/raw/tax/`
- Financial reports → `Archive/reports/`
- Property docs → `Archive/raw/property/`
- Transaction data → `Archive/raw/exports/`
- Screenshots → `Archive/raw/screenshots/`

Then rebuild: `python3 build_all.py`

---

## 🐛 Troubleshooting

### "No files showing in HTML"
- Rebuild: `python3 financial_docs/build_all.py`
- Clear browser cache and reload

### "Transaction analysis failing"
- Make sure `Archive/raw/exports/AllTransactions.csv` exists
- Check CSV format matches expected columns

### "Scripts not found"
- Make sure you're running from the repository root
- Use full paths: `python3 financial_docs/build_all.py`

---

## 💡 Before vs After

**Before (6 separate commands):**
```bash
python3 analyze_transactions.py
python3 budget_vs_actual.py
python3 calculate_health_score.py
python3 track_monthly_snapshot.py
python3 scenario_calculator.py
python3 build_financial_docs.py
```

**After (ONE command):**
```bash
python3 build_all.py  # 🎉
```

---

## 📝 Configuration Files

### `Archive/processed/financial_config.json`
Contains:
- **recurring_expenses** - Monthly bills, subscriptions, loans
- **debt_balances** - Mortgages, auto loans, credit cards
- **credit_cards** - Card balances, limits, APRs
- **cash_accounts** - Checking, savings, brokerage balances

### `Archive/processed/budget.json`
Contains:
- **monthly_income** - Your monthly earnings
- **category_budgets** - Budget allocations by category
- **fixed_expenses** - Unchanging monthly costs

### `Archive/processed/financial_goals.json`
Contains:
- **goals** - Defined financial goals with targets and deadlines
- Each goal includes: name, description, type, target amount, priority

---

**Last Updated:** November 2025
**Status:** Template - Ready for Use
**Next Steps:** Add your data and run `build_all.py`!
