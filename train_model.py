import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Load dataset
filename = "datasetccfrauds"
data_lines = []
header = [
    "distance_from_home",
    "distance_from_last_transaction",
    "ratio_to_median_purchase_price",
    "repeat_retailer",
    "used_chip",
    "used_pin_number",
    "online_order",
    "fraud"
]

print("Reading dataset...")
with open(filename, 'r') as f:
    lines = f.readlines()
    is_data = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.upper() == '@DATA':
            is_data = True
            continue
        if is_data:
            data_lines.append(line.split(','))

print(f"Loaded {len(data_lines)} rows.")

# Create DataFrame
df = pd.DataFrame(data_lines, columns=header)

# Convert columns to numeric
for col in header:
    df[col] = pd.to_numeric(df[col])

# Split features and target
X = df.drop('fraud', axis=1)
y = df['fraud']

# Train model
print("Training Random Forest model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
accuracy = clf.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.4f}")

# Save model
with open('fraud_model.pkl', 'wb') as f:
    pickle.dump(clf, f)

print("Model saved to fraud_model.pkl")
