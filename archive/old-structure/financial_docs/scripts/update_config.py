#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Config Updater
Easy interface to update recurring expenses, debt balances, and cash accounts

Usage:
    python scripts/update_config.py

Interactive prompts to update:
- Recurring expenses (mortgages, subscriptions, utilities)
- Debt balances (mortgages, loans, credit cards)
- Cash accounts (checking, savings, brokerage)
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "Archive" / "processed"
CONFIG_FILE = PROCESSED_DIR / "financial_config.json"

def load_config():
    """Load financial configuration"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Save financial configuration"""
    config['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')

    # Calculate totals
    total_recurring = 0
    for section in config['recurring_expenses'].values():
        for item in section.values():
            if item.get('status') != 'cancelled':
                total_recurring += item['amount']

    total_debt = 0
    for section in config['debt_balances'].values():
        for item in section.values():
            total_debt += item['balance']

    for card in config['credit_cards'].values():
        total_debt += card['balance']

    total_cash = sum(acct['balance'] for acct in config['cash_accounts'].values())

    config['metadata']['total_recurring_expenses'] = round(total_recurring, 2)
    config['metadata']['total_debt'] = round(total_debt, 2)
    config['metadata']['total_liquid_cash'] = round(total_cash, 2)

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def display_menu():
    """Display main menu"""
    print()
    print("=" * 70)
    print("⚙️  FINANCIAL CONFIG UPDATER")
    print("=" * 70)
    print()
    print("What would you like to update?")
    print()
    print("  1. Recurring Expenses (mortgages, subscriptions, utilities)")
    print("  2. Debt Balances (mortgages, loans, car payments)")
    print("  3. Credit Card Balances")
    print("  4. Cash Accounts (checking, savings, brokerage)")
    print("  5. View Current Summary")
    print("  6. Exit")
    print()

def update_recurring_expenses(config):
    """Update recurring expenses"""
    print()
    print("=" * 70)
    print("💸 UPDATE RECURRING EXPENSES")
    print("=" * 70)
    print()

    sections = config['recurring_expenses']

    for section_name, items in sections.items():
        print(f"\n{section_name.replace('_', ' ').title()}:")
        print("-" * 70)

        for key, item in items.items():
            current = item['amount']
            status = item.get('status', 'active')

            print(f"\n{item['name']}: ${current:.2f} [{status}]")
            response = input("  New amount (or press Enter to skip): ").strip()

            if response:
                try:
                    new_amount = float(response)
                    item['amount'] = new_amount
                    print(f"  ✅ Updated to ${new_amount:.2f}")
                except ValueError:
                    print("  ❌ Invalid amount, skipping")

def update_debt_balances(config):
    """Update debt balances"""
    print()
    print("=" * 70)
    print("🏦 UPDATE DEBT BALANCES")
    print("=" * 70)
    print()

    sections = config['debt_balances']

    for section_name, items in sections.items():
        print(f"\n{section_name.title()}:")
        print("-" * 70)

        for key, item in items.items():
            current = item['balance']
            rate = item.get('interest_rate', 0)

            print(f"\n{item['name']}: ${current:,.2f} ({rate}% APR)")
            response = input("  New balance (or press Enter to skip): ").strip()

            if response:
                try:
                    new_balance = float(response)
                    item['balance'] = new_balance
                    print(f"  ✅ Updated to ${new_balance:,.2f}")
                except ValueError:
                    print("  ❌ Invalid amount, skipping")

def update_credit_cards(config):
    """Update credit card balances"""
    print()
    print("=" * 70)
    print("💳 UPDATE CREDIT CARD BALANCES")
    print("=" * 70)
    print()

    cards = config['credit_cards']

    for key, card in cards.items():
        current = card['balance']
        apr = card.get('apr', 'N/A')

        print(f"\n{card['name']}: ${current:,.2f} (APR: {apr}%)")
        response = input("  New balance (or press Enter to skip): ").strip()

        if response:
            try:
                new_balance = float(response)
                card['balance'] = new_balance
                print(f"  ✅ Updated to ${new_balance:,.2f}")
            except ValueError:
                print("  ❌ Invalid amount, skipping")

def update_cash_accounts(config):
    """Update cash account balances"""
    print()
    print("=" * 70)
    print("💰 UPDATE CASH ACCOUNTS")
    print("=" * 70)
    print()

    accounts = config['cash_accounts']

    for key, acct in accounts.items():
        current = acct['balance']
        acct_type = acct['type']

        print(f"\n{acct['name']} ({acct_type}): ${current:,.2f}")
        response = input("  New balance (or press Enter to skip): ").strip()

        if response:
            try:
                new_balance = float(response)
                acct['balance'] = new_balance
                print(f"  ✅ Updated to ${new_balance:,.2f}")
            except ValueError:
                print("  ❌ Invalid amount, skipping")

def view_summary(config):
    """Display current financial summary"""
    print()
    print("=" * 70)
    print("📊 CURRENT FINANCIAL SUMMARY")
    print("=" * 70)
    print()

    metadata = config['metadata']

    print("Last Updated:", metadata.get('last_updated', 'Never'))
    print()

    print(f"Monthly Recurring Expenses: ${metadata.get('total_recurring_expenses', 0):,.2f}")
    print(f"Total Debt:                 ${metadata.get('total_debt', 0):,.2f}")
    print(f"Liquid Cash:                ${metadata.get('total_liquid_cash', 0):,.2f}")
    print()

    # Breakdown
    print("Recurring Expense Breakdown:")
    for section_name, items in config['recurring_expenses'].items():
        total = sum(item['amount'] for item in items.values() if item.get('status') != 'cancelled')
        print(f"  {section_name.replace('_', ' ').title():30s} ${total:>10,.2f}")

    print()
    print("Debt Breakdown:")
    for section_name, items in config['debt_balances'].items():
        total = sum(item['balance'] for item in items.values())
        if total > 0:
            print(f"  {section_name.title():30s} ${total:>10,.2f}")

    cc_total = sum(card['balance'] for card in config['credit_cards'].values())
    print(f"  {'Credit Cards':30s} ${cc_total:>10,.2f}")

    print()

def main():
    """Main updater loop"""

    if not CONFIG_FILE.exists():
        print(f"❌ Config file not found: {CONFIG_FILE}")
        print("   Run build_all.py first to initialize")
        return 1

    config = load_config()

    while True:
        display_menu()
        choice = input("Enter choice (1-6): ").strip()

        if choice == '1':
            update_recurring_expenses(config)
            save_config(config)
            print("\n✅ Recurring expenses updated")

        elif choice == '2':
            update_debt_balances(config)
            save_config(config)
            print("\n✅ Debt balances updated")

        elif choice == '3':
            update_credit_cards(config)
            save_config(config)
            print("\n✅ Credit card balances updated")

        elif choice == '4':
            update_cash_accounts(config)
            save_config(config)
            print("\n✅ Cash accounts updated")

        elif choice == '5':
            view_summary(config)

        elif choice == '6':
            print("\n✅ Exiting")
            break

        else:
            print("\n❌ Invalid choice")

    print()
    print("=" * 70)
    print("💾 Changes saved to:", CONFIG_FILE)
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Run: python build_all.py")
    print("  2. Open: financial_hub.html")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
