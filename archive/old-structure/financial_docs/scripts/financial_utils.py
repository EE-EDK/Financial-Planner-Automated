#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial Utilities Module
Shared functions and constants used across all financial analysis scripts.

This module eliminates code duplication by providing:
- Common path definitions
- Unified data loading (config, budget, transactions)
- Shared calculation functions
- Standard formatting utilities
"""

import csv
import json
import sys
import io
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Any, Tuple

# ============================================================================
# PATH CONSTANTS
# ============================================================================

# Base directories (relative to this file)
SCRIPTS_DIR = Path(__file__).parent
BASE_DIR = SCRIPTS_DIR.parent  # financial_docs/
PROJECT_ROOT = BASE_DIR.parent  # Finances-Kunz/
ARCHIVE_DIR = BASE_DIR / "Archive"
PROCESSED_DIR = ARCHIVE_DIR / "processed"
EXPORTS_DIR = ARCHIVE_DIR / "raw" / "exports"
REPORTS_DIR = ARCHIVE_DIR / "reports"
SNAPSHOTS_DIR = ARCHIVE_DIR / "snapshots"

# Data files
CONFIG_FILE = PROCESSED_DIR / "financial_config.json"
BUDGET_FILE = PROCESSED_DIR / "budget.json"
GOALS_FILE = PROCESSED_DIR / "financial_goals.json"
TRANSACTIONS_FILE = EXPORTS_DIR / "AllTransactions.csv"
DASHBOARD_DATA_FILE = PROCESSED_DIR / "dashboard_data.json"

# ============================================================================
# ENCODING SETUP
# ============================================================================

def setup_windows_encoding():
    """
    Fix Windows console encoding for emoji and UTF-8 support.
    Call this at the start of any script that uses emojis or special characters.
    """
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_config() -> Dict[str, Any]:
    """
    Load financial configuration from JSON.

    Returns:
        Dictionary containing cash_accounts, debt_balances, recurring_expenses, etc.
        Returns empty dict if file doesn't exist.
    """
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_budget() -> Dict[str, Any]:
    """
    Load budget configuration from JSON.

    Returns:
        Dictionary containing category_budgets and fixed_expenses.
        Returns empty dict if file doesn't exist.
    """
    if BUDGET_FILE.exists():
        with open(BUDGET_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_goals() -> Dict[str, Any]:
    """
    Load financial goals from JSON.

    Returns:
        Dictionary containing goal definitions.
        Returns empty dict if file doesn't exist.
    """
    if GOALS_FILE.exists():
        with open(GOALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_transactions(
    months: Optional[int] = None,
    include_ignored: bool = False,
    include_cc_payments: bool = False
) -> List[Dict[str, Any]]:
    """
    Load transactions from CSV file with optional filtering.

    Args:
        months: If specified, only load transactions from last N months
        include_ignored: Include transactions marked as ignored
        include_cc_payments: Include credit card payment transactions

    Returns:
        List of transaction dictionaries with standardized fields:
        - date (str): YYYY-MM-DD format
        - name (str): Transaction name
        - amount (float): Transaction amount
        - category (str): Category
        - account (str): Account name
        - description (str): Description
    """
    transactions = []

    if not TRANSACTIONS_FILE.exists():
        return transactions

    # Calculate cutoff date if months specified
    cutoff_date = None
    if months is not None:
        now = datetime.now()
        cutoff_date = now.replace(month=now.month - months if now.month > months else 12 + now.month - months)

    with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Skip ignored transactions if requested
            if not include_ignored and row.get('Ignored From'):
                continue

            # Skip credit card payments if requested
            if not include_cc_payments and row.get('Category') == 'Credit Card Payment':
                continue

            # Parse date and check if within range
            date_str = row.get('Date', '')
            trans_date = None

            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d']:
                try:
                    trans_date = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue

            # Skip if date parsing failed
            if trans_date is None:
                continue

            # Skip if outside date range
            if cutoff_date and trans_date < cutoff_date:
                continue

            # Parse amount
            try:
                amount = float(row.get('Amount', 0))
            except (ValueError, TypeError):
                amount = 0.0

            # Add standardized transaction
            transactions.append({
                'date': trans_date.strftime('%Y-%m-%d'),
                'name': row.get('Custom Name') or row.get('Name', ''),
                'amount': amount,
                'category': row.get('Category', ''),
                'account': row.get('Account Name', ''),
                'description': row.get('Description', '')
            })

    return transactions

# ============================================================================
# DATA MANIPULATION FUNCTIONS
# ============================================================================

def flatten_dict(nested_dict: Dict, value_key: str = 'balance') -> Dict[str, float]:
    """
    Flatten nested dictionary structure to simple key-value pairs.

    Handles nested category structures like:
    {
        'checking': {'usaa': {'balance': 1000}, 'chase': {'balance': 500}},
        'savings': {'balance': 2000}
    }

    Args:
        nested_dict: Dictionary to flatten
        value_key: Key to extract from nested objects (default: 'balance')

    Returns:
        Flat dictionary with string keys and float values
    """
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


def calculate_financial_snapshot(config: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate current financial snapshot from config.

    Args:
        config: Financial configuration dictionary

    Returns:
        Dictionary with:
        - liquid_cash: Total liquid cash
        - total_debt: Total debt across all accounts
        - net_worth: Cash - debt (simplified)
        - monthly_recurring: Total recurring expenses
        - monthly_income: Total income (if available)
        - consumer_debt: Credit cards + car loans (excluding mortgages)
        - mortgage_debt: Mortgage balances only
    """
    # Calculate liquid cash
    cash_accounts = config.get('cash_accounts', {})
    liquid_cash = 0
    for acct in cash_accounts.values():
        if isinstance(acct, dict):
            if acct.get('liquid', True):  # Default to liquid if not specified
                liquid_cash += acct.get('balance', 0)
        else:
            liquid_cash += acct

    # Calculate total debt and categorize
    total_debt = 0
    mortgage_debt = 0
    consumer_debt = 0

    # Add debt balances
    for section_name, section in config.get('debt_balances', {}).items():
        for item in section.values():
            if isinstance(item, dict):
                balance = item.get('balance', 0)
                total_debt += balance

                # Categorize debt
                if 'mortgage' in section_name.lower() or item.get('type') == 'mortgage':
                    mortgage_debt += balance
                else:
                    consumer_debt += balance
            else:
                total_debt += item
                consumer_debt += item

    # Add credit card debt
    for card in config.get('credit_cards', {}).values():
        if isinstance(card, dict):
            balance = card.get('balance', 0)
            total_debt += balance
            consumer_debt += balance
        else:
            total_debt += card
            consumer_debt += card

    # Calculate net worth (simplified: cash - debt)
    net_worth = liquid_cash - total_debt

    # Calculate monthly recurring expenses
    monthly_recurring = 0
    for section in config.get('recurring_expenses', {}).values():
        for item in section.values():
            if isinstance(item, dict):
                if item.get('status') != 'cancelled':
                    monthly_recurring += item.get('amount', 0)
            else:
                monthly_recurring += item

    # Get monthly income if available
    monthly_income = config.get('income', {}).get('monthly_total', 0)

    return {
        'liquid_cash': round(liquid_cash, 2),
        'total_debt': round(total_debt, 2),
        'net_worth': round(net_worth, 2),
        'monthly_recurring': round(monthly_recurring, 2),
        'monthly_income': round(monthly_income, 2),
        'consumer_debt': round(consumer_debt, 2),
        'mortgage_debt': round(mortgage_debt, 2)
    }


def categorize_spending(transactions: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Categorize spending from transactions.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Dictionary mapping category names to total spending
    """
    spending = defaultdict(float)

    for trans in transactions:
        category = trans.get('category', 'Unknown')
        amount = trans.get('amount', 0)

        # Only count expenses (positive amounts or explicitly expenses)
        if amount > 0:
            spending[category] += amount
        elif amount < 0:
            # Negative amounts are income/refunds - skip
            continue

    return dict(spending)

# ============================================================================
# FORMATTING FUNCTIONS
# ============================================================================

def format_currency(amount: float, show_sign: bool = False) -> str:
    """
    Format amount as currency string.

    Args:
        amount: Dollar amount
        show_sign: Include + for positive amounts

    Returns:
        Formatted string like "$1,234.56" or "+$1,234.56"
    """
    sign = ""
    if show_sign and amount > 0:
        sign = "+"
    elif amount < 0:
        sign = "-"
        amount = abs(amount)

    return f"{sign}${amount:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage string.

    Args:
        value: Decimal value (0.25 = 25%)
        decimals: Number of decimal places

    Returns:
        Formatted string like "25.0%"
    """
    return f"{value * 100:.{decimals}f}%"

# ============================================================================
# DATE UTILITIES
# ============================================================================

def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string in various formats.

    Args:
        date_str: Date string

    Returns:
        datetime object or None if parsing fails
    """
    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%Y/%m/%d']:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def get_month_key(date: datetime = None) -> str:
    """
    Get month key in YYYY-MM format.

    Args:
        date: datetime object (defaults to now)

    Returns:
        String like "2025-11"
    """
    if date is None:
        date = datetime.now()
    return date.strftime('%Y-%m')

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate financial config structure.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required sections
    required_sections = ['cash_accounts', 'debt_balances', 'recurring_expenses']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    # Check metadata
    if 'metadata' not in config:
        errors.append("Missing metadata section")
    elif 'last_updated' not in config['metadata']:
        errors.append("Missing metadata.last_updated")

    return (len(errors) == 0, errors)


def ensure_directories():
    """
    Ensure all required directories exist.
    Creates them if they don't exist.
    """
    for directory in [ARCHIVE_DIR, PROCESSED_DIR, EXPORTS_DIR, REPORTS_DIR, SNAPSHOTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# SAVING FUNCTIONS
# ============================================================================

def save_json(data: Dict[str, Any], filepath: Path, update_metadata: bool = True):
    """
    Save data to JSON file with optional metadata update.

    Args:
        data: Dictionary to save
        filepath: Path to save to
        update_metadata: If True, updates metadata.last_updated timestamp
    """
    if update_metadata and 'metadata' in data:
        data['metadata']['last_updated'] = datetime.now().isoformat()

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_report(content: str, filename: str):
    """
    Save markdown report to reports directory.

    Args:
        content: Markdown content
        filename: Filename (e.g., "BUDGET_VS_ACTUAL.md")
    """
    filepath = REPORTS_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# ============================================================================
# MODULE INFO
# ============================================================================

__all__ = [
    # Constants
    'BASE_DIR', 'ARCHIVE_DIR', 'PROCESSED_DIR', 'EXPORTS_DIR', 'REPORTS_DIR',
    'CONFIG_FILE', 'BUDGET_FILE', 'GOALS_FILE', 'TRANSACTIONS_FILE',

    # Setup
    'setup_windows_encoding', 'ensure_directories',

    # Loading
    'load_config', 'load_budget', 'load_goals', 'load_transactions',

    # Calculations
    'calculate_financial_snapshot', 'categorize_spending', 'flatten_dict',

    # Formatting
    'format_currency', 'format_percentage',

    # Dates
    'parse_date', 'get_month_key',

    # Validation
    'validate_config',

    # Saving
    'save_json', 'save_report'
]
