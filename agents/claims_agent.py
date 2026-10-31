"""
Claims Agent: Analyzes claims history and patterns
Frequency, severity, fraud indicators, similarity to known cases
"""

import json
from pathlib import Path
from collections import Counter

class ClaimsAgent:
    """Analyzes claims history and patterns"""

    def __init__(self):
        # Load simulated claims database
        self.claims_database = self._load_claims_database()
        print("[OK] Claims Agent initialized")

    def _load_claims_database(self):
        """Load simulated claims database"""
        # In production, this would be a real database
        return {
            "known_fraud_patterns": [
                "Multiple claims in short time period",
                "Claim amount exactly at coverage limit",
                "Inconsistent incident descriptions",
                "Claims immediately after policy start"
            ],
            "severity_buckets": {
                "low": (0, 5000),
                "medium": (5000, 15000),
                "high": (15000, 50000),
                "severe": (50000, float('inf'))
            }
        }

    def process(self, application):
        """Analyze claims history for this application"""

        claim_amount = application.get('claim_amount', 0)
        fraud_flag = application.get('fraud_flag', False)
        premium = application.get('premium_amount', 1000)

        result = {
            'agent': 'Claims',
            'claims_analysis': {},
            'fraud_indicators': [],
            'severity_assessment': '',
            'similarity_score': 0.0
        }

        # Calculate claim-to-premium ratio
        claim_premium_ratio = claim_amount / premium if premium > 0 else 0
        result['claims_analysis']['claim_premium_ratio'] = claim_premium_ratio

        # Severity assessment
        if claim_amount == 0:
            result['severity_assessment'] = 'No claims'
        elif claim_amount < 5000:
            result['severity_assessment'] = 'Low severity'
        elif claim_amount < 15000:
            result['severity_assessment'] = 'Medium severity'
        elif claim_amount < 50000:
            result['severity_assessment'] = 'High severity'
        else:
            result['severity_assessment'] = 'Severe'

        # Fraud pattern detection
        if fraud_flag:
            result['fraud_indicators'].append("Previous fraud indicator")

        if claim_premium_ratio > 10:
            result['fraud_indicators'].append(f"High claim-to-premium ratio: {claim_premium_ratio:.1f}")

        if claim_amount > 0 and claim_amount % 1000 == 0:
            result['fraud_indicators'].append("Round claim amount (potential fraud)")

        # Similarity to known cases (simulated)
        # In production, would use embeddings to find similar cases
        similarity_score = self._calculate_similarity(application)
        result['similarity_score'] = similarity_score

        if similarity_score > 0.8:
            result['fraud_indicators'].append(f"High similarity to known fraud cases: {similarity_score:.2f}")

        return result

    def _calculate_similarity(self, application):
        """Calculate similarity to known cases (simulated)"""
        # In production, would use embedding similarity
        claim_amount = application.get('claim_amount', 0)
        fraud_flag = application.get('fraud_flag', False)

        similarity = 0.0

        if fraud_flag:
            similarity += 0.5

        if claim_amount > 10000:
            similarity += 0.2

        if claim_amount > 0 and claim_amount % 1000 == 0:
            similarity += 0.1

        return min(similarity, 1.0)
