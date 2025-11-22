# Raw Financial Documents

This folder contains your original source financial documents organized by category.

## 📂 Folder Structure

### `/tax/`
Place all tax-related documents here:
- W2 forms
- 1099 forms (1099-INT, 1099-DIV, 1099-K, etc.)
- 1098 forms (mortgage interest, tuition)
- Tax returns (annual PDF copies)
- HSA distribution forms
- Any other tax documents

**Example files:**
- `2024_W2_Employer.pdf`
- `2024_1099-INT_Bank.pdf`
- `2024_Tax_Return.pdf`

---

### `/property/`
Place all property-related documents here:
- Property tax assessments
- Maintenance receipts
- Repair invoices
- HOA documents
- Property insurance
- Rental agreements

**Example files:**
- `2024_Property_Tax_Assessment.pdf`
- `HVAC_Repair_Invoice.pdf`
- `Rental_Agreement_2024.pdf`

---

### `/screenshots/`
Place budget and financial app screenshots here:
- Monthly budget screenshots
- Account balance screenshots
- Investment portfolio snapshots
- Spending category screenshots from budgeting apps

**Example files:**
- `2024-11_Budget_Screenshot.png`
- `Account_Balances_Nov_2024.png`

---

### `/exports/`
Place exported transaction data here:
- **AllTransactions.csv** - Master transaction file (auto-updated by import script)
- CSV exports from Rocket Money, Mint, YNAB, or other budgeting apps
- Bank transaction exports
- Credit card statement exports

**Example files:**
- `AllTransactions.csv` (required for transaction analysis)
- `RocketMoney_Export_2024-11.csv`
- `Bank_Transactions_Nov_2024.csv`

---

## 📝 How to Use

1. **Add documents** to the appropriate subfolder
2. **Run the build script** to regenerate reports:
   ```bash
   python3 financial_docs/build_all.py
   ```
3. **View in the hub** - Open `financial_docs/financial_hub.html`

---

## 🔒 Privacy Note

These are your personal financial documents. Keep this folder secure and never commit to public repositories without removing sensitive information.
