"""
External Agent: Retrieves external information
Geographic risks, weather data, public registries
For this prototype, we simulate external data sources
"""

import json
from pathlib import Path

class ExternalAgent:
    """Retrieves and analyzes external information"""

    def __init__(self):
        # Load simulated external data
        self.geographic_risks = self._load_geographic_risks()
        print("[OK] External Agent initialized")

    def _load_geographic_risks(self):
        """Load simulated geographic risk data"""
        # In production, this would be from external APIs
        return {
            "high_risk_areas": ["flood_zone_a", "flood_zone_b", "earthquake_zone"],
            "crime_rates": {
                "urban": 0.05,
                "suburban": 0.02,
                "rural": 0.01
            }
        }

    def process(self, application):
        """Retrieve and analyze external information"""

        # Simulate location extraction
        location = application.get('location', 'suburban')

        result = {
            'agent': 'External',
            'external_factors': [],
            'risk_adjustments': [],
            'data_sources': []
        }

        # Geographic risk assessment
        if location in self.geographic_risks['high_risk_areas']:
            result['external_factors'].append(f"High-risk geographic area: {location}")
            result['risk_adjustments'].append("Geographic risk premium surcharge")
            result['data_sources'].append("Geographic risk database")

        # Crime rate assessment
        crime_rate = self.geographic_risks['crime_rates'].get(location, 0.02)
        if crime_rate > 0.03:
            result['external_factors'].append(f"High crime rate area: {crime_rate*100:.1f}%")
            result['risk_adjustments'].append("Crime risk premium adjustment")
            result['data_sources'].append("Crime statistics database")

        # Weather risk (simulated)
        # In production, would integrate with weather API
        result['external_factors'].append("Weather risk: normal (historical data)")
        result['data_sources'].append("Historical weather database")

        # Public registry check (simulated)
        # In production, would check sanctions lists, etc.
        result['external_factors'].append("Public registry: clear")
        result['data_sources'].append("Public registries")

        return result
