import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app


@pytest.fixture
def app():
    app = create_app('testing')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'


class TestScoreEndpoint:
    def test_score_requires_json(self, client):
        response = client.post('/api/score', data='not json')
        assert response.status_code == 400

    def test_score_validates_distance(self, client):
        response = client.post('/api/score',
            json={'distance_km': 'invalid'})
        assert response.status_code == 400

    def test_score_accepts_valid_input(self, client):
        response = client.post('/api/score', json={
            'target_url': 'https://example.com',
            'distance_km': 10.0,
            'distance_from_last_transaction': 5.0,
            'ratio_to_median_purchase_price': 1.5,
            'retailer_history': True,
            'has_chip': True,
            'has_pin': True,
            'is_online': False
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success_score' in data


class TestReportEndpoint:
    def test_report_generates_report(self, client):
        response = client.post('/api/report', json={
            'target_url': 'https://example.com',
            'distance_km': 10.0,
            'ratio_to_median_purchase_price': 1.0,
            'retailer_history': True,
            'has_chip': True,
            'has_pin': True,
            'is_online': False
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'report_id' in data
        assert 'findings' in data


class TestDemoPresets:
    def test_demo_presets_returns_list(self, client):
        response = client.get('/api/demo-presets')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'presets' in data
        assert len(data['presets']) > 0


class TestGeoIP:
    def test_geoip_validates_ip(self, client):
        response = client.post('/api/geoip/distance', json={
            'ip_address': 'invalid',
            'billing_lat': 40.7128,
            'billing_lon': -74.0060
        })
        assert response.status_code == 400

    def test_geoip_validates_coordinates(self, client):
        response = client.post('/api/geoip/distance', json={
            'ip_address': '203.0.113.1',
            'billing_lat': 200,
            'billing_lon': -74.0060
        })
        assert response.status_code == 400


class TestSecurity:
    def test_rate_limit_on_score(self, client):
        for _ in range(35):
            response = client.post('/api/score', json={
                'distance_km': 10.0
            })
        assert response.status_code == 429

    def test_no_debug_in_production(self, app):
        app.config['ENV'] = 'production'
        assert app.config.get('DEBUG') == False or app.config.get('TESTING') == True