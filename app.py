import pandas as pd
import pickle
from flask import Flask, request, jsonify, render_template
import os
import math
import geoip2.database

app = Flask(__name__)

# Load the trained model
model_path = 'fraud_model.pkl'
if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
else:
    model = None
    print("Warning: Model file not found. Please run train_model.py first.")

# MaxMind DB Path (Optional)
MAXMIND_DB_PATH = 'GeoLite2-City.mmdb'
reader = None
if os.path.exists(MAXMIND_DB_PATH):
    try:
        reader = geoip2.database.Reader(MAXMIND_DB_PATH)
        print(f"MaxMind DB loaded from {MAXMIND_DB_PATH}")
    except Exception as e:
        print(f"Error loading MaxMind DB: {e}")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate_distance', methods=['POST'])
def calculate_distance():
    data = request.json
    ip_address = data.get('ip_address')
    billing_lat = float(data.get('billing_lat', 0))
    billing_lon = float(data.get('billing_lon', 0))

    result = {
        "distance_km": 0,
        "ip_location": "Unknown",
        "error": None
    }

    if not reader:
        result["error"] = "MaxMind DB not available. Using manual input."
        return jsonify(result)

    try:
        response = reader.city(ip_address)
        ip_lat = response.location.latitude
        ip_lon = response.location.longitude
        result["ip_location"] = f"{response.city.name}, {response.country.name}"
        
        dist = haversine(billing_lat, billing_lon, ip_lat, ip_lon)
        result["distance_km"] = round(dist, 1)
        
    except geoip2.errors.AddressNotFoundError:
        result["error"] = "IP Address not found in database."
    except Exception as e:
        result["error"] = str(e)

    return jsonify(result)

@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500

    data = request.json
    
    # Log the target URL for context (simulation)
    target_url = data.get('target_url', 'Unknown')
    print(f"Analyzing target: {target_url}")

    # Extract features
    features = [
        float(data.get('distance_from_home', 0)),
        float(data.get('distance_from_last_transaction', 0)),
        float(data.get('ratio_to_median_purchase_price', 0)),
        int(data.get('repeat_retailer', 0)),
        int(data.get('used_chip', 0)),
        int(data.get('used_pin_number', 0)),
        int(data.get('online_order', 0))
    ]

    # Predict probability
    # Class 1 is fraud, Class 0 is legitimate
    fraud_probability = model.predict_proba([features])[0][1]
    
    # Success Score = Likelihood of bypassing detection (Inverse of fraud probability)
    success_score = 1.0 - fraud_probability
    
    return jsonify({
        'fraud_probability': fraud_probability,
        'success_score': success_score,
        'is_bypassed': success_score > 0.5
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
