document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('fraudForm');
    const gaugeFill = document.getElementById('gaugeFill');
    const scoreValue = document.getElementById('scoreValue');
    const statusMessage = document.getElementById('statusMessage');
    const tipsList = document.getElementById('tipsList');

    const calcDistanceBtn = document.getElementById('calcDistanceBtn');

    calcDistanceBtn.addEventListener('click', async () => {
        const ipAddress = document.getElementById('ip_address').value;
        const billingLat = document.getElementById('billing_lat').value;
        const billingLon = document.getElementById('billing_lon').value;

        if (!ipAddress || !billingLat || !billingLon) {
            alert('Please enter IP Address, Billing Latitude, and Billing Longitude.');
            return;
        }

        calcDistanceBtn.textContent = 'CALCULATING...';

        try {
            const response = await fetch('/calculate_distance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ip_address: ipAddress,
                    billing_lat: billingLat,
                    billing_lon: billingLon
                })
            });

            const result = await response.json();

            if (result.error) {
                alert('Error: ' + result.error);
            } else {
                document.getElementById('distance_from_home').value = result.distance_km;
                alert(`Distance Calculated: ${result.distance_km} km\nIP Location: ${result.ip_location}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to calculate distance.');
        } finally {
            calcDistanceBtn.textContent = 'AUTO-CALCULATE DISTANCE (MAXMIND)';
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Gather data
        const data = {
            target_url: document.getElementById('target_url').value,
            distance_from_home: document.getElementById('distance_from_home').value,
            distance_from_last_transaction: document.getElementById('distance_from_last_transaction').value,
            ratio_to_median_purchase_price: document.getElementById('ratio_to_median_purchase_price').value,
            repeat_retailer: document.getElementById('repeat_retailer').checked ? 1 : 0,
            used_chip: document.getElementById('used_chip').checked ? 1 : 0,
            used_pin_number: document.getElementById('used_pin_number').checked ? 1 : 0,
            online_order: document.getElementById('online_order').checked ? 1 : 0
        };

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.error) {
                alert('Error: ' + result.error);
                return;
            }

            updateUI(result.success_score, data);

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while analyzing the transaction.');
        }
    });

    function updateUI(successScore, currentData) {
        // Update Gauge
        // 0% -> 0deg, 100% -> 180deg
        const degrees = successScore * 180;
        gaugeFill.style.transform = `rotate(${degrees}deg)`;

        // Update Text
        const percentage = (successScore * 100).toFixed(1) + '%';
        scoreValue.textContent = percentage;

        // Update Color and Status
        // High Success Score = Good for Attacker (Green)
        // Low Success Score = Bad for Attacker (Red)
        if (successScore > 0.5) {
            gaugeFill.style.backgroundColor = 'var(--accent-color)'; // Green
            statusMessage.textContent = 'HIGH BYPASS PROBABILITY';
            statusMessage.className = 'status safe';
        } else {
            gaugeFill.style.backgroundColor = 'var(--danger-color)'; // Red
            statusMessage.textContent = 'DETECTION LIKELY';
            statusMessage.className = 'status danger';
        }

        // Generate Report
        generateReport(successScore, currentData);
    }

    function generateReport(successScore, data) {
        tipsList.innerHTML = '';
        const tips = [];

        if (successScore > 0.9) {
            tips.push("CRITICAL VULNERABILITY: The target system is highly likely to approve this transaction.");
            tips.push("ANALYSIS: The combination of trusted parameters (e.g., Chip/PIN, low distance) effectively masks the activity, mimicking a legitimate user perfectly.");
        } else if (successScore < 0.5) {
            tips.push("RESILIENT: The target system is likely to flag this attempt.");

            const distHome = parseFloat(data.distance_from_home);
            const distLast = parseFloat(data.distance_from_last_transaction);
            const ratio = parseFloat(data.ratio_to_median_purchase_price);
            const online = data.online_order === 1;
            const pin = data.used_pin_number === 1;

            if (distHome > 50) {
                tips.push("FACTOR: Geo-IP anomaly detected (Distance > 50km).");
                tips.push("  -> ADVICE: High distance from billing address suggests account takeover. Ensure IP geolocation matches the cardholder's region.");
            }
            if (distLast > 20) {
                tips.push("FACTOR: Velocity check triggered (High distance from last location).");
                tips.push("  -> ADVICE: 'Impossible Travel' detected. The system sees two transactions far apart in a short time. Use a proxy close to the last known location.");
            }
            if (ratio > 4) {
                tips.push("FACTOR: Spending pattern anomaly (High value ratio).");
                tips.push("  -> ADVICE: The amount is significantly higher than the user's median spending. Start with smaller amounts to build trust.");
            }
            if (online) {
                tips.push("FACTOR: CNP (Card Not Present) transactions carry higher risk weight.");
                tips.push("  -> ADVICE: Online transactions lack physical card verification. Systems are stricter. Ensure all other parameters (IP, Device Fingerprint) are perfect.");
            }
            if (!pin) {
                tips.push("FACTOR: Lack of strong authentication (No PIN).");
                tips.push("  -> ADVICE: Without a PIN, the bank is liable for fraud, so they block aggressively. Use Chip & PIN if simulating a physical terminal.");
            }
        } else {
            tips.push("UNCERTAIN: The system may challenge this transaction (e.g., SMS OTP).");
            tips.push("Recommendation: Mimic standard user behavior more closely to increase success rate.");
        }

        tips.forEach(tip => {
            const li = document.createElement('li');
            li.textContent = tip;
            tipsList.appendChild(li);
        });
    }
});
