# Fraud Evasion Penetration Testing Tool

A dual-mode project providing both a production Flask backend and a static frontend demo for fraud detection resilience assessment.

## Overview

The **Fraud Evasion Penetration Testing Tool** is a defensive security tool designed for corporate security teams and authorized penetration testers. It simulates how fraud detection systems might evaluate transaction patterns, producing a detection resilience score and vulnerability report.

**Purpose:** Educational and authorized security testing only.

## Project Structure

```
fraud-evasion-assessor/
├── backend/              # Production Flask application
│   ├── app/
│   │   ├── routes/       # Web and API endpoints
│   │   ├── services/     # Core business logic
│   │   ├── security/     # Security hardening modules
│   │   ├── templates/    # Jinja2 templates
│   │   └── static/       # CSS and JS assets
│   ├── tests/            # Unit tests
│   ├── wsgi.py           # WSGI entry point
│   └── requirements.txt  # Python dependencies
├── docs/                 # GitHub Pages static demo
│   ├── index.html
│   └── assets/
├── shared/
│   └── rules/            # Shared configuration files
├── scripts/              # Automation scripts
└── .github/workflows/    # GitHub Actions
```

## Two Modes

### 1. Backend Edition (Production)
- Flask application with real scoring logic
- Optional GeoIP integration with MaxMind GeoLite2
- Secure API endpoints with rate limiting
- Full vulnerability reporting
- **Requires Python runtime and dependencies**

### 2. Frontend Demo (Static)
- Pure HTML/CSS/JS - runs in any browser
- GitHub Pages compatible
- Client-side scoring simulation
- No server required
- **Suitable for documentation and demonstrations**

## Features

- **Detection Resilience Scoring** - Evaluates transaction patterns against fraud detection criteria
- **Vulnerability Reports** - Provides findings and recommendations
- **GeoIP Integration** - Optional IP geolocation with MaxMind GeoLite2
- **Risk Factor Analysis** - Geolocation, velocity, spending patterns, authentication
- **Demo Presets** - Quick test configurations

## Quick Start

### Backend Setup

```bash
# Clone repository
git clone https://github.com/MarcoCasanova00/fraud-evasion-assessor.git
cd fraud-evasion-assessor

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Train model (optional, uses demo scoring if missing)
python train_model.py

# Copy environment template
cp .env.example .env

# Run the application
python wsgi.py
```

Visit `http://127.0.0.1:5000`

### Frontend Demo

Simply open `docs/index.html` in any browser, or deploy the `docs/` directory to GitHub Pages.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main interface |
| `/health` | GET | Health check |
| `/api/score` | POST | Calculate detection resilience score |
| `/api/report` | POST | Generate vulnerability report |
| `/api/geoip/distance` | POST | Calculate IP-to-billing distance |
| `/api/demo-presets` | GET | List available presets |

### Example Request

```bash
curl -X POST http://localhost:5000/api/score \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com/checkout",
    "distance_km": 10.0,
    "distance_from_last_transaction": 5.0,
    "ratio_to_median_purchase_price": 1.5,
    "retailer_history": true,
    "has_chip": true,
    "has_pin": true,
    "is_online": false
  }'
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | (generated) |
| `FLASK_ENV` | Environment mode | development |
| `GEOIP_DB_PATH` | Path to GeoLite2 database | GeoLite2-City.mmdb |
| `MODEL_PATH` | Path to ML model | fraud_model.pkl |

## GitHub Pages Deployment

1. Push to main branch
2. Enable GitHub Pages in repository settings
3. Select `gh-pages` branch as source
4. Demo available at `https://username.github.io/repo/`

## Security Disclaimer

**IMPORTANT:** This tool is designed for:
- Educational purposes
- Authorized security testing
- Fraud detection system resilience assessment

**DO NOT use this tool to:**
- Facilitate actual fraud
- Attack systems without permission
- Violate applicable laws

Unauthorized use is strictly prohibited.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with security best practices
4. Submit a pull request with description

## License

See [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Additional ML model training options
- [ ] Enhanced reporting with charts
- [ ] API authentication
- [ ] Multi-language support
- [ ] Integration test suite

---

**Version:** 2.0 | **Author:** Security Engineering Team