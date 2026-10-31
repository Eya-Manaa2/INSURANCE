"""
Evaluate Fairness Metrics on Baseline B2 Results
"""

import json
import numpy as np
from pathlib import Path
import sys
import os

# Add fairness module to path
fairness_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fairness_dir)

from fairness_metrics import evaluate_fairness


def evaluate_b2_fairness():
    """Evaluate fairness metrics on B2 baseline results"""

    print("=" * 60)
    print("Fairness Metrics Evaluation on B2 Baseline")
    print("=" * 60)

    # Load B2 results
    results_path = Path("experiments/baselines/baseline_b2_results.json")
    if not results_path.exists():
        print("B2 results not found. Running B2 first...")
        return

    with open(results_path, 'r') as f:
        b2_results = json.load(f)

    # Load original data to get attributes
    data_path = Path("data/processed/labeled_research_data_improved.json")
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Extract predictions and confidences
    predictions = []
    true_labels = []

    for result in b2_results:
        predictions.append(result.get('decision'))
        true_labels.append(result.get('true_decision'))

    # Evaluate fairness
    results = evaluate_fairness(data, predictions, true_labels)

    print(f"\nFairness Analysis Results:\n")

    for metric_name, metric_value in results.items():
        print(f"{metric_name}:")
        if isinstance(metric_value, dict) and 'ratio' in metric_value:
            print(f"  Ratio: {metric_value['ratio']:.4f}")
            print(f"  Rates: {metric_value['rates']}")
        elif isinstance(metric_value, dict):
            for k, v in metric_value.items():
                print(f"  {k}: {v:.4f}")
        else:
            print(f"  {metric_value}")

    return results


if __name__ == "__main__":
    evaluate_b2_fairness()
