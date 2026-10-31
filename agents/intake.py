"""
Agent 1: Intake/Validation Agent
Validates application completeness and normalizes data
"""

import json
from pathlib import Path
from typing import Dict, List

class IntakeAgent:
    """Intake and validation agent"""

    def __init__(self):
        self.required_fields = [
            'age', 'credit_score', 'vehicle_value', 'premium_amount',
            'claim_amount', 'fraud_flag'
        ]
        self.valid_regions = ['North', 'South', 'East', 'West']
        self.valid_genders = ['Male', 'Female', 'Other']

    def validate(self, application: Dict) -> Dict:
        """
        Validate an application

        Returns:
            dict: {is_valid, missing_fields, errors, normalized_data}
        """
        missing_fields = []
        errors = []
        normalized = application.copy()

        # Check required fields
        for field in self.required_fields:
            if field not in application or application[field] is None:
                missing_fields.append(field)

        # Validate age
        if 'age' in application:
            age = application['age']
            if not isinstance(age, (int, float)) or age < 18 or age > 100:
                errors.append(f"Invalid age: {age}")
                normalized['age'] = 30  # Default value

        # Validate credit score
        if 'credit_score' in application:
            credit = application['credit_score']
            if not isinstance(credit, (int, float)) or credit < 300 or credit > 850:
                errors.append(f"Invalid credit score: {credit}")
                normalized['credit_score'] = 500  # Default value

        # Validate region
        if 'region' in application:
            region = application['region']
            if region not in self.valid_regions:
                errors.append(f"Invalid region: {region}")
                normalized['region'] = 'North'  # Default value

        # Validate gender
        if 'gender' in application:
            gender = application['gender']
            if gender not in self.valid_genders:
                errors.append(f"Invalid gender: {gender}")
                normalized['gender'] = 'Other'  # Default value

        is_valid = len(missing_fields) == 0 and len(errors) == 0

        return {
            'is_valid': is_valid,
            'missing_fields': missing_fields,
            'errors': errors,
            'normalized_data': normalized,
            'agent': 'intake',
            'confidence': 1.0 if is_valid else 0.5
        }


def test_intake_agent():
    """Test the intake agent"""
    print("=" * 60)
    print("Testing Intake Agent")
    print("=" * 60)

    agent = IntakeAgent()

    # Test 1: Valid application
    valid_app = {
        'age': 35,
        'gender': 'Male',
        'region': 'North',
        'credit_score': 650,
        'vehicle_value': 25000,
        'premium_amount': 1200,
        'claim_amount': 5000,
        'fraud_flag': False
    }

    result = agent.validate(valid_app)
    print(f"\nTest 1 - Valid application:")
    print(f"  Is valid: {result['is_valid']}")
    print(f"  Missing fields: {result['missing_fields']}")
    print(f"  Errors: {result['errors']}")

    # Test 2: Invalid application
    invalid_app = {
        'age': 150,  # Invalid
        'credit_score': 200,  # Invalid
        'region': 'Mars',  # Invalid
        'gender': 'Alien',  # Invalid
        'vehicle_value': 25000,
        'premium_amount': 1200,
        'claim_amount': 5000,
        'fraud_flag': False
    }

    result = agent.validate(invalid_app)
    print(f"\nTest 2 - Invalid application:")
    print(f"  Is valid: {result['is_valid']}")
    print(f"  Missing fields: {result['missing_fields']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Normalized age: {result['normalized_data']['age']}")
    print(f"  Normalized credit_score: {result['normalized_data']['credit_score']}")

    print("\n" + "=" * 60)
    print("Intake Agent Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_intake_agent()
