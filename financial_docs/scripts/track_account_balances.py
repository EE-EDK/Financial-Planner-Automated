#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Account Balance History Tracker
Tracks account balances over time

Reads: financial_config.json
Appends: Archive/data/account_balance_history.json

This allows tracking how balances change month-over-month:
- Cash accounts
- Credit cards
- Debt balances
- Net worth
"""

import json
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32' and sys.stdout is not None:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "Archive" / "processed"
CONFIG_FILE = PROCESSED_DIR / "financial_config.json"
HISTORY_FILE = PROCESSED_DIR / "account_balance_history.json"

def load_config():
    """Load financial configuration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_history():
    """Load balance history"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'created': datetime.now().isoformat(),
        'cash_accounts': {},
        'credit_cards': {},
        'debt_balances': {},
        'totals': []
    }

def record_balance_snapshot(config, history):
    """Record current balances to history"""

    timestamp = datetime.now().isoformat()
    date_key = datetime.now().strftime('%Y-%m-%d')

    # Track cash accounts
    for account_id, account in config.get('cash_accounts', {}).items():
        if account_id not in history['cash_accounts']:
            history['cash_accounts'][account_id] = {
                'name': account['name'],
                'type': account['type'],
                'history': []
            }

        history['cash_accounts'][account_id]['history'].append({
            'date': date_key,
            'balance': account['balance']
        })

    # Track credit cards
    for card_id, card in config.get('credit_cards', {}).items():
        if card_id not in history['credit_cards']:
            history['credit_cards'][card_id] = {
                'name': card['name'],
                'history': []
            }

        history['credit_cards'][card_id]['history'].append({
            'date': date_key,
            'balance': card['balance']
        })

    # Track debt balances
    for debt_type, debts in config.get('debt_balances', {}).items():
        for debt_id, debt in debts.items():
            full_id = f"{debt_type}.{debt_id}"

            if full_id not in history['debt_balances']:
                history['debt_balances'][full_id] = {
                    'name': debt['name'],
                    'type': debt_type,
                    'history': []
                }

            history['debt_balances'][full_id]['history'].append({
                'date': date_key,
                'balance': debt['balance']
            })

    # Calculate totals
    total_cash = sum(acct['balance'] for acct in config.get('cash_accounts', {}).values())

    total_cc_debt = sum(card['balance'] for card in config.get('credit_cards', {}).values())

    total_other_debt = 0
    for debt_section in config.get('debt_balances', {}).values():
        for debt in debt_section.values():
            total_other_debt += debt['balance']

    total_debt = total_cc_debt + total_other_debt
    net_worth = total_cash - total_debt

    history['totals'].append({
        'date': date_key,
        'total_cash': round(total_cash, 2),
        'total_credit_card_debt': round(total_cc_debt, 2),
        'total_other_debt': round(total_other_debt, 2),
        'total_debt': round(total_debt, 2),
        'net_worth': round(net_worth, 2)
    })

    history['last_updated'] = timestamp

    return history

def get_recent_changes(history, days=30):
    """Get changes over the last N days"""

    if not history['totals']:
        return None

    # Get latest and earliest in window
    recent_totals = history['totals'][-2:]  # Last 2 entries

    if len(recent_totals) < 2:
        return None

    prev = recent_totals[0]
    curr = recent_totals[1]

    changes = {
        'period': f"{prev['date']} to {curr['date']}",
        'cash_change': round(curr['total_cash'] - prev['total_cash'], 2),
        'debt_change': round(curr['total_debt'] - prev['total_debt'], 2),
        'net_worth_change': round(curr['net_worth'] - prev['net_worth'], 2),
        'previous': prev,
        'current': curr
    }

    return changes

def save_history(history):
    """Save balance history"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def main():
    """Track account balances"""

    print()
    print("=" * 70)
    print("📈 ACCOUNT BALANCE HISTORY TRACKER")
    print("=" * 70)
    print()

    # Load data
    print("Loading data...")
    config = load_config()
    history = load_history()
    print("  ✅ Configuration loaded")
    print("  ✅ History loaded")
    print()

    # Record snapshot
    print("Recording balance snapshot...")
    history = record_balance_snapshot(config, history)
    print("  ✅ Balances recorded")
    print()

    # Save
    save_history(history)
    print(f"✅ History saved to {HISTORY_FILE}")
    print()

    # Show changes
    changes = get_recent_changes(history)
    if changes:
        print("📊 Recent Changes:")
        print(f"  Period: {changes['period']}")
        print()
        print(f"  Cash Change:       ${changes['cash_change']:>12,.2f}")
        print(f"  Debt Change:       ${changes['debt_change']:>12,.2f}")
        print(f"  Net Worth Change:  ${changes['net_worth_change']:>12,.2f}")
        print()

    # Summary
    print("📈 History Summary:")
    print(f"  Total snapshots:   {len(history['totals'])}")
    print(f"  Cash accounts:     {len(history['cash_accounts'])}")
    print(f"  Credit cards:      {len(history['credit_cards'])}")
    print(f"  Debt accounts:     {len(history['debt_balances'])}")
    print()

    print("=" * 70)
    print("✅ COMPLETE")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
