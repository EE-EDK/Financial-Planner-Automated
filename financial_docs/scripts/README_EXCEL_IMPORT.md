# Excel Budget Importer

Import financial transactions from Excel budget spreadsheets into your Financial Planner system.

## 📋 Overview

The `import_excel_budget.py` script processes Excel files with a budget-style format where:
- Each row represents a date/transaction period
- Each column represents an expense or income category
- Cells contain transaction amounts for that category on that date

## 🎯 Supported Format

Your Excel file should follow this structure:

```
| Date       | Description | Auto  | Utilities | Groceries | ... | Deposit | Balance |
|------------|-------------|-------|-----------|-----------|-----|---------|---------|
| 11/23/2025 | TSP deposit | 50.00 | 348.00    | 80.00     | ... | 1708.00 | 1708.00 |
| 12/1/2025  | visa        |-63.80 | -298.50   | -45.00    | ... | -552.58 | 1155.42 |
| Totals     |             | 50.00 | 49.50     | 35.00     | ... | 1155.42 | 0.00    |
```

### Key Features:
- **Date Column**: First column with dates (required)
- **Description Column**: Optional second column for transaction notes
- **Category Columns**: Each column represents an expense/income category
- **Balance Column**: Optional, will be ignored (not imported as transaction)
- **Totals Row**: Automatically detected and skipped

## 🚀 Usage

### Basic Usage

```bash
# Import a specific Excel file
python financial_docs/scripts/import_excel_budget.py path/to/your/budget.xlsx

# Auto-detect and import the most recent Excel file in exports folder
python financial_docs/scripts/import_excel_budget.py
```

### Step-by-Step Guide

1. **Place your Excel file** in the exports directory:
   ```
   financial_docs/Archive/raw/exports/YourBudget.xlsx
   ```

2. **Run the import script**:
   ```bash
   python financial_docs/scripts/import_excel_budget.py
   ```

3. **Review the output** - The script will show:
   - Number of transactions imported
   - Spending summary by category
   - Monthly totals

4. **Check the results** - Transactions are saved to:
   ```
   financial_docs/Archive/raw/exports/AllTransactions.csv
   ```

5. **Rebuild your financial reports**:
   ```bash
   python financial_docs/build_all.py
   ```

## 📊 Category Mapping

The script automatically maps common budget categories to standardized names:

| Excel Column       | Standardized Category    |
|-------------------|--------------------------|
| Auto, Xtra Car    | Auto & Transport         |
| Car Ins.          | Auto Insurance           |
| Utilities         | Bills & Utilities        |
| Medical           | Healthcare & Medical     |
| X-mas, B-Day      | Gifts & Donations        |
| Vacation          | Travel                   |
| Clothes           | Shopping                 |
| Furniture, Mower  | Home & Garden            |
| Savings, Extra RSP| Savings & Investments    |
| Deposit           | Income                   |

You can customize these mappings by editing the `CATEGORY_MAPPING` dictionary in the script.

## 🔧 Requirements

The script requires one of these Python packages:
- **openpyxl** (recommended) - `pip install openpyxl`
- **pandas** (alternative) - `pip install pandas openpyxl`

If neither is installed, the script will show an error with installation instructions.

## 📝 Date Formats

The script supports multiple date formats:
- `11/23/2025` (M/D/YYYY)
- `2025-11-23` (YYYY-MM-DD)
- `11/23/25` (M/D/YY)
- `23/11/2025` (D/M/YYYY)
- `2025/11/23` (YYYY/MM/DD)

## ⚙️ Advanced Features

### Multi-Sheet Support
If your Excel file has multiple sheets, all sheets will be processed automatically.

### Duplicate Detection
The script automatically prevents duplicate transactions by comparing:
- Date
- Description
- Amount
- Category

### Data Validation
- Empty cells are ignored
- Zero amounts are skipped
- Invalid dates generate warnings but don't stop processing
- Rows with "total" in the date field are automatically skipped

## 🧪 Testing

Create a sample budget file to test the importer:

```bash
python financial_docs/scripts/create_sample_budget.py
python financial_docs/scripts/import_excel_budget.py
```

This creates and imports a sample budget with test data.

## 🎯 Example Output

```
======================================================================
📊 EXCEL BUDGET TRANSACTION IMPORTER
======================================================================

📥 Importing Excel budget from: Sample_Budget.xlsx

📊 Processing sheet: November 2025
✅ Imported 16 transactions

======================================================================
📊 SPENDING SUMMARY
======================================================================

Categories:
  Income                         $  5,760.58
  Savings & Investments          $    845.28
  Bills & Utilities              $    766.50
  Groceries                      $    180.00
  Auto & Transport               $    113.80
  Healthcare & Medical           $     45.00

Monthly Totals:
  2025-11: $2,386.00
  2025-12: $5,341.15

✅ Saved to: AllTransactions.csv
   Total transactions: 24
   New transactions: 16
```

## 🔄 Integration with Financial Planner

After importing Excel data:

1. **View transactions**: Check `AllTransactions.csv`
2. **Rebuild reports**: Run `python build_all.py`
3. **View dashboard**: Open `financial_hub.html`

## 🐛 Troubleshooting

### "No date column found"
- Ensure your first column is labeled "Date" or "DT"
- Check that the date column contains valid dates

### "Could not parse date"
- Check date format matches supported formats
- Ensure dates are actual date values, not formulas

### "Need openpyxl or pandas"
- Install required package: `pip install openpyxl`

### Transactions seem incorrect
- Verify category column headers match your intended categories
- Check for merged cells or complex formatting
- Try simplifying the Excel file structure

## 📚 Related Scripts

- `import_rocket_money.py` - Import from Rocket Money CSV exports
- `analyze_transactions.py` - Analyze spending patterns
- `budget_vs_actual.py` - Compare budget to actual spending
- `build_financial_docs.py` - Generate financial reports

## 💡 Tips

1. **Consistent Headers**: Use the same column headers across all your budget files for consistency
2. **One Transaction Per Cell**: Each cell should contain a single transaction amount
3. **Keep It Simple**: Avoid complex Excel formulas, merged cells, or formatting
4. **Regular Imports**: Import regularly to keep your financial data up-to-date
5. **Backup First**: Make a copy of your Excel file before importing

## 📖 File Locations

- Script: `financial_docs/scripts/import_excel_budget.py`
- Input: `financial_docs/Archive/raw/exports/*.xlsx`
- Output: `financial_docs/Archive/raw/exports/AllTransactions.csv`
- Config: `financial_docs/Archive/processed/financial_config.json`
