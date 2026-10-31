"""
Fairness Agent: Checks for bias and ensures fair decisions
Implements fairness metrics and bias mitigation
"""

import json
from pathlib import Path
from collections import Counter

class FairnessAgent:
    """Monitors fairness and detects bias in decisions"""

    def __init__(self):
        self.fairness_thresholds = {
            'demographic_parity_diff': 0.1,  # Max 10% difference
            'equal_opportunity_diff': 0.1,
            'disparate_impact_ratio': 0.8  # Min 80% ratio
        }
        print("[OK] Fairness Agent initialized")

    def process(self, application, decision_result):
        """Check fairness of this decision"""

        result = {
            'agent': 'Fairness',
            'fairness_checks': [],
            'bias_detected': False,
            'bias_factors': [],
            'recommendations': []
        }

        # Check for age-based bias
        age = application.get('age', 30)
        decision = decision_result['final_decision']

        if age < 25 and decision == 'Reject':
            result['fairness_checks'].append('Age-based bias check: Young driver rejected')
            result['bias_factors'].append('Potential age discrimination for young drivers')
            result['bias_detected'] = True
            result['recommendations'].append('Review age-based rejection patterns')

        if age > 65 and decision == 'Reject':
            result['fairness_checks'].append('Age-based bias check: Senior driver rejected')
            result['bias_factors'].append('Potential age discrimination for senior drivers')
            result['bias_detected'] = True
            result['recommendations'].append('Review age-based rejection patterns')

        # Check for credit score impact (proxy for socioeconomic status)
        credit = application.get('credit_score', 500)
        if credit < 500 and decision == 'Reject':
            result['fairness_checks'].append('Credit score bias check: Low credit rejected')
            result['bias_factors'].append('Potential socioeconomic bias')
            result['recommendations'].append('Ensure credit score is not sole rejection factor')

        # Overall fairness assessment
        if not result['bias_detected']:
            result['fairness_checks'].append('No bias detected in this decision')

        return result

    def calculate_batch_fairness(self, results):
        """Calculate fairness metrics across a batch of decisions"""

        decisions_by_age = {}
        decisions_by_credit = {}

        for r in results:
            age = r.get('age', 30)
            credit = r.get('credit_score', 500)
            decision = r.get('final_decision')

            # Age groups
            if age < 25:
                age_group = 'young'
            elif age > 65:
                age_group = 'senior'
            else:
                age_group = 'adult'

            if age_group not in decisions_by_age:
                decisions_by_age[age_group] = []
            decisions_by_age[age_group].append(decision)

            # Credit groups
            if credit < 500:
                credit_group = 'low'
            elif credit < 700:
                credit_group = 'medium'
            else:
                credit_group = 'high'

            if credit_group not in decisions_by_credit:
                decisions_by_credit[credit_group] = []
            decisions_by_credit[credit_group].append(decision)

        # Calculate rejection rates
        fairness_metrics = {}

        for group, decisions in decisions_by_age.items():
            reject_rate = decisions.count('Reject') / len(decisions)
            fairness_metrics[f'age_{group}_reject_rate'] = reject_rate

        for group, decisions in decisions_by_credit.items():
            reject_rate = decisions.count('Reject') / len(decisions)
            fairness_metrics[f'credit_{group}_reject_rate'] = reject_rate

        # Demographic parity difference
        if 'young' in decisions_by_age and 'adult' in decisions_by_age:
            young_reject = decisions_by_age['young'].count('Reject') / len(decisions_by_age['young'])
            adult_reject = decisions_by_age['adult'].count('Reject') / len(decisions_by_age['adult'])
            fairness_metrics['demographic_parity_diff_age'] = abs(young_reject - adult_reject)

        return fairness_metrics
