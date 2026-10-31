"""
Baseline B4 Extended: Complete Multi-Agent Pipeline
Implements all specialized agents with the trained XGBoost model
"""

import json
import numpy as np
from pathlib import Path
import xgboost as xgb
import pickle
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.document_agent import DocumentAgent
from agents.external_agent import ExternalAgent
from agents.claims_agent import ClaimsAgent


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
    """Aggregates all inputs and makes final decision"""

    def process(self, application, all_agent_results):
        """Aggregate and make final decision"""
        risk_result = all_agent_results['risk']
        customer_result = all_agent_results['customer']
        document_result = all_agent_results['document']
        external_result = all_agent_results['external']
        claims_result = all_agent_results['claims']

        # Start with ML decision
        final_decision = risk_result['decision']
        reasons = ['ML-based primary decision']

        # Override based on document exclusions
        if document_result['exclusions']:
            final_decision = 'Reject'
            reasons.append(f"Document exclusions: {', '.join(document_result['exclusions'])}")

        # Consider fraud indicators from claims
        if claims_result['fraud_indicators']:
            reasons.append(f"Claims fraud indicators: {', '.join(claims_result['fraud_indicators'])}")
            if len(claims_result['fraud_indicators']) >= 2:
                final_decision = 'Reject'
                reasons.append('Multiple fraud indicators triggered rejection')

        # Consider external risk factors
        if external_result['risk_adjustments']:
            reasons.append(f"External risk adjustments: {', '.join(external_result['risk_adjustments'])}")

        # Calculate final risk score
        final_risk_score = risk_result['risk_score']

        # Adjust based on exclusions
        if document_result['exclusions']:
            final_risk_score += 20

        # Adjust based on fraud indicators
        final_risk_score += len(claims_result['fraud_indicators']) * 10

        # Adjust based on external factors
        final_risk_score += len(external_result['risk_adjustments']) * 5

        final_risk_score = min(final_risk_score, 100)

        return {
            'agent': 'Decision',
            'final_decision': final_decision,
            'final_risk_score': final_risk_score,
            'confidence': risk_result['confidence'],
            'reasons': reasons,
            'ml_decision': risk_result['decision'],
            'customer_band': customer_result['credit_band'],
            'exclusions_found': len(document_result['exclusions']),
            'fraud_indicators': len(claims_result['fraud_indicators'])
        }


class ExtendedMultiAgentPipeline:
    """Complete multi-agent pipeline with all specialized agents"""

    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.customer_agent = CustomerAgent()
        self.risk_agent = RiskAgent()
        self.document_agent = DocumentAgent()
        self.external_agent = ExternalAgent()
        self.claims_agent = ClaimsAgent()
        self.decision_agent = DecisionAgent()
        print("[OK] Extended Multi-Agent Pipeline initialized")

    def evaluate(self, application):
        """Run complete pipeline"""
        # Step 1: Intake
        intake_result = self.intake_agent.process(application)

        # Step 2: Customer analysis
        customer_result = self.customer_agent.process(application, intake_result)

        # Step 3: Risk evaluation (ML)
        risk_result = self.risk_agent.process(application, intake_result, customer_result)

        # Step 4: Document analysis
        document_result = self.document_agent.process(application, risk_result)

        # Step 5: External information
        external_result = self.external_agent.process(application)

        # Step 6: Claims history
        claims_result = self.claims_agent.process(application)

        # Step 7: Final decision
        all_results = {
            'intake': intake_result,
            'customer': customer_result,
            'risk': risk_result,
            'document': document_result,
            'external': external_result,
            'claims': claims_result
        }
        decision_result = self.decision_agent.process(application, all_results)

        # Aggregate all results
        result = {
            'baseline': 'B4_extended_pipeline',
            'application_id': application.get('application_id'),
            'final_decision': decision_result['final_decision'],
            'risk_score': decision_result['final_risk_score'],
            'confidence': decision_result['confidence'],
            'reasons': decision_result['reasons'],
            'pipeline_steps': all_results,
            'decision_summary': decision_result
        }

        return result


def run_baseline_b4_extended(data_path):
    """Run extended baseline B4 on the dataset"""

    print("=" * 60)
    print("Baseline B4 Extended: Complete Multi-Agent Pipeline")
    print("=" * 60)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records")

    # Initialize pipeline
    pipeline = ExtendedMultiAgentPipeline()

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
            'location': 'suburban',  # Simulated
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

    # Exclusions found
    exclusions_count = sum(1 for r in results if r['decision_summary']['exclusions_found'] > 0)
    print(f"\nExclusions found: {exclusions_count} ({exclusions_count/len(data)*100:.1f}%)")

    # Fraud indicators
    fraud_count = sum(1 for r in results if r['decision_summary']['fraud_indicators'] > 0)
    print(f"Fraud indicators detected: {fraud_count} ({fraud_count/len(data)*100:.1f}%)")

    # Save results
    output_path = Path("experiments/baselines/baseline_b4_extended_results.json")
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
    results, accuracy = run_baseline_b4_extended(data_path)
