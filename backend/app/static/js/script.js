document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('fraudForm');
    const gaugeFill = document.getElementById('gaugeFill');
    const scoreValue = document.getElementById('scoreValue');
    const statusMessage = document.getElementById('statusMessage');
    const tipsList = document.getElementById('tipsList');
    const calcDistanceBtn = document.getElementById('calcDistanceBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');

    calcDistanceBtn.addEventListener('click', async () => {
        const ipAddress = document.getElementById('ip_address').value;
        const billingLat = document.getElementById('billing_lat').value;
        const billingLon = document.getElementById('billing_lon').value;

        if (!ipAddress || !billingLat || !billingLon) {
            alert('Please enter IP Address, Billing Latitude, and Billing Longitude.');
            return;
        }

        calcDistanceBtn.textContent = 'CALCULATING...';
        calcDistanceBtn.disabled = true;

        try {
            const response = await fetch('/api/geoip/distance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ip_address: ipAddress,
                    billing_lat: parseFloat(billingLat),
                    billing_lon: parseFloat(billingLon)
                })
            });

            const result = await response.json();

            if (result.error) {
                alert('Error: ' + result.error);
            } else {
                document.getElementById('distance_from_home').value = result.distance_km;
                alert('Distance Calculated: ' + result.distance_km + ' km\nIP Location: ' + result.ip_location);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to calculate distance.');
        } finally {
            calcDistanceBtn.textContent = 'AUTO-CALCULATE DISTANCE';
            calcDistanceBtn.disabled = false;
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        analyzeBtn.textContent = 'ANALYZING...';
        analyzeBtn.disabled = true;

        const data = {
            target_url: document.getElementById('target_url').value,
            distance_km: parseFloat(document.getElementById('distance_from_home').value) || 10.0,
            distance_from_last_transaction: parseFloat(document.getElementById('distance_from_last_transaction').value) || 1.0,
            ratio_to_median_purchase_price: parseFloat(document.getElementById('ratio_to_median_purchase_price').value) || 1.0,
            retailer_history: document.getElementById('repeat_retailer').checked,
            has_chip: document.getElementById('used_chip').checked,
            has_pin: document.getElementById('used_pin_number').checked,
            is_online: document.getElementById('online_order').checked
        };

        try {
            const response = await fetch('/api/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.error) {
                alert('Error: ' + result.error);
                return;
            }

            updateUI(result.assessment.success_score, result);
            updateReport(result);

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while analyzing the transaction.');
        } finally {
            analyzeBtn.textContent = 'RUN SECURITY ASSESSMENT';
            analyzeBtn.disabled = false;
        }
    });

    function updateUI(successScore, result) {
        const degrees = successScore * 180;
        gaugeFill.style.transform = 'rotate(' + degrees + 'deg)';

        const percentage = (successScore * 100).toFixed(1) + '%';
        scoreValue.textContent = percentage;

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

    function updateReport(result) {
        tipsList.innerHTML = '';

        const findings = result.findings || [];
        const recommendations = result.recommendations || [];

        if (result.risk_profile && result.risk_profile.severity) {
            const severityItem = document.createElement('li');
            severityItem.textContent = 'Overall Risk: ' + result.risk_profile.risk_level + ' (' + result.risk_profile.severity.toUpperCase() + ')';
            if (result.risk_profile.severity === 'critical' || result.risk_profile.severity === 'high') {
                severityItem.style.color = 'var(--danger-color)';
            } else if (result.risk_profile.severity === 'medium') {
                severityItem.style.color = 'var(--warning-color)';
            } else {
                severityItem.style.color = 'var(--accent-color)';
            }
            tipsList.appendChild(severityItem);
        }

        if (findings.length > 0) {
            const findingsHeader = document.createElement('li');
            findingsHeader.textContent = 'Findings:';
            findingsHeader.style.color = 'var(--accent-color)';
            findingsHeader.style.fontWeight = 'bold';
            tipsList.appendChild(findingsHeader);

            findings.forEach(finding => {
                const li = document.createElement('li');
                li.innerHTML = '<strong>[' + finding.id + ']</strong> ' + finding.title + ': ' + finding.description;
                li.style.marginLeft = '20px';
                tipsList.appendChild(li);
            });
        }

        if (recommendations.length > 0) {
            const recHeader = document.createElement('li');
            recHeader.textContent = 'Recommendations:';
            recHeader.style.color = 'var(--accent-color)';
            recHeader.style.fontWeight = 'bold';
            tipsList.appendChild(recHeader);

            recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                li.style.marginLeft = '20px';
                tipsList.appendChild(li);
            });
        }
    }
});