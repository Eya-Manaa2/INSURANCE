"""
Explainability with SHAP
- Feature importance
- SHAP values
- Local explanations
- Feature contributions
"""

import json
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
import pickle
from pathlib import Path


def load_model_and_data():
    """Load the trained XGBoost model and data"""

    print("=" * 60)
    print("Loading Model and Data for SHAP Analysis")
    print("=" * 60)

    # Load model
    model_path = "models/underwriter_xgboost_model.json"
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    print(f"[OK] Model loaded from {model_path}")

    # Load label encoder
    with open("models/label_encoder.pkl", 'rb') as f:
        label_encoder = pickle.load(f)
    print(f"[OK] Label encoder loaded")

    # Load feature names
    with open("models/feature_names.pkl", 'rb') as f:
        feature_names = pickle.load(f)
    print(f"[OK] Feature names loaded: {feature_names}")

    # Load data
    data_path = "data/processed/labeled_research_data_improved.json"
    with open(data_path, 'r') as f:
        data = json.load(f)
    print(f"[OK] Data loaded: {len(data)} records")

    # Prepare features
    X = []
    for record in data:
        features = [
            record.get('age', 30),
            record.get('credit_score', 500),
            record.get('vehicle_value', 20000),
            record.get('premium_amount', 1000),
            record.get('claim_amount', 0),
            1 if record.get('fraud_flag', False) else 0
        ]
        X.append(features)

    X = np.array(X)
    print(f"[OK] Features prepared: shape {X.shape}")

    return model, X, feature_names, label_encoder, data


def global_feature_importance(model, X, feature_names):
    """Calculate global feature importance using SHAP"""

    print("\n" + "=" * 60)
    print("Global Feature Importance (SHAP)")
    print("=" * 60)

    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # For multi-class, shap_values is a list
    if isinstance(shap_values, list):
        # Use first class for global importance
        shap_values_mean = np.abs(shap_values[0]).mean(axis=0)
    else:
        shap_values_mean = np.abs(shap_values).mean(axis=0)

    # Ensure 1D array
    shap_values_mean = np.array(shap_values_mean).flatten()

    # Create feature importance dict
    importance_dict = {feature_names[i]: shap_values_mean[i] for i in range(len(feature_names))}
    importance_dict = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))

    print("\nFeature Importance:")
    for feature, importance in importance_dict.items():
        print(f"  {feature}: {importance:.4f}")

    return importance_dict, explainer, shap_values


def local_explanation(explainer, shap_values, X, feature_names, data, n_samples=5):
    """Generate local explanations for specific samples"""

    print("\n" + "=" * 60)
    print("Local Explanations (SHAP)")
    print("=" * 60)

    np.random.seed(42)
    sample_indices = np.random.choice(len(X), n_samples, replace=False)

    explanations = []

    for idx in sample_indices:
        print(f"\nSample {idx + 1}:")

        # Get true decision
        true_decision = data[idx].get('decision')

        # Get SHAP values for this sample
        if isinstance(shap_values, list):
            sample_shap = shap_values[0][idx]  # First class
        else:
            sample_shap = shap_values[idx]

        sample_shap = np.array(sample_shap).flatten()

        print(f"  True decision: {true_decision}")
        print(f"  Feature contributions:")

        # Sort by absolute contribution
        feature_contributions = list(zip(feature_names, sample_shap))
        feature_contributions.sort(key=lambda x: abs(x[1]), reverse=True)

        for feature, contribution in feature_contributions:
            direction = "+" if contribution > 0 else "-"
            print(f"    {feature}: {direction}{abs(contribution):.4f}")

        explanations.append({
            'sample_index': int(idx),
            'true_decision': true_decision,
            'contributions': {feature: float(contribution) for feature, contribution in feature_contributions}
        })

    return explanations


def feature_stability_analysis(model, X, feature_names, n_samples=100):
    """Analyze feature stability across samples"""

    print("\n" + "=" * 60)
    print("Feature Stability Analysis")
    print("=" * 60)

    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values_mean = shap_values[0]
    else:
        shap_values_mean = shap_values

    # Calculate stability metrics
    stability_metrics = {}

    for i, feature in enumerate(feature_names):
        values = shap_values_mean[:, i]
        values = np.array(values).flatten()
        stability_metrics[feature] = {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'range': float(np.max(values) - np.min(values))
        }

    print("\nFeature Stability:")
    for feature, metrics in stability_metrics.items():
        print(f"  {feature}:")
        print(f"    Mean: {metrics['mean']:.4f}")
        print(f"    Std: {metrics['std']:.4f}")
        print(f"    Range: {metrics['range']:.4f}")

    return stability_metrics


def explanation_fidelity(model, X, y, feature_names, label_encoder):
    """Test explanation fidelity by examining feature contributions vs model decisions"""

    print("\n" + "=" * 60)
    print("Explanation Fidelity Analysis")
    print("=" * 60)

    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    if isinstance(shap_values, list):
        shap_values_mean = shap_values[0]
    else:
        shap_values_mean = shap_values

    # Predict
    y_pred = model.predict(X)

    # Analyze fidelity
    fidelity_scores = []

    for i in range(len(X)):
        # Get SHAP values
        sample_shap = shap_values_mean[i]

        # Calculate total contribution magnitude
        total_contribution = np.sum(np.abs(sample_shap))

        # If contribution is high, confidence should be high
        # This is a simple fidelity test
        fidelity_scores.append(total_contribution)

    avg_fidelity = np.mean(fidelity_scores)
    print(f"\nAverage explanation magnitude: {avg_fidelity:.4f}")

    return fidelity_scores


def run_shap_analysis():
    """Run complete SHAP analysis"""

    # Load model and data
    model, X, feature_names, label_encoder, data = load_model_and_data()

    # Global feature importance
    importance_dict, explainer, shap_values = global_feature_importance(model, X, feature_names)

    # Local explanations
    local_explanations = local_explanation(explainer, shap_values, X, feature_names, data)

    # Feature stability
    stability_metrics = feature_stability_analysis(model, X, feature_names)

    # Explanation fidelity
    y = [label_encoder.transform([d.get('decision')])[0] for d in data]
    fidelity_scores = explanation_fidelity(model, X, y, feature_names, label_encoder)

    # Summary
    print("\n" + "=" * 60)
    print("SHAP Analysis Summary")
    print("=" * 60)

    print("\nTop 3 Most Important Features:")
    for i, (feature, importance) in enumerate(list(importance_dict.items())[:3]):
        print(f"  {i + 1}. {feature}: {importance:.4f}")

    print("\nFeature Stability (std):")
    for feature in feature_names:
        print(f"  {feature}: {stability_metrics[feature]['std']:.4f}")

    return {
        'feature_importance': importance_dict,
        'local_explanations': local_explanations,
        'stability_metrics': stability_metrics,
        'fidelity_scores': fidelity_scores
    }


if __name__ == "__main__":
    results = run_shap_analysis()
