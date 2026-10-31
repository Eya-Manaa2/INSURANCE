"""
Intake Agent: Validates and prepares application data
"""

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
