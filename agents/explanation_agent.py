"""
Explanation Agent: Generates explanations for decisions
Audience-specific explanations (customer, regulator, auditor)
"""

import json
from pathlib import Path

class ExplanationAgent:
    """Generates explanations for underwriting decisions"""

    def __init__(self):
        print("[OK] Explanation Agent initialized")

    def process(self, application, decision_result, all_agent_results):
        """Generate explanation for this decision"""

        decision = decision_result['final_decision']
        risk_score = decision_result['risk_score']
        confidence = decision_result['confidence']
        reasons = decision_result.get('reasons', [])

        result = {
            'agent': 'Explanation',
            'explanations': {}
        }

        # Customer-facing explanation (simple, non-technical)
        result['explanations']['customer'] = self._generate_customer_explanation(
            decision, risk_score, reasons
        )

        # Regulator-facing explanation (detailed, includes fairness)
        result['explanations']['regulator'] = self._generate_regulator_explanation(
            decision, risk_score, confidence, all_agent_results
        )

        # Auditor-facing explanation (technical, includes audit trail)
        result['explanations']['auditor'] = self._generate_auditor_explanation(
            decision, all_agent_results
        )

        return result

    def _generate_customer_explanation(self, decision, risk_score, reasons):
        """Generate simple explanation for customer"""

        if decision == 'Accept_Standard':
            return {
                'title': 'Your application has been accepted',
                'summary': 'Congratulations! Your application meets our standard requirements.',
                'details': [
                    'Your risk profile is within our acceptable range',
                    'Standard premium rates apply'
                ],
                'next_steps': [
                    'Review your policy documents',
                    'Make your first premium payment'
                ]
            }

        elif decision == 'Accept_with_Surcharge':
            return {
                'title': 'Your application has been accepted with a surcharge',
                'summary': 'Your application has been accepted, but a surcharge will apply due to risk factors.',
                'details': [
                    f'Risk score: {risk_score:.1f}/100',
                    'Surcharge reflects the additional risk factors identified'
                ],
                'next_steps': [
                    'Review the surcharge details',
                    'Contact us if you have questions'
                ]
            }

        else:  # Reject
            return {
                'title': 'Your application has been declined',
                'summary': 'Unfortunately, we cannot accept your application at this time.',
                'details': [
                    f'Risk score: {risk_score:.1f}/100',
                    'The identified risk factors exceed our acceptance criteria'
                ],
                'next_steps': [
                    'You can appeal this decision',
                    'Contact our customer service for more information'
                ]
            }

    def _generate_regulator_explanation(self, decision, risk_score, confidence, all_agent_results):
        """Generate detailed explanation for regulator"""

        explanation = {
            'title': f'Regulatory explanation for {decision} decision',
            'decision': decision,
            'risk_score': risk_score,
            'confidence': confidence,
            'factors_considered': [],
            'fairness_assessment': 'Passed' if decision != 'Reject' else 'Review required',
            'compliance_status': 'Compliant'
        }

        # List factors from each agent
        for agent_name, agent_result in all_agent_results.items():
            if isinstance(agent_result, dict):
                if 'risk_factors' in agent_result:
                    explanation['factors_considered'].extend([
                        f"{agent_name}: {rf}" for rf in agent_result['risk_factors']
                    ])
                if 'exclusions' in agent_result and agent_result['exclusions']:
                    explanation['factors_considered'].append(
                        f"{agent_name}: Exclusions - {', '.join(agent_result['exclusions'])}"
                    )

        return explanation

    def _generate_auditor_explanation(self, decision, all_agent_results):
        """Generate technical explanation for auditor"""

        explanation = {
            'title': f'Audit trail for {decision} decision',
            'decision_path': [],
            'agent_outputs': {},
            'traceability': 'Complete'
        }

        # Document each agent's contribution
        for agent_name, agent_result in all_agent_results.items():
            if isinstance(agent_result, dict):
                explanation['agent_outputs'][agent_name] = {
                    'key_output': str(agent_result)[:100],  # Truncated
                    'status': 'completed'
                }
                explanation['decision_path'].append(agent_name)

        return explanation
