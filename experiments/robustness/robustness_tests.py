"""
Robustness Tests
- Missing fields
- Noise perturbations
- Out of distribution samples
"""

import json
import numpy as np
from pathlib import Path
import sys
import os

# Add agents directory to path
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'agents'))
sys.path.append(agents_dir)

from risk_agent import RiskAgent


def test_missing_fields(data_path):
    """Test robustness to missing fields"""

    print("=" * 60)
    print("Robustness Test: Missing Fields")
    print("=" * 60)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Initialize agent
    risk_agent = RiskAgent()

    # Test scenarios
    scenarios = [
        {'name': 'Missing age', 'remove': 'age'},
        {'name': 'Missing credit_score', 'remove': 'credit_score'},
        {'name': 'Missing vehicle_value', 'remove': 'vehicle_value'},
        {'name': 'Missing premium_amount', 'remove': 'premium_amount'},
        {'name': 'Missing claim_amount', 'remove': 'claim_amount'},
        {'name': 'Missing fraud_flag', 'remove': 'fraud_flag'},
    ]

    results = {}

    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")

        correct = 0
        total = len(data)

        for record in data:
            # Create application with missing field
            application = {
                'application_id': record.get('application_id'),
                'age': record.get('age'),
                'credit_score': record.get('credit_score'),
                'vehicle_value': record.get('vehicle_value'),
                'premium_amount': record.get('premium_amount'),
                'claim_amount': record.get('claim_amount'),
                'fraud_flag': record.get('fraud_flag'),
                'location': 'suburban',
            }

            # Remove field
            field_to_remove = scenario['remove']
            if field_to_remove in application:
                del application[field_to_remove]

            # Process
            intake_result = {'valid': True, 'missing_fields': [field_to_remove]}
            customer_result = {'credit_risk': 'medium'}
            risk_result = risk_agent.process(application, intake_result, customer_result)

            # Evaluate
            if risk_result['decision'] == record.get('decision'):
                correct += 1

        accuracy = correct / total
        results[scenario['name']] = accuracy
        print(f"  Accuracy: {accuracy:.4f} ({correct}/{total})")

    return results


def test_noise_perturbation(data_path):
    """Test robustness to noise perturbations"""

    print("\n" + "=" * 60)
    print("Robustness Test: Noise Perturbation")
    print("=" * 60)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Initialize agent
    risk_agent = RiskAgent()

    # Test noise levels
    noise_levels = [0.05, 0.10, 0.20, 0.50]  # 5%, 10%, 20%, 50% noise

    results = {}

    for noise_level in noise_levels:
        print(f"\nNoise level: {noise_level*100:.0f}%")

        correct = 0
        total = len(data)

        for record in data:
            # Create application
            application = {
                'application_id': record.get('application_id'),
                'age': record.get('age'),
                'credit_score': record.get('credit_score'),
                'vehicle_value': record.get('vehicle_value'),
                'premium_amount': record.get('premium_amount'),
                'claim_amount': record.get('claim_amount'),
                'fraud_flag': record.get('fraud_flag'),
                'location': 'suburban',
            }

            # Add noise to numeric fields
            for field in ['age', 'credit_score', 'vehicle_value', 'premium_amount', 'claim_amount']:
                if field in application and application[field] is not None:
                    original = application[field]
                    noise = np.random.normal(0, original * noise_level)
                    application[field] = max(0, original + noise)  # Ensure non-negative

            # Process
            intake_result = {'valid': True}
            customer_result = {'credit_risk': 'medium'}
            risk_result = risk_agent.process(application, intake_result, customer_result)

            # Evaluate
            if risk_result['decision'] == record.get('decision'):
                correct += 1

        accuracy = correct / total
        results[f'noise_{noise_level}'] = accuracy
        print(f"  Accuracy: {accuracy:.4f} ({correct}/{total})")

    return results


def test_out_of_distribution(data_path):
    """Test robustness to out-of-distribution samples"""

    print("\n" + "=" * 60)
    print("Robustness Test: Out-of-Distribution Samples")
    print("=" * 60)

    # Initialize agent
    risk_agent = RiskAgent()

    # Create extreme OOD samples
    ood_samples = [
        {'name': 'Very high value', 'age': 18, 'credit_score': 850, 'vehicle_value': 500000, 'premium_amount': 10000, 'claim_amount': 0, 'fraud_flag': False},
        {'name': 'Very old applicant', 'age': 90, 'credit_score': 300, 'vehicle_value': 5000, 'premium_amount': 500, 'claim_amount': 0, 'fraud_flag': False},
        {'name': 'Very high claims', 'age': 30, 'credit_score': 500, 'vehicle_value': 20000, 'premium_amount': 1000, 'claim_amount': 100000, 'fraud_flag': False},
        {'name': 'Zero premium', 'age': 30, 'credit_score': 500, 'vehicle_value': 20000, 'premium_amount': 0, 'claim_amount': 0, 'fraud_flag': False},
    ]

    results = {}

    for sample in ood_samples:
        print(f"\nSample: {sample['name']}")

        application = {
            'application_id': 99999,
            'age': sample['age'],
            'credit_score': sample['credit_score'],
            'vehicle_value': sample['vehicle_value'],
            'premium_amount': sample['premium_amount'],
            'claim_amount': sample['claim_amount'],
            'fraud_flag': sample['fraud_flag'],
            'location': 'suburban',
        }

        # Process
        intake_result = {'valid': True}
        customer_result = {'credit_risk': 'medium'}
        risk_result = risk_agent.process(application, intake_result, customer_result)

        print(f"  Decision: {risk_result['decision']}")
        print(f"  Confidence: {risk_result['confidence']:.4f}")
        print(f"  Risk Score: {risk_result['risk_score']:.2f}")

        results[sample['name']] = {
            'decision': risk_result['decision'],
            'confidence': risk_result['confidence'],
            'risk_score': risk_result['risk_score']
        }

    return results


def run_all_robustness_tests():
    """Run all robustness tests"""

    data_path = "data/processed/labeled_research_data_improved.json"

    # Set seed for reproducibility
    np.random.seed(42)

    # Run tests
    missing_results = test_missing_fields(data_path)
    noise_results = test_noise_perturbation(data_path)
    ood_results = test_out_of_distribution(data_path)

    # Summary
    print("\n" + "=" * 60)
    print("Robustness Test Summary")
    print("=" * 60)

    print("\nMissing Fields Robustness:")
    for scenario, accuracy in missing_results.items():
        degradation = (0.9740 - accuracy) / 0.9740 * 100  # vs baseline 97.40%
        print(f"  {scenario}: {accuracy:.4f} (degradation: {degradation:.2f}%)")

    print("\nNoise Perturbation Robustness:")
    for noise, accuracy in noise_results.items():
        degradation = (0.9740 - accuracy) / 0.9740 * 100
        print(f"  {noise}: {accuracy:.4f} (degradation: {degradation:.2f}%)")

    print("\nOut-of-Distribution Samples:")
    for sample, result in ood_results.items():
        print(f"  {sample}: {result['decision']} (confidence: {result['confidence']:.4f})")

    return {
        'missing_fields': missing_results,
        'noise_perturbation': noise_results,
        'out_of_distribution': ood_results
    }


if __name__ == "__main__":
    results = run_all_robustness_tests()
