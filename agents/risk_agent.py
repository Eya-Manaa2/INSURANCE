"""
Risk Agent: Evaluates risk using trained ML model
"""

import numpy as np
from pathlib import Path
import xgboost as xgb
import pickle

class RiskAgent:
    """Evaluates risk using trained ML model"""

    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self._load_model()

    def _load_model(self):
        """Load the trained XGBoost model"""
        model_path = Path("models/underwriter_xgboost_model.json")
        encoder_path = Path("models/label_encoder.pkl")
        features_path = Path("models/feature_names.pkl")

        if model_path.exists():
            self.model = xgb.XGBClassifier()
            self.model.load_model(str(model_path))
            print("[OK] Risk Agent: Model loaded")

        if encoder_path.exists():
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)

        if features_path.exists():
            with open(features_path, 'rb') as f:
                self.feature_names = pickle.load(f)

    def process(self, application, intake_result, customer_result):
        """Evaluate risk using ML model"""
        if self.model is None:
            return {
                'agent': 'Risk',
                'decision': 'Error',
                'risk_score': 0,
                'confidence': 0,
                'error': 'Model not loaded'
            }

        # Prepare features
        features = np.array([[
            application.get('age', 30),
            application.get('credit_score', 500),
            application.get('vehicle_value', 20000),
            application.get('premium_amount', 1000),
            application.get('claim_amount', 0),
            1 if application.get('fraud_flag', False) else 0
        ]])

        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]

        # Decode label
        decision = self.label_encoder.inverse_transform([prediction])[0]

        # Get confidence
        confidence = max(probabilities)

        # Calculate risk score
        if decision == 'Reject':
            risk_score = 70 + (1 - confidence) * 30
        elif decision == 'Accept_with_Surcharge':
            risk_score = 50 + (1 - confidence) * 20
        else:
            risk_score = 30 * (1 - confidence)

        return {
            'agent': 'Risk',
            'decision': decision,
            'risk_score': risk_score,
            'confidence': confidence,
            'ml_probabilities': {
                'Accept_Standard': float(probabilities[0]),
                'Accept_with_Surcharge': float(probabilities[1]),
                'Reject': float(probabilities[2])
            }
        }
