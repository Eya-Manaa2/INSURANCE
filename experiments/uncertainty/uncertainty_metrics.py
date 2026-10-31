"""
Uncertainty Metrics Module
- Brier Score
- Expected Calibration Error (ECE)
- Risk-Coverage Curves
- Selective Accuracy
- Escalation Rate
"""

import numpy as np
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve
from pathlib import Path


class UncertaintyMetrics:
    """Calculate uncertainty metrics for model predictions"""

    def __init__(self):
        self.calibration_bins = 10

    def brier_score(self, y_true, y_prob, pos_label=None):
        """
        Calculate Brier Score (mean squared error of predicted probabilities)

        Lower is better. Range: [0, 1]
        0 = perfect calibration, 1 = worst
        """
        if pos_label is None:
            # Handle multi-class by treating each class as binary
            classes = np.unique(y_true)
            brier_scores = []
            for cls in classes:
                y_true_binary = (y_true == cls).astype(int)
                y_prob_binary = y_prob[:, np.where(classes == cls)[0][0]]
                bs = brier_score_loss(y_true_binary, y_prob_binary)
                brier_scores.append(bs)
            return np.mean(brier_scores)
        else:
            return brier_score_loss((y_true == pos_label).astype(int), y_prob)

    def expected_calibration_error(self, y_true, y_prob, n_bins=10):
        """
        Calculate Expected Calibration Error (ECE)

        Measures how well predicted probabilities match actual frequencies
        Lower is better. Range: [0, 1]
        """
        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)

        # Weight by number of samples in each bin
        bin_counts = np.histogram(y_prob, bins=n_bins, range=(0, 1))[0]
        weights = bin_counts / len(y_true)

        # Calculate weighted average of calibration error
        ece = np.sum(weights * np.abs(prob_true - prob_pred))

        return ece

    def risk_coverage_curve(self, y_true, y_prob, n_points=20):
        """
        Calculate Risk-Coverage Curve points

        As confidence threshold increases:
        - Coverage decreases (fewer predictions)
        - Accuracy typically increases

        Returns list of (coverage, accuracy) tuples
        """
        thresholds = np.linspace(0, 1, n_points)
        curve_points = []

        for threshold in thresholds:
            # Select predictions with confidence >= threshold
            mask = y_prob >= threshold
            selected_true = y_true[mask]
            selected_pred = np.round(y_prob[mask])

            if len(selected_true) > 0:
                accuracy = np.mean(selected_true == selected_pred)
                coverage = len(selected_true) / len(y_true)
                curve_points.append((coverage, accuracy))
            else:
                curve_points.append((0, 0))

        return curve_points

    def selective_accuracy(self, y_true, y_prob, threshold):
        """
        Calculate accuracy on selected high-confidence predictions

        Returns: (accuracy, coverage)
        """
        mask = y_prob >= threshold
        selected_true = y_true[mask]
        selected_pred = np.round(y_prob[mask])

        if len(selected_true) == 0:
            return 0, 0

        accuracy = np.mean(selected_true == selected_pred)
        coverage = len(selected_true) / len(y_true)

        return accuracy, coverage

    def escalation_rate(self, confidences, threshold):
        """
        Calculate escalation rate (fraction of cases below confidence threshold)

        Higher threshold = higher escalation rate
        """
        escalated = np.sum(confidences < threshold)
        return escalated / len(confidences)

    def confidence_statistics(self, confidences):
        """
        Calculate basic statistics on confidence scores
        """
        return {
            'mean': np.mean(confidences),
            'std': np.std(confidences),
            'min': np.min(confidences),
            'max': np.max(confidences),
            'median': np.median(confidences),
            'percentile_25': np.percentile(confidences, 25),
            'percentile_75': np.percentile(confidences, 75)
        }


def evaluate_uncertainty(predictions, true_labels, confidences):
    """
    Comprehensive uncertainty evaluation

    predictions: predicted labels
    true_labels: ground truth labels
    confidences: confidence scores
    """
    metrics = UncertaintyMetrics()

    # Convert to numpy
    y_true = np.array(true_labels)
    y_pred = np.array(predictions)
    y_conf = np.array(confidences)

    # Basic metrics
    accuracy = np.mean(y_pred == y_true)

    # Confidence statistics
    conf_stats = metrics.confidence_statistics(y_conf)

    # Escalation rates at different thresholds
    escalation_rates = {}
    for threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:
        escalation_rates[f'threshold_{threshold}'] = metrics.escalation_rate(y_conf, threshold)

    # Selective accuracy at different thresholds
    selective_acc = {}
    for threshold in [0.5, 0.6, 0.7, 0.8, 0.9]:
        acc, cov = metrics.selective_accuracy(y_true, y_conf, threshold)
        selective_acc[f'threshold_{threshold}'] = {
            'accuracy': acc,
            'coverage': cov
        }

    # Risk-coverage curve
    risk_coverage = metrics.risk_coverage_curve(y_true, y_conf)

    return {
        'accuracy': accuracy,
        'confidence_statistics': conf_stats,
        'escalation_rates': escalation_rates,
        'selective_accuracy': selective_acc,
        'risk_coverage_curve': risk_coverage
    }


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)

    # Simulate predictions
    n_samples = 1000
    y_true = np.random.randint(0, 2, n_samples)
    y_conf = np.random.uniform(0.5, 1.0, n_samples)
    y_pred = (y_conf > 0.5).astype(int)

    # Evaluate
    results = evaluate_uncertainty(y_pred, y_true, y_conf)

    print("Uncertainty Metrics Evaluation")
    print("=" * 50)
    print(f"Accuracy: {results['accuracy']:.4f}")
    print(f"\nConfidence Statistics:")
    for k, v in results['confidence_statistics'].items():
        print(f"  {k}: {v:.4f}")

    print(f"\nEscalation Rates:")
    for k, v in results['escalation_rates'].items():
        print(f"  {k}: {v:.4f}")

    print(f"\nSelective Accuracy:")
    for k, v in results['selective_accuracy'].items():
        print(f"  {k}: accuracy={v['accuracy']:.4f}, coverage={v['coverage']:.4f}")
