"""
Baseline B2: ML-Based Underwriting (XGBoost)
Machine learning model for underwriting decisions
"""

import json
from pathlib import Path
import pickle
import numpy as np

# Try to import sklearn
try:
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score, classification_report
    sklearn_available = True
except ImportError:
    sklearn_available = False
    print("Warning: scikit-learn not available, using simple baseline")

# Try to import XGBoost
try:
    import xgboost as xgb
    xgb_available = True
except ImportError:
    xgb_available = False
    print("Warning: XGBoost not available, will use scikit-learn")

class MLUnderwriter:
    """ML-based underwriting baseline"""

    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_names = [
            'age', 'credit_score', 'vehicle_value', 'premium_amount',
            'claim_amount', 'fraud_flag'
        ]

    def prepare_features(self, data):
        """Prepare features for ML model"""
        X = []
        for record in data:
            features = [
                record.get('age', 30),
                record.get('credit_score', 500),
                record.get('vehicle_value', 20000),
                record.get('premium_amount', 1000),
                record.get('claim_amount', 0),
                1 if record.get('fraud_flag', False) else 0
            ]
            X.append(features)
        return np.array(X)

    def prepare_labels(self, data):
        """Prepare labels for ML model"""
        y = [record.get('decision', 'Accept_Standard') for record in data]
        return np.array(y)

    def train(self, data):
        """Train the ML model"""
        print("Training ML model...")

        # Prepare data
        X = self.prepare_features(data)
        y = self.prepare_labels(data)

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        # Train model
        if xgb_available:
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        else:
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            )

        self.model.fit(X_train, y_train)

        # Validate
        y_pred = self.model.predict(X_val)
        val_accuracy = accuracy_score(y_val, y_pred)

        print(f"  Validation accuracy: {val_accuracy:.4f}")

        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            print(f"\n  Feature importance:")
            for name, imp in zip(self.feature_names, importance):
                print(f"    {name}: {imp:.4f}")

        return val_accuracy

    def evaluate(self, applicant):
        """
        Evaluate an application using ML model

        Returns:
            dict: {decision, risk_score, confidence, reasons}
        """
        # Prepare features
        features = np.array([[
            applicant.get('age', 30),
            applicant.get('credit_score', 500),
            applicant.get('vehicle_value', 20000),
            applicant.get('premium_amount', 1000),
            applicant.get('claim_amount', 0),
            1 if applicant.get('fraud_flag', False) else 0
        ]])

        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        # Decode label
        decision = self.label_encoder.inverse_transform([prediction])[0]

        # Get confidence
        confidence = max(probabilities)

        # Calculate risk score (inverse of confidence for high-risk decisions)
        if decision == 'Reject':
            risk_score = 70 + (1 - confidence) * 30
        elif decision == 'Accept_with_Surcharge':
            risk_score = 50 + (1 - confidence) * 20
        else:
            risk_score = 30 * (1 - confidence)

        reasons = ['ML-based decision']
        if applicant.get('fraud_flag', False):
            reasons.append('Fraud indicator present')

        return {
            'decision': decision,
            'risk_score': risk_score,
            'confidence': confidence,
            'reasons': reasons,
            'baseline': 'B2_ml'
        }


def run_baseline_b2(data_path):
    """Run baseline B2 on the dataset"""

    print("=" * 60)
    print("Baseline B2: ML-Based Underwriting")
    print("=" * 60)

    if not sklearn_available:
        print("ERROR: scikit-learn not available")
        return None, 0

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records")

    # Initialize underwriter
    underwriter = MLUnderwriter()

    # Train model
    val_accuracy = underwriter.train(data)

    # Evaluate all records
    results = []
    correct = 0
    for record in data:
        # Prepare applicant data
        applicant = {
            'age': record.get('age'),
            'credit_score': record.get('credit_score'),
            'vehicle_value': record.get('vehicle_value'),
            'premium_amount': record.get('premium_amount'),
            'claim_amount': record.get('claim_amount'),
            'fraud_flag': record.get('fraud_flag'),
        }

        # Evaluate
        result = underwriter.evaluate(applicant)
        result['true_decision'] = record.get('decision')
        result['application_id'] = record.get('application_id')

        # Check accuracy
        if result['decision'] == result['true_decision']:
            correct += 1

        results.append(result)

    # Calculate metrics
    accuracy = correct / len(data)

    # Print results
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Correct: {correct}/{len(data)}")

    # Decision distribution
    decisions = [r['decision'] for r in results]
    print(f"\nDecision distribution:")
    for decision in set(decisions):
        count = decisions.count(decision)
        pct = count / len(data) * 100
        print(f"  {decision}: {count} ({pct:.1f}%)")

    # Risk score distribution
    risk_scores = [r['risk_score'] for r in results]
    print(f"\nRisk score statistics:")
    print(f"  Mean: {sum(risk_scores)/len(risk_scores):.2f}")
    print(f"  Min: {min(risk_scores):.2f}")
    print(f"  Max: {max(risk_scores):.2f}")

    # Save results
    output_path = Path("experiments/baselines/baseline_b2_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")

    # Save model
    model_path = Path("models/underwriter_model.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(underwriter, f)
    print(f"Model saved to {model_path}")

    return results, accuracy


if __name__ == "__main__":
    data_path = "data/processed/labeled_research_data.json"
    results, accuracy = run_baseline_b2(data_path)
