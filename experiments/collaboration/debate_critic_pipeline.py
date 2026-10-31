"""
Debate/Critique Collaboration Pattern
Agents debate and critique each other's decisions before final agreement
"""

import json
import numpy as np
from pathlib import Path
import sys
import os
# Add agents directory to path
agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'agents'))
sys.path.append(agents_dir)

from intake_agent import IntakeAgent
from customer_agent import CustomerAgent
from risk_agent import RiskAgent
from decision_agent_enhanced import EnhancedDecisionAgent


class DebateAgent:
    """Agent that critiques decisions"""

    def __init__(self, role):
        self.role = role  # "conservative" or "liberal"
        print(f"[OK] Debate Agent initialized (role: {self.role})")

    def critique(self, application, proposed_decision):
        """Critique a proposed decision"""

        critique = {
            'agent': 'Debate',
            'role': self.role,
            'proposed_decision': proposed_decision,
            'critique_points': [],
            'agreement': True,
            'alternative_decision': None
        }

        # Conservative agent is more cautious
        if self.role == "conservative":
            if proposed_decision == 'Accept_Standard':
                credit = application.get('credit_score', 500)
                if credit < 600:
                    critique['critique_points'].append(f"Low credit score ({credit}) suggests surcharge needed")
                    critique['agreement'] = False
                    critique['alternative_decision'] = 'Accept_with_Surcharge'
            elif proposed_decision == 'Accept_with_Surcharge':
                critique['critique_points'].append("Surcharge may be too risky")
                critique['agreement'] = False
                critique['alternative_decision'] = 'Reject'

        # Liberal agent is more accepting
        elif self.role == "liberal":
            if proposed_decision == 'Reject':
                credit = application.get('credit_score', 500)
                if credit > 650:
                    critique['critique_points'].append(f"Good credit score ({credit}) suggests acceptance")
                    critique['agreement'] = False
                    critique['alternative_decision'] = 'Accept_Standard'
            elif proposed_decision == 'Accept_with_Surcharge':
                critique['critique_points'].append("Surcharge may discourage good customers")
                critique['agreement'] = False
                critique['alternative_decision'] = 'Accept_Standard'

        return critique


class VotingAgent:
    """Agent that implements confidence-weighted voting"""

    def __init__(self):
        print("[OK] Voting Agent initialized")

    def vote(self, application, agent_decisions):
        """Combine agent decisions with confidence weighting"""

        # In a real system, this would collect votes from multiple agents
        # For this prototype, we simulate voting based on ML confidence

        # Weight votes by confidence
        votes = {}
        total_weight = 0

        for agent_name, decision in agent_decisions.items():
            if 'decision' in decision:
                conf = decision.get('confidence', 0.5)
                decision_type = decision['decision']
                votes[decision_type] = votes.get(decision_type, 0) + conf
                total_weight += conf

        # Weighted voting
        if votes:
            final_decision = max(votes, key=votes.get)
        else:
            # Fallback to original proposed decision
            final_decision = proposed_decision

        return {
            'agent': 'Voting',
            'final_decision': final_decision,
            'votes': votes,
            'total_weight': total_weight,
            'method': 'confidence_weighted'
        }


def run_debate_pipeline(data_path):
    """Run debate/critique collaboration experiment"""

    print("=" * 60)
    print("Debate/Critique Collaboration Pattern")
    print("=" * 60)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    # Initialize agents
    intake_agent = IntakeAgent()
    customer_agent = CustomerAgent()
    risk_agent = RiskAgent()
    conservative_debater = DebateAgent("conservative")
    liberal_debater = DebateAgent("liberal")
    voting_agent = VotingAgent()

    print(f"Loaded {len(data)} records")

    # Evaluate with debate pattern
    results = []
    correct = 0

    for i, record in enumerate(data):
        if (i + 1) % 500 == 0:
            print(f"Processing {i+1}/{len(data)}...")

        # Prepare application
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

        # Step 1: Standard pipeline
        intake_result = intake_agent.process(application)
        customer_result = customer_agent.process(application, intake_result)
        risk_result = risk_agent.process(application, intake_result, customer_result)

        # Step 2: Debate phase
        proposed_decision = risk_result['decision']

        conservative_critique = conservative_debater.critique(application, proposed_decision)
        liberal_critique = liberal_debater.critique(application, proposed_decision)

        # Step 3: Resolve debate
        if conservative_critique['agreement'] and liberal_critique['agreement']:
            final_decision = proposed_decision
            consensus = "Full agreement"
        elif not conservative_critique['agreement'] and not liberal_critique['agreement']:
            # Both disagree, escalate to voting
            agent_decisions = {
                'conservative': {'decision': conservative_critique.get('alternative_decision', proposed_decision), 'confidence': 0.8},
                'liberal': {'decision': liberal_critique.get('alternative_decision', proposed_decision), 'confidence': 0.8},
                'risk': risk_result
            }
            vote_result = voting_agent.vote(application, agent_decisions)
            final_decision = vote_result['final_decision']
            consensus = "Voting resolution"
        else:
            # One agrees, one disagrees - go with the agreed one
            if conservative_critique['agreement']:
                final_decision = proposed_decision
            elif liberal_critique['agreement']:
                final_decision = proposed_decision
            else:
                # Neither agrees, use conservative alternative or proposed
                alt = conservative_critique.get('alternative_decision')
                final_decision = alt if alt else proposed_decision
            consensus = "Partial agreement"

        # Evaluate
        result = {
            'collaboration_pattern': 'debate_critic',
            'final_decision': final_decision,
            'proposed_decision': proposed_decision,
            'consensus': consensus,
            'conservative_critique': conservative_critique,
            'liberal_critique': liberal_critique,
            'risk_confidence': risk_result['confidence']
        }
        result['true_decision'] = record.get('decision')

        if result['final_decision'] == result['true_decision']:
            correct += 1

        results.append(result)

    # Calculate metrics
    accuracy = correct / len(data)

    # Print results
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Correct: {correct}/{len(data)}")

    # Decision distribution
    decisions = [r['final_decision'] for r in results]
    print(f"\nDecision distribution:")
    for decision in set(decisions):
        count = decisions.count(decision)
        pct = count / len(data) * 100
        print(f"  {decision}: {count} ({pct:.1f}%)")

    # Consensus analysis
    consensus_types = [r['consensus'] for r in results]
    print(f"\nConsensus analysis:")
    for consensus in set(consensus_types):
        count = consensus_types.count(consensus)
        pct = count / len(data) * 100
        print(f"  {consensus}: {count} ({pct:.1f}%)")

    return results, accuracy


if __name__ == "__main__":
    data_path = "data/processed/labeled_research_data_improved.json"
    results, accuracy = run_debate_pipeline(data_path)
