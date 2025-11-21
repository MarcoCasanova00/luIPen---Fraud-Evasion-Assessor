# Fraud Evasion Penetration Testing Tool

## Overview
The **Fraud Evasion Penetration Testing Tool** is a specialized web application designed for corporate security teams and penetration testers. It simulates how an attacker might attempt to evade fraud detection systems (specifically those based on Random Forest classifiers) and provides a "Success Score" indicating the likelihood of bypassing these controls.

The tool allows you to assess the resilience of your fraud detection logic against various attack vectors, including:
- **Geolocation Spoofing**: Testing distance-based anomalies.
- **Velocity Checks**: Simulating "impossible travel" scenarios.
- **Card Configuration**: Testing the impact of Chip, PIN, and Retailer History.

## Features
- **Bypass Success Score**: Calculates the probability (0-100%) of a transaction bypassing the fraud model.
- **Vulnerability Report**: Generates detailed, actionable advice on *why* a transaction was flagged (e.g., "Velocity check triggered").
- **MaxMind GeoIP Integration**: Optional integration with MaxMind GeoLite2 to resolve real IP addresses to locations and calculate distances.
- **Educational Hints**: In-app explanations of fraud detection concepts like "Behavioral Baselining" and "EMV Liability Shift".

## Prerequisites
- Python 3.8+
- `pip` (Python Package Manager)

## Installation

1.  **Clone the repository** (or extract the files):
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **MaxMind DB Setup (Optional)**:
    - To enable the "Auto-Calculate Distance" feature, download the `GeoLite2-City.mmdb` file from [MaxMind](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data).
    - Place the `.mmdb` file in the root directory of the project.
    - *Note: The app works without this file, but the IP-to-Location feature will be disabled.*

## Usage

1.  **Train the Model** (First Run Only):
    The app requires a trained Random Forest model. Run the training script to generate `fraud_model.pkl`:
    ```bash
    python train_model.py
    ```

2.  **Start the Application**:
    ```bash
    python app.py
    ```

3.  **Access the Tool**:
    Open your web browser and navigate to:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

4.  **Run a Test**:
    - Enter a **Target URL** (e.g., the payment page you are auditing).
    - Configure the **Connection & Geolocation** settings (or use the Auto-Calculate button if MaxMind is set up).
    - Configure the **Card Details** (Chip, PIN, etc.).
    - Click **RUN PENETRATION TEST** to see the Success Score and Vulnerability Report.

## Project Structure
- `app.py`: Main Flask application backend.
- `train_model.py`: Script to train the Machine Learning model.
- `templates/index.html`: Frontend user interface.
- `static/style.css`: "Cybersecurity" themed styling.
- `static/script.js`: Frontend logic and report generation.
- `requirements.txt`: Python dependencies.

## Disclaimer
This tool is intended for **educational and authorized testing purposes only**. Do not use this tool to facilitate actual fraud or attack systems you do not own or have explicit permission to test.
