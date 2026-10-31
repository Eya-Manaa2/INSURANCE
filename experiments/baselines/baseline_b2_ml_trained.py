"""
Baseline B2: ML-Based Underwriting (XGBoost) - Production Version
Uses the trained model from Colab
"""

import json
import pickle
import joblib
import numpy as np
from pathlib import Path
import xgboost as xgb
from collections import Counter

class MLUnderwriter:
    """ML-based underwriting baseline with trained model"""

    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self._load_model()

    def _load_model(self):
        """Load the trained model and encoders"""
        model_path = Path("models/underwriter_xgboost_model.json")
        encoder_path = Path("models/label_encoder.pkl")
        features_path = Path("models/feature_names.pkl")

        if model_path.exists():
            self.model = xgb.XGBClassifier()
            self.model.load_model(str(model_path))
            print("[OK] Model loaded from", model_path)
        else:
            print("[ERROR] Model not found at", model_path)

        if encoder_path.exists():
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            print("[OK] Label encoder loaded from", encoder_path)
        else:
            print("[ERROR] Label encoder not found at", encoder_path)

        if features_path.exists():
            with open(features_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            print("[OK] Feature names loaded from", features_path)
        else:
            print("[ERROR] Feature names not found at", features_path)

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

    def evaluate(self, applicant):
        """
        Evaluate an application using trained ML model

        Returns:
            dict: {decision, risk_score, confidence, reasons}
        """
        if self.model is None:
            return {
                'decision': 'Error',
                'risk_score': 0,
                'confidence': 0,
                'reasons': ['Model not loaded'],
                'baseline': 'B2_ml'
            }

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

        reasons = ['ML-based decision with XGBoost']
        if applicant.get('fraud_flag', False):
            reasons.append('Fraud indicator present')

        return {
            'decision': decision,
            'risk_score': risk_score,
            'confidence': confidence,
            'reasons': reasons,
            'baseline': 'B2_ml',
            'model_metadata': {
                'features': self.feature_names,
                'n_estimators': self.model.n_estimators if hasattr(self.model, 'n_estimators') else 'unknown',
                'max_depth': self.model.max_depth if hasattr(self.model, 'max_depth') else 'unknown'
            }
        }


def run_baseline_b2(data_path):
    """Run baseline B2 on the dataset with trained model"""

    print("=" * 60)
    print("Baseline B2: ML-Based Underwriting (Trained Model)")
    print("=" * 60)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records")

    # Initialize underwriter
    underwriter = MLUnderwriter()

    if underwriter.model is None:
        print("ERROR: Model not loaded. Please ensure model files are in models/")
        return None, 0

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

    # Confidence distribution
    confidences = [r['confidence'] for r in results]
    print(f"\nConfidence statistics:")
    print(f"  Mean: {sum(confidences)/len(confidences):.2f}")
    print(f"  Min: {min(confidences):.2f}")
    print(f"  Max: {max(confidences):.2f}")

    # Save results (convert numpy types to Python types for JSON)
    output_path = Path("experiments/baselines/baseline_b2_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert numpy types to regular Python types
    serializable_results = []
    for r in results:
        r_copy = {}
        for k, v in r.items():
            if isinstance(v, (np.float32, np.float64)):
                r_copy[k] = float(v)
            elif isinstance(v, (np.int32, np.int64)):
                r_copy[k] = int(v)
            else:
                r_copy[k] = v
        serializable_results.append(r_copy)

    with open(output_path, 'w') as f:
        json.dump(serializable_results, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return results, accuracy


if __name__ == "__main__":
    data_path = "data/processed/labeled_research_data_improved.json"
    results, accuracy = run_baseline_b2(data_path)
