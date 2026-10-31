"""
Ablation Study: Compare pipeline performance with/without different components
"""

import json
import numpy as np
from pathlib import Path
import sys

# Add agents directory to path
agents_dir = Path(__file__).parent.parent.parent / "agents"
sys.path.append(str(agents_dir))

from intake_agent import IntakeAgent
from customer_agent import CustomerAgent
from risk_agent import RiskAgent
from document_agent import DocumentAgent
from external_agent import ExternalAgent
from claims_agent import ClaimsAgent
from decision_agent_enhanced import EnhancedDecisionAgent


def run_ablation_experiment(data_path, configuration):
    """
    Run pipeline with specified configuration

    Configuration is a dict with keys:
    - include_intake: bool
    - include_customer: bool
    - include_document: bool
    - include_external: bool
    - include_claims: bool
    - mode: "automated" or "human_in_the_loop"
    """

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Initialize agents based on configuration
    agents = {}
    if configuration.get('include_intake', True):
        agents['intake'] = IntakeAgent()
    if configuration.get('include_customer', True):
        agents['customer'] = CustomerAgent()
    if configuration.get('include_document', True):
        agents['document'] = DocumentAgent()
    if configuration.get('include_external', True):
        agents['external'] = ExternalAgent()
    if configuration.get('include_claims', True):
        agents['claims'] = ClaimsAgent()

    # Always include risk (ML) and decision
    agents['risk'] = RiskAgent()
    agents['decision'] = EnhancedDecisionAgent(mode=configuration.get('mode', 'automated'))

    print(f"[Ablation] Configuration: {configuration}")
    print(f"[Ablation] Active agents: {list(agents.keys())}")

    # Evaluate all records
    results = []
    correct = 0

    for i, record in enumerate(data):
        if (i + 1) % 500 == 0:
            print(f"Processing {i+1}/{len(data)}...")

        # Prepare application data
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

        # Run agents
        agent_results = {}

        if 'intake' in agents:
            agent_results['intake'] = agents['intake'].process(application)

        if 'customer' in agents:
            agent_results['customer'] = agents['customer'].process(
                application,
                agent_results.get('intake', {})
            )

        if 'risk' in agents:
            agent_results['risk'] = agents['risk'].process(
                application,
                agent_results.get('intake', {}),
                agent_results.get('customer', {})
            )

        if 'document' in agents:
            agent_results['document'] = agents['document'].process(
                application,
                agent_results.get('risk', {})
            )

        if 'external' in agents:
            agent_results['external'] = agents['external'].process(application)

        if 'claims' in agents:
            agent_results['claims'] = agents['claims'].process(application)

        if 'decision' in agents:
            agent_results['decision'] = agents['decision'].process(application, agent_results)

        # Evaluate
        result = agent_results['decision']
        result['true_decision'] = record.get('decision')

        # Check accuracy (exclude Escalate_to_Human from accuracy calc)
        if result['final_decision'] == result['true_decision']:
            correct += 1

        results.append(result)

    # Calculate metrics
    # Exclude escalations from accuracy calculation
    non_escalated = [r for r in results if r['final_decision'] != 'Escalate_to_Human']
    correct_non_escalated = sum(1 for r in non_escalated if r['final_decision'] == r['true_decision'])
    accuracy = correct_non_escalated / len(non_escalated) if non_escalated else 0

    # Decision distribution
    decisions = [r['final_decision'] for r in results]
    decision_counts = {}
    for d in decisions:
        d_str = str(d)  # Convert numpy string to regular string
        decision_counts[d_str] = decision_counts.get(d_str, 0) + 1

    # Escalation rate
    escalation_rate = decisions.count('Escalate_to_Human') / len(results)

    # Confidence statistics
    confidences = [r['confidence'] for r in results]
    mean_confidence = sum(confidences) / len(confidences)

    print(f"\n[Ablation] Results:")
    print(f"  Accuracy (non-escalated): {accuracy:.4f}")
    print(f"  Correct: {correct_non_escalated}/{len(non_escalated)}")
    print(f"  Escalation rate: {escalation_rate:.4f}")
    print(f"  Mean confidence: {mean_confidence:.4f}")
    print(f"  Decision distribution: {decision_counts}")

    return {
        'configuration': configuration,
        'accuracy': accuracy,
        'escalation_rate': escalation_rate,
        'mean_confidence': mean_confidence,
        'decision_distribution': decision_counts,
        'results': results
    }


def run_full_ablation_study(data_path):
    """Run multiple ablation experiments"""

    print("=" * 60)
    print("Ablation Study: Impact of Different Components")
    print("=" * 60)

    ablation_results = []

    # Configuration 1: Full pipeline (baseline)
    config1 = {
        'include_intake': True,
        'include_customer': True,
        'include_document': True,
        'include_external': True,
        'include_claims': True,
        'mode': 'automated'
    }
    result1 = run_ablation_experiment(data_path, config1)
    ablation_results.append(('Full Pipeline', result1))

    # Configuration 2: Without Document, External, Claims
    config2 = {
        'include_intake': True,
        'include_customer': True,
        'include_document': False,
        'include_external': False,
        'include_claims': False,
        'mode': 'automated'
    }
    result2 = run_ablation_experiment(data_path, config2)
    ablation_results.append(('Without Document/External/Claims', result2))

    # Configuration 3: ML Only (Risk + Decision)
    config3 = {
        'include_intake': False,
        'include_customer': False,
        'include_document': False,
        'include_external': False,
        'include_claims': False,
        'mode': 'automated'
    }
    result3 = run_ablation_experiment(data_path, config3)
    ablation_results.append(('ML Only', result3))

    # Configuration 4: Full Pipeline with Human-in-the-Loop
    config4 = {
        'include_intake': True,
        'include_customer': True,
        'include_document': True,
        'include_external': True,
        'include_claims': True,
        'mode': 'human_in_the_loop'
    }
    result4 = run_ablation_experiment(data_path, config4)
    ablation_results.append(('Full Pipeline (Human-in-the-Loop)', result4))

    # Print comparison
    print("\n" + "=" * 60)
    print("Ablation Comparison")
    print("=" * 60)

    for name, result in ablation_results:
        print(f"\n{name}:")
        print(f"  Accuracy: {result['accuracy']:.4f}")
        print(f"  Escalation rate: {result['escalation_rate']:.4f}")
        print(f"  Mean confidence: {result['mean_confidence']:.4f}")

    print(f"\nAblation results complete")
    print(f"Results are displayed above")

    return ablation_results


if __name__ == "__main__":
    data_path = "data/processed/labeled_research_data_improved.json"
    results = run_full_ablation_study(data_path)
