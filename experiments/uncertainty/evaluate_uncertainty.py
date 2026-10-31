"""
Evaluate Uncertainty Metrics on Baseline B2 Results
"""

import json
import numpy as np
from pathlib import Path
import sys
import os

# Add uncertainty module to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from uncertainty_metrics import evaluate_uncertainty


def evaluate_b2_uncertainty():
    """Evaluate uncertainty metrics on B2 baseline results"""

    print("=" * 60)
    print("Uncertainty Metrics Evaluation on B2 Baseline")
    print("=" * 60)

    # Load B2 results
    results_path = Path("experiments/baselines/baseline_b2_results.json")
    if not results_path.exists():
        print("B2 results not found. Running B2 first...")
        return

    with open(results_path, 'r') as f:
        b2_results = json.load(f)

    # Extract predictions and confidences
    predictions = []
    true_labels = []
    confidences = []

    for result in b2_results:
        predictions.append(result.get('decision'))
        true_labels.append(result.get('true_decision'))
        confidences.append(result.get('confidence', 0.5))

    # Convert to numeric labels for metrics
    label_map = {
        'Accept_Standard': 0,
        'Accept_with_Surcharge': 1,
        'Reject': 2
    }

    y_pred = np.array([label_map.get(p, 0) for p in predictions])
    y_true = np.array([label_map.get(t, 0) for t in true_labels])
    y_conf = np.array(confidences)

    # Normalize confidences for multi-class
    # For binary classification, confidence is straightforward
    # For multi-class, we need max probability
    y_conf_norm = y_conf / 3.0  # Simple normalization

    # Evaluate uncertainty
    results = evaluate_uncertainty(y_pred, y_true, y_conf_norm)

    print(f"\nAccuracy: {results['accuracy']:.4f}")

    print(f"\nConfidence Statistics:")
    for k, v in results['confidence_statistics'].items():
        print(f"  {k}: {v:.4f}")

    print(f"\nEscalation Rates (cases below threshold):")
    for k, v in results['escalation_rates'].items():
        print(f"  {k}: {v:.4f} ({v*100:.2f}%)")

    print(f"\nSelective Accuracy (accuracy on high-confidence cases):")
    for k, v in results['selective_accuracy'].items():
        print(f"  {k}: accuracy={v['accuracy']:.4f}, coverage={v['coverage']:.4f}")

    print(f"\nRisk-Coverage Curve (first 5 points):")
    for i, (cov, acc) in enumerate(results['risk_coverage_curve'][:5]):
        print(f"  Point {i}: coverage={cov:.4f}, accuracy={acc:.4f}")

    return results


if __name__ == "__main__":
    evaluate_b2_uncertainty()
