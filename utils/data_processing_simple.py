"""
Phase 1: Data Collection and Preparation - Simplified Version
Uses existing data from the insurance-underwriting-ai-system project
"""

import json
from pathlib import Path
import random

def load_existing_data():
    """
    Load existing data from the insurance project
    """
    print("Loading existing data from insurance project...")

    source_path = Path("C:/DEVELOPER/insurance-underwriting-ai-system/data/json/insurance-claims-enriched.json")

    if source_path.exists():
        with open(source_path, 'r') as f:
            data = json.load(f)

        print(f"   Loaded {len(data)} records")
        return data
    else:
        print("   Source data not found")
        return None


def prepare_research_dataset(data, n_samples=5000):
    """
    Prepare a smaller dataset for research (focus on auto insurance)
    """
    print(f"Preparing research dataset with {n_samples} samples...")

    # Filter for auto claims only
    auto_data = [d for d in data if d.get('caseType') == 'auto']

    print(f"   Found {len(auto_data)} auto claims")

    # Sample n_samples
    if len(auto_data) > n_samples:
        auto_data = random.sample(auto_data, n_samples)

    # Transform to research format
    research_data = []
    for i, case in enumerate(auto_data):
        record = {
            'application_id': i + 1,
            'age': case.get('applicant', {}).get('age', 30),
            'gender': case.get('applicant', {}).get('gender', 'Unknown'),
            'region': case.get('applicant', {}).get('region', 'Unknown'),
            'credit_score': case.get('applicant', {}).get('creditScore', 500),
            'vehicle_value': case.get('policy', {}).get('coverageAmount', 20000),
            'premium_amount': case.get('policy', {}).get('premiumAmount', 1000),
            'claim_amount': case.get('claim', {}).get('claimAmount', 0),
            'fraud_flag': case.get('riskAssessment', {}).get('fraudFlag', False),
            'fraud_risk_score': case.get('riskAssessment', {}).get('fraudRiskScore', 0),
            'features': case.get('features', {}),
        }
        research_data.append(record)

    # Save to processed data
    output_path = Path("data/processed/research_dataset.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(research_data, f, indent=2)

    print(f"   Prepared {len(research_data)} research records")
    print(f"   Saved to {output_path}")

    return research_data


def construct_labels(data):
    """
    Construct underwriting decision labels
    Rule: Based on fraud risk score
    - fraud_risk_score > 70 -> Reject
    - fraud_risk_score > 50 -> Accept with Surcharge
    - fraud_risk_score <= 50 -> Accept Standard
    """
    print("Constructing underwriting decision labels...")

    for record in data:
        fraud_score = record.get('fraud_risk_score', 0)

        if fraud_score > 70:
            record['decision'] = 'Reject'
            record['risk_level'] = 'High'
        elif fraud_score > 50:
            record['decision'] = 'Accept_with_Surcharge'
            record['risk_level'] = 'Medium'
        else:
            record['decision'] = 'Accept_Standard'
            record['risk_level'] = 'Low'

    # Count distribution
    decisions = [r['decision'] for r in data]
    print(f"   Decision distribution:")
    for decision in set(decisions):
        count = decisions.count(decision)
        pct = count / len(data) * 100
        print(f"      {decision}: {count} ({pct:.1f}%)")

    # Save labeled data
    output_path = Path("data/processed/labeled_research_data.json")
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"   Saved to {output_path}")

    return data


def main():
    """Main data preparation pipeline"""

    print("=" * 60)
    print("Phase 1: Data Collection and Preparation")
    print("=" * 60)

    # Load existing data
    data = load_existing_data()

    if data is None:
        print("Cannot proceed without source data")
        return

    # Prepare research dataset
    research_data = prepare_research_dataset(data, n_samples=5000)

    # Construct labels
    labeled_data = construct_labels(research_data)

    print("\n" + "=" * 60)
    print("Phase 1 Complete: Data ready for modeling")
    print("=" * 60)
    print(f"\nDataset size: {len(labeled_data)} records")
    print(f"Location: data/processed/labeled_research_data.json")


if __name__ == "__main__":
    main()
