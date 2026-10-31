"""
Repeated Runs with Confidence Intervals
- Run experiments multiple times with different seeds
- Calculate mean, std, and confidence intervals
- Statistical significance testing
"""

import json
import numpy as np
from pathlib import Path
import sys
import os
from scipy import stats

# Add agents directory to path
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'agents'))
sys.path.append(agents_dir)

from risk_agent import RiskAgent


def run_single_baseline(data_path, seed):
    """Run baseline B2 with specific seed"""

    np.random.seed(seed)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Initialize agent
    risk_agent = RiskAgent()

    # Shuffle data
    indices = np.random.permutation(len(data))
    shuffled_data = [data[i] for i in indices]

    # Run on subset (for speed)
    subset_size = min(1000, len(shuffled_data))
    subset = shuffled_data[:subset_size]

    correct = 0
    for record in subset:
        application = {
            'application_id': record.get('application_id'),
            'age': record.get('age'),
            'credit_score': record.get('credit_score'),
            'vehicle_value': record.get('vehicle_value'),
            'premium_amount': record.get('premium_amount'),
            'claim_amount': record.get('claim_amount'),
            'fraud_flag': record.get('fraud_flag'),
            'location': 'suburban',
        }

        intake_result = {'valid': True}
        customer_result = {'credit_risk': 'medium'}
        risk_result = risk_agent.process(application, intake_result, customer_result)

        if risk_result['decision'] == record.get('decision'):
            correct += 1

    accuracy = correct / len(subset)
    return accuracy


def calculate_confidence_interval(values, confidence=0.95):
    """Calculate confidence interval for mean"""

    n = len(values)
    mean = np.mean(values)
    std = np.std(values, ddof=1)

    # Standard error
    se = std / np.sqrt(n)

    # t-distribution critical value
    t_critical = stats.t.ppf((1 + confidence) / 2, n - 1)

    # Margin of error
    margin = t_critical * se

    return {
        'mean': mean,
        'std': std,
        'se': se,
        'ci_lower': mean - margin,
        'ci_upper': mean + margin,
        'margin': margin
    }


def run_repeated_experiments(n_runs=10):
    """Run experiments multiple times with different seeds"""

    print("=" * 60)
    print("Repeated Runs with Confidence Intervals")
    print("=" * 60)

    data_path = "data/processed/labeled_research_data_improved.json"

    # Different seeds for reproducibility
    seeds = [42, 123, 456, 789, 1011, 1213, 1415, 1617, 1819, 2021]

    if len(seeds) > n_runs:
        seeds = seeds[:n_runs]

    print(f"\nRunning {len(seeds)} experiments with different seeds...")

    accuracies = []
    for i, seed in enumerate(seeds):
        print(f"  Run {i+1}/{len(seeds)} (seed={seed})...", end=' ')
        acc = run_single_baseline(data_path, seed)
        accuracies.append(acc)
        print(f"accuracy={acc:.4f}", flush=True)

    # Calculate statistics
    stats_results = calculate_confidence_interval(accuracies)

    print(f"\nStatistical Results:")
    print(f"  Mean accuracy: {stats_results['mean']:.4f}")
    print(f"  Std deviation: {stats_results['std']:.4f}")
    print(f"  Standard error: {stats_results['se']:.4f}")
    print(f"  95% CI: [{stats_results['ci_lower']:.4f}, {stats_results['ci_upper']:.4f}]")
    print(f"  Margin of error: {stats_results['margin']:.4f}")

    # Compare with single run baseline
    baseline_accuracy = 0.9740  # From B2
    print(f"\nComparison with single run baseline ({baseline_accuracy:.4f}):")
    diff = stats_results['mean'] - baseline_accuracy
    print(f"  Difference: {diff:+.4f}")

    # Check if baseline is within CI
    if stats_results['ci_lower'] <= baseline_accuracy <= stats_results['ci_upper']:
        print(f"  Baseline is within 95% CI (YES)")
    else:
        print(f"  Baseline is outside 95% CI (NO)")

    return {
        'seeds': seeds,
        'accuracies': accuracies,
        'statistics': stats_results
    }


def compare_two_methods(method1_accuracies, method2_accuracies, method1_name="Method 1", method2_name="Method 2"):
    """Perform statistical significance test between two methods"""

    print(f"\n" + "=" * 60)
    print(f"Statistical Comparison: {method1_name} vs {method2_name}")
    print("=" * 60)

    # Calculate statistics for each method
    stats1 = calculate_confidence_interval(method1_accuracies)
    stats2 = calculate_confidence_interval(method2_accuracies)

    print(f"\n{method1_name}:")
    print(f"  Mean: {stats1['mean']:.4f}")
    print(f"  Std: {stats1['std']:.4f}")
    print(f"  95% CI: [{stats1['ci_lower']:.4f}, {stats1['ci_upper']:.4f}]")

    print(f"\n{method2_name}:")
    print(f"  Mean: {stats2['mean']:.4f}")
    print(f"  Std: {stats2['std']:.4f}")
    print(f"  95% CI: [{stats2['ci_lower']:.4f}, {stats2['ci_upper']:.4f}]")

    # Perform t-test
    t_stat, p_value = stats.ttest_ind(method1_accuracies, method2_accuracies)

    print(f"\nStatistical Test (two-sample t-test):")
    print(f"  t-statistic: {t_stat:.4f}")
    print(f"  p-value: {p_value:.4f}")

    if p_value < 0.05:
        print(f"  Result: Significant difference (p < 0.05) (YES)")
    else:
        print(f"  Result: No significant difference (p >= 0.05)")

    # Check for overlap in CIs
    if stats1['ci_upper'] < stats2['ci_lower'] or stats2['ci_upper'] < stats1['ci_lower']:
        print(f"  CIs do not overlap: Significant difference (YES)")
    else:
        print(f"  CIs overlap: No significant difference")

    return {
        'method1_stats': stats1,
        'method2_stats': stats2,
        't_statistic': t_stat,
        'p_value': p_value
    }


if __name__ == "__main__":
    # Run repeated experiments
    results = run_repeated_experiments(n_runs=10)

    # Example: Compare with hypothetical method2
    # In practice, this would be from actual second method runs
    print("\n" + "=" * 60)
    print("Note: To compare two methods, run both with different configurations")
    print("and pass their accuracy lists to compare_two_methods()")
    print("=" * 60)
