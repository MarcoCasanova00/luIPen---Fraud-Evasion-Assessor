from functools import wraps
from flask import request, jsonify, current_app
from .logging_safety import log_security_event
import time


def csrf_protect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            if current_app.config.get('WTF_CSRF_ENABLED', True):
                csrf_token = request.headers.get('X-CSRF-Token')
                session_token = current_app.config.get('CSRF_TOKEN', 'default-token')
                if not csrf_token:
                    log_security_event(
                        current_app.logger,
                        'CSRF_MISSING_TOKEN',
                        'CSRF token missing in request'
                    )
                    return jsonify({'error': 'CSRF token required', 'code': 'CSRF_MISSING'}), 403
        return f(*args, **kwargs)
    return decorated_function


def validate_origin():
    origin = request.headers.get('Origin') or request.headers.get('Referer')
    allowed_origins = current_app.config.get('ALLOWED_ORIGINS', ['http://localhost:5000', 'http://127.0.0.1:5000'])
    if origin:
        from urllib.parse import urlparse
        parsed = urlparse(origin)
        host = f"{parsed.scheme}://{parsed.netloc}"
        if host not in allowed_origins and current_app.config.get('ENV') == 'production':
            log_security_event(
                current_app.logger,
                'ORIGIN_CHECK_FAILED',
                f'Request from untrusted origin: {origin}'
            )
            return False
    return True