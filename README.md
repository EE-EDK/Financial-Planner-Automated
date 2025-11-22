# Personal Financial Hub

**Consolidated financial documentation and planning system**

---

## 📊 Financial Hub

**[Open Financial Hub](financial_docs/financial_hub.html)** - View all financial documents in one place

### Quick Access

- **Transaction Analysis:** [TRANSACTION_ANALYSIS_REPORT.md](financial_docs/Archive/reports/TRANSACTION_ANALYSIS_REPORT.md)
- **Budget vs Actual:** [BUDGET_VS_ACTUAL.md](financial_docs/Archive/reports/BUDGET_VS_ACTUAL.md)
- **Financial Health Score:** [FINANCIAL_HEALTH_SCORE.md](financial_docs/Archive/reports/FINANCIAL_HEALTH_SCORE.md)
- **Scenario Analysis:** [SCENARIO_ANALYSIS.md](financial_docs/Archive/reports/SCENARIO_ANALYSIS.md)
- **Dashboard:** [DASHBOARD.md](financial_docs/Archive/reports/DASHBOARD.md)

---

## 💰 Financial Documentation System

All financial documents are organized in the `financial_docs/` folder:

### Structure

```
financial_docs/
├── financial_hub.html          # 🌐 Open this in browser to view all docs
├── build_all.py                # 🔧 Run this to rebuild after changes
├── README.md                   # 📖 Full system documentation
└── Archive/                    # 📁 All financial documents
    ├── raw/                    # Original source files
    │   ├── tax/                # Tax documents (W2s, 1099s, 1098s)
    │   ├── property/           # Property-related documents
    │   ├── screenshots/        # Budget screenshots
    │   └── exports/            # Transaction CSV files
    ├── processed/              # Generated JSON data files
    │   ├── financial_config.json    # Account balances & recurring expenses
    │   ├── budget.json              # Budget categories
    │   └── financial_goals.json     # Financial goals
    ├── reports/                # Auto-generated markdown reports
    └── snapshots/              # Monthly financial snapshots
        └── YYYY-MM/            # Archived state per month
```

### How to Use

1. **View Documents:** Open `financial_docs/financial_hub.html` in any browser
2. **Add Documents:** Drop new files in `financial_docs/Archive/raw/` subfolders
3. **Update Data:** Edit JSON files in `financial_docs/Archive/processed/`
4. **Rebuild Everything:** Run `python3 financial_docs/build_all.py`

---

## 🚀 Quick Start

### First Time Setup

1. **Add your financial data:**
   - Update `Archive/processed/financial_config.json` with your accounts
   - Update `Archive/processed/budget.json` with your budget
   - Add transaction data to `Archive/raw/exports/AllTransactions.csv`

2. **Generate reports:**
   ```bash
   python3 financial_docs/build_all.py
   ```

3. **View your dashboard:**
   ```bash
   open financial_docs/financial_hub.html
   ```

---

## 📊 System Features

### Dashboard
- 💰 **Real-Time Snapshot Cards** - Liquid cash, total debt, net worth, monthly recurring
- ⚠️  **Automated Alerts** - Low cash warnings, over-budget alerts, high spending
- 🎯 **Budget vs Actual** - Progress bars for all budget categories
- 📊 **Spending Trends** - Multi-month charts by category

### Goal Tracking
- 🎯 **Emergency Fund Progress** - Track progress to savings goals
- 💳 **Debt Payoff Scenarios** - Compare different payment strategies
- 📈 **Financial Goals** - Define and track custom goals

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

## 🎯 Monthly Workflow

### Week 1
- [ ] Export transactions from budgeting app
- [ ] Run `python scripts/import_rocket_money.py` to import
- [ ] Review spending vs budget

### Week 2
- [ ] Update account balances in `financial_config.json`
- [ ] Check for new recurring expenses

### Week 3
- [ ] Save monthly snapshot: `python scripts/save_monthly_snapshot.py`
- [ ] Review financial goals progress

### Week 4
- [ ] Generate reports: `python build_all.py`
- [ ] Review dashboard and plan for next month

---

## 📁 Adding New Documents

Simply add files to the appropriate Archive subdirectory:
- Tax forms → `Archive/raw/tax/`
- Financial reports → `Archive/reports/`
- Property docs → `Archive/raw/property/`
- Transaction exports → `Archive/raw/exports/`
- Screenshots → `Archive/raw/screenshots/`

Then rebuild: `python3 financial_docs/build_all.py`

---

## 📚 Documentation

For complete system documentation, see:
**[financial_docs/README.md](financial_docs/README.md)**

---

## 🔧 Maintenance

### Monthly Updates
1. Export new transactions from your budgeting app
2. Update `financial_config.json` with latest balances
3. Rebuild: `python3 financial_docs/build_all.py`

### Annual Tax Season
1. Add all W2s, 1099s, 1098s to `Archive/raw/tax/`
2. Add tax return PDF
3. Rebuild viewer

---

**Last Updated:** November 2025
**Status:** Template - Ready for Your Data
**Next Steps:** Add your financial data to get started!
