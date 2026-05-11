from flask_talisman import Talisman
from datetime import timedelta


def get_security_headers():
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'self';"
        ),
    }


def init_security_headers(app):
    csp = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
        'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data:",
        'connect-src': "'self'",
        'frame-ancestors': "'self'",
    }

    Talisman(
        app,
        force_https=False,
        strict_transport_security=False,
        frame_options='SAMEORIGIN',
        frame_options_allow_from=None,
        content_security_policy=csp,
        content_security_policy_nonce_in=None,
        referrer_policy='strict-origin-when-cross-origin',
        permissions_policy='geolocation=(), microphone=(), camera=()',
        feature_policy='geolocation \'none\'; microphone \'none\'; camera \'none\'',
    )


def set_cache_control(response, max_age=3600):
    response.cache_control.public = True
    response.cache_control.max_age = max_age
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response