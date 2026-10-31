"""
Customer Agent: Analyzes customer profile and history
"""

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
