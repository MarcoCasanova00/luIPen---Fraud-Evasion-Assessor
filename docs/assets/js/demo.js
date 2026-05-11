const PRESETS = {
    legitimate: {
        target_url: 'https://trusted-store.com/checkout',
        distance_from_home: 5.0,
        distance_from_last_transaction: 1.0,
        ratio_to_median_purchase_price: 0.8,
        repeat_retailer: true,
        used_chip: true,
        used_pin_number: true,
        online_order: false
    },
    travel: {
        target_url: 'https://travel-booking.com/reservation',
        distance_from_home: 350.0,
        distance_from_last_transaction: 200.0,
        ratio_to_median_purchase_price: 2.0,
        repeat_retailer: true,
        used_chip: false,
        used_pin_number: false,
        online_order: true
    },
    large_purchase: {
        target_url: 'https://electronics-store.com/cart',
        distance_from_home: 150.0,
        distance_from_last_transaction: 50.0,
        ratio_to_median_purchase_price: 8.0,
        repeat_retailer: false,
        used_chip: false,
        used_pin_number: false,
        online_order: true
    },
    anomaly: {
        target_url: 'https://suspicious-site.com/pay',
        distance_from_home: 5000.0,
        distance_from_last_transaction: 3000.0,
        ratio_to_median_purchase_price: 15.0,
        repeat_retailer: false,
        used_chip: false,
        used_pin_number: false,
        online_order: true
    }
};

function normalizeBoolean(value, defaultValue) {
    if (typeof value === 'boolean') return value ? 1 : 0;
    if (typeof value === 'number') return value ? 1 : 0;
    if (typeof value === 'string') {
        const lower = value.toLowerCase();
        if (['true', '1', 'yes', 'on'].includes(lower)) return 1;
        if (['false', '0', 'no', 'off', ''].includes(lower)) return 0;
    }
    return defaultValue ? 1 : 0;
}

function normalizeNumeric(value, defaultValue) {
    const num = parseFloat(value);
    return isNaN(num) ? defaultValue : num;
}

function scoreTransaction(data) {
    let score = 1.0;

    const distanceHome = normalizeNumeric(data.distance_from_home || data.distance_km, 0);
    if (distanceHome > 100) score -= 0.3;
    else if (distanceHome > 50) score -= 0.15;
    else if (distanceHome > 20) score -= 0.05;

    const distanceLast = normalizeNumeric(data.distance_from_last_transaction, 1);
    if (distanceLast > 50) score -= 0.25;
    else if (distanceLast > 25) score -= 0.1;

    const ratio = normalizeNumeric(data.ratio_to_median_purchase_price || data.ratio, 1.0);
    if (ratio > 5) score -= 0.25;
    else if (ratio > 3) score -= 0.15;
    else if (ratio > 2) score -= 0.05;

    const retailerHistory = normalizeBoolean(data.retailer_history || data.repeat_retailer, true);
    if (!retailerHistory) score -= 0.1;

    const hasChip = normalizeBoolean(data.has_chip || data.used_chip, true);
    if (!hasChip) score -= 0.2;

    const hasPin = normalizeBoolean(data.has_pin || data.used_pin_number, true);
    if (!hasPin) score -= 0.15;

    const isOnline = normalizeBoolean(data.is_online || data.online_order, false);
    if (isOnline) score -= 0.1;

    score = Math.max(0.0, Math.min(1.0, score));
    return score;
}

function generateReport(data, successScore) {
    const findings = [];
    const recommendations = [];

    const distanceHome = normalizeNumeric(data.distance_from_home || data.distance_km, 0);
    if (distanceHome > 50) {
        findings.push({
            id: 'GEO-001',
            title: 'Significant Geolocation Anomaly',
            description: `${distanceHome}km from billing address exceeds 50km threshold`,
            severity: 'high'
        });
        recommendations.push('Implement stricter geolocation verification for high-distance transactions');
    } else if (distanceHome > 20) {
        findings.push({
            id: 'GEO-002',
            title: 'Moderate Geolocation Deviation',
            description: `${distanceHome}km from billing address exceeds 20km threshold`,
            severity: 'medium'
        });
    }

    const distanceLast = normalizeNumeric(data.distance_from_last_transaction, 1);
    if (distanceLast > 25) {
        findings.push({
            id: 'VEL-001',
            title: 'Impossible Travel Detected',
            description: `${distanceLast}km between transactions suggests rapid location change`,
            severity: 'high'
        });
        recommendations.push('Deploy velocity checking with configurable distance thresholds');
    }

    const ratio = normalizeNumeric(data.ratio_to_median_purchase_price || data.ratio, 1.0);
    if (ratio > 4) {
        findings.push({
            id: 'SPE-001',
            title: 'Abnormal Transaction Value',
            description: `Transaction is ${ratio}x user's median spending`,
            severity: 'high'
        });
        recommendations.push('Implement adaptive transaction limits based on spending history');
    } else if (ratio > 2.5) {
        findings.push({
            id: 'SPE-002',
            title: 'Elevated Spending Pattern',
            description: `Transaction is ${ratio}x user's median spending`,
            severity: 'medium'
        });
    }

    const hasChip = normalizeBoolean(data.has_chip || data.used_chip, true);
    if (!hasChip) {
        findings.push({
            id: 'AUT-001',
            title: 'Card Not Present Transaction',
            description: 'No chip authentication detected',
            severity: 'high'
        });
        recommendations.push('Require additional verification for CNP transactions');
    }

    const hasPin = normalizeBoolean(data.has_pin || data.used_pin_number, true);
    if (!hasPin) {
        findings.push({
            id: 'AUT-002',
            title: 'Missing PIN Verification',
            description: 'No PIN authentication recorded',
            severity: 'medium'
        });
    }

    const riskLevel = successScore > 0.8 ? 'CRITICAL' : successScore > 0.5 ? 'MEDIUM' : 'LOW';

    if (recommendations.length === 0 && findings.length > 0) {
        recommendations.push('Review flagged transactions manually');
        recommendations.push('Consider multi-factor authentication requirements');
    }

    return { findings, recommendations, riskLevel };
}

function updateUI(successScore) {
    const degrees = successScore * 180;
    const gaugeFill = document.getElementById('gaugeFill');
    const scoreValue = document.getElementById('scoreValue');
    const statusMessage = document.getElementById('statusMessage');

    gaugeFill.style.transform = `rotate(${degrees}deg)`;
    scoreValue.textContent = (successScore * 100).toFixed(1) + '%';

    if (successScore > 0.7) {
        gaugeFill.style.backgroundColor = 'var(--danger-color)';
        statusMessage.textContent = 'HIGH BYPASS RISK';
        statusMessage.className = 'status danger';
    } else if (successScore > 0.4) {
        gaugeFill.style.backgroundColor = 'var(--warning-color)';
        statusMessage.textContent = 'MODERATE RISK';
        statusMessage.className = 'status warning';
    } else {
        gaugeFill.style.backgroundColor = 'var(--accent-color)';
        statusMessage.textContent = 'LOW BYPASS RISK';
        statusMessage.className = 'status safe';
    }
}

function updateReport(report) {
    const tipsList = document.getElementById('tipsList');
    tipsList.innerHTML = '';

    const riskItem = document.createElement('li');
    riskItem.textContent = `Overall Risk: ${report.riskLevel}`;
    riskItem.style.fontWeight = 'bold';
    if (report.riskLevel === 'CRITICAL') riskItem.style.color = 'var(--danger-color)';
    else if (report.riskLevel === 'MEDIUM') riskItem.style.color = 'var(--warning-color)';
    else riskItem.style.color = 'var(--accent-color)';
    tipsList.appendChild(riskItem);

    if (report.findings.length > 0) {
        const findingsHeader = document.createElement('li');
        findingsHeader.textContent = 'Findings:';
        findingsHeader.style.color = 'var(--accent-color)';
        findingsHeader.style.fontWeight = 'bold';
        tipsList.appendChild(findingsHeader);

        report.findings.forEach(f => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>[${f.id}]</strong> ${f.title}: ${f.description}`;
            li.style.marginLeft = '20px';
            tipsList.appendChild(li);
        });
    }

    if (report.recommendations.length > 0) {
        const recHeader = document.createElement('li');
        recHeader.textContent = 'Recommendations:';
        recHeader.style.color = 'var(--accent-color)';
        recHeader.style.fontWeight = 'bold';
        tipsList.appendChild(recHeader);

        report.recommendations.forEach(r => {
            const li = document.createElement('li');
            li.textContent = r;
            li.style.marginLeft = '20px';
            tipsList.appendChild(li);
        });
    }
}

function loadPreset(presetName) {
    const preset = PRESETS[presetName];
    if (!preset) return;

    document.getElementById('target_url').value = preset.target_url || '';
    document.getElementById('distance_from_home').value = preset.distance_from_home || 10;
    document.getElementById('distance_from_last_transaction').value = preset.distance_from_last_transaction || 1;
    document.getElementById('ratio_to_median_purchase_price').value = preset.ratio_to_median_purchase_price || 1;
    document.getElementById('repeat_retailer').checked = preset.repeat_retailer || false;
    document.getElementById('used_chip').checked = preset.used_chip !== undefined ? preset.used_chip : true;
    document.getElementById('used_pin_number').checked = preset.used_pin_number !== undefined ? preset.used_pin_number : true;
    document.getElementById('online_order').checked = preset.online_order || false;
}

function getFormData() {
    return {
        target_url: document.getElementById('target_url').value,
        distance_from_home: document.getElementById('distance_from_home').value,
        distance_from_last_transaction: document.getElementById('distance_from_last_transaction').value,
        ratio_to_median_purchase_price: document.getElementById('ratio_to_median_purchase_price').value,
        retailer_history: document.getElementById('repeat_retailer').checked,
        has_chip: document.getElementById('used_chip').checked,
        has_pin: document.getElementById('used_pin_number').checked,
        is_online: document.getElementById('online_order').checked
    };
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('fraudForm');
    const analyzeBtn = document.getElementById('analyzeBtn');

    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const presetName = btn.getAttribute('data-preset');
            loadPreset(presetName);
        });
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        analyzeBtn.textContent = 'ANALYZING...';
        analyzeBtn.disabled = true;

        const data = getFormData();
        const successScore = scoreTransaction(data);
        const report = generateReport(data, successScore);

        updateUI(successScore);
        updateReport(report);

        setTimeout(() => {
            analyzeBtn.textContent = 'RUN ASSESSMENT';
            analyzeBtn.disabled = false;
        }, 500);
    });
});