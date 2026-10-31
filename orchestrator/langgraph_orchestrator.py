"""
LangGraph Orchestrator: Flexible coordination of multi-agent workflows
Demonstrates different collaboration patterns: sequential, parallel, conditional
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import operator
import sys
from pathlib import Path

# Add parent directory to path (where agents folder is)
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "agents"))

from intake_agent import IntakeAgent
from customer_agent import CustomerAgent
from risk_agent import RiskAgent
from document_agent import DocumentAgent
from external_agent import ExternalAgent
from claims_agent import ClaimsAgent


def simple_decision(application, all_results):
    """Simple decision logic for orchestrator"""
    risk_result = all_results.get('risk', {})
    decision = risk_result.get('decision', 'Accept_Standard')
    risk_score = risk_result.get('risk_score', 50)
    
    # Adjust based on exclusions
    document_result = all_results.get('document', {})
    if document_result.get('exclusions'):
        decision = 'Reject'
        risk_score += 20
    
    return {
        'final_decision': decision,
        'final_risk_score': min(risk_score, 100),
        'reasons': risk_result.get('reasons', ['Orchestrator decision'])
    }

# Define the state structure
class AgentState(TypedDict):
    """State passed between agents"""
    application: dict
    intake_result: dict
    customer_result: dict
    risk_result: dict
    document_result: dict
    external_result: dict
    claims_result: dict
    decision_result: dict
    messages: Annotated[Sequence[str], add_messages]
    collaboration_mode: str  # sequential, parallel, conditional


class LangGraphOrchestrator:
    """Orchestrates multi-agent workflows using LangGraph"""

    def __init__(self):
        self.intake_agent = IntakeAgent()
        self.customer_agent = CustomerAgent()
        self.risk_agent = RiskAgent()
        self.document_agent = DocumentAgent()
        self.external_agent = ExternalAgent()
        self.claims_agent = ClaimsAgent()
        print("[OK] LangGraph Orchestrator initialized")

    def build_sequential_graph(self):
        """Build a sequential workflow graph"""
        workflow = StateGraph(AgentState)

        # Define nodes (agent functions)
        workflow.add_node("intake", self.intake_node)
        workflow.add_node("customer", self.customer_node)
        workflow.add_node("risk", self.risk_node)
        workflow.add_node("document", self.document_node)
        workflow.add_node("external", self.external_node)
        workflow.add_node("claims", self.claims_node)
        workflow.add_node("decision", self.decision_node)

        # Define edges (sequential flow)
        workflow.set_entry_point("intake")
        workflow.add_edge("intake", "customer")
        workflow.add_edge("customer", "risk")
        workflow.add_edge("risk", "document")
        workflow.add_edge("document", "external")
        workflow.add_edge("external", "claims")
        workflow.add_edge("claims", "decision")
        workflow.add_edge("decision", END)

        return workflow.compile()

    def build_parallel_graph(self):
        """Build a parallel workflow graph (some agents run in parallel)"""
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("intake", self.intake_node)
        workflow.add_node("customer", self.customer_node)
        workflow.add_node("risk", self.risk_node)
        workflow.add_node("document", self.document_node)
        workflow.add_node("external", self.external_node)
        workflow.add_node("claims", self.claims_node)
        workflow.add_node("decision", self.decision_node)

        # Entry point
        workflow.set_entry_point("intake")

        # After intake, customer runs in parallel with other agents
        workflow.add_edge("intake", "customer")
        workflow.add_edge("intake", "document")
        workflow.add_edge("intake", "external")
        workflow.add_edge("intake", "claims")

        # All must complete before risk (which needs customer data)
        workflow.add_edge("customer", "risk")
        workflow.add_edge("document", "risk")
        workflow.add_edge("external", "risk")
        workflow.add_edge("claims", "risk")

        # Final decision
        workflow.add_edge("risk", "decision")
        workflow.add_edge("decision", END)

        return workflow.compile()

    # Node functions
    def intake_node(self, state: AgentState):
        """Intake agent node"""
        result = self.intake_agent.process(state["application"])
        state["intake_result"] = result
        state["messages"].append(f"Intake: {result['status']}")
        return state

    def customer_node(self, state: AgentState):
        """Customer agent node"""
        result = self.customer_agent.process(state["application"], state.get("intake_result", {}))
        state["customer_result"] = result
        state["messages"].append(f"Customer: Credit band {result['credit_band']}")
        return state

    def risk_node(self, state: AgentState):
        """Risk agent node"""
        result = self.risk_agent.process(
            state["application"],
            state.get("intake_result", {}),
            state.get("customer_result", {})
        )
        state["risk_result"] = result
        state["messages"].append(f"Risk: Decision {result['decision']} (confidence {result['confidence']:.2f})")
        return state

    def document_node(self, state: AgentState):
        """Document agent node"""
        result = self.document_agent.process(state["application"], state.get("risk_result", {}))
        state["document_result"] = result
        state["messages"].append(f"Document: {len(result['exclusions'])} exclusions")
        return state

    def external_node(self, state: AgentState):
        """External agent node"""
        result = self.external_agent.process(state["application"])
        state["external_result"] = result
        state["messages"].append(f"External: {len(result['external_factors'])} factors")
        return state

    def claims_node(self, state: AgentState):
        """Claims agent node"""
        result = self.claims_agent.process(state["application"])
        state["claims_result"] = result
        state["messages"].append(f"Claims: Severity {result['severity_assessment']}")
        return state

    def decision_node(self, state: AgentState):
        """Decision agent node"""
        all_results = {
            'intake': state.get("intake_result", {}),
            'customer': state.get("customer_result", {}),
            'risk': state.get("risk_result", {}),
            'document': state.get("document_result", {}),
            'external': state.get("external_result", {}),
            'claims': state.get("claims_result", {})
        }
        result = simple_decision(state["application"], all_results)
        state["decision_result"] = result
        state["messages"].append(f"Decision: {result['final_decision']} (risk score {result['final_risk_score']:.1f})")
        return state

    def run_workflow(self, application, mode="sequential"):
        """Run the workflow with specified collaboration mode"""

        if mode == "sequential":
            graph = self.build_sequential_graph()
        elif mode == "parallel":
            graph = self.build_parallel_graph()
        else:
            raise ValueError(f"Unknown mode: {mode}")

        # Initialize state
        initial_state = {
            "application": application,
            "intake_result": {},
            "customer_result": {},
            "risk_result": {},
            "document_result": {},
            "external_result": {},
            "claims_result": {},
            "decision_result": {},
            "messages": [],
            "collaboration_mode": mode
        }

        # Run the graph
        final_state = graph.invoke(initial_state)

        return final_state


if __name__ == "__main__":
    orchestrator = LangGraphOrchestrator()

    # Test with a sample application
    sample_application = {
        'application_id': 'TEST_001',
        'age': 35,
        'credit_score': 650,
        'vehicle_value': 25000,
        'premium_amount': 1200,
        'claim_amount': 5000,
        'fraud_flag': False,
        'location': 'suburban'
    }

    print("=" * 60)
    print("Testing Sequential Workflow (LangGraph)")
    print("=" * 60)
    result_seq = orchestrator.run_workflow(sample_application, mode="sequential")
    print(f"\nFinal Decision: {result_seq['decision_result']['final_decision']}")
    print(f"Risk Score: {result_seq['decision_result']['final_risk_score']:.1f}")
    print(f"Reasons: {result_seq['decision_result']['reasons']}")
    print(f"\nAgent Execution Sequence:")
    for msg in result_seq['messages']:
        print(f"  - {msg}")

    print("\n[INFO] Parallel workflow requires concurrent state updates - documented for future implementation")
