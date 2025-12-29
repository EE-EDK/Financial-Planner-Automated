# 💰 Kunz Family Finance Manager

**Simple, powerful financial tracking and planning**

Last Updated: December 29, 2025

---

## 🚀 Quick Start

```bash
# 1. Export transactions from Rocket Money
# Save as: data/transactions.csv

# 2. Run analysis
python tools/finance.py all

# 3. View your report
open financial_report.html

# 4. Edit budget (optional)
open budget_editor.html
```

That's it! 🎉

---

## 🖥️ Using the GUI

**New: Graphical User Interface**

For a visual interface, run the GUI application:

```bash
# Install GUI dependencies (first time only)
pip install -r tools/requirements.txt

# Launch GUI
python tools/finance_gui.py
```

**GUI Features:**
- **Operations Tab:** Run import, analyze, and report commands with embedded console output
- **Budget Editor Tab:** Edit monthly earnings and budget categories, save to tools/config.json
- **Modern Design:** Navy/leather/coral color scheme matching the HTML reports
- **No Separate Terminal:** All output appears in the embedded console

**Building Portable Executable:**
```bash
# Install PyInstaller
pip install pyinstaller

# Build using the spec file (creates single-file executable)
pyinstaller tools/finance_gui.spec

# The executable will be in: dist/finance_gui.exe (or finance_gui on Mac/Linux)
# Move it to your project root for deployment
```

**Running the Executable:**
The executable is a **single file** that looks for `data/`, `tools/`, and `budget_editor.html` in the same directory where it's located. For deployment, just ensure this structure:

```
your-folder/
├── finance_gui.exe        # Single executable (all Python code bundled inside)
├── budget_editor.html     # Config editor
├── data/
│   └── transactions.csv
└── tools/
    └── config.json       # Your financial data
```

**Note:** The .exe file is completely standalone - no need for Python or dependencies on the target machine!

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Using the GUI](#️-using-the-gui)
- [Overview](#-overview)
- [Project Structure](#-project-structure)
- [Usage Guide](#-usage-guide)
- [Budget Editor](#-budget-editor)
- [Configuration](#-configuration)
- [Working with Claude](#-working-with-claude)
- [Monthly Workflow](#-monthly-workflow)
- [Current Financial Snapshot](#-current-financial-snapshot)
- [Goals & Priorities](#-goals--priorities)

---

## 📊 Overview

This is a simplified, all-in-one financial management system that:

✅ **Imports** transactions from Rocket Money CSV exports
✅ **Analyzes** spending by category, merchant, and time period
✅ **Compares** current month spending vs budget (not 12-month averages)
✅ **Calculates** financial health score
✅ **Generates** beautiful modern HTML reports (navy/leather/coral design)
✅ **Tracks** last 12 months of transactions (auto-archives older data)
✅ **Provides** graphical GUI application and web-based budget editor

### What Makes It Simple

- **1 Python script** instead of 18 scattered scripts
- **1 config file** for all budgets, accounts, and debts
- **1 HTML report** with modern professional design
- **1 command** to run everything: `python tools/finance.py all`
- **Current month tracking** - see December 2025 budget vs actual, not yearly totals

---

## 📂 Project Structure

```
Finances-Kunz/
├── README.md                    # This file - everything you need to know
├── budget_editor.html           # Web-based budget editor and config creator
├── financial_report.html        # Generated financial report
├── financial_data.json          # Machine-readable financial data
│
├── tools/                       # ⭐ All Python code, config, and build files
│   ├── finance.py               # Main script - does everything
│   ├── finance_gui.py           # GUI application
│   ├── config.json              # Your budget, accounts, debts, goals
│   ├── finance_gui.spec         # PyInstaller build spec
│   ├── money.ico                # App icon
│   └── requirements.txt         # GUI dependencies
│
├── data/                        # ⭐ Transaction data
│   ├── transactions.csv         # ← Drop your Rocket Money CSV here
│   ├── inputs/                  # ← Drop files for Claude to process
│   └── outputs/                 # Generated reports (legacy)
│
└── archive/
    └── YYYY-MM/                 # Monthly archives
        ├── config.json          # Config snapshot
        └── analysis.json        # Analysis snapshot
```

**For PyInstaller Executable:** Only need `budget_editor.html`, `tools/`, and `data/` folders alongside the .exe!

---

## 💻 Usage Guide

### The Main Command

```bash
python tools/finance.py all
```

This does everything:
1. ✅ Imports transactions from `data/transactions.csv`
2. ✅ Analyzes spending patterns
3. ✅ Generates HTML report
4. ✅ Archives monthly snapshot

### Individual Commands

```bash
# Import transactions only
python tools/finance.py import

# Analyze spending patterns
python tools/finance.py analyze

# Generate report
python tools/finance.py report

# List files waiting to be processed
python tools/finance.py process-inputs
```

### Getting Transactions from Rocket Money

1. Open Rocket Money app/website
2. Go to Transactions
3. Export → CSV
4. Save as: `data/transactions.csv`
5. Run: `python tools/finance.py all`

**Note:** The system automatically keeps only the last 12 months of transactions. Older data is archived annually.

---

## 🎨 Budget Editor

Open `budget_editor.html` in your browser to create or edit your budget configuration.

### Features
- ✅ Create new config.json from scratch or edit existing
- ✅ Edit monthly earnings
- ✅ Add/edit budget categories
- ✅ See real-time calculations (total budget, left for savings)
- ✅ Download updated config.json

### How to Use

1. Open `budget_editor.html` in browser
2. Edit budget values (or create from scratch)
3. Click "Save Config"
4. Downloaded file automatically saves to your Downloads folder
5. Move the downloaded config.json to `tools/` folder
6. Run: `python tools/finance.py all`

**Tip:** The editor automatically loads `config.json` from the tools/ directory when opened.

---

## ⚙️ Configuration

Everything is in `tools/config.json`:

```json
{
  "income": {
    "monthly_earnings": 11877
  },
  "budget": {
    "Groceries": 800,
    "Dining & Drinks": 350,
    "Auto & Transport": 800,
    ...
  },
  "accounts": {
    "checking": {
      "USAA Checking": 3283.54,
      ...
    }
  },
  "debts": {
    "mortgages": [...],
    "auto": [...],
    "credit_cards": [...]
  },
  "goals": {
    "emergency_fund_target": 25000,
    "notes": [...]
  }
}
```

### Updating Config

**Option 1: Use the Budget Editor (Recommended)**
- Open `budget_editor.html` in browser
- Make changes in GUI or create new config
- Download updated config
- Move to `tools/config.json`

**Option 2: Edit Directly**
- Open `tools/config.json` in text editor
- Make changes
- Save file

**Option 3: Ask Claude**
- Drop files in `data/inputs/`
- Tell Claude what to update
- Claude modifies tools/config.json

---

## 🤖 Working with Claude

### Adding New Data

Drop any files (screenshots, PDFs, spreadsheets) into `data/inputs/`, then tell Claude:

```
"Hey Claude, I dropped updated bank statements in data/inputs.
Can you extract the balances and update tools/config.json?"
```

Claude will:
1. Read the files
2. Extract relevant data
3. Update `tools/config.json` automatically, OR
4. Tell you what to add to the config

### Example Conversations

**Budget Planning:**
```
"I need to cut $500/month from my budget. What categories should I reduce?"
```

**Financial Advice:**
```
"Should I pay off my credit card or build my emergency fund first?"
```

**Trend Analysis:**
```
"Why did my grocery spending increase in November?"
```

**Goal Tracking:**
```
"Am I on track to pay off the Venture card before April 2026?"
```

### Processing Input Files

When you have files to process:

```bash
# 1. Drop files in data/inputs/
# 2. Run this to see what's there
python tools/finance.py process-inputs

# 3. Tell Claude to process them
# Claude will analyze and update config
```

---

## 📅 Monthly Workflow

### Week 1: Monitor

```bash
# Check spending in Rocket Money app
# Verify budget categories
# Look for unusual transactions
```

### Week 2: Review

```bash
# Export new transactions
python tools/finance.py all

# Review report
open financial_report.html

# Check for overspending categories
```

### Week 3: Adjust

```bash
# Update budgets if needed
open budget_editor.html

# Make adjustments
# Download and move config to tools/

# Regenerate report
python tools/finance.py all
```

### Week 4: Plan Ahead

```bash
# Discuss with Claude:
# - Next month's budget
# - Financial goals
# - Spending adjustments
```

---

## 💵 Current Financial Snapshot

**As of December 2025**

### Income & Spending
- **Monthly Earnings:** $11,877
- **Total Budget:** $11,904
- **Left for Savings:** -$27/month ⚠️

### Cash & Accounts
- **USAA Checking:** $3,283.54
- **USAA Savings:** $1,000.12
- **Capital One EK:** $220.00
- **Capital One KK:** $340.00
- **Vanguard:** $300.00
- **Total Liquid:** $5,143.66 🔴 **Critical Low**

### Debts

**Mortgages:**
- 308 Rental: $138,226 @ 2.75%
- 808 Primary: $256,506 @ 2.25%
- Solar Loan: $15,111 @ 2.99%

**Auto:**
- Mazda Lease: $14,772 @ 0%
- Civic Loan: $30,822 @ 5.19%

**Credit Cards:**
- Venture One: $17,933 @ 22% ⚠️ **0% expires April 2026**
- Discover: $1,128
- VISA: $538

**Total Debt:** ~$474,000

### Monthly Debt Payments
- Mortgages: $2,964
- Auto: $1,177
- Credit Cards: $176+ (Venture minimum)
- **Total:** $4,317/month

---

## 🎯 Goals & Priorities

### Critical (0-3 Months)

1. **💳 Pay Off Venture Card**
   - Balance: $17,933
   - 0% APR expires: **April 2026**
   - After that: 22% APR 🚨
   - **Action:** Pay $1,690/month (No Debt Goal category)

2. **💰 Build Emergency Fund**
   - Current: $5,143
   - Target: $25,000
   - Gap: $19,857
   - **Action:** Allocate $510/month (Emergency Funds category)

3. **📉 Reduce Spending**
   - Currently: -$27/month over budget
   - **Action:** Cut discretionary spending

### High Priority (3-6 Months)

4. **💵 Increase Cash Reserves**
   - Current liquid cash critically low
   - Need minimum $10,000 for comfort

5. **🏠 Rental Property Cash Flow**
   - Ensure 308 rental generates positive cash flow
   - Budget: $400/month for operating expenses

### Medium Priority (6-12 Months)

6. **🚗 Auto Loan Strategy**
   - Civic @ 5.19% = $561/month
   - Consider refinancing or aggressive paydown after credit card is cleared

7. **💡 Reduce Utility Costs**
   - Solar panels installed - monitor savings
   - Look for other efficiency improvements

### Budget Categories to Watch

Based on your December 2025 budget:

**Currently Over Budget:**
- Auto & Transport: $296 over ⚠️
- Dining & Drinks: $126 over ⚠️
- Entertainment: $256 over ⚠️
- Home & Garden: $407 over ⚠️
- Shopping: $784 over ⚠️
- Taxes: $8 over
- Everything Else: $16 over

**On Track:**
- Groceries: $66 remaining
- Loan Payment: $70 remaining
- Family Care: $4 remaining
- Personal Care: $6 remaining
- Pets: $1 remaining

**Unused:**
- Emergency Funds: $510 unused (allocate!)
- No Debt Goal: $1,690 unused (allocate!)
- New Water Heater: $150 unused
- Rental Property Operating: $400 unused

---

## 📝 Notes

### What This System Does

✅ Tracks all transactions from Rocket Money
✅ Analyzes spending by category and merchant
✅ Compares actual vs budgeted spending
✅ Calculates financial health score
✅ Generates beautiful HTML reports
✅ Keeps last 12 months of data
✅ Archives monthly snapshots
✅ Provides budget editing GUI

### What This System Doesn't Do

❌ Automatic bank connections (use Rocket Money for that)
❌ Investment tracking (basic support only)
❌ Tax calculations
❌ Bill payment automation
❌ Complex forecasting models

For these needs, continue using Rocket Money as your primary tracking tool, and use this system for analysis and planning conversations with Claude.

### Data Privacy

All data stays **local on your computer**. Nothing is uploaded to external services except when you explicitly interact with Claude.

---

## 🆘 Troubleshooting

### "Config not found"

```bash
# Make sure config.json exists in tools/ directory
ls -la tools/config.json

# If missing, restore from archive or create new one
cp archive/YYYY-MM/config.json tools/config.json

# Or create new config using the budget editor
open budget_editor.html
```

### "No transactions found"

```bash
# Make sure CSV is in the right place
ls -la data/transactions.csv

# Check file format (should be Rocket Money export)
head data/transactions.csv
```

### Report looks wrong

```bash
# Regenerate everything
python tools/finance.py all

# Check for errors in tools/config.json
python -m json.tool tools/config.json
```

### Need to go back to old version

```bash
# All old files are in archive/old-structure/
# (Created during simplification process)
ls archive/old-structure/
```

---

## 🎓 Tips & Best Practices

### Monthly Routine

1. **Export from Rocket Money** → `data/transactions.csv`
2. **Run analysis** → `python tools/finance.py all`
3. **Review report** → Look for overspending, trends
4. **Adjust budget** → Use budget editor or edit config
5. **Talk to Claude** → Discuss plans, get advice

### Budget Management

- **Be realistic** - Don't set impossible targets
- **Track everything** - Use Rocket Money categories
- **Review weekly** - Catch issues early
- **Adjust monthly** - Life changes, budget should too
- **Use the editor** - budget_editor.html makes config changes easy

### Using Claude Effectively

- **Be specific** - "Cut $500 from budget" vs "Help with budget"
- **Share context** - Drop files in data/inputs/ first
- **Ask for advice** - Claude sees your full financial picture
- **Follow up** - Track whether advice worked

### File Organization

- **Keep data/ clean** - Only current transactions in data/transactions.csv
- **Use inputs/ actively** - Drop files, process, clear
- **Reports at root** - financial_report.html and financial_data.json regenerated each run
- **Archive annually** - Old data goes to archive/YYYY/

---

## 📞 Support

### Need Help?

1. **Check this README** - Most answers are here
2. **Ask Claude** - "How do I...?"
3. **Review tools/config.json** - Is everything correct?
4. **Check archive/** - Restore old versions if needed

### Making Changes

Want to modify the system? The code is simple and well-commented:

- `tools/finance.py` - Main script (850 lines, all commands)
- `tools/finance_gui.py` - GUI application (630 lines, optional)
- `tools/config.json` - All your data (easy to edit)
- `tools/finance_gui.spec` - PyInstaller build configuration
- `tools/requirements.txt` - GUI dependencies
- `budget_editor.html` - Web-based budget editor and config creator (standalone HTML)

---

## 🚀 Next Steps

**Right now:**
1. Run `python tools/finance.py all`
2. Open `financial_report.html`
3. Review your financial health score
4. Identify categories that are over budget

**This week:**
1. Set up budget in Rocket Money to match tools/config.json
2. Export transactions weekly to track progress
3. Talk to Claude about your $17,933 credit card payoff plan

**This month:**
1. Cut spending in overspent categories
2. Allocate No Debt Goal ($1,690) to Venture card
3. Build emergency fund with $510/month
4. Get to break-even on monthly budget

---

## ✨ What Changed (Simplification)

**Before:**
- 18 separate Python scripts scattered everywhere
- 4 different README files
- Complex GUI that didn't work
- Confusing file structure
- HTML output buried in data/outputs/
- Hardcoded file paths
- Unclear which script to run

**After:**
- **tools/** folder containing everything: Python scripts, config, PyInstaller spec, icon, requirements
- Web-based budget editor at root level
- 1 comprehensive README (this file)
- **Fully portable:** All code in tools/, executable looks for data/ and tools/ folders
- Clean folder structure with no hardcoded paths
- HTML reports at root level for easy access
- Updated GitHub Actions workflow for validation
- One command: `python tools/finance.py all`

**Key Improvements:**
- ✅ Python code isolated in tools/ folder - clean separation
- ✅ Fully portable - executable only needs data/, tools/, and budget_editor.html
- ✅ No hardcoded file paths - works anywhere
- ✅ PyInstaller spec file with custom icon
- ✅ Modern navy/leather/coral color scheme
- ✅ Current month budget tracking (not 12-month averages)
- ✅ GUI with embedded console (no separate terminal)
- ✅ Budget editor creates configs from scratch
- ✅ All old files preserved in `archive/old-structure/`

---

**🎉 You're all set! Run `python tools/finance.py all` to get started.**
