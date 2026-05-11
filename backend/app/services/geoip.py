import math
import geoip2.database
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

reader = None


def init_geoip(db_path: str) -> bool:
    global reader
    if not db_path or not hasattr(db_path, '__str__'):
        logger.warning("GeoIP database path not configured")
        return False

    try:
        if isinstance(db_path, str) and db_path.strip():
            reader = geoip2.database.Reader(db_path)
            logger.info(f"GeoIP database loaded from {db_path}")
            return True
    except FileNotFoundError:
        logger.warning(f"GeoIP database not found at {db_path}")
    except Exception as e:
        logger.error(f"Failed to load GeoIP database: {e}")

    reader = None
    return False


def is_valid_ip(ip: str) -> bool:
    if not ip:
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def resolve_ip_location(ip_address: str) -> Optional[Dict]:
    if reader is None:
        return None

    try:
        response = reader.city(ip_address)
        return {
            'city': response.city.name or 'Unknown',
            'country': response.country.name or 'Unknown',
            'latitude': response.location.latitude,
            'longitude': response.location.longitude
        }
    except geoip2.errors.AddressNotFoundError:
        logger.warning(f"IP address {ip_address} not found in GeoIP database")
        return None
    except Exception as e:
        logger.error(f"GeoIP lookup error for {ip_address}: {e}")
        return None


def calculate_distance(ip_address: str, billing_lat: float, billing_lon: float) -> Dict:
    result = {
        'distance_km': None,
        'ip_location': None,
        'error': None
    }

    if not is_valid_ip(ip_address):
        result['error'] = 'Invalid IP address format'
        return result

    if not (-90 <= billing_lat <= 90) or not (-180 <= billing_lon <= 180):
        result['error'] = 'Invalid coordinate values'
        return result

    location = resolve_ip_location(ip_address)
    if location is None:
        result['error'] = 'GeoIP lookup unavailable or IP not found'
        return result

    distance = haversine(billing_lat, billing_lon, location['latitude'], location['longitude'])
    result['distance_km'] = round(distance, 1)
    result['ip_location'] = f"{location['city']}, {location['country']}"
    result['ip_latitude'] = location['latitude']
    result['ip_longitude'] = location['longitude']

    return result