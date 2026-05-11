import os
from flask import Flask, jsonify
from .config import config_by_name
from .routes.web import web_bp
from .routes.api import api_bp
from .services.geoip import init_geoip
from .security.headers import init_security_headers
from .security.logging_safety import setup_secure_logging


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    setup_secure_logging(app)
    init_security_headers(app)

    try:
        geoip_path = app.config.get('GEOIP_DB_PATH')
        if geoip_path and os.path.exists(geoip_path):
            init_geoip(geoip_path)
            app.logger.info("GeoIP service initialized")
    except Exception as e:
        app.logger.warning(f"GeoIP initialization skipped: {e}")

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'code': 'BAD_REQUEST'}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found', 'code': 'NOT_FOUND'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'error': 'Method not allowed', 'code': 'METHOD_NOT_ALLOWED'}), 405

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'error': 'Too many requests', 'code': 'RATE_LIMITED'}), 429

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal error: {e}")
        return jsonify({'error': 'Internal server error', 'code': 'INTERNAL_ERROR'}), 500

    @app.before_request
    def log_request_info():
        app.logger.debug(f"{request.method} {request.path}")

    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response

    return app