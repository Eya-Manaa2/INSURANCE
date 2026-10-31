"""
Document Agent: Analyzes policy documents using RAG
In a production system, this would use embeddings and vector search
For this prototype, we simulate RAG with keyword-based retrieval
"""

import json
from pathlib import Path

class DocumentAgent:
    """Analyzes policy documents and conditions"""

    def __init__(self):
        # Load simulated policy knowledge base
        self.knowledge_base = self._load_knowledge_base()
        print("[OK] Document Agent initialized")

    def _load_knowledge_base(self):
        """Load simulated policy knowledge base"""
        # In production, this would be a vector database
        kb = {
            "exclusions": [
                "Fraudulent claims",
                "Unlicensed drivers",
                "Vehicles used for commercial purposes without proper coverage",
                "Intentional damage",
                "Racing or speed competitions"
            ],
            "conditions": [
                "Must maintain valid driver's license",
                "Must report accidents within 30 days",
                "Premium payments must be made on time",
                "Vehicle must be roadworthy",
                "No modifications that increase risk without notification"
            ],
            "coverage_limits": {
                "third_party": 100000,
                "property_damage": 50000,
                "personal_injury": 250000
            }
        }
        return kb

    def process(self, application, risk_result):
        """Analyze application against policy documents"""

        fraud_flag = application.get('fraud_flag', False)
        claim_amount = application.get('claim_amount', 0)
        premium = application.get('premium_amount', 1000)

        result = {
            'agent': 'Document',
            'document_checks': [],
            'exclusions': [],
            'conditions': [],
            'warnings': []
        }

        # Check for fraud exclusion
        if fraud_flag:
            result['exclusions'].append("Fraudulent claims")
            result['warnings'].append("Previous fraud indicator may lead to exclusion")

        # Check claim vs coverage
        if claim_amount > self.knowledge_base['coverage_limits']['third_party']:
            result['warnings'].append(f"Claim amount (${claim_amount}) exceeds third-party coverage limit")

        # Check premium adequacy
        if premium < 500:
            result['conditions'].append("Low premium may indicate under-insurance")

        # Simulate RAG retrieval (in production, would use embeddings)
        relevant_docs = self._retrieve_relevant_documents(application)

        result['document_checks'] = relevant_docs

        return result

    def _retrieve_relevant_documents(self, application):
        """Simulate RAG retrieval"""
        # In production, this would:
        # 1. Convert application to embedding
        # 2. Search vector database for similar cases
        # 3. Return relevant policy sections

        retrieved = []

        claim_amount = application.get('claim_amount', 0)
        if claim_amount > 0:
            retrieved.append({
                'section': 'Claims Process',
                'content': 'Claims must be reported within 30 days of incident',
                'relevance': 0.9
            })

        if application.get('fraud_flag', False):
            retrieved.append({
                'section': 'Exclusions',
                'content': 'Fraudulent claims are excluded from coverage',
                'relevance': 0.95
            })

        return retrieved
