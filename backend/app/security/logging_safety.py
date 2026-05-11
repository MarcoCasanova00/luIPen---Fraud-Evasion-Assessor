import os
import logging
import re
from datetime import datetime


class SecurityFormatter(logging.Formatter):
    SENSITIVE_PATTERNS = [
        (re.compile(r'(password|passwd|pwd|secret|key|token|api_key|bearer)["\s:=]+[^\s,}]+', re.I), '[REDACTED]'),
        (re.compile(r'(ip_address|source_ip|ip)["\s:=]+[^\s,}]+', re.I), lambda m: f'"{m.group(1)}"="[MASKED_IP]"'),
        (re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'), '[MASKED_IP]'),
    ]

    def format(self, record):
        message = super().format(record)
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            if callable(replacement):
                message = pattern.sub(replacement, message)
            else:
                message = pattern.sub(replacement, message)
        return message


def setup_secure_logging(app):
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    formatter = SecurityFormatter(log_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(console_handler)

    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('flask_limiter').setLevel(logging.WARNING)


def log_security_event(logger, event_type, details, request=None):
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
    }
    if request:
        log_data['request_path'] = request.path
        log_data['request_method'] = request.method
        log_data['remote_addr'] = request.remote_addr
        log_data['user_agent'] = request.headers.get('User-Agent', 'Unknown')
    logger.warning(f"SECURITY_EVENT: {log_data}")