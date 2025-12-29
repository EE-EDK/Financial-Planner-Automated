# 💰 Kunz Family Financial Hub

**One unified system for all your financial documents, analysis, and reports.**

---

## 🚀 Quick Start

### Build Everything (Recommended)

Run **ONE command** to generate all reports and build the financial hub:

```bash
python3 financial_docs/build_all.py
```

Then open the generated HTML:

```bash
open financial_docs/financial_hub.html
```

That's it! 🎉

### View Your Dashboard

Simply open `financial_hub.html` in any browser to access:
- 💰 Real-time financial snapshot
- ⚠️ Automated alerts and warnings
- 🎯 Budget vs actual progress bars
- 📊 6-month spending trend charts
- 🔍 Search across all documents

---

## 📦 What Gets Generated

When you run `build_all.py`, it automatically:

1. **💳 Analyzes Transactions** → `TRANSACTION_ANALYSIS_REPORT.md`
2. **📊 Budget vs Actual** → `BUDGET_VS_ACTUAL.md`
3. **🏆 Financial Health Score** → `FINANCIAL_HEALTH_SCORE.md`
4. **📈 Monthly Snapshot** → `FINANCIAL_TRENDS.md`
5. **🎯 Scenario Analysis** → `SCENARIO_ANALYSIS.md`
6. **🌐 Financial Hub HTML** → `financial_hub.html` (all documents across categories)

---

## 📂 Project Structure

> ✨ **Recent Consolidation:** Scripts have been streamlined with shared utilities and consolidated functionality!

```
financial_docs/
├── build_all.py                    # 🎯 RUN THIS ONE SCRIPT
├── financial_hub.html              # 🌐 OPEN THIS TO VIEW
├── README.md                       # This file
├── scripts/                        # Analysis scripts (auto-run by build_all.py)
│   ├── financial_utils.py          # ✨ NEW: Shared utilities (eliminates duplication)
│   ├── analyze_transactions.py
│   ├── budget_vs_actual.py
│   ├── calculate_health_score.py  # ✨ UPDATED: Now uses config files dynamically
│   ├── generate_dashboard_data.py
│   ├── import_rocket_money.py
│   ├── snapshot_manager.py         # ✨ NEW: Consolidates track + save snapshots
│   ├── track_account_balances.py
│   ├── track_goals.py
│   ├── scenario_calculator.py
│   ├── update_config.py
│   ├── quick_update.py
│   ├── reorganize_archive.py
│   ├── fix_dashboard_embed.py
│   ├── watch_and_rebuild.py
│   └── build_financial_docs.py
├── tests/                          # Automated tests
├── Archive/                        # Your financial documents
│   ├── raw/                        # Original source files
│   │   ├── tax/                    # Tax documents (W2s, 1099s, 1098s)
│   │   ├── property/               # Property-related documents
│   │   ├── screenshots/            # Budget screenshots
│   │   └── exports/                # Rocket Money CSV exports
│   ├── processed/                  # Generated JSON data files
│   │   ├── dashboard_data.json     # Dashboard metrics
│   │   ├── financial_config.json   # Account balances and recurring expenses
│   │   ├── budget.json             # Budget categories
│   │   ├── financial_goals.json    # Goal definitions
│   │   ├── account_balance_history.json
│   │   ├── financial_health_history.json
│   │   └── financial_history.json
│   ├── reports/                    # Generated markdown reports
│   │   ├── TRANSACTION_ANALYSIS_REPORT.md
│   │   ├── BUDGET_VS_ACTUAL.md
│   │   ├── FINANCIAL_HEALTH_SCORE.md
│   │   └── SCENARIO_ANALYSIS.md
│   └── snapshots/                  # Monthly financial snapshots
│       └── YYYY-MM/                # Archived state per month
└── pytest.ini, .coveragerc, etc.   # Testing configuration
```

---

## 🎨 Dashboard Features

### Real-Time Snapshot Cards
- 💰 **Liquid Cash** - Current available funds
- 💳 **Total Debt** - All outstanding balances
- 📊 **Net Worth** - Assets minus liabilities
- 🔄 **Monthly Recurring** - Fixed monthly expenses

### Automated Alerts
- ⚠️ **Low Cash Warnings** - When liquid cash drops below thresholds
- 🔴 **Over-Budget Alerts** - Categories exceeding budget
- 📈 **High Spending Notifications** - Unusual spending patterns

### Budget vs Actual
- 🎯 **Progress Bars** - Visual comparison for all Rocket Money categories
- 📊 **Variance Analysis** - Over/under budget by category
- 🔍 **Trend Detection** - Identify spending patterns

### 6-Month Spending Trends
- 📦 **Amazon** - Track online shopping
- 🍽️ **Dining** - Restaurant and takeout
- 🛒 **Groceries** - Food shopping
- 🛍️ **Shopping** - General purchases

### Goal Tracking
- 🎯 **Emergency Fund Progress** - Track progress to 3-month and 6-month goals
- 💳 **Credit Card Payoff Scenarios** - Compare different payment strategies
- 📈 **Custom Financial Goals** - Define and track goals (debt payoff, savings, spending reduction)

### Design
- 📱 **Responsive** - Works on all devices
- 🌙 **Dark Theme** with purple accents
- 💾 **Self-Contained** - No internet required (except Chart.js CDN)
- ⚡ **Dynamic Data** - Updates automatically from JSON files
- 🔍 **Search** - Find anything across all documents

---

## 🔄 Monthly Workflow

### Step 1: Export from Rocket Money

1. Export transactions CSV from Rocket Money
2. Save to `Archive/raw/exports/` folder

### Step 2: Import Transactions

```bash
python3 scripts/import_rocket_money.py
```

This will:
- Import new transactions into AllTransactions.csv
- Show spending summary by category
- Identify potential recurring expenses

### Step 3: Update Balances (Monthly)

```bash
python3 scripts/update_config.py
```

Interactive menu to update:
- Recurring expenses (mortgages, subscriptions, utilities)
- Debt balances (mortgages, loans, credit cards)
- Cash accounts (checking, savings, brokerage)

### Step 4: Generate All Reports

```bash
python3 build_all.py
```

Generates all financial reports and HTML dashboard in one command!

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

### Step 5: Review

Open `financial_hub.html` in your browser 📊

---

## 🛠️ Individual Scripts Reference

### Transaction Analysis
```bash
python3 scripts/analyze_transactions.py
```
- Analyzes spending patterns from AllTransactions.csv
- Identifies waste (Amazon, dining, etc.)
- Highlights recurring charges
- **Output:** `Archive/reports/TRANSACTION_ANALYSIS_REPORT.md`

### Budget vs Actual
```bash
python3 scripts/budget_vs_actual.py
```
- Compares budgeted vs actual spending
- Variance analysis by category
- **Output:** `Archive/reports/BUDGET_VS_ACTUAL.md`
- **Input:** `Archive/processed/budget.json`

### Financial Health Score
```bash
python3 scripts/calculate_health_score.py
```
- Calculates 0-100 financial health score
- Grades: Emergency Fund, Debt, Savings, Cash Flow
- **Output:** `Archive/reports/FINANCIAL_HEALTH_SCORE.md`
- **History:** `Archive/processed/financial_health_history.json`

### Snapshot Manager (✨ New Consolidated Script)
```bash
# Record current financial state
python3 scripts/snapshot_manager.py record

# Archive to snapshots/YYYY-MM/
python3 scripts/snapshot_manager.py archive

# Generate trend report
python3 scripts/snapshot_manager.py trends

# Do all three
python3 scripts/snapshot_manager.py all
```
- **Consolidates:** `track_monthly_snapshot.py` + `save_monthly_snapshot.py`
- Records monthly financial snapshot
- Archives to snapshots directory
- Generates trend analysis reports
- **Outputs:**
  - `Archive/processed/financial_history.json`
  - `Archive/snapshots/YYYY-MM/`
  - `Archive/reports/FINANCIAL_TRENDS.md`

### Scenario Calculator
```bash
python3 scripts/scenario_calculator.py
```
- Models different financial scenarios
- Compares: Sell property, Furlough, Perfect execution
- **Output:** `Archive/reports/SCENARIO_ANALYSIS.md`

### Track Account Balances
```bash
python3 scripts/track_account_balances.py
```
- Records balance history over time
- **Output:** `Archive/processed/account_balance_history.json`

### Track Financial Goals
```bash
python3 scripts/track_goals.py
```
- View progress toward your financial goals
- **Input:** `Archive/processed/financial_goals.json`

### Generate Dashboard Data
```bash
python3 scripts/generate_dashboard_data.py
```
- Generates metrics for the HTML dashboard
- **Output:** `Archive/processed/dashboard_data.json`

### Update Configuration
```bash
python3 scripts/update_config.py
```
- Interactive tool to update account balances and recurring expenses
- **Updates:** `Archive/processed/financial_config.json`

### Reorganize Archive
```bash
python3 scripts/reorganize_archive.py
```
- Reorganizes files in Archive/ into proper subdirectories
- Auto-categorizes by file type (tax, property, screenshots, exports)

### Build Financial Hub HTML
```bash
python3 scripts/build_financial_docs.py
```
- Builds the interactive HTML viewer
- **Output:** `financial_hub.html`
- **Note:** This is run automatically by `build_all.py`

### Shared Utilities Module (✨ New)
```python
# Import in your scripts
from financial_utils import (
    load_config,
    load_budget,
    load_transactions,
    calculate_financial_snapshot,
    setup_windows_encoding,
    format_currency,
    save_json
)
```
- **Purpose:** Eliminates code duplication across all scripts
- **Features:**
  - Common path definitions (BASE_DIR, ARCHIVE_DIR, etc.)
  - Unified data loading (config, budget, transactions)
  - Standard calculation functions
  - Formatting utilities (currency, percentages)
  - Date parsing and validation
- **Location:** `scripts/financial_utils.py`

---

## 📁 Adding New Documents

Simply add files to the appropriate Archive subdirectory:

- **Tax forms** → `Archive/raw/tax/`
- **Property docs** → `Archive/raw/property/`
- **Screenshots** → `Archive/raw/screenshots/`
- **CSV exports** → `Archive/raw/exports/`
- **Reports** → `Archive/reports/` (auto-generated)
- **Data files** → `Archive/processed/` (auto-generated)

Then rebuild:
```bash
python3 build_all.py
```

---

## 🔍 Using the Search Feature

1. Open `financial_hub.html` in browser
2. Type in search box (e.g., "emergency fund", "credit card", "Amazon")
3. Click any result to view that document
4. Press `ESC` to close document viewer

**Search Shortcuts:**
- "credit card" - Find all credit card info
- "emergency" - Emergency fund details
- "Amazon" - All Amazon spending analysis
- "property" - Rental property analysis
- "0%" - Credit card deadline info

---

## 📈 Understanding the Dashboard

### Emergency Fund Progress
- Shows how much you've saved toward emergency fund goal
- Target: 3-6 months of expenses
- Visual progress bar with percentage

### Debt Payoff Timeline
- Shows timeline to pay off all debts
- Compares different payoff strategies
- Highlights critical deadlines (e.g., 0% APR expiration)

### Monthly Cash Flow
- Current: Income minus expenses
- After Actions: With planned changes
- Target: Ideal cash flow goal

### Spending by Category
- **Fixed:** Can't easily change (mortgages, insurance)
- **Discretionary:** Can reduce (dining, shopping, Amazon)
- **Debt Payments:** Credit cards, loans
- **Savings:** Amount saved each month

---

## 🧪 Running Tests

The project includes comprehensive test coverage:

```bash
# Run all tests
python3 run_tests.py

# Run specific test file
pytest tests/test_specific.py

# Run with coverage report
pytest --cov=scripts --cov-report=html
```

Tests are located in `tests/` directory and cover:
- All analysis scripts
- Data validation
- Report generation
- Configuration updates

---

## 📱 Mobile Usage

The HTML viewer is fully mobile-optimized:
- Responsive layout adapts to screen size
- Touch-friendly buttons (44px minimum)
- Swipeable document viewer
- Charts resize automatically

Open `financial_hub.html` on your phone to access finances anywhere!

---

## 🐛 Troubleshooting

### "No files showing in HTML"
- Rebuild: `python3 financial_docs/build_all.py`
- Clear browser cache and reload (Ctrl+F5 / Cmd+Shift+R)

### "Transaction analysis failing"
- Make sure `Archive/raw/exports/AllTransactions.csv` exists
- Check CSV format is correct (Date, Description, Amount, Category columns)

### "Search not working"
- Make sure you opened `financial_hub.html` (not the builder script)
- Check browser console for errors (F12)
- Try hard reload (Ctrl+F5)

### "Charts not showing"
- Ensure internet connection (Chart.js loads from CDN)
- Check browser console for errors
- Try different browser (Chrome/Firefox recommended)

### "Scripts not running"
- Check they're executable: `chmod +x scripts/*.py`
- Verify Python 3.6+: `python3 --version`
- Check for error messages in output

### "Mobile view broken"
- Clear browser cache
- Try landscape mode
- Zoom to 100%

---

## 💡 Pro Tips

### Monthly Checklist
1. ☐ Export Rocket Money transactions to `Archive/raw/exports/`
2. ☐ Run `python3 scripts/import_rocket_money.py`
3. ☐ Update balances with `python3 scripts/update_config.py`
4. ☐ Run `python3 build_all.py`
5. ☐ Review dashboard for alerts
6. ☐ Save monthly snapshot: `python3 scripts/save_monthly_snapshot.py`

### Updating Financial Data
1. Edit `Archive/processed/financial_config.json` for account balances
2. Edit `Archive/processed/budget.json` for budget categories
3. Edit `Archive/processed/financial_goals.json` for goals
4. Re-run `python3 build_all.py`

### Key Files to Review Monthly
1. **Dashboard** - Current status at a glance
2. **FINANCIAL_HEALTH_SCORE.md** - Overall health score and trends
3. **BUDGET_VS_ACTUAL.md** - Spending vs budget by category
4. **TRANSACTION_ANALYSIS_REPORT.md** - Spending patterns and waste
5. **SCENARIO_ANALYSIS.md** - What-if planning

---

## 🎯 System Philosophy

### Auto-Categorization
The system automatically categorizes documents:
- Tax documents (W2s, 1099s, 1098s)
- Transaction data (CSV files)
- Property documents (receipts, assessments)
- Budget screenshots
- Analysis reports

### Future-Proof Design
- **Python + HTML** - No complex frameworks
- **Self-contained viewer** - Works offline
- **Easy to update** - Drop files + rebuild
- **Human-readable** - All source in markdown/JSON
- **Version controlled** - Git tracks all changes

### Data Management
- **Raw files** - Original source files never modified
- **Processed data** - JSON files generated from raw data
- **Reports** - Markdown files generated from processed data
- **Snapshots** - Monthly archives for historical tracking

### Code Consolidation (Recent Improvement)
- **Shared Utilities Module** - `financial_utils.py` eliminates 200+ lines of duplicate code
- **Consolidated Snapshots** - `snapshot_manager.py` combines track + save functionality
- **Dynamic Data Loading** - `calculate_health_score.py` now reads from config files instead of hardcoded values
- **Consistent APIs** - All scripts use standard functions for loading data
- **Reduced Complexity** - Easier to maintain and extend

**Benefits:**
- 🎯 Single source of truth for common functions
- 🔧 Easier to update and maintain
- 🐛 Fewer bugs from code duplication
- 📈 More consistent behavior across scripts
- ⚡ Faster development of new features

---

## 📊 Current System Status

### Version Information
- **System Version:** 2.1 (Consolidated)
- **Python Required:** 3.6+
- **Last Major Update:** December 2025 (Code Consolidation)

### Capabilities
- ✅ Transaction import from Rocket Money
- ✅ Automated financial health scoring (dynamic data loading)
- ✅ Budget vs actual tracking
- ✅ Scenario modeling
- ✅ Monthly snapshots (consolidated record + archive + trends)
- ✅ Account balance history
- ✅ Goal tracking
- ✅ Interactive HTML dashboard
- ✅ Full-text search
- ✅ Mobile responsive
- ✅ Comprehensive test coverage
- ✅ **NEW:** Shared utilities module (eliminates duplication)
- ✅ **NEW:** Consolidated snapshot management

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| **View Dashboard** | Open `financial_hub.html` in browser |
| **Generate Everything** | `python3 build_all.py` |
| **Import Transactions** | `python3 scripts/import_rocket_money.py` |
| **Update Balances** | `python3 scripts/update_config.py` |
| **Monthly Snapshot** | `python3 scripts/snapshot_manager.py all` |
| **Run Tests** | `python3 run_tests.py` |
| **Add Document** | Copy to `Archive/raw/[category]/` → rebuild |

---

**Last Updated:** December 7, 2025 (Code Consolidation)
**Documentation Status:** ✅ Consolidated & Streamlined
**Next Review:** January 2026
