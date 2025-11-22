#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures for financial scripts tests.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_config():
    """Sample financial configuration data."""
    return {
        "cash_accounts": {
            "checking": {"name": "Main Checking", "balance": 5000, "liquid": True},
            "savings": {"name": "Savings", "balance": 10000, "liquid": True}
        },
        "credit_cards": {
            "card1": {"name": "Visa", "balance": 5000, "apr": 22.99},
            "card2": {"name": "Mastercard", "balance": 3000, "apr": 18.99}
        },
        "debt_balances": {
            "loans": {
                "car": {"name": "Car Loan", "balance": 15000}
            }
        },
        "recurring_expenses": {
            "housing": {
                "rent": {"name": "Rent", "amount": 2000, "status": "active"},
                "utilities": {"name": "Utilities", "amount": 200, "status": "active"}
            },
            "subscriptions": {
                "netflix": {"name": "Netflix", "amount": 15, "status": "active"},
                "cancelled": {"name": "Old Sub", "amount": 10, "status": "cancelled"}
            }
        }
    }


@pytest.fixture
def sample_budget():
    """Sample budget data."""
    return {
        "monthly_income": {"earnings": 10000},
        "category_budgets": {
            "Dining & Drinks": 300,
            "Groceries": 800,
            "Shopping": 200,
            "Entertainment & Rec.": 100,
            "Auto & Transport": 400
        },
        "fixed_expenses": {
            "Bills & Utilities": 500
        },
        "metadata": {
            "total_spending_budget": 2300,
            "last_updated": "2025-11-21"
        }
    }


@pytest.fixture
def sample_transactions():
    """Sample transaction data as list of dicts."""
    today = datetime.now()
    return [
        {
            "Date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "Name": "Grocery Store",
            "Amount": "150.00",
            "Category": "Groceries",
            "Account Name": "Checking"
        },
        {
            "Date": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
            "Name": "Restaurant",
            "Amount": "75.50",
            "Category": "Dining & Drinks",
            "Account Name": "Credit Card"
        },
        {
            "Date": (today - timedelta(days=15)).strftime("%Y-%m-%d"),
            "Name": "Amazon",
            "Amount": "200.00",
            "Category": "Shopping",
            "Account Name": "Credit Card"
        },
        {
            "Date": (today - timedelta(days=20)).strftime("%Y-%m-%d"),
            "Name": "Gas Station",
            "Amount": "50.00",
            "Category": "Auto & Transport",
            "Account Name": "Checking"
        },
        {
            "Date": (today - timedelta(days=45)).strftime("%Y-%m-%d"),
            "Name": "Old Purchase",
            "Amount": "100.00",
            "Category": "Shopping",
            "Account Name": "Checking"
        }
    ]


@pytest.fixture
def sample_transactions_csv(temp_dir, sample_transactions):
    """Create a sample CSV file with transactions."""
    import csv
    csv_path = temp_dir / "AllTransactions.csv"

    fieldnames = ["Date", "Name", "Amount", "Category", "Account Name",
                  "Custom Name", "Description", "Ignored From"]

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for txn in sample_transactions:
            row = {k: txn.get(k, '') for k in fieldnames}
            writer.writerow(row)

    return csv_path


@pytest.fixture
def mock_archive_structure(temp_dir, sample_config, sample_budget):
    """Create a mock Archive directory structure with sample data."""
    archive = temp_dir / "Archive"
    (archive / "raw" / "exports").mkdir(parents=True)
    (archive / "processed").mkdir(parents=True)
    (archive / "reports").mkdir(parents=True)
    (archive / "snapshots").mkdir(parents=True)

    # Write config
    config_path = archive / "processed" / "financial_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f)

    # Write budget
    budget_path = archive / "processed" / "budget.json"
    with open(budget_path, 'w', encoding='utf-8') as f:
        json.dump(sample_budget, f)

    return archive
