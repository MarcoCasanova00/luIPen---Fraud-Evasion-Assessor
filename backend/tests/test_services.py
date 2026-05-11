import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.scoring import score_transaction, calculate_risk_factors, normalize_boolean, normalize_numeric
from app.services.validation import validate_score_request, validate_geoip_request


class TestScoringService:
    def test_normalize_boolean_true(self):
        assert normalize_boolean(True, False) == 1
        assert normalize_boolean('true', False) == 1
        assert normalize_boolean('1', False) == 1
        assert normalize_boolean(1, False) == 1

    def test_normalize_boolean_false(self):
        assert normalize_boolean(False, True) == 0
        assert normalize_boolean('false', True) == 0
        assert normalize_boolean('0', True) == 0
        assert normalize_boolean(0, True) == 0

    def test_normalize_numeric(self):
        assert normalize_numeric(10.5, 0.0) == 10.5
        assert normalize_numeric('15', 0.0) == 15.0
        assert normalize_numeric(None, 5.0) == 5.0

    def test_score_transaction_returns_score(self):
        data = {
            'distance_km': 10.0,
            'distance_from_last_transaction': 5.0,
            'ratio_to_median_purchase_price': 1.0,
            'retailer_history': True,
            'has_chip': True,
            'has_pin': True,
            'is_online': False
        }
        result = score_transaction(data)
        assert 'success_score' in result
        assert 0 <= result['success_score'] <= 1
        assert 'fraud_probability' in result

    def test_score_high_risk_low_score(self):
        data = {
            'distance_km': 5000,
            'distance_from_last_transaction': 3000,
            'ratio_to_median_purchase_price': 15,
            'retailer_history': False,
            'has_chip': False,
            'has_pin': False,
            'is_online': True
        }
        result = score_transaction(data)
        assert result['success_score'] < 0.5

    def test_score_low_risk_high_score(self):
        data = {
            'distance_km': 5,
            'distance_from_last_transaction': 1,
            'ratio_to_median_purchase_price': 0.8,
            'retailer_history': True,
            'has_chip': True,
            'has_pin': True,
            'is_online': False
        }
        result = score_transaction(data)
        assert result['success_score'] > 0.7


class TestValidationService:
    def test_validate_score_request_valid(self):
        data = {
            'target_url': 'https://example.com',
            'distance_km': 10.0,
            'ratio_to_median_purchase_price': 1.5,
            'retailer_history': True
        }
        is_valid, errors = validate_score_request(data)
        assert is_valid
        assert len(errors) == 0

    def test_validate_score_request_invalid_url(self):
        data = {
            'target_url': 'not-a-url',
            'distance_km': 10.0
        }
        is_valid, errors = validate_score_request(data)
        assert not is_valid
        assert any('URL' in e for e in errors)

    def test_validate_score_request_invalid_distance(self):
        data = {
            'distance_km': -100
        }
        is_valid, errors = validate_score_request(data)
        assert not is_valid

    def test_validate_geoip_request_valid(self):
        data = {
            'ip_address': '203.0.113.1',
            'billing_lat': 40.7128,
            'billing_lon': -74.0060
        }
        is_valid, errors = validate_geoip_request(data)
        assert is_valid

    def test_validate_geoip_request_invalid_ip(self):
        data = {
            'ip_address': '999.999.999.999',
            'billing_lat': 40.7128,
            'billing_lon': -74.0060
        }
        is_valid, errors = validate_geoip_request(data)
        assert not is_valid

    def test_validate_geoip_request_invalid_lat(self):
        data = {
            'ip_address': '203.0.113.1',
            'billing_lat': 200,
            'billing_lon': -74.0060
        }
        is_valid, errors = validate_geoip_request(data)
        assert not is_valid


class TestRiskFactors:
    def test_calculate_risk_factors_high_distance(self):
        data = {'distance_km': 100}
        factors = calculate_risk_factors(data)
        assert len(factors) > 0
        assert any(f['factor'] == 'geoip_distance' for f in factors)

    def test_calculate_risk_factors_velocity_anomaly(self):
        data = {'distance_from_last_transaction': 50}
        factors = calculate_risk_factors(data)
        assert any(f['factor'] == 'velocity_anomaly' for f in factors)

    def test_calculate_risk_factors_no_chip(self):
        data = {'has_chip': False}
        factors = calculate_risk_factors(data)
        assert len(factors) > 0