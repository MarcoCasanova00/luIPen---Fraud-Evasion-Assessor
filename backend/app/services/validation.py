import re
from typing import Dict, Tuple, List, Any
from urllib.parse import urlparse


class ValidationError(Exception):
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field
        self.message = message


def validate_score_request(data: Dict) -> Tuple[bool, List[str]]:
    errors = []

    target_url = data.get('target_url')
    if target_url:
        if not isinstance(target_url, str):
            errors.append('target_url must be a string')
        elif not _is_valid_url(target_url):
            errors.append('target_url must be a valid URL')

    distance_km = data.get('distance_km', data.get('distance_from_home'))
    if distance_km is not None:
        try:
            dist = float(distance_km)
            if dist < 0 or dist > 20000:
                errors.append('distance_km must be between 0 and 20000')
        except (TypeError, ValueError):
            errors.append('distance_km must be a valid number')

    distance_last = data.get('distance_from_last_transaction')
    if distance_last is not None:
        try:
            dist = float(distance_last)
            if dist < 0 or dist > 20000:
                errors.append('distance_from_last_transaction must be between 0 and 20000')
        except (TypeError, ValueError):
            errors.append('distance_from_last_transaction must be a valid number')

    ratio = data.get('ratio_to_median_purchase_price')
    if ratio is not None:
        try:
            r = float(ratio)
            if r < 0 or r > 100:
                errors.append('ratio_to_median_purchase_price must be between 0 and 100')
        except (TypeError, ValueError):
            errors.append('ratio_to_median_purchase_price must be a valid number')

    for field in ['retailer_history', 'has_chip', 'has_pin', 'is_online',
                 'repeat_retailer', 'used_chip', 'used_pin_number', 'online_order']:
        value = data.get(field)
        if value is not None:
            if not isinstance(value, (bool, int, float, str)):
                errors.append(f'{field} must be a boolean, number, or string')

    return len(errors) == 0, errors


def validate_report_request(data: Dict) -> Tuple[bool, List[str]]:
    errors = []

    if 'target_url' not in data and 'target_url' not in str(data):
        pass

    if not isinstance(data, dict):
        errors.append('Request body must be a JSON object')

    return len(errors) == 0, errors


def validate_geoip_request(data: Dict) -> Tuple[bool, List[str]]:
    errors = []

    ip_address = data.get('ip_address')
    if not ip_address:
        errors.append('ip_address is required')
    elif not isinstance(ip_address, str):
        errors.append('ip_address must be a string')
    elif not _is_valid_ipv4(ip_address):
        errors.append('ip_address must be a valid IPv4 address')

    billing_lat = data.get('billing_lat')
    if billing_lat is not None:
        try:
            lat = float(billing_lat)
            if lat < -90 or lat > 90:
                errors.append('billing_lat must be between -90 and 90')
        except (TypeError, ValueError):
            errors.append('billing_lat must be a valid number')

    billing_lon = data.get('billing_lon')
    if billing_lon is not None:
        try:
            lon = float(billing_lon)
            if lon < -180 or lon > 180:
                errors.append('billing_lon must be between -180 and 180')
        except (TypeError, ValueError):
            errors.append('billing_lon must be a valid number')

    return len(errors) == 0, errors


def sanitize_input(value: str) -> str:
    if not isinstance(value, str):
        return value
    return re.sub(r'[<>"\';]', '', value)


def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


def _is_valid_ipv4(ip: str) -> bool:
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)