import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, '..', 'datasetccfrauds')
model_path = os.path.join(script_dir, 'fraud_model.pkl')

def train_model():
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
    data_lines = []

    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        print("The model will use fallback demo scoring if not trained.")
        return False

    try:
        with open(dataset_path, 'r') as f:
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

        df = pd.DataFrame(data_lines, columns=header)

        for col in header:
            df[col] = pd.to_numeric(df[col])

        X = df.drop('fraud', axis=1)
        y = df['fraud']

        print("Training Random Forest model...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        accuracy = clf.score(X_test, y_test)
        print(f"Model Accuracy: {accuracy:.4f}")

        with open(model_path, 'wb') as f:
            pickle.dump(clf, f)

        print(f"Model saved to {model_path}")
        return True

    except Exception as e:
        print(f"Error during training: {e}")
        return False


if __name__ == '__main__':
    print("=" * 50)
    print("Fraud Detection Model Training")
    print("=" * 50)
    train_model()
    print("=" * 50)