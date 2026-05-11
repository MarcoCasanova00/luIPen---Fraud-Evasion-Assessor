from flask import jsonify, request
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class SimpleRateLimiter:
    def __init__(self):
        self.requests = {}

    def is_rate_limited(self, key, limit, window):
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key] = [t for t in self.requests[key] if now - t < window]
        if len(self.requests[key]) >= limit:
            return True
        self.requests[key].append(now)
        return False


limiter = SimpleRateLimiter()


def rate_limit(limit=30, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in client_ip:
                client_ip = client_ip.split(',')[0]

            key = f"{f.__name__}:{client_ip}"
            if limiter.is_rate_limited(key, limit, window):
                logger.warning(f"Rate limit exceeded for {client_ip} on {f.__name__}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'code': 'RATE_LIMITED',
                    'retry_after': window
                }), 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def api_rate_limit(limit=20, window=60):
    return rate_limit(limit, window)