import os
import pickle
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

MODEL_CACHE = None


def load_model(model_path: str) -> Optional[object]:
    global MODEL_CACHE
    if MODEL_CACHE is not None:
        return MODEL_CACHE

    if not os.path.exists(model_path):
        logger.warning(f"Model file not found at {model_path}")
        return None

    try:
        with open(model_path, 'rb') as f:
            MODEL_CACHE = pickle.load(f)
        logger.info(f"Model loaded from {model_path}")
        return MODEL_CACHE
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return None


def normalize_boolean(value, default=False) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return 1 if value else 0
    if isinstance(value, str):
        return 1 if value.lower() in ('true', '1', 'yes', 'on') else 0
    return 1 if default else 0


def normalize_numeric(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def score_transaction(data: Dict) -> Dict:
    model = load_model(os.environ.get('MODEL_PATH', 'fraud_model.pkl'))

    distance_home = normalize_numeric(data.get('distance_km', data.get('distance_from_home', 0)))
    distance_last = normalize_numeric(data.get('distance_from_last_transaction', data.get('distance_km', 1)))
    ratio = normalize_numeric(data.get('ratio_to_median_purchase_price', data.get('ratio', 1.0)))
    repeat_retailer = normalize_boolean(data.get('retailer_history', data.get('repeat_retailer', True)))
    has_chip = normalize_boolean(data.get('has_chip', data.get('used_chip', True)))
    has_pin = normalize_boolean(data.get('has_pin', data.get('used_pin_number', True)))
    is_online = normalize_boolean(data.get('is_online', data.get('online_order', False)))

    if model is None:
        return score_demo_mode(distance_home, distance_last, ratio, repeat_retailer, has_chip, has_pin, is_online)

    features = [
        [distance_home, distance_last, ratio, repeat_retailer, has_chip, has_pin, is_online]
    ]

    fraud_probability = model.predict_proba(features)[0][1]
    success_score = 1.0 - fraud_probability

    return {
        'success_score': round(success_score, 4),
        'fraud_probability': round(fraud_probability, 4),
        'is_bypassed': success_score > 0.5,
        'confidence': 'high' if abs(success_score - 0.5) > 0.3 else 'medium' if abs(success_score - 0.5) > 0.15 else 'low'
    }


def score_demo_mode(distance_home: float, distance_last: float, ratio: float, repeat_retailer: int, has_chip: int, has_pin: int, is_online: int) -> Dict:
    score = 1.0

    if distance_home > 100:
        score -= 0.3
    elif distance_home > 50:
        score -= 0.15
    elif distance_home > 20:
        score -= 0.05

    if distance_last > 50:
        score -= 0.25
    elif distance_last > 25:
        score -= 0.1

    if ratio > 5:
        score -= 0.25
    elif ratio > 3:
        score -= 0.15
    elif ratio > 2:
        score -= 0.05

    if not repeat_retailer:
        score -= 0.1

    if not has_chip:
        score -= 0.2

    if not has_pin:
        score -= 0.15

    if is_online:
        score -= 0.1

    score = max(0.0, min(1.0, score))
    fraud_probability = 1.0 - score

    return {
        'success_score': round(score, 4),
        'fraud_probability': round(fraud_probability, 4),
        'is_bypassed': score > 0.5,
        'confidence': 'medium',
        'mode': 'demo'
    }


def calculate_risk_factors(data: Dict) -> List[Dict]:
    factors = []

    distance_home = normalize_numeric(data.get('distance_km', data.get('distance_from_home', 0)))
    if distance_home > 50:
        factors.append({
            'factor': 'geoip_distance',
            'severity': 'high',
            'description': 'Large distance from billing address',
            'threshold': f'{distance_home}km exceeds 50km threshold'
        })
    elif distance_home > 20:
        factors.append({
            'factor': 'geoip_distance',
            'severity': 'medium',
            'description': 'Moderate distance from billing address',
            'threshold': f'{distance_home}km exceeds 20km threshold'
        })

    distance_last = normalize_numeric(data.get('distance_from_last_transaction', data.get('distance_km', 1)))
    if distance_last > 25:
        factors.append({
            'factor': 'velocity_anomaly',
            'severity': 'high',
            'description': 'Impossible travel detected',
            'threshold': f'{distance_last}km exceeds velocity threshold'
        })

    ratio = normalize_numeric(data.get('ratio_to_median_purchase_price', 1.0))
    if ratio > 4:
        factors.append({
            'factor': 'spending_anomaly',
            'severity': 'high',
            'description': 'Transaction significantly above normal spending',
            'threshold': f'Ratio {ratio}x exceeds 4x threshold'
        })
    elif ratio > 2.5:
        factors.append({
            'factor': 'spending_anomaly',
            'severity': 'medium',
            'description': 'Transaction above normal spending pattern',
            'threshold': f'Ratio {ratio}x exceeds 2.5x threshold'
        })

    if not normalize_boolean(data.get('has_chip', data.get('used_chip', False))):
        factors.append({
            'factor': 'weak_authentication',
            'severity': 'high',
            'description': 'No chip authentication (CNP transaction)',
            'threshold': 'Card not present'
        })

    if not normalize_boolean(data.get('has_pin', data.get('used_pin_number', True))):
        factors.append({
            'factor': 'weak_authentication',
            'severity': 'medium',
            'description': 'No PIN verification',
            'threshold': 'Missing secondary authentication'
        })

    return factors