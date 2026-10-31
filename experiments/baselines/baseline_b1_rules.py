"""
Baseline B1: Rule-Based Underwriting
Simple if-then rules for underwriting decisions
"""

import json
from pathlib import Path

class RuleBasedUnderwriter:
    """Rule-based underwriting baseline"""

    def __init__(self):
        self.rules = {
            'age_young_threshold': 25,
            'age_senior_threshold': 65,
            'credit_poor_threshold': 550,
            'credit_excellent_threshold': 700,
            'claim_amount_high_threshold': 10000,
            'vehicle_value_low_threshold': 5000,
        }

    def evaluate(self, applicant):
        """
        Evaluate an application using rule-based logic

        Returns:
            dict: {decision, risk_score, confidence, reasons}
        """
        reasons = []
        risk_score = 0
        max_risk = 100

        # Age-based rules
        age = applicant.get('age', 30)
        if age < self.rules['age_young_threshold']:
            risk_score += 20
            reasons.append('Young driver (<25)')
        elif age > self.rules['age_senior_threshold']:
            risk_score += 15
            reasons.append('Senior driver (>65)')

        # Credit score rules
        credit = applicant.get('credit_score', 500)
        if credit < self.rules['credit_poor_threshold']:
            risk_score += 30
            reasons.append('Poor credit score')
        elif credit > self.rules['credit_excellent_threshold']:
            risk_score -= 10
            reasons.append('Excellent credit score')

        # Vehicle value rules
        vehicle_value = applicant.get('vehicle_value', 20000)
        if vehicle_value < self.rules['vehicle_value_low_threshold']:
            risk_score += 10
            reasons.append('Low value vehicle')

        # Claim amount rules
        claim_amount = applicant.get('claim_amount', 0)
        if claim_amount > self.rules['claim_amount_high_threshold']:
            risk_score += 25
            reasons.append('High claim amount')

        # Fraud flag
        if applicant.get('fraud_flag', False):
            risk_score += 50
            reasons.append('Fraud indicator present')

        # Normalize risk score
        risk_score = min(risk_score, max_risk)

        # Decision based on risk score
        if risk_score > 70:
            decision = 'Reject'
            confidence = 0.8
        elif risk_score > 50:
            decision = 'Accept_with_Surcharge'
            confidence = 0.7
        else:
            decision = 'Accept_Standard'
            confidence = 0.85

        return {
            'decision': decision,
            'risk_score': risk_score,
            'confidence': confidence,
            'reasons': reasons,
            'baseline': 'B1_rules'
        }


def run_baseline_b1(data_path):
    """Run baseline B1 on the dataset"""

    print("=" * 60)
    print("Baseline B1: Rule-Based Underwriting")
    print("=" * 60)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records")

    # Initialize underwriter
    underwriter = RuleBasedUnderwriter()

    # Evaluate all records
    results = []
    correct = 0
    for record in data:
        # Prepare applicant data
        applicant = {
            'age': record.get('age'),
            'credit_score': record.get('credit_score'),
            'vehicle_value': record.get('vehicle_value'),
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
    output_path = Path("experiments/baselines/baseline_b1_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return results, accuracy


if __name__ == "__main__":
    data_path = "data/processed/labeled_research_data.json"
    results, accuracy = run_baseline_b1(data_path)
