from flask import Blueprint, request, jsonify, current_app
from ..services.scoring import score_transaction, calculate_risk_factors
from ..services.geoip import calculate_distance, init_geoip, is_valid_ip
from ..services.reporting import generate_vulnerability_report
from ..services.validation import validate_score_request, validate_geoip_request, sanitize_input
from ..security.rate_limit import api_rate_limit
from ..security.logging_safety import log_security_event

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/score', methods=['POST'])
@api_rate_limit(limit=30, window=60)
def score():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json', 'code': 'INVALID_CONTENT_TYPE'}), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid JSON body', 'code': 'INVALID_JSON'}), 400

    is_valid, errors = validate_score_request(data)
    if not is_valid:
        log_security_event(
            current_app.logger,
            'VALIDATION_FAILED',
            f'Score validation errors: {errors}',
            request
        )
        return jsonify({'error': 'Validation failed', 'details': errors, 'code': 'VALIDATION_ERROR'}), 400

    data['target_url'] = sanitize_input(data.get('target_url', ''))

    try:
        result = score_transaction(data)
        log_security_event(
            current_app.logger,
            'SCORE_CALCULATED',
            f'Success score: {result["success_score"]:.4f}',
            request
        )
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Scoring error: {e}")
        return jsonify({'error': 'Internal scoring error', 'code': 'INTERNAL_ERROR'}), 500


@api_bp.route('/report', methods=['POST'])
@api_rate_limit(limit=20, window=120)
def report():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json', 'code': 'INVALID_CONTENT_TYPE'}), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid JSON body', 'code': 'INVALID_JSON'}), 400

    data['target_url'] = sanitize_input(data.get('target_url', ''))

    try:
        score_result = score_transaction(data)
        report = generate_vulnerability_report(data, score_result)
        log_security_event(
            current_app.logger,
            'REPORT_GENERATED',
            f'Report ID: {report["report_id"]}',
            request
        )
        return jsonify(report)
    except Exception as e:
        current_app.logger.error(f"Report generation error: {e}")
        return jsonify({'error': 'Internal report error', 'code': 'INTERNAL_ERROR'}), 500


@api_bp.route('/geoip/distance', methods=['POST'])
@api_rate_limit(limit=30, window=60)
def geoip_distance():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json', 'code': 'INVALID_CONTENT_TYPE'}), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid JSON body', 'code': 'INVALID_JSON'}), 400

    is_valid, errors = validate_geoip_request(data)
    if not is_valid:
        return jsonify({'error': 'Validation failed', 'details': errors, 'code': 'VALIDATION_ERROR'}), 400

    try:
        result = calculate_distance(data['ip_address'], float(data['billing_lat']), float(data['billing_lon']))
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"GeoIP error: {e}")
        return jsonify({'error': 'GeoIP calculation failed', 'code': 'GEOIP_ERROR'}), 500


@api_bp.route('/demo-presets', methods=['GET'])
def demo_presets():
    import json
    import os
    presets_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'shared', 'rules', 'demo_profiles.json'
    )
    try:
        with open(presets_path, 'r') as f:
            presets = json.load(f)
        return jsonify({'presets': presets})
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({
            'presets': [
                {
                    'name': 'low_risk',
                    'description': 'Low risk transaction configuration',
                    'data': {
                        'distance_km': 5.0,
                        'distance_from_last_transaction': 2.0,
                        'ratio_to_median_purchase_price': 1.0,
                        'retailer_history': True,
                        'has_chip': True,
                        'has_pin': True,
                        'is_online': False
                    }
                },
                {
                    'name': 'medium_risk',
                    'description': 'Medium risk transaction configuration',
                    'data': {
                        'distance_km': 30.0,
                        'distance_from_last_transaction': 15.0,
                        'ratio_to_median_purchase_price': 2.5,
                        'retailer_history': True,
                        'has_chip': False,
                        'has_pin': True,
                        'is_online': True
                    }
                },
                {
                    'name': 'high_risk',
                    'description': 'High risk transaction configuration',
                    'data': {
                        'distance_km': 150.0,
                        'distance_from_last_transaction': 80.0,
                        'ratio_to_median_purchase_price': 6.0,
                        'retailer_history': False,
                        'has_chip': False,
                        'has_pin': False,
                        'is_online': True
                    }
                }
            ]
        })


@api_bp.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'code': 'RATE_LIMITED',
        'message': str(e)
    }), 429


@api_bp.errorhandler(500)
def internal_error_handler(e):
    return jsonify({
        'error': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500