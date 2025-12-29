#!/usr/bin/env python3
"""
Quick Update CLI - Fast command-line tool for updating financial data
Usage:
    python3 quick_update.py cash USAA_Checking 3450
    python3 quick_update.py debt Venture_Card 17200
    python3 quick_update.py recurring Netflix 19.99
    python3 quick_update.py recurring Hulu 0 --cancelled
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

class QuickUpdate:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.processed_path = self.base_path / "Archive" / "processed"
        self.config_file = self.processed_path / "financial_config.json"

        # Load config
        self.load_config()

    def load_config(self):
        """Load financial config"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.create_default_config()

    def create_default_config(self):
        """Create default config structure"""
        return {
            "cash_accounts": {},
            "debt_balances": {},
            "recurring_expenses": {},
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

    def save_config(self):
        """Save config to file"""
        self.config['metadata']['last_updated'] = datetime.now().isoformat()
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

        print(f"✓ Configuration saved to {self.config_file}")

    def flatten_nested_dict(self, nested_dict, value_key='balance'):
        """Flatten nested dictionary structure"""
        flat = {}
        for category, items in nested_dict.items():
            if isinstance(items, dict):
                # Check if this is a nested category structure
                has_nested_items = any(isinstance(v, dict) for v in items.values())

                if has_nested_items:
                    # This is a category with nested items
                    for item_key, item_val in items.items():
                        if isinstance(item_val, dict):
                            if value_key in item_val:
                                flat[item_key] = float(item_val[value_key])
                            elif 'amount' in item_val:
                                flat[item_key] = float(item_val['amount'])
                else:
                    # This item itself has the value
                    if value_key in items:
                        flat[category] = float(items[value_key])
                    elif 'amount' in items:
                        flat[category] = float(items['amount'])
            elif isinstance(items, (int, float)):
                flat[category] = float(items)

        return flat

    def update_cash(self, account, amount):
        """Update cash account balance"""
        cash_accounts = self.config.get('cash_accounts', {})

        # Find and update the account
        old_value = 0
        account_key = account.lower().replace(' ', '_').replace('-', '_')

        if account_key in cash_accounts:
            if isinstance(cash_accounts[account_key], dict):
                old_value = cash_accounts[account_key].get('balance', 0)
                cash_accounts[account_key]['balance'] = amount
            else:
                old_value = cash_accounts[account_key]
                cash_accounts[account_key] = amount
        else:
            # Create new account
            cash_accounts[account_key] = {
                'name': account,
                'balance': amount,
                'type': 'checking',
                'liquid': True
            }

        print(f"✓ Updated cash account: {account}")
        print(f"  Old balance: ${old_value:,.2f}")
        print(f"  New balance: ${amount:,.2f}")
        print(f"  Change: ${amount - old_value:+,.2f}")

        self.save_config()

    def update_debt(self, account, amount):
        """Update debt balance"""
        # Search through all debt categories
        old_value = 0
        found = False
        account_key = account.lower().replace(' ', '_').replace('-', '_')

        debt_balances = self.config.get('debt_balances', {})

        # Search existing categories
        for category in debt_balances.values():
            if isinstance(category, dict) and account_key in category:
                if isinstance(category[account_key], dict):
                    old_value = category[account_key].get('balance', 0)
                    category[account_key]['balance'] = amount
                else:
                    old_value = category[account_key]
                    category[account_key] = amount
                found = True
                break

        # Also check credit cards
        credit_cards = self.config.get('credit_cards', {})
        if not found and account_key in credit_cards:
            if isinstance(credit_cards[account_key], dict):
                old_value = credit_cards[account_key].get('balance', 0)
                credit_cards[account_key]['balance'] = amount
            else:
                old_value = credit_cards[account_key]
                credit_cards[account_key] = amount
            found = True

        if not found:
            # Create in personal category
            if 'personal' not in debt_balances:
                debt_balances['personal'] = {}
            debt_balances['personal'][account_key] = {
                'name': account,
                'balance': amount,
                'interest_rate': 0.0,
                'type': 'personal_loan'
            }

        print(f"✓ Updated debt account: {account}")
        print(f"  Old balance: ${old_value:,.2f}")
        print(f"  New balance: ${amount:,.2f}")
        print(f"  Change: ${amount - old_value:+,.2f}")

        if amount < old_value and old_value > 0:
            paid_down = old_value - amount
            pct = (paid_down / old_value) * 100
            print(f"  🎉 Paid down ${paid_down:,.2f} ({pct:.1f}%)")

        self.save_config()

    def update_recurring(self, expense, amount, cancelled=False):
        """Update recurring expense"""
        # Search through all recurring categories
        old_value = 0
        found = False
        expense_key = expense.lower().replace(' ', '_').replace('-', '_')

        recurring = self.config.get('recurring_expenses', {})

        # Search existing categories
        for category in recurring.values():
            if isinstance(category, dict) and expense_key in category:
                if isinstance(category[expense_key], dict):
                    old_value = category[expense_key].get('amount', 0)

                    if cancelled or amount == 0:
                        del category[expense_key]
                        print(f"✓ Cancelled recurring expense: {expense}")
                        print(f"  Old amount: ${old_value:,.2f}/month")
                        print(f"  Monthly savings: ${old_value:,.2f}")
                    else:
                        category[expense_key]['amount'] = amount
                        print(f"✓ Updated recurring expense: {expense}")
                        print(f"  Old amount: ${old_value:,.2f}/month")
                        print(f"  New amount: ${amount:,.2f}/month")
                        print(f"  Change: ${amount - old_value:+,.2f}/month")
                else:
                    old_value = category[expense_key]
                    if cancelled or amount == 0:
                        del category[expense_key]
                        print(f"✓ Cancelled recurring expense: {expense}")
                        print(f"  Old amount: ${old_value:,.2f}/month")
                        print(f"  Monthly savings: ${old_value:,.2f}")
                    else:
                        category[expense_key] = amount
                        print(f"✓ Updated recurring expense: {expense}")
                        print(f"  Old amount: ${old_value:,.2f}/month")
                        print(f"  New amount: ${amount:,.2f}/month")
                        print(f"  Change: ${amount - old_value:+,.2f}/month")
                found = True
                break

        if not found and not cancelled and amount > 0:
            # Create in subscriptions category
            if 'subscriptions' not in recurring:
                recurring['subscriptions'] = {}
            recurring['subscriptions'][expense_key] = {
                'name': expense,
                'amount': amount,
                'category': 'Software & Tech',
                'frequency': 'monthly'
            }
            print(f"✓ Added recurring expense: {expense}")
            print(f"  Amount: ${amount:,.2f}/month")

        self.save_config()

    def show_summary(self):
        """Show summary of current finances"""
        print("\n" + "=" * 60)
        print("FINANCIAL SUMMARY")
        print("=" * 60)

        # Cash accounts
        cash_accounts = self.config.get('cash_accounts', {})
        cash_flat = self.flatten_nested_dict(cash_accounts, 'balance')
        total_cash = sum(cash_flat.values())

        print(f"\n💵 Cash Accounts (Total: ${total_cash:,.2f}):")
        for account, balance in sorted(cash_flat.items()):
            print(f"  {account:.<40} ${balance:>12,.2f}")

        # Debt balances (including credit cards)
        debt_balances = self.config.get('debt_balances', {})
        debt_flat = self.flatten_nested_dict(debt_balances, 'balance')

        credit_cards = self.config.get('credit_cards', {})
        credit_flat = self.flatten_nested_dict(credit_cards, 'balance')

        all_debt = {**debt_flat, **credit_flat}
        total_debt = sum(all_debt.values())

        print(f"\n💳 Debt Balances (Total: ${total_debt:,.2f}):")
        for account, balance in sorted(all_debt.items()):
            if balance > 0:  # Only show non-zero debts
                print(f"  {account:.<40} ${balance:>12,.2f}")

        # Recurring expenses
        recurring = self.config.get('recurring_expenses', {})
        recurring_flat = self.flatten_nested_dict(recurring, 'amount')
        total_recurring = sum(recurring_flat.values())

        print(f"\n🔄 Recurring Expenses (Total: ${total_recurring:,.2f}/month):")
        for expense, amount in sorted(recurring_flat.items()):
            if amount > 0:  # Only show active expenses
                print(f"  {expense:.<40} ${amount:>12,.2f}/mo")

        # Summary
        net_worth = total_cash - total_debt

        print("\n" + "=" * 60)
        print(f"Net Worth: ${net_worth:,.2f}")
        print(f"Liquid/Debt Ratio: {(total_cash/total_debt*100) if total_debt > 0 else 0:.1f}%")

        if total_debt > 0:
            months_coverage = total_cash / (total_recurring if total_recurring > 0 else 1)
            print(f"Emergency Fund Coverage: {months_coverage:.1f} months")

        print("=" * 60 + "\n")

        # Last updated
        last_updated = self.config.get('metadata', {}).get('last_updated', 'Unknown')
        print(f"Last updated: {last_updated}\n")

    def list_accounts(self, account_type=None):
        """List all accounts of a specific type"""
        if account_type == 'cash' or account_type is None:
            print("\n💵 Cash Accounts:")
            cash_flat = self.flatten_nested_dict(self.config.get('cash_accounts', {}), 'balance')
            for account in sorted(cash_flat.keys()):
                print(f"  - {account}")

        if account_type == 'debt' or account_type is None:
            print("\n💳 Debt Accounts:")
            debt_flat = self.flatten_nested_dict(self.config.get('debt_balances', {}), 'balance')
            credit_flat = self.flatten_nested_dict(self.config.get('credit_cards', {}), 'balance')
            all_debt = {**debt_flat, **credit_flat}
            for account in sorted(all_debt.keys()):
                print(f"  - {account}")

        if account_type == 'recurring' or account_type is None:
            print("\n🔄 Recurring Expenses:")
            recurring_flat = self.flatten_nested_dict(self.config.get('recurring_expenses', {}), 'amount')
            for expense in sorted(recurring_flat.keys()):
                print(f"  - {expense}")

        print()


def main():
    parser = argparse.ArgumentParser(
        description='Quick financial data updater',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s cash USAA_Checking 3450
  %(prog)s debt Venture_Card 17200
  %(prog)s recurring Netflix 19.99
  %(prog)s recurring Hulu 0 --cancelled
  %(prog)s summary
  %(prog)s list cash
        """
    )

    parser.add_argument('type', choices=['cash', 'debt', 'recurring', 'summary', 'list'],
                       help='Type of update or action')
    parser.add_argument('account', nargs='?', help='Account or expense name')
    parser.add_argument('amount', nargs='?', type=float, help='New amount')
    parser.add_argument('--cancelled', action='store_true', help='Mark recurring expense as cancelled')

    args = parser.parse_args()

    updater = QuickUpdate()

    if args.type == 'summary':
        updater.show_summary()

    elif args.type == 'list':
        updater.list_accounts(args.account)

    elif args.type == 'cash':
        if not args.account or args.amount is None:
            parser.error("cash update requires account name and amount")
        updater.update_cash(args.account, args.amount)

    elif args.type == 'debt':
        if not args.account or args.amount is None:
            parser.error("debt update requires account name and amount")
        updater.update_debt(args.account, args.amount)

    elif args.type == 'recurring':
        if not args.account:
            parser.error("recurring update requires expense name")
        if args.amount is None and not args.cancelled:
            parser.error("recurring update requires amount or --cancelled flag")

        amount = args.amount if args.amount is not None else 0
        updater.update_recurring(args.account, amount, args.cancelled)


if __name__ == "__main__":
    main()
