# Monthly Financial Snapshots

This folder stores archived copies of your financial state month-by-month.

## 📸 What Are Snapshots?

Snapshots are point-in-time captures of your:
- Account balances
- Debt balances
- Budget allocations
- Financial goals progress
- Transaction summaries

## 🗂️ Folder Structure

```
snapshots/
├── 2024-11/
│   ├── financial_config.json
│   ├── budget.json
│   ├── financial_goals.json
│   ├── dashboard_data.json
│   └── monthly_summary.md
├── 2024-12/
│   └── ...
└── 2025-01/
    └── ...
```

## 📅 How to Create a Snapshot

Run the snapshot script at the end of each month:

```bash
python3 scripts/save_monthly_snapshot.py
```

This will:
1. Create a folder for the current month (YYYY-MM)
2. Copy all current JSON configuration files
3. Generate a monthly summary report
4. Archive the data for historical tracking

## 📈 Why Take Snapshots?

- **Track progress** over time
- **Visualize trends** in spending, debt, and savings
- **Historical reference** for tax season
- **Audit trail** of financial decisions
- **Monthly comparison** year-over-year

## 🔍 Viewing Snapshot Data

You can manually compare snapshots or use analysis scripts:

```bash
# Compare this month vs last month
python3 scripts/compare_snapshots.py 2024-11 2024-10

# View trend analysis
python3 scripts/trend_analysis.py
```

---

**Tip:** Take snapshots on the same day each month (e.g., the 1st) for consistent comparisons.
