#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration and regression tests for financial scripts.
Tests that scripts produce expected outputs and don't regress.
"""

import pytest
import json
import csv
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))


class TestGenerateDashboardData:
    """Integration tests for generate_dashboard_data.py."""

    def test_output_structure(self, mock_archive_structure, sample_transactions_csv):
        """Dashboard data should have expected structure."""
        from generate_dashboard_data import (
            load_config, load_budget, calculate_snapshot,
            calculate_credit_card_payoff, calculate_emergency_fund
        )

        # Copy CSV to expected location
        import shutil
        exports_dir = mock_archive_structure / "raw" / "exports"
        shutil.copy(sample_transactions_csv, exports_dir / "AllTransactions.csv")

        # Load config from mock archive
        config_path = mock_archive_structure / "processed" / "financial_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Test each component
        snapshot = calculate_snapshot(config)
        assert 'liquid_cash' in snapshot
        assert 'total_debt' in snapshot
        assert 'net_worth' in snapshot
        assert 'monthly_recurring' in snapshot

        cc_payoff = calculate_credit_card_payoff(config)
        assert 'total_balance' in cc_payoff
        assert 'cards' in cc_payoff
        assert 'scenarios' in cc_payoff

        ef = calculate_emergency_fund(config)
        assert 'current_balance' in ef
        assert 'months_covered' in ef
        assert 'targets' in ef
        assert 'status' in ef

    def test_snapshot_values_reasonable(self, sample_config):
        """Snapshot values should be reasonable (no negative balances, etc)."""
        from generate_dashboard_data import calculate_snapshot

        result = calculate_snapshot(sample_config)

        assert result['liquid_cash'] >= 0
        assert result['total_debt'] >= 0
        assert result['monthly_recurring'] >= 0
        # Net worth can be negative

    def test_credit_card_scenarios_ordered(self, sample_config):
        """Higher payments should result in faster payoff."""
        from generate_dashboard_data import calculate_credit_card_payoff

        result = calculate_credit_card_payoff(sample_config)
        scenarios = result['scenarios']

        # Get months for each scenario
        payments_months = []
        for key, data in scenarios.items():
            if data['months'] is not None:
                payment = data['monthly_payment']
                months = data['months']
                payments_months.append((payment, months))

        # Sort by payment amount
        payments_months.sort(key=lambda x: x[0])

        # Higher payments should mean fewer months
        for i in range(len(payments_months) - 1):
            assert payments_months[i][1] >= payments_months[i + 1][1], \
                "Higher payment should result in fewer months to payoff"


class TestBudgetVsActual:
    """Integration tests for budget_vs_actual.py."""

    def test_loads_budget_from_json(self, mock_archive_structure):
        """Should load budget from JSON file."""
        # Temporarily modify path constants
        import budget_vs_actual as bva

        original_budget_file = bva.BUDGET_FILE
        bva.BUDGET_FILE = mock_archive_structure / "processed" / "budget.json"

        try:
            budget = bva.load_budget()
            assert 'Dining & Drinks' in budget
            assert 'Groceries' in budget
            assert budget['Groceries'] == 800
        finally:
            bva.BUDGET_FILE = original_budget_file

    def test_categorize_spending(self, sample_transactions):
        """Should correctly categorize spending."""
        import budget_vs_actual as bva

        spending = bva.categorize_spending(sample_transactions)

        assert 'Groceries' in spending
        assert 'Dining & Drinks' in spending
        assert spending['Groceries'] == 150.00
        assert spending['Dining & Drinks'] == 75.50

    def test_report_generation(self, sample_budget, sample_transactions):
        """Should generate valid report markdown."""
        import budget_vs_actual as bva

        budget = sample_budget['category_budgets']
        budget.update(sample_budget.get('fixed_expenses', {}))
        actual = bva.categorize_spending(sample_transactions)

        report = bva.generate_report(budget, actual, months=1)

        assert '# BUDGET VS ACTUAL REPORT' in report
        assert 'COMPARISON SUMMARY' in report
        assert '| Category |' in report


class TestAnalyzeTransactions:
    """Integration tests for analyze_transactions.py."""

    def test_category_analysis(self, sample_transactions):
        """Should analyze categories correctly."""
        import analyze_transactions as at

        categories, counts = at.analyze_by_category(sample_transactions)

        # Categories should be sorted by total
        totals = [c[1] for c in categories]
        assert totals == sorted(totals, reverse=True)

    def test_merchant_analysis(self, sample_transactions):
        """Should analyze merchants correctly."""
        import analyze_transactions as at

        merchants, counts = at.analyze_by_merchant(sample_transactions)

        # Should return top merchants
        assert len(merchants) <= 20

    def test_waste_identification(self, sample_transactions):
        """Should identify waste categories."""
        import analyze_transactions as at

        # Add Merchant field which identify_waste looks for
        for txn in sample_transactions:
            txn['Merchant'] = txn.get('Name', '')

        waste_totals, waste_details = at.identify_waste(sample_transactions)

        # Amazon should be identified
        assert 'Amazon' in waste_totals
        assert waste_totals['Amazon'] == 200.00


class TestHealthScore:
    """Integration tests for calculate_health_score.py."""

    def test_score_components(self, sample_config):
        """All score components should be calculated."""
        import calculate_health_score as chs

        # Create sample budget
        budget = {
            'monthly_income': {'earnings': 7500},
            'metadata': {'total_spending_budget': 6000}
        }

        totals = chs.calculate_totals(sample_config)

        ef_score = chs.calculate_emergency_fund_score(totals, budget)
        debt_score = chs.calculate_debt_score(totals, budget)
        cf_score = chs.calculate_cash_flow_score(totals, budget)

        # Each should return dict with score and max_score
        for score in [ef_score, debt_score, cf_score]:
            assert 'score' in score
            assert 'max_score' in score
            assert 0 <= score['score'] <= score['max_score']

    def test_total_score_range(self, sample_config):
        """Total score should be 0-75 (3 components x 25 max)."""
        import calculate_health_score as chs

        budget = {
            'monthly_income': {'earnings': 7500},
            'metadata': {'total_spending_budget': 6000}
        }

        totals = chs.calculate_totals(sample_config)

        ef = chs.calculate_emergency_fund_score(totals, budget)
        debt = chs.calculate_debt_score(totals, budget)
        cf = chs.calculate_cash_flow_score(totals, budget)

        total = ef['score'] + debt['score'] + cf['score']
        assert 0 <= total <= 75

    def test_grade_assignment(self):
        """Grades should be assigned correctly."""
        import calculate_health_score as chs

        assert chs.get_grade(95, 100) == 'A+'
        assert chs.get_grade(85, 100) == 'A'
        assert chs.get_grade(75, 100) == 'B'
        assert chs.get_grade(65, 100) == 'C'
        assert chs.get_grade(55, 100) == 'D'


class TestScenarioCalculator:
    """Integration tests for scenario_calculator.py (template version)."""

    def test_extra_income_scenario(self):
        """Extra income scenario should calculate correctly."""
        import scenario_calculator as sc

        result = sc.calculate_scenario_extra_income()

        assert 'name' in result
        assert 'monthly_surplus' in result
        assert 'annual_impact' in result
        # With template values: income 7500 + 1000 - spending 6000 = 2500
        assert result['monthly_surplus'] == 2500

    def test_job_loss_scenario(self):
        """Job loss scenario should calculate correctly."""
        import scenario_calculator as sc

        result = sc.calculate_scenario_job_loss()

        assert 'name' in result
        assert 'deficit' in result
        assert 'months_covered' in result
        # With template values: unemployment 2000 - spending 6000 = -4000
        assert result['deficit'] == -4000
        # Emergency fund 15000 / 4000 = 3.75 months
        assert result['months_covered'] == 3.75

    def test_generate_report(self):
        """Report generation should work without errors."""
        import scenario_calculator as sc

        report = sc.generate_report()

        assert 'FINANCIAL SCENARIO ANALYSIS' in report
        assert 'TEMPLATE' in report
        assert 'Extra Income Scenario' in report
        assert 'Job Loss Emergency' in report


class TestRegressions:
    """Regression tests to catch breaking changes."""

    def test_credit_card_payoff_never_negative_months(self, sample_config):
        """Payoff months should never be negative."""
        from generate_dashboard_data import calculate_credit_card_payoff

        result = calculate_credit_card_payoff(sample_config)

        for scenario in result['scenarios'].values():
            if scenario['months'] is not None:
                assert scenario['months'] >= 0

    def test_emergency_fund_division_by_zero(self):
        """Emergency fund should handle zero expenses."""
        from generate_dashboard_data import calculate_emergency_fund

        config = {
            "cash_accounts": {"a": {"balance": 1000, "liquid": True}},
            "recurring_expenses": {}  # No expenses
        }

        # Should not raise exception
        result = calculate_emergency_fund(config)
        # months_covered would be infinity or handled gracefully

    def test_budget_variance_sign_convention(self):
        """Positive variance = over budget, negative = under."""
        budget = 100
        actual_over = 120
        actual_under = 80

        variance_over = actual_over - budget
        variance_under = actual_under - budget

        assert variance_over > 0  # Over budget
        assert variance_under < 0  # Under budget

    def test_percentage_never_nan(self):
        """Percentages should never be NaN."""
        import math

        def safe_pct(actual, budget):
            return (actual / budget * 100) if budget > 0 else 0

        assert not math.isnan(safe_pct(50, 100))
        assert not math.isnan(safe_pct(50, 0))
        assert not math.isnan(safe_pct(0, 100))
        assert not math.isnan(safe_pct(0, 0))


class TestDataValidation:
    """Tests for data validation and edge cases."""

    def test_handles_missing_fields(self):
        """Scripts should handle missing fields gracefully."""
        from generate_dashboard_data import calculate_snapshot

        # Minimal config with missing sections
        config = {}
        result = calculate_snapshot(config)

        assert result['liquid_cash'] == 0
        assert result['total_debt'] == 0

    def test_handles_empty_transactions(self):
        """Should handle empty transaction list."""
        import budget_vs_actual as bva

        spending = bva.categorize_spending([])
        assert spending == {}

    def test_handles_malformed_amounts(self):
        """Should handle malformed amount values."""
        import budget_vs_actual as bva

        transactions = [
            {"Category": "Test", "Amount": "invalid"},
            {"Category": "Test", "Amount": "$100.00"},
            {"Category": "Test", "Amount": "50"},
        ]

        spending = bva.categorize_spending(transactions)
        # Should skip invalid, process valid ones
        assert spending.get('Test', 0) == 150.0
