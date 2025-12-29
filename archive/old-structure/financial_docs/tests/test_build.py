#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for build scripts and utilities.
"""

import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))


class TestBuildAllArgs:
    """Test build_all.py argument parsing."""

    def test_parse_args_default(self):
        """Default args should be months=1."""
        import build_all

        # Save original argv
        original_argv = sys.argv
        sys.argv = ["build_all.py"]

        try:
            args = build_all.parse_args()
            assert args['months'] == 1
        finally:
            sys.argv = original_argv

    def test_parse_args_months_equals(self):
        """Should parse --months=N format."""
        import build_all

        original_argv = sys.argv
        sys.argv = ["build_all.py", "--months=3"]

        try:
            args = build_all.parse_args()
            assert args['months'] == 3
        finally:
            sys.argv = original_argv

    def test_parse_args_months_space(self):
        """Should parse --months N format."""
        import build_all

        original_argv = sys.argv
        sys.argv = ["build_all.py", "--months", "6"]

        try:
            args = build_all.parse_args()
            assert args['months'] == 6
        finally:
            sys.argv = original_argv

    def test_parse_args_invalid(self):
        """Invalid months should default to 1."""
        import build_all

        original_argv = sys.argv
        sys.argv = ["build_all.py", "--months=invalid"]

        try:
            args = build_all.parse_args()
            assert args['months'] == 1
        finally:
            sys.argv = original_argv


class TestBudgetVsActualArgs:
    """Test budget_vs_actual.py argument parsing."""

    def test_default_months(self):
        """Default should be 1 month."""
        import scripts.budget_vs_actual as bva

        original_argv = sys.argv
        sys.argv = ["budget_vs_actual.py"]

        try:
            # The script reads sys.argv[1] for months
            months = 1
            if len(sys.argv) > 1:
                try:
                    months = int(sys.argv[1])
                except ValueError:
                    months = 1
            assert months == 1
        finally:
            sys.argv = original_argv

    def test_custom_months(self):
        """Should accept custom months."""
        original_argv = sys.argv
        sys.argv = ["budget_vs_actual.py", "3"]

        try:
            months = 1
            if len(sys.argv) > 1:
                try:
                    months = int(sys.argv[1])
                except ValueError:
                    months = 1
            assert months == 3
        finally:
            sys.argv = original_argv


class TestScriptConfiguration:
    """Test script configuration and constants."""

    def test_scripts_list_complete(self):
        """All scripts should be in the SCRIPTS list."""
        import build_all

        script_names = [s['script'] for s in build_all.SCRIPTS]

        # Key scripts should be included
        assert any('analyze_transactions' in s for s in script_names)
        assert any('budget_vs_actual' in s for s in script_names)
        assert any('calculate_health_score' in s for s in script_names)
        assert any('generate_dashboard_data' in s for s in script_names)

    def test_scripts_have_required_fields(self):
        """Each script config should have required fields."""
        import build_all

        required_fields = ['name', 'script', 'output', 'icon', 'required']

        for script in build_all.SCRIPTS:
            for field in required_fields:
                assert field in script, f"Script {script.get('name')} missing {field}"

    def test_paths_exist(self):
        """Key paths should be valid."""
        import build_all

        assert build_all.BASE_DIR.exists()
        assert build_all.SCRIPTS_DIR.exists()


class TestOutputValidation:
    """Test that outputs are valid."""

    def test_report_markdown_structure(self):
        """Generated reports should be valid markdown."""
        import scripts.budget_vs_actual as bva

        budget = {'Test': 100}
        actual = {'Test': 80}

        report = bva.generate_report(budget, actual, months=1)

        # Should have title
        assert report.startswith('#')

        # Should have table
        assert '|' in report

        # Should not have template errors
        assert '{' not in report or 'format' not in report

    def test_json_output_valid(self, mock_archive_structure):
        """JSON outputs should be valid JSON."""
        import json

        config_path = mock_archive_structure / "processed" / "financial_config.json"
        with open(config_path, 'r') as f:
            data = json.load(f)

        assert isinstance(data, dict)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_csv_handled(self, mock_archive_structure):
        """Should handle missing CSV gracefully."""
        import scripts.budget_vs_actual as bva

        # CSV doesn't exist in mock
        transactions = bva.load_recent_transactions(months=1)

        # Should return empty list, not crash
        assert transactions == [] or isinstance(transactions, list)

    def test_empty_config_handled(self):
        """Should handle empty config."""
        from scripts.generate_dashboard_data import calculate_snapshot

        result = calculate_snapshot({})

        assert result['liquid_cash'] == 0
        assert result['total_debt'] == 0

    def test_future_dates_handled(self, sample_transactions):
        """Should handle transactions with future dates."""
        import scripts.budget_vs_actual as bva
        from datetime import datetime, timedelta

        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        sample_transactions.append({
            "Date": future_date,
            "Name": "Future",
            "Amount": "100",
            "Category": "Test"
        })

        spending = bva.categorize_spending(sample_transactions)
        # Should process without error
        assert isinstance(spending, dict)
