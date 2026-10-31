"""
Recreate dataset with improved label construction (same logic as Colab)
"""

import json
from pathlib import Path

def construct_improved_labels(data):
    """
    Improved label construction using multiple criteria
    (Same logic as used in Colab)
    """
    for record in data:
        fraud_score = record.get('fraud_risk_score', 0)
        claim_amount = record.get('claim_amount', 0)
        premium = record.get('premium_amount', 1000)
        credit = record.get('credit_score', 500)
        fraud_flag = record.get('fraud_flag', False)
        
        # Multiple criteria
        claim_to_premium_ratio = claim_amount / premium if premium > 0 else 0
        high_claim = claim_amount > 15000
        poor_credit = credit < 550
        recent_claim = fraud_flag
        
        # Decision logic (more nuanced)
        if fraud_score > 80 or (fraud_flag and claim_amount > 10000):
            record['decision'] = 'Reject'
            record['risk_level'] = 'Very High'
        elif fraud_score > 60 or (high_claim and poor_credit):
            record['decision'] = 'Accept_with_Surcharge'
            record['risk_level'] = 'High'
        elif claim_to_premium_ratio > 5 or (fraud_score > 40 and poor_credit):
            record['decision'] = 'Accept_with_Surcharge'
            record['risk_level'] = 'Medium'
        else:
            record['decision'] = 'Accept_Standard'
            record['risk_level'] = 'Low'

# Load original dataset
data_path = Path("data/processed/labeled_research_data.json")
with open(data_path, 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} records")

# Apply improved labels
construct_improved_labels(data)

# Count distribution
from collections import Counter
decisions = [r['decision'] for r in data]
print("\nNew label distribution:")
for decision, count in Counter(decisions).items():
    pct = count / len(data) * 100
    print(f"  {decision}: {count} ({pct:.1f}%)")

# Save updated dataset
output_path = Path("data/processed/labeled_research_data_improved.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\nUpdated dataset saved to {output_path}")
