"""
Baseline B4: Sequential Multi-Agent Pipeline for Underwriting
Implements a sequential pipeline with specialized agents
Uses the trained XGBoost model in the Risk Agent
"""

import json
import numpy as np
from pathlib import Path
import xgboost as xgb
import pickle
from collections import Counter
import copy

class IntakeAgent:
    """Validates and prepares application data"""

    def process(self, application):
        """Validate and standardize application data"""
        result = {
            'agent': 'Intake',
            'status': 'validated',
            'warnings': [],
            'prepared_data': {}
        }

        # Validate required fields
        required_fields = ['age', 'credit_score', 'vehicle_value', 'premium_amount', 'claim_amount']
        for field in required_fields:
            if field not in application or application[field] is None:
                result['warnings'].append(f"Missing field: {field}")
                result['prepared_data'][field] = 0
            else:
                result['prepared_data'][field] = application[field]

        # Prepare fraud flag
        result['prepared_data']['fraud_flag'] = application.get('fraud_flag', False)

        # Check for anomalies
        if application.get('age', 0) < 18:
            result['warnings'].append("Applicant under 18 years old")

        if application.get('credit_score', 0) < 300:
            result['warnings'].append("Credit score below minimum")

        return result


class CustomerAgent:
    """Analyzes customer profile and history"""

    def process(self, application, intake_result):
        """Analyze customer profile"""
        age = application.get('age', 30)
        credit = application.get('credit_score', 500)
        fraud_flag = application.get('fraud_flag', False)

        result = {
            'agent': 'Customer',
            'risk_factors': [],
            'credit_band': 'Medium'
        }

        # Credit banding
        if credit >= 700:
            result['credit_band'] = 'Excellent'
        elif credit >= 600:
            result['credit_band'] = 'Good'
        elif credit >= 500:
            result['credit_band'] = 'Medium'
        else:
            result['credit_band'] = 'Poor'
            result['risk_factors'].append('Poor credit score')

        # Age-based risk
        if age < 25:
            result['risk_factors'].append('Young driver (<25)')
        elif age > 65:
            result['risk_factors'].append('Senior driver (>65)')

        # Fraud indicator
        if fraud_flag:
            result['risk_factors'].append('Fraud indicator present')

        return result


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


class DecisionAgent:
    """Aggregates inputs and makes final decision"""

    def process(self, application, intake_result, customer_result, risk_result):
        """Aggregate and make final decision"""
        # Start with ML decision
        final_decision = risk_result['decision']
        reasons = ['ML-based primary decision']

        # Override based on warnings
        if intake_result['warnings']:
            reasons.append(f"Intake warnings: {', '.join(intake_result['warnings'])}")

        # Consider customer risk factors
        if customer_result['risk_factors']:
            reasons.append(f"Customer risk factors: {', '.join(customer_result['risk_factors'])}")

            # Escalate to surcharge if poor credit and ML says standard
            if (customer_result['credit_band'] == 'Poor' and
                final_decision == 'Accept_Standard'):
                final_decision = 'Accept_with_Surcharge'
                reasons.append('Escalated to surcharge due to poor credit')

        # Calculate final risk score
        final_risk_score = risk_result['risk_score']

        # Adjust based on warnings
        if intake_result['warnings']:
            final_risk_score += 10

        if customer_result['risk_factors']:
            final_risk_score += len(customer_result['risk_factors']) * 5

        final_risk_score = min(final_risk_score, 100)

        return {
            'agent': 'Decision',
            'final_decision': final_decision,
            'final_risk_score': final_risk_score,
            'confidence': risk_result['confidence'],
            'reasons': reasons,
            'ml_decision': risk_result['decision'],
            'customer_band': customer_result['credit_band']
        }


class MultiAgentPipeline:
    """Sequential multi-agent pipeline for underwriting"""

    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.customer_agent = CustomerAgent()
        self.risk_agent = RiskAgent()
        self.decision_agent = DecisionAgent()
        print("[OK] Multi-Agent Pipeline initialized")

    def evaluate(self, application):
        """Run sequential pipeline"""
        # Step 1: Intake
        intake_result = self.intake_agent.process(application)

        # Step 2: Customer analysis
        customer_result = self.customer_agent.process(application, intake_result)

        # Step 3: Risk evaluation (ML)
        risk_result = self.risk_agent.process(application, intake_result, customer_result)

        # Step 4: Final decision
        decision_result = self.decision_agent.process(
            application, intake_result, customer_result, risk_result
        )

        # Aggregate all results
        result = {
            'baseline': 'B4_multi_agent_pipeline',
            'application_id': application.get('application_id'),
            'final_decision': decision_result['final_decision'],
            'risk_score': decision_result['final_risk_score'],
            'confidence': decision_result['confidence'],
            'reasons': decision_result['reasons'],
            'pipeline_steps': {
                'intake': intake_result,
                'customer': customer_result,
                'risk': risk_result,
                'decision': decision_result
            }
        }

        return result


def run_baseline_b4(data_path):
    """Run baseline B4 on the dataset"""

    print("=" * 60)
    print("Baseline B4: Sequential Multi-Agent Pipeline")
    print("=" * 60)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records")

    # Initialize pipeline
    pipeline = MultiAgentPipeline()

    # Evaluate all records
    results = []
    correct = 0

    for i, record in enumerate(data):
        if (i + 1) % 500 == 0:
            print(f"Processing {i+1}/{len(data)}...")

        # Prepare application data
        application = {
            'application_id': record.get('application_id'),
            'age': record.get('age'),
            'credit_score': record.get('credit_score'),
            'vehicle_value': record.get('vehicle_value'),
            'premium_amount': record.get('premium_amount'),
            'claim_amount': record.get('claim_amount'),
            'fraud_flag': record.get('fraud_flag'),
        }

        # Evaluate
        result = pipeline.evaluate(application)
        result['true_decision'] = record.get('decision')

        # Check accuracy
        if result['final_decision'] == result['true_decision']:
            correct += 1

        results.append(result)

    # Calculate metrics
    accuracy = correct / len(data)

    # Print results
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Correct: {correct}/{len(data)}")

    # Decision distribution
    decisions = [r['final_decision'] for r in results]
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

    # Save results
    output_path = Path("experiments/baselines/baseline_b4_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert numpy types for JSON (deep conversion)
    def convert_to_serializable(obj):
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        else:
            return obj

    serializable_results = [convert_to_serializable(r) for r in results]

    with open(output_path, 'w') as f:
        json.dump(serializable_results, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return results, accuracy


if __name__ == "__main__":
    data_path = "data/processed/labeled_research_data_improved.json"
    results, accuracy = run_baseline_b4(data_path)
