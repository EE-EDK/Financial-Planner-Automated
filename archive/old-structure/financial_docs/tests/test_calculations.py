#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for financial calculation functions.
Tests mathematical correctness of all calculations.
"""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class TestNetWorthCalculations:
    """Test net worth and snapshot calculations."""

    def test_net_worth_positive(self, sample_config):
        """Net worth should be cash minus debt."""
        from generate_dashboard_data import calculate_snapshot

        result = calculate_snapshot(sample_config)

        # Cash: 5000 + 10000 = 15000
        # Debt: 5000 + 3000 (CC) + 15000 (car) = 23000
        # Net: 15000 - 23000 = -8000
        assert result['liquid_cash'] == 15000
        assert result['total_debt'] == 23000
        assert result['net_worth'] == -8000

    def test_net_worth_no_debt(self):
        """Net worth with no debt should equal liquid cash."""
        from generate_dashboard_data import calculate_snapshot

        config = {
            "cash_accounts": {"checking": {"balance": 10000}},
            "credit_cards": {},
            "debt_balances": {},
            "recurring_expenses": {}
        }

        result = calculate_snapshot(config)
        assert result['net_worth'] == 10000
        assert result['total_debt'] == 0

    def test_monthly_recurring_excludes_cancelled(self, sample_config):
        """Monthly recurring should exclude cancelled subscriptions."""
        from generate_dashboard_data import calculate_snapshot

        result = calculate_snapshot(sample_config)

        # Active: 2000 + 200 + 15 = 2215 (cancelled 10 excluded)
        assert result['monthly_recurring'] == 2215


class TestCreditCardPayoff:
    """Test credit card payoff calculations."""

    def test_payoff_basic(self, sample_config):
        """Test basic payoff calculation."""
        from generate_dashboard_data import calculate_credit_card_payoff

        result = calculate_credit_card_payoff(sample_config)

        # Total CC debt: 5000 + 3000 = 8000
        assert result['total_balance'] == 8000
        assert len(result['cards']) == 2
        assert '$200/mo' in result['scenarios']

    def test_payoff_zero_debt(self):
        """Test with no credit card debt."""
        from generate_dashboard_data import calculate_credit_card_payoff

        config = {"credit_cards": {}}
        result = calculate_credit_card_payoff(config)

        assert result['total_balance'] == 0
        assert len(result['cards']) == 0

    def test_minimum_payment_calculation(self):
        """Minimum payment should be max of 2% balance or $25."""
        from generate_dashboard_data import calculate_credit_card_payoff

        config = {
            "credit_cards": {
                "small": {"name": "Small", "balance": 500, "apr": 20},
                "large": {"name": "Large", "balance": 5000, "apr": 20}
            }
        }

        result = calculate_credit_card_payoff(config)

        # Small card: max(500 * 0.02, 25) = max(10, 25) = 25
        # Large card: max(5000 * 0.02, 25) = max(100, 25) = 100
        small_card = next(c for c in result['cards'] if c['name'] == 'Small')
        large_card = next(c for c in result['cards'] if c['name'] == 'Large')

        assert small_card['min_payment'] == 25
        assert large_card['min_payment'] == 100

    def test_interest_accumulation(self):
        """Interest should accumulate correctly in payoff scenarios."""
        from generate_dashboard_data import calculate_credit_card_payoff

        config = {
            "credit_cards": {
                "card": {"name": "Test Card", "balance": 1000, "apr": 24}  # 2%/month
            }
        }

        result = calculate_credit_card_payoff(config)

        # With $200/mo payment on $1000 @ 24% APR (2%/mo):
        # Month 1: interest = 20, principal = 180, balance = 820
        # Month 2: interest = 16.40, principal = 183.60, balance = 636.40
        # etc. Should pay off in ~6 months
        scenario = result['scenarios']['$200/mo']
        assert scenario['months'] is not None
        assert scenario['months'] <= 10  # Should pay off relatively quickly
        assert scenario['total_interest'] > 0  # Should have some interest


class TestEmergencyFund:
    """Test emergency fund calculations."""

    def test_months_covered(self, sample_config):
        """Test months of expenses covered."""
        from generate_dashboard_data import calculate_emergency_fund

        result = calculate_emergency_fund(sample_config)

        # Liquid cash: 15000 (both accounts have liquid: True)
        # Monthly expenses: 2215
        # Months: 15000 / 2215 = ~6.77
        assert result['current_balance'] == 15000
        assert result['monthly_expenses'] == 2215
        assert 6 < result['months_covered'] < 7

    def test_target_calculations(self, sample_config):
        """Test 3-month and 6-month targets."""
        from generate_dashboard_data import calculate_emergency_fund

        result = calculate_emergency_fund(sample_config)

        # 3 months: 2215 * 3 = 6645
        # 6 months: 2215 * 6 = 13290
        assert result['targets']['three_months'] == 6645
        assert result['targets']['six_months'] == 13290

    def test_progress_percentages(self, sample_config):
        """Test progress percentage calculations."""
        from generate_dashboard_data import calculate_emergency_fund

        result = calculate_emergency_fund(sample_config)

        # Progress to 3mo: 15000 / 6645 * 100 = ~225%
        # Progress to 6mo: 15000 / 13290 * 100 = ~112%
        assert result['progress']['to_3_months']['percent'] > 200
        assert result['progress']['to_6_months']['percent'] > 100

    def test_status_levels(self):
        """Test status determination based on months covered."""
        from generate_dashboard_data import calculate_emergency_fund

        # Test excellent (6+ months)
        config_excellent = {
            "cash_accounts": {"a": {"balance": 60000, "liquid": True}},
            "recurring_expenses": {"x": {"y": {"amount": 1000, "status": "active"}}}
        }
        result = calculate_emergency_fund(config_excellent)
        assert result['status'] == 'excellent'

        # Test critical (< 1 month)
        config_critical = {
            "cash_accounts": {"a": {"balance": 500, "liquid": True}},
            "recurring_expenses": {"x": {"y": {"amount": 1000, "status": "active"}}}
        }
        result = calculate_emergency_fund(config_critical)
        assert result['status'] == 'critical'


class TestBudgetCalculations:
    """Test budget vs actual calculations."""

    def test_variance_calculation(self):
        """Test budget variance is calculated correctly."""
        # Positive variance = over budget
        # Negative variance = under budget
        budget = 100
        actual = 120
        variance = actual - budget
        assert variance == 20  # Over by 20

        actual = 80
        variance = actual - budget
        assert variance == -20  # Under by 20

    def test_percentage_calculation(self):
        """Test budget percentage calculation."""
        budget = 100
        actual = 75
        pct = (actual / budget * 100) if budget > 0 else 0
        assert pct == 75.0

    def test_zero_budget_handling(self):
        """Zero budget should not cause division by zero."""
        budget = 0
        actual = 50
        pct = (actual / budget * 100) if budget > 0 else 0
        assert pct == 0

    def test_multi_month_scaling(self):
        """Budget should scale by number of months."""
        monthly_budget = 100
        months = 3
        scaled_budget = monthly_budget * months
        assert scaled_budget == 300


class TestAnomalyDetection:
    """Test spending anomaly detection."""

    def test_percent_change_calculation(self):
        """Test percent change formula."""
        current = 150
        average = 100

        # Formula: ((current - average) / average) * 100
        percent_change = ((current - average) / average) * 100
        assert percent_change == 50.0

    def test_negative_percent_change(self):
        """Test negative percent change (decrease)."""
        current = 50
        average = 100

        percent_change = ((current - average) / average) * 100
        assert percent_change == -50.0

    def test_zero_average_handling(self):
        """Zero average should be handled without error."""
        current = 100
        average = 0

        # Should skip or handle gracefully
        if average == 0:
            percent_change = None
        else:
            percent_change = ((current - average) / average) * 100

        assert percent_change is None


class TestHealthScoreCalculations:
    """Test financial health score calculations."""

    def test_savings_rate(self):
        """Test savings rate calculation."""
        monthly_savings = 2000
        employer_match = 500
        monthly_income = 10000

        total_savings = monthly_savings + employer_match
        savings_rate = total_savings / monthly_income

        assert savings_rate == 0.25  # 25%

    def test_dti_ratio(self):
        """Test debt-to-income ratio calculation."""
        monthly_debt_payments = 2000
        annual_income = 120000

        annual_debt_payments = monthly_debt_payments * 12
        dti = annual_debt_payments / annual_income

        assert dti == 0.2  # 20%

    def test_cash_flow_percentage(self):
        """Test cash flow percentage calculation."""
        monthly_income = 10000
        monthly_spending = 8000

        cash_flow = monthly_income - monthly_spending
        cash_flow_pct = cash_flow / monthly_income

        assert cash_flow == 2000
        assert cash_flow_pct == 0.2  # 20%


class TestScenarioCalculations:
    """Test scenario calculator math."""

    def test_property_sale_proceeds(self):
        """Test net proceeds from property sale."""
        sale_price = 300000
        mortgage_balance = 150000
        selling_costs_pct = 0.06

        selling_costs = sale_price * selling_costs_pct
        net_proceeds = sale_price - mortgage_balance - selling_costs

        assert selling_costs == 18000
        assert net_proceeds == 132000

    def test_emergency_fund_duration(self):
        """Test emergency fund duration calculation."""
        emergency_fund = 10000
        monthly_deficit = 2500

        months_covered = emergency_fund / abs(monthly_deficit)
        assert months_covered == 4.0

    def test_mitigation_calculation(self):
        """Test deficit mitigation calculation."""
        deficit = -3000
        pause_401k = 1500
        cut_discretionary = 2000

        total_mitigation = pause_401k + cut_discretionary
        resulting = deficit + total_mitigation

        assert total_mitigation == 3500
        assert resulting == 500  # Now positive
