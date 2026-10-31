"""
Phase 1: Data Collection and Preparation
Collect and prepare public datasets for auto insurance underwriting
"""

import pandas as pd
import numpy as np
from pathlib import Path
import requests
import zipfile
import io

class DataCollector:
    """Collect public datasets for auto insurance underwriting"""

    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def collect_kaggle_motor_data(self):
        """
        Collect Motor Insurance Data
        Source: Available in existing Data folder
        """
        print("📦 Collecting Motor Insurance Data...")

        # Use existing data from the insurance project
        source_path = Path("C:/DEVELOPER/insurance-underwriting-ai-system/Data/Vehicle Insurance Data")

        if source_path.exists():
            # Copy motor data files
            for file in source_path.glob("*.csv"):
                target = self.data_dir / file.name
                pd.read_csv(file).to_csv(target, index=False)
                print(f"   ✅ Copied {file.name}")
        else:
            print("   ⚠️  Source path not found, will use synthetic data")

    def collect_kaggle_auto_claims(self):
        """
        Collect Auto Insurance Claims Dataset
        Alternative: Generate synthetic data if not available
        """
        print("📦 Collecting Auto Insurance Claims Data...")

        # For now, we'll use the existing fraud detection dataset
        source_path = Path("C:/DEVELOPER/insurance-underwriting-ai-system/Data/Insurance Claim Fraud Detection Dataset")

        if source_path.exists():
            for file in source_path.glob("*.csv"):
                target = self.data_dir / file.name
                pd.read_csv(file).to_csv(target, index=False)
                print(f"   ✅ Copied {file.name}")
        else:
            print("   ⚠️  Source path not found")

    def generate_synthetic_underwriting_data(self, n_samples: int = 10000):
        """
        Generate synthetic underwriting data
        This simulates real insurance application data
        """
        print(f"📊 Generating {n_samples} synthetic underwriting records...")

        np.random.seed(42)

        # Generate synthetic data
        data = {
            'application_id': range(1, n_samples + 1),
            'age': np.random.randint(18, 80, n_samples),
            'gender': np.random.choice(['Male', 'Female'], n_samples),
            'region': np.random.choice(['North', 'South', 'East', 'West'], n_samples),
            'vehicle_age': np.random.randint(0, 20, n_samples),
            'vehicle_value': np.random.uniform(5000, 50000, n_samples),
            'annual_mileage': np.random.uniform(5000, 30000, n_samples),
            'credit_score': np.random.randint(300, 850, n_samples),
            'years_with_license': np.random.randint(0, 50, n_samples),
            'previous_claims': np.random.poisson(0.5, n_samples),
            'vehicle_type': np.random.choice(['Sedan', 'SUV', 'Hatchback', 'Truck'], n_samples),
            'coverage_type': np.random.choice(['Third Party', 'Comprehensive', 'Third Party Fire & Theft'], n_samples),
            'desired_premium': np.random.uniform(500, 3000, n_samples),
        }

        df = pd.DataFrame(data)

        # Save synthetic data
        output_path = self.data_dir / "synthetic_underwriting.csv"
        df.to_csv(output_path, index=False)
        print(f"   ✅ Generated {n_samples} synthetic records")
        print(f"   📁 Saved to {output_path}")

        return df

    def generate_historical_claims(self, n_samples: int = 10000):
        """
        Generate historical claims data for the same applicants
        Used to construct underwriting decision labels
        """
        print(f"📊 Generating {n_samples} historical claims records...")

        np.random.seed(43)

        data = {
            'application_id': range(1, n_samples + 1),
            'total_claims_5years': np.random.poisson(0.3, n_samples),
            'total_payout_5years': np.random.exponential(1000, n_samples),
            'total_premium_5years': np.random.uniform(2000, 10000, n_samples),
            'fraud_flag': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
            'claim_severity': np.random.choice(['Minor', 'Moderate', 'Severe'], n_samples),
        }

        df = pd.DataFrame(data)

        # Save claims data
        output_path = self.data_dir / "synthetic_claims.csv"
        df.to_csv(output_path, index=False)
        print(f"   ✅ Generated {n_samples} claims records")
        print(f"   📁 Saved to {output_path}")

        return df


def construct_underwriting_labels(underwriting_df: pd.DataFrame, claims_df: pd.DataFrame):
    """
    Construct underwriting decision labels from historical claims data
    Following the cahier des charges: define a rule and justify it

    Rule: Ratio of total payout to total premium
    - If ratio > 0.8 → Reject (high risk)
    - If ratio > 0.5 → Accept with Surcharge
    - If ratio <= 0.5 → Accept Standard
    """
    print("🏷️  Constructing underwriting decision labels...")

    # Merge data
    merged = underwriting_df.merge(claims_df, on='application_id', how='left')

    # Calculate loss ratio
    merged['loss_ratio'] = merged['total_payout_5years'] / (merged['total_premium_5years'] + 1e-6)

    # Apply decision rule
    conditions = [
        merged['loss_ratio'] > 0.8,
        merged['loss_ratio'] > 0.5,
        merged['loss_ratio'] <= 0.5
    ]
    choices = ['Reject', 'Accept_with_Surcharge', 'Accept_Standard']
    merged['decision'] = np.select(conditions, choices, default='Accept_Standard')

    # Add risk score (inverse of loss ratio, normalized)
    merged['risk_score'] = 1 - np.clip(merged['loss_ratio'], 0, 1)

    # Save labeled data
    output_path = Path("data/processed/labeled_underwriting.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)

    print(f"   ✅ Constructed labels using loss ratio rule")
    print(f"   📊 Decision distribution:")
    print(merged['decision'].value_counts())
    print(f"   📁 Saved to {output_path}")

    return merged


def main():
    """Main data collection pipeline"""

    print("=" * 60)
    print("🚀 Phase 1: Data Collection and Preparation")
    print("=" * 60)

    # Initialize collector
    collector = DataCollector()

    # Collect data
    collector.collect_kaggle_motor_data()
    collector.collect_kaggle_auto_claims()

    # Generate synthetic data
    underwriting_df = collector.generate_synthetic_underwriting_data(n_samples=10000)
    claims_df = collector.generate_historical_claims(n_samples=10000)

    # Construct labels
    labeled_df = construct_underwriting_labels(underwriting_df, claims_df)

    print("\n" + "=" * 60)
    print("✅ Phase 1 Complete: Data ready for modeling")
    print("=" * 60)

    return labeled_df


if __name__ == "__main__":
    main()
