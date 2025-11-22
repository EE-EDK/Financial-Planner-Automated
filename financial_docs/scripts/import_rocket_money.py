#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rocket Money Transaction Importer
Imports transaction CSV exports from Rocket Money and processes them for analysis

Usage:
    python scripts/import_rocket_money.py [path/to/transactions.csv]

Output:
    - Updates Archive/data/AllTransactions.csv
    - Generates monthly summary
    - Identifies recurring transactions
"""

import csv
import json
import sys
import io
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from decimal import Decimal

# Fix Windows console encoding
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
ARCHIVE_DIR = BASE_DIR / "Archive"
PROCESSED_DIR = ARCHIVE_DIR / "processed"
EXPORTS_DIR = ARCHIVE_DIR / "raw" / "exports"
CONFIG_FILE = PROCESSED_DIR / "financial_config.json"

def load_config():
    """Load financial configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(config):
    """Save financial configuration"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def import_rocket_money_csv(csv_file):
    """Import Rocket Money CSV export"""

    print(f"📥 Importing Rocket Money transactions from: {csv_file}")
    print()

    transactions = []
    categories = defaultdict(Decimal)
    merchants = defaultdict(Decimal)
    monthly_totals = defaultdict(Decimal)

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Parse transaction
            date = row['Date']
            amount = Decimal(row['Amount']) if row['Amount'] else Decimal('0')
            category = row['Category']
            name = row['Custom Name'] if row['Custom Name'] else row['Name']
            account = row['Account Name']

            # Skip credit card payments and ignored transactions
            if row['Ignored From'] or category == 'Credit Card Payment':
                continue

            transactions.append({
                'date': date,
                'name': name,
                'amount': float(amount),
                'category': category,
                'account': account,
                'description': row['Description']
            })

            # Track categories (only expenses)
            if amount > 0:
                categories[category] += amount
                merchants[name] += amount

                # Monthly totals
                month = date[:7]  # YYYY-MM
                monthly_totals[month] += amount

    print(f"✅ Imported {len(transactions)} transactions")
    print()

    # Summary
    print("=" * 70)
    print("📊 SPENDING SUMMARY")
    print("=" * 70)
    print()

    print("Top Categories:")
    sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]
    for cat, amount in sorted_cats:
        print(f"  {cat:30s} ${amount:>10,.2f}")
    print()

    print("Top Merchants:")
    sorted_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)[:10]
    for merchant, amount in sorted_merchants:
        print(f"  {merchant:30s} ${amount:>10,.2f}")
    print()

    print("Monthly Totals:")
    sorted_months = sorted(monthly_totals.items())
    for month, amount in sorted_months[-6:]:  # Last 6 months
        print(f"  {month}: ${amount:,.2f}")
    print()

    # Save to AllTransactions.csv
    output_file = EXPORTS_DIR / "AllTransactions.csv"

    # Read existing if it exists
    existing_dates = set()
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_dates.add(row['Date'])

    # Merge and save
    all_transactions = []

    # Load existing
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_transactions.append(row)

    # Add new transactions
    new_count = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Date'] not in existing_dates:
                all_transactions.append(row)
                new_count += 1

    # Sort by date
    all_transactions.sort(key=lambda x: x['Date'])

    # Save merged file
    if all_transactions:
        fieldnames = all_transactions[0].keys()
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_transactions)

        print(f"✅ Saved to: {output_file}")
        print(f"   Total transactions: {len(all_transactions)}")
        print(f"   New transactions: {new_count}")

    return transactions

def identify_recurring_expenses(transactions, config):
    """Identify recurring expenses and compare to config"""

    print()
    print("=" * 70)
    print("🔄 RECURRING EXPENSE ANALYSIS")
    print("=" * 70)
    print()

    # Group by merchant and category
    recurring = defaultdict(list)

    for txn in transactions:
        if txn['amount'] > 0:  # Expenses only
            key = (txn['name'], txn['category'])
            recurring[key].append(txn['amount'])

    # Find items that appear monthly
    potential_recurring = []
    for (name, category), amounts in recurring.items():
        if len(amounts) >= 3:  # Appears at least 3 times
            avg_amount = sum(amounts) / len(amounts)
            potential_recurring.append({
                'name': name,
                'category': category,
                'frequency': len(amounts),
                'avg_amount': avg_amount,
                'amounts': amounts
            })

    # Sort by frequency
    potential_recurring.sort(key=lambda x: x['frequency'], reverse=True)

    print("Potential Recurring Expenses (appearing 3+ times):")
    print()
    for item in potential_recurring[:15]:
        print(f"  {item['name']:30s} ({item['frequency']}x) avg: ${item['avg_amount']:.2f}")

    # Compare to config
    if config:
        print()
        print("Comparing to configured recurring expenses...")
        print()

        config_names = set()
        for section in config.get('recurring_expenses', {}).values():
            for item in section.values():
                config_names.add(item['name'].lower())

        missing = []
        for item in potential_recurring:
            if item['name'].lower() not in config_names and item['frequency'] >= 6:
                missing.append(item)

        if missing:
            print("⚠️  Found recurring expenses NOT in config:")
            for item in missing[:10]:
                print(f"  {item['name']:30s} ${item['avg_amount']:.2f}/mo")
        else:
            print("✅ All major recurring expenses are in config")

def main():
    """Main import function"""

    print()
    print("=" * 70)
    print("💳 ROCKET MONEY TRANSACTION IMPORTER")
    print("=" * 70)
    print()

    # Get CSV file path
    if len(sys.argv) > 1:
        csv_file = Path(sys.argv[1])
    else:
        # Look for most recent CSV in Archive/raw/exports
        csv_files = list(EXPORTS_DIR.glob("*transactions*.csv"))
        csv_files = [f for f in csv_files if f.name != "AllTransactions.csv"]

        if csv_files:
            csv_file = max(csv_files, key=lambda x: x.stat().st_mtime)
            print(f"📁 Found recent CSV: {csv_file.name}")
        else:
            print("❌ No Rocket Money CSV found")
            print()
            print("Usage:")
            print("  python scripts/import_rocket_money.py path/to/transactions.csv")
            print()
            print("Or place CSV in Archive/raw/exports/ and run without arguments")
            return 1

    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        return 1

    # Load config
    config = load_config()

    # Import transactions
    transactions = import_rocket_money_csv(csv_file)

    # Analyze recurring expenses
    if config:
        identify_recurring_expenses(transactions, config)

    print()
    print("=" * 70)
    print("✅ IMPORT COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Run: python build_all.py")
    print("  2. Open: financial_hub.html")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
