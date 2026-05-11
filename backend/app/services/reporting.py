import json
import os
from typing import Dict, List, Any
from datetime import datetime


def load_report_template(template_name: str = 'default') -> Dict:
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'shared', 'rules', 'report_templates.json'
    )

    try:
        with open(template_path, 'r') as f:
            templates = json.load(f)
            return templates.get(template_name, templates.get('default', {}))
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            'title': 'Vulnerability Assessment Report',
            'summary_template': 'Assessment for {target_url} reveals {risk_level} risk profile.',
            'recommendations': [
                'Implement additional verification steps',
                'Review transaction velocity rules',
                'Consider multi-factor authentication'
            ]
        }


def generate_vulnerability_report(data: Dict, score_result: Dict) -> Dict:
    template = load_report_template()

    severity = _determine_severity(score_result['success_score'])
    risk_level = _determine_risk_level(score_result['success_score'])

    findings = _generate_findings(data, score_result)
    recommendations = _generate_recommendations(findings, severity)
    mitigation = _generate_mitigation(findings)

    report = {
        'report_id': _generate_report_id(),
        'generated_at': datetime.utcnow().isoformat(),
        'target_url': data.get('target_url', 'Unknown'),
        'assessment': {
            'success_score': score_result['success_score'],
            'fraud_probability': score_result.get('fraud_probability', 0),
            'is_bypassed': score_result.get('is_bypassed', False),
            'confidence': score_result.get('confidence', 'unknown'),
            'mode': score_result.get('mode', 'production')
        },
        'risk_profile': {
            'severity': severity,
            'risk_level': risk_level,
            'detection_likelihood': _calculate_detection_likelihood(score_result['success_score'])
        },
        'findings': findings,
        'recommendations': recommendations,
        'mitigation': mitigation,
        'disclaimer': (
            'This report is generated for authorized security testing and educational purposes only. '
            'Do not use this information for unauthorized activities.'
        )
    }

    return report


def _determine_severity(score: float) -> str:
    if score > 0.8:
        return 'critical'
    elif score > 0.6:
        return 'high'
    elif score > 0.4:
        return 'medium'
    else:
        return 'low'


def _determine_risk_level(score: float) -> str:
    if score > 0.8:
        return 'HIGH'
    elif score > 0.5:
        return 'MEDIUM'
    else:
        return 'LOW'


def _calculate_detection_likelihood(score: float) -> float:
    return round(1.0 - score, 4)


def _generate_report_id() -> str:
    from uuid import uuid4
    return f"FEPT-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"


def _generate_findings(data: Dict, score_result: Dict) -> List[Dict]:
    findings = []

    distance_home = float(data.get('distance_km', data.get('distance_from_home', 0)))
    if distance_home > 50:
        findings.append({
            'id': 'GEO-001',
            'category': 'Geolocation',
            'title': 'Significant Geolocation Anomaly',
            'description': f'Transaction IP located {distance_home}km from billing address',
            'severity': 'high',
            'impact': 'Could indicate account takeover or VPN/Proxy usage',
            'recommendation': 'Implement stricter geolocation verification'
        })
    elif distance_home > 20:
        findings.append({
            'id': 'GEO-002',
            'category': 'Geolocation',
            'title': 'Moderate Geolocation Deviation',
            'description': f'Transaction IP located {distance_home}km from billing address',
            'severity': 'medium',
            'impact': 'May indicate travel or VPN usage',
            'recommendation': 'Review transaction context and device information'
        })

    distance_last = float(data.get('distance_from_last_transaction', data.get('distance_km', 1)))
    if distance_last > 25:
        findings.append({
            'id': 'VEL-001',
            'category': 'Velocity',
            'title': 'Impossible Travel Detected',
            'description': f'{distance_last}km between last transaction and current location',
            'severity': 'high',
            'impact': 'Suggests rapid location change in short time window',
            'recommendation': 'Implement velocity checking with distance thresholds'
        })

    ratio = float(data.get('ratio_to_median_purchase_price', 1.0))
    if ratio > 4:
        findings.append({
            'id': 'SPE-001',
            'category': 'Spending Pattern',
            'title': 'Abnormal Transaction Value',
            'description': f'Transaction is {ratio}x the user\'s median spending',
            'severity': 'high',
            'impact': 'Could indicate stolen card or account compromise',
            'recommendation': 'Implement adaptive transaction limits'
        })

    if not data.get('has_chip', data.get('used_chip', True)):
        findings.append({
            'id': 'AUT-001',
            'category': 'Authentication',
            'title': 'Card Not Present Transaction',
            'description': 'No chip authentication detected',
            'severity': 'high',
            'impact': 'Higher fraud risk due to lack of physical card verification',
            'recommendation': 'Require additional verification for CNP transactions'
        })

    if not data.get('has_pin', data.get('used_pin_number', True)):
        findings.append({
            'id': 'AUT-002',
            'category': 'Authentication',
            'title': 'Missing PIN Verification',
            'description': 'No PIN authentication recorded',
            'severity': 'medium',
            'impact': 'Reduced authentication confidence',
            'recommendation': 'Implement PIN verification requirements'
        })

    return findings


def _generate_recommendations(findings: List[Dict], severity: str) -> List[str]:
    recommendations = []

    if severity in ['critical', 'high']:
        recommendations.append('Immediately review and enhance fraud detection thresholds')
        recommendations.append('Implement multi-layer verification for high-value transactions')

    if any(f['category'] == 'Geolocation' for f in findings):
        recommendations.append('Deploy IP geolocation validation with configurable thresholds')
        recommendations.append('Consider VPN/Proxy detection mechanisms')

    if any(f['category'] == 'Velocity' for f in findings):
        recommendations.append('Implement velocity checking with reasonable distance thresholds')
        recommendations.append('Add time-window based transaction analysis')

    if any(f['category'] == 'Spending Pattern' for f in findings):
        recommendations.append('Use adaptive limits based on user spending history')
        recommendations.append('Implement gradual limit increases after account verification')

    if any(f['category'] == 'Authentication' for f in findings):
        recommendations.append('Enforce chip and PIN requirements where possible')
        recommendations.append('Implement step-up authentication for CNP transactions')

    return recommendations if recommendations else [
        'Continue monitoring transaction patterns',
        'Review system configuration regularly',
        'Maintain updated fraud detection rules'
    ]


def _generate_mitigation(findings: List[Dict]) -> Dict:
    return {
        'immediate_actions': [
            'Review flagged transactions manually',
            'Contact cardholder if abnormal activity detected',
            'Temporarily restrict account if fraud suspected'
        ],
        'long_term': [
            'Deploy machine learning fraud detection model',
            'Implement real-time transaction scoring',
            'Establish fraud intelligence sharing with network'
        ]
    }