"""
Fairness Metrics Module
- Demographic Parity
- Equal Opportunity
- Disparate Impact
- Counterfactual Sensitivity
- Subgroup Analysis
"""

import numpy as np
from collections import defaultdict


class FairnessMetrics:
    """Calculate fairness metrics for model predictions"""

    def __init__(self):
        pass

    def demographic_parity(self, y_pred, sensitive_attribute):
        """
        Demographic Parity: Equal positive prediction rates across groups

        P(Y_hat = 1 | A = 0) should equal P(Y_hat = 1 | A = 1)

        Returns: ratio of positive rates (closer to 1 is better)
        """
        groups = np.unique(sensitive_attribute)
        if len(groups) != 2:
            return None, "Demographic parity requires binary sensitive attribute"

        positive_rates = {}
        for group in groups:
            mask = sensitive_attribute == group
            positive_rate = np.mean(y_pred[mask] == 1)
            positive_rates[group] = positive_rate

        ratio = min(positive_rates.values()) / max(positive_rates.values()) if max(positive_rates.values()) > 0 else 0

        return ratio, positive_rates

    def equal_opportunity(self, y_true, y_pred, sensitive_attribute):
        """
        Equal Opportunity: Equal true positive rates across groups

        P(Y_hat = 1 | Y = 1, A = 0) should equal P(Y_hat = 1 | Y = 1, A = 1)

        Returns: ratio of TPRs (closer to 1 is better)
        """
        groups = np.unique(sensitive_attribute)
        if len(groups) != 2:
            return None, "Equal opportunity requires binary sensitive attribute"

        tprs = {}
        for group in groups:
            mask = (sensitive_attribute == group) & (y_true == 1)
            if np.sum(mask) > 0:
                tpr = np.mean(y_pred[mask] == 1)
            else:
                tpr = 0
            tprs[group] = tpr

        ratio = min(tprs.values()) / max(tprs.values()) if max(tprs.values()) > 0 else 0

        return ratio, tprs

    def disparate_impact(self, y_pred, sensitive_attribute):
        """
        Disparate Impact: Ratio of positive prediction rates

        P(Y_hat = 1 | A = disadvantaged) / P(Y_hat = 1 | A = advantaged)

        Returns: ratio (closer to 1 is better, < 0.8 is concerning)
        """
        groups = np.unique(sensitive_attribute)
        if len(groups) != 2:
            return None, "Disparate impact requires binary sensitive attribute"

        positive_rates = {}
        for group in groups:
            mask = sensitive_attribute == group
            positive_rate = np.mean(y_pred[mask] == 1)
            positive_rates[group] = positive_rate

        # Assume lower value is disadvantaged
        group_0, group_1 = sorted(groups)
        ratio = positive_rates[group_0] / positive_rates[group_1] if positive_rates[group_1] > 0 else 0

        return ratio, positive_rates

    def counterfactual_sensitivity(self, y_pred_original, y_pred_modified):
        """
        Counterfactual Sensitivity: How many predictions change when sensitive attribute changes

        Returns: flip rate (lower is better)
        """
        flips = np.sum(y_pred_original != y_pred_modified)
        flip_rate = flips / len(y_pred_original)

        return flip_rate, flips

    def subgroup_accuracy(self, y_true, y_pred, sensitive_attribute):
        """
        Calculate accuracy per subgroup

        Returns: dict of accuracy per group
        """
        groups = np.unique(sensitive_attribute)
        accuracies = {}

        for group in groups:
            mask = sensitive_attribute == group
            if np.sum(mask) > 0:
                acc = np.mean(y_true[mask] == y_pred[mask])
            else:
                acc = 0
            accuracies[group] = acc

        return accuracies

    def subgroup_error_analysis(self, y_true, y_pred, sensitive_attribute):
        """
        Analyze error rates per subgroup

        Returns: dict of error rates per group
        """
        groups = np.unique(sensitive_attribute)
        error_rates = {}

        for group in groups:
            mask = sensitive_attribute == group
            if np.sum(mask) > 0:
                error_rate = 1 - np.mean(y_true[mask] == y_pred[mask])
            else:
                error_rate = 0
            error_rates[group] = error_rate

        return error_rates


def evaluate_fairness(data, predictions, true_labels):
    """
    Comprehensive fairness evaluation

    data: list of application dicts with attributes
    predictions: predicted labels
    true_labels: ground truth labels
    """
    metrics = FairnessMetrics()

    # Extract sensitive attributes
    # Using age as proxy for demographic analysis (simplified)
    # In real system, would use actual demographic data
    ages = np.array([d.get('age', 30) for d in data])
    credit_scores = np.array([d.get('credit_score', 500) for d in data])

    # Create binary groups for analysis
    # Age: < 35 vs >= 35
    age_group = (ages >= 35).astype(int)

    # Credit: < 600 vs >= 600
    credit_group = (credit_scores >= 600).astype(int)

    # Convert labels to binary for fairness metrics
    # Treat "Reject" as positive (1), others as negative (0)
    y_pred_binary = np.array([1 if p == 'Reject' else 0 for p in predictions])
    y_true_binary = np.array([1 if t == 'Reject' else 0 for t in true_labels])

    results = {}

    # Demographic Parity (by age)
    dp_ratio_age, dp_rates_age = metrics.demographic_parity(y_pred_binary, age_group)
    results['demographic_parity_age'] = {
        'ratio': dp_ratio_age,
        'rates': dp_rates_age
    }

    # Demographic Parity (by credit)
    dp_ratio_credit, dp_rates_credit = metrics.demographic_parity(y_pred_binary, credit_group)
    results['demographic_parity_credit'] = {
        'ratio': dp_ratio_credit,
        'rates': dp_rates_credit
    }

    # Equal Opportunity (by age)
    eo_ratio_age, eo_rates_age = metrics.equal_opportunity(y_true_binary, y_pred_binary, age_group)
    results['equal_opportunity_age'] = {
        'ratio': eo_ratio_age,
        'rates': eo_rates_age
    }

    # Disparate Impact (by age)
    di_ratio_age, di_rates_age = metrics.disparate_impact(y_pred_binary, age_group)
    results['disparate_impact_age'] = {
        'ratio': di_ratio_age,
        'rates': di_rates_age
    }

    # Subgroup Accuracy (by age)
    acc_age = metrics.subgroup_accuracy(y_true_binary, y_pred_binary, age_group)
    results['subgroup_accuracy_age'] = acc_age

    # Subgroup Accuracy (by credit)
    acc_credit = metrics.subgroup_accuracy(y_true_binary, y_pred_binary, credit_group)
    results['subgroup_accuracy_credit'] = acc_credit

    # Subgroup Error Analysis
    error_age = metrics.subgroup_error_analysis(y_true_binary, y_pred_binary, age_group)
    results['subgroup_error_age'] = error_age

    error_credit = metrics.subgroup_error_analysis(y_true_binary, y_pred_binary, credit_group)
    results['subgroup_error_credit'] = error_credit

    return results


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)

    n_samples = 1000
    data = [
        {'age': np.random.randint(18, 70), 'credit_score': np.random.randint(300, 800)}
        for _ in range(n_samples)
    ]

    y_true = np.random.randint(0, 2, n_samples)
    y_pred = y_true.copy()

    # Introduce some bias
    y_pred[:100] = 1  # Bias against first 100 samples

    results = evaluate_fairness(data, y_pred, y_true)

    print("Fairness Metrics Evaluation")
    print("=" * 50)

    for metric_name, metric_value in results.items():
        print(f"\n{metric_name}:")
        if isinstance(metric_value, dict) and 'ratio' in metric_value:
            print(f"  Ratio: {metric_value['ratio']:.4f}")
            print(f"  Rates: {metric_value['rates']}")
        else:
            print(f"  {metric_value}")
