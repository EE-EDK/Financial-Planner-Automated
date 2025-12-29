# Financial Manager GUI - User Guide

## 🚀 Quick Start

### Launch the GUI

```bash
# From the financial_docs directory:
./launch_gui.sh

# Or directly:
python3 financial_manager_gui.py
```

## 📋 Overview

The Financial Manager GUI is a modern, bootstrap-style interface for managing your financial data. It provides:

- **Visual Dashboard** with real-time metrics
- **CSV Import** with validation and preview
- **Quick Updates** for balances and expenses
- **Auto-Rebuild** watcher for automatic dashboard updates
- **Month-over-Month Comparisons** for tracking progress
- **Data Validation** to catch errors before saving
- **Report Viewer** for all generated reports

---

## 🎯 Features by Tab

### 📊 Dashboard Tab

**What it shows:**
- **Metric Cards**:
  - 💵 Liquid Cash
  - 💳 Total Debt
  - 📈 Net Worth
  - 🔄 Monthly Recurring Expenses
  - 💰 Monthly Income
  - 🎯 Emergency Fund Progress

- **Alerts Section**: Critical financial warnings
  - Low cash alerts
  - Over-budget warnings
  - High spending notifications

- **Recent Activity**: Log of all actions performed

**How to use:**
- The dashboard auto-refreshes when data changes (if auto-rebuild is enabled)
- Click "🔄 Refresh from File" to manually reload data
- Alerts are color-coded: Red (critical), Yellow (warning), Blue (info)

---

### 📥 Import CSV Tab

**Purpose:** Import financial data from CSV or Excel files (supports multiple files).

**Supported Formats:**
- CSV files (`.csv`)
- Excel files (`.xlsx`, `.xls`)
- Multiple files at once

**Steps:**
1. Click **Browse...** to select file(s)
   - Hold **Ctrl** (Windows/Linux) or **Cmd** (Mac) to select multiple files
   - Mix CSV and Excel files in one selection
2. Click **Validate All** to preview and check all files
3. Review the preview for each file:
   - File type indicator (CSV/XLSX/XLS)
   - Headers detected
   - Row count
   - Sample rows shown
   - Validation results
4. Click **✓ Import & Process All** to import all files

**What happens:**
- **CSV files:** Copied to `Archive/raw/exports/`
- **Excel files:** Automatically converted to CSV, then copied to `Archive/raw/exports/`
- If `import_rocket_money.py` exists, it runs for each file
- Transactions are appended to AllTransactions.csv
- Dashboard auto-rebuilds (if enabled)
- Import summary shows success/failure count for each file

**Validation checks:**
- Required fields: Date, Amount (recommended)
- File format validation
- Sample data preview (2 rows per file)
- Each file validated individually

**Excel Support:**
Requires `openpyxl` library:
```bash
pip install openpyxl
```
If not installed, you'll see a helpful error message with installation instructions.

---

### ✏️ Update Balances Tab

**Purpose:** Quickly update account balances and recurring expenses.

**Sections:**

#### 💵 Cash Accounts
- Shows all cash accounts (checking, savings, etc.)
- Edit balances directly in the text fields
- Click **+ Add Cash Account** to add new accounts
- Click **🗑️** to delete an account

#### 💳 Debt Balances
- Shows all debt accounts (credit cards, mortgages, loans)
- Update balances to track payoff progress
- Click **+ Add Debt Account** to add new debts
- Click **🗑️** to delete paid-off accounts

#### 🔄 Recurring Expenses
- Shows monthly recurring expenses
- Update amounts for subscription changes
- Click **+ Add Recurring Expense** to add new subscriptions
- Click **🗑️** to remove cancelled subscriptions

**How to save:**
1. Edit any balances you need to update
2. Click **💾 Save All Changes**
3. Validation runs automatically (if enabled)
4. Confirmation dialog shows changes detected
5. Dashboard auto-rebuilds (if enabled)

**Validation features:**
- Alerts on large changes (>20% by default)
- Prevents saving invalid numbers
- Shows before/after comparison

---

### 📈 Comparisons Tab

**Purpose:** Compare financial snapshots across months.

**How to use:**
1. Select first month from dropdown (e.g., "2025-11")
2. Select second month from dropdown (e.g., "2025-10")
3. Click **Compare**

**Results show:**
- Liquid cash change
- Total debt change
- Net worth improvement
- Recurring expense changes
- Percentage changes with arrows (↑ ↓ →)

**Example output:**
```
Liquid Cash:
  2025-11: $5,143.00
  2025-10: $5,990.00
  Change: ↓ $847.00 (-14.1%)
```

**Requirements:**
- Monthly snapshots must exist (use "📸 Save Snapshot" button)
- At least 2 months of data needed

---

### ⚙️ Automation Tab

**Purpose:** Configure automatic processes and data validation.

#### Auto-Rebuild Dashboard

**What it does:**
- Monitors `Archive/processed/*.json` for changes
- Automatically runs `build_all.py` when files change
- Debounces rapid changes (5-second delay)

**How to use:**
1. Click **▶️ Start Watcher**
2. Status changes to "Running" (green)
3. Make changes to financial data
4. Dashboard rebuilds automatically
5. Click **⏹️ Stop Watcher** when done

**Benefits:**
- Drop CSV → Auto-import → Auto-rebuild
- Update balance → Auto-save → Auto-rebuild
- No manual rebuilds needed

#### Monthly Snapshots

**What it does:**
- Saves complete financial state to `Archive/snapshots/YYYY-MM/`
- Enables month-over-month comparisons
- Preserves historical data

**How to use:**
- Enable "Enable automatic monthly snapshots" checkbox (future feature)
- Or click **💾 Save Snapshot Now** to save manually

#### Data Validation

**Options:**
- ✅ **Validate data before saving**: Checks for errors before writing
- ✅ **Alert on large balance changes**: Warns if >20% change detected

**How to use:**
- Click **🔍 Run Validation Now** to check current data
- Review validation results in Activity Log

**What it checks:**
- Negative cash balances (warning)
- Zero debt balances (info - might be paid off)
- Very large recurring expenses (>$2,000/month)
- Low cash reserves (<1% of total debt)

---

### 📄 Reports Tab

**Purpose:** View all generated markdown reports.

**Available reports:**
- TRANSACTION_ANALYSIS_REPORT.md
- BUDGET_VS_ACTUAL.md
- FINANCIAL_HEALTH_SCORE.md
- SCENARIO_ANALYSIS.md
- And more...

**How to use:**
1. Select report from dropdown
2. Content displays automatically
3. Click **🔄 Refresh** to reload reports list

---

## 🎮 Footer Buttons

### 🔄 Rebuild Dashboard
- Manually trigger full dashboard rebuild
- Runs all analysis scripts and generates HTML
- Shows progress in status indicator

### 📸 Save Snapshot
- Save current financial state to Archive/snapshots/
- Required for month-over-month comparisons
- Preserves point-in-time data

### 🌐 Open Dashboard
- Opens `financial_hub.html` in your default browser
- View interactive dashboard with charts
- Search across all reports

### ❌ Exit
- Closes the GUI
- Stops auto-rebuild watcher if running

---

## 🔧 Command-Line Tools

### Quick Update CLI

Fast command-line updates without opening GUI:

```bash
# Update cash account
python3 scripts/quick_update.py cash USAA_Checking 3450

# Update debt balance
python3 scripts/quick_update.py debt Venture_Card 17200

# Update recurring expense
python3 scripts/quick_update.py recurring Netflix 19.99

# Cancel subscription
python3 scripts/quick_update.py recurring Hulu 0 --cancelled

# Show summary
python3 scripts/quick_update.py summary

# List accounts
python3 scripts/quick_update.py list
python3 scripts/quick_update.py list cash
python3 scripts/quick_update.py list debt
```

**Benefits:**
- Faster than GUI for quick updates
- Scriptable for automation
- Shows before/after comparison
- Calculates change automatically

### Standalone Watcher

Run auto-rebuild watcher without GUI:

```bash
# Start watcher with defaults
python3 scripts/watch_and_rebuild.py

# Custom check interval (every 5 seconds)
python3 scripts/watch_and_rebuild.py --interval 5

# Custom debounce time (wait 10s between rebuilds)
python3 scripts/watch_and_rebuild.py --debounce 10

# Stop with Ctrl+C
```

**Benefits:**
- Runs in background/terminal
- No GUI overhead
- Great for SSH sessions
- Logs all activity with timestamps

---

## 💡 Workflow Examples

### Monthly Financial Update (New Streamlined Method)

**Old way (5 steps):**
1. Export CSV from Rocket Money
2. Run `import_rocket_money.py`
3. Run `update_config.py` (navigate menus)
4. Run `build_all.py`
5. Open HTML

**New way (3 steps):**
1. Open GUI, start auto-rebuild watcher
2. Import CSV (drag-and-drop in future)
3. Update balances in GUI

*Dashboard rebuilds automatically!*

### Quick Balance Check

```bash
# Command line - super fast
python3 scripts/quick_update.py summary
```

### Update Multiple Accounts

**Using GUI:**
1. Go to "Update Balances" tab
2. Edit all accounts you need
3. Click "Save All Changes" once

**Using CLI (faster for multiple):**
```bash
python3 scripts/quick_update.py cash USAA_Checking 3450
python3 scripts/quick_update.py cash USAA_Savings 1200
python3 scripts/quick_update.py debt Venture_Card 16500
```

### Monthly Comparison

1. Save snapshot at end of each month
2. Go to "Comparisons" tab
3. Select two months to compare
4. Review changes and progress

---

## ⚙️ Settings & Configuration

### Auto-Rebuild Toggle (Header)
- Checkbox in top-right of GUI
- Enables/disables file watcher
- Persists while GUI is open

### Validation Settings (Automation Tab)
- **Validate on save**: Enabled by default
- **Alert on large changes**: Enabled by default (>20% threshold)

### File Paths
All paths are auto-detected relative to `financial_docs/`:
- Watch: `Archive/processed/`
- Build: `build_all.py`
- Config: `Archive/processed/financial_config.json`

---

## 🐛 Troubleshooting

### GUI won't start
```bash
# Check Python version (needs 3.6+)
python3 --version

# Check tkinter is installed
python3 -c "import tkinter"

# Run directly to see errors
python3 financial_manager_gui.py
```

### Import CSV button disabled
- Click "Validate" first
- Ensure CSV has Date and Amount columns
- Check validation errors in preview

### Auto-rebuild not working
- Check "Status: Running" is green
- Verify files are in `Archive/processed/`
- Check Activity Log for errors
- Ensure `build_all.py` exists

### Changes not saving
- Check file permissions
- Ensure `Archive/processed/` directory exists
- Review validation errors
- Check Activity Log

### Dashboard HTML not opening
- Ensure `financial_hub.html` exists
- Try "Rebuild Dashboard" first
- Check build errors in Activity Log

---

## 📊 Data Validation Details

### Automatic Checks

**On Save:**
- ✅ Valid numbers only
- ✅ No negative cash balances (warning)
- ✅ Large changes >20% (confirmation required)

**On Validation Run:**
- ✅ Negative balances
- ✅ Zero debts (might be paid off)
- ✅ Large recurring expenses (>$2,000)
- ✅ Low cash reserves (<1% of debt)

**CSV Import:**
- ✅ Required fields present
- ✅ Valid date formats
- ✅ Numeric amounts
- ✅ No duplicate headers

---

## 🎨 UI Elements

### Color Coding

- **Green**: Success, positive actions
- **Red**: Errors, critical alerts, debt
- **Blue**: Info, neutral status
- **Yellow**: Warnings
- **Purple**: Primary actions

### Status Indicator (Top Right)

- **● Ready** (Green): System ready
- **● Building...** (Yellow): Dashboard rebuilding
- **● Build Complete** (Green): Build successful
- **● Build Failed** (Red): Build errors

### Alert Levels

- **[CRITICAL]**: Immediate action needed
- **[WARNING]**: Review recommended
- **[INFO]**: FYI only

---

## 🔐 Security & Privacy

- All data stored locally (no cloud)
- No external API calls (except Chart.js CDN for dashboard)
- Git-tracked for version history
- `.gitignore` excludes sensitive files

**Never commit:**
- Actual transaction CSVs with personal info
- Screenshots with account numbers
- Tax documents

---

## 📦 File Structure

```
financial_docs/
├── financial_manager_gui.py     # Main GUI application
├── launch_gui.sh                # Quick launcher script
├── GUI_GUIDE.md                 # This guide
├── build_all.py                 # Master build script
├── financial_hub.html           # Generated dashboard
├── scripts/
│   ├── quick_update.py          # CLI quick updater
│   ├── watch_and_rebuild.py     # Standalone watcher
│   └── [other scripts...]
└── Archive/
    ├── processed/
    │   ├── financial_config.json
    │   └── [other JSON files...]
    ├── raw/
    │   └── exports/
    │       └── [CSV files...]
    ├── reports/
    │   └── [Markdown reports...]
    └── snapshots/
        ├── 2025-11/
        └── [monthly snapshots...]
```

---

## 🚀 Advanced Tips

### Run Watcher in Background
```bash
# Linux/Mac
nohup python3 scripts/watch_and_rebuild.py &

# View logs
tail -f nohup.out
```

### Schedule Monthly Snapshots (Cron)
```bash
# Edit crontab
crontab -e

# Add line (runs 1st of every month at 11pm)
0 23 1 * * cd /path/to/financial_docs && python3 scripts/save_monthly_snapshot.py
```

### Batch Updates
```bash
# Create a script with multiple updates
cat > update_nov.sh << 'EOF'
#!/bin/bash
python3 scripts/quick_update.py cash USAA_Checking 3450
python3 scripts/quick_update.py cash USAA_Savings 1200
python3 scripts/quick_update.py debt Venture_Card 16800
EOF

chmod +x update_nov.sh
./update_nov.sh
```

---

## 🤝 Getting Help

1. Check this guide
2. Review Activity Log in GUI
3. Run validation to check data
4. Check `build_all.py` output
5. Review error messages in terminal

---

## 📝 Future Enhancements

Planned features:
- ✨ Drag-and-drop CSV import directly in GUI
- ✨ Inline config editor in dashboard HTML
- ✨ Mobile PWA version
- ✨ Transaction auto-categorization with learning
- ✨ Goal progress notifications
- ✨ Export to Excel/PDF
- ✨ Budget vs actual charts
- ✨ Scenario modeling in GUI

---

**Last Updated:** November 30, 2025
**Version:** 1.0.0
