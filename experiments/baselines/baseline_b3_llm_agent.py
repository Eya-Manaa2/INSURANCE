"""
Baseline B3: Single LLM Agent for Underwriting
Uses Groq API with Mixtral model to evaluate insurance applications
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from collections import Counter

# Load environment variables
load_dotenv()

class SingleLLMAgent:
    """Single LLM agent for underwriting decisions"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=self.api_key)
        self.model = "openai/gpt-oss-20b"
        print(f"[OK] Groq client initialized with model: {self.model}")

    def _create_prompt(self, applicant):
        """Create a structured prompt for the LLM"""

        prompt = f"""You are an insurance underwriting expert. Evaluate the following automobile insurance application and provide a decision.

APPLICANT INFORMATION:
- Age: {applicant.get('age', 'N/A')}
- Credit Score: {applicant.get('credit_score', 'N/A')}
- Vehicle Value: ${applicant.get('vehicle_value', 'N/A')}
- Premium Amount: ${applicant.get('premium_amount', 'N/A')}
- Claim Amount: ${applicant.get('claim_amount', 'N/A')}
- Fraud Flag: {applicant.get('fraud_flag', False)}

UNDERWRITING DECISIONS:
You must choose one of the following decisions:
1. Accept_Standard - Standard acceptance with normal premium
2. Accept_with_Surcharge - Acceptance with additional premium due to risk factors
3. Reject - Reject the application due to high risk

EVALUATION CRITERIA:
- High fraud risk score or fraud indicator → Reject
- Poor credit score + high claim amount → Accept_with_Surcharge
- High claim-to-premium ratio → Accept_with_Surcharge
- Good credit, low claims, reasonable premium → Accept_Standard

Your response must be in the following JSON format exactly:
{{
    "decision": "Accept_Standard|Accept_with_Surcharge|Reject",
    "risk_score": <number between 0 and 100>,
    "confidence": <number between 0 and 1>,
    "reasons": ["reason1", "reason2", ...]
}}

Respond ONLY with the JSON object, no additional text."""

        return prompt

    def evaluate(self, applicant):
        """
        Evaluate an application using LLM

        Returns:
            dict: {decision, risk_score, confidence, reasons}
        """
        try:
            prompt = self._create_prompt(applicant)

            # Generate response using Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an insurance underwriting expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # Parse response
            response_text = response.choices[0].message.content.strip()
            result = json.loads(response_text)

            result['baseline'] = 'B3_llm_agent'
            return result

        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return {
                'decision': 'Error',
                'risk_score': 0,
                'confidence': 0,
                'reasons': [str(e)],
                'baseline': 'B3_llm_agent'
            }


def run_baseline_b3(data_path, sample_size=10):
    """Run baseline B3 on a sample of the dataset"""

    print("=" * 60)
    print("Baseline B3: Single LLM Agent (Groq - GPT OSS 20B)")
    print("=" * 60)

    # Load data
    with open(data_path, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records")
    print(f"Running on sample of {sample_size} records (to save API costs)")

    # Initialize agent
    try:
        agent = SingleLLMAgent()
    except Exception as e:
        print(f"ERROR: {e}")
        return None, 0

    # Evaluate sample
    results = []
    correct = 0

    for i, record in enumerate(data[:sample_size]):
        print(f"\nProcessing record {i+1}/{sample_size}...")

        # Prepare applicant data
        applicant = {
            'age': record.get('age'),
            'credit_score': record.get('credit_score'),
            'vehicle_value': record.get('vehicle_value'),
            'premium_amount': record.get('premium_amount'),
            'claim_amount': record.get('claim_amount'),
            'fraud_flag': record.get('fraud_flag'),
        }

        # Evaluate
        result = agent.evaluate(applicant)
        result['true_decision'] = record.get('decision')
        result['application_id'] = record.get('application_id')

        # Check accuracy
        if result['decision'] == result['true_decision']:
            correct += 1
            print(f"  [CORRECT] {result['decision']}")
        else:
            print(f"  [WRONG] Predicted: {result['decision']}, True: {result['true_decision']}")

        results.append(result)

    # Calculate metrics
    accuracy = correct / len(results)

    # Print results
    print(f"\n" + "=" * 60)
    print(f"Results on {sample_size} records:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Correct: {correct}/{len(results)}")

    # Decision distribution
    decisions = [r['decision'] for r in results]
    print(f"\nDecision distribution:")
    for decision in set(decisions):
        count = decisions.count(decision)
        pct = count / len(results) * 100
        print(f"  {decision}: {count} ({pct:.1f}%)")

    # Risk score distribution
    risk_scores = [r['risk_score'] for r in results if isinstance(r['risk_score'], (int, float))]
    if risk_scores:
        print(f"\nRisk score statistics:")
        print(f"  Mean: {sum(risk_scores)/len(risk_scores):.2f}")
        print(f"  Min: {min(risk_scores):.2f}")
        print(f"  Max: {max(risk_scores):.2f}")

    # Confidence distribution
    confidences = [r['confidence'] for r in results if isinstance(r['confidence'], (int, float))]
    if confidences:
        print(f"\nConfidence statistics:")
        print(f"  Mean: {sum(confidences)/len(confidences):.2f}")
        print(f"  Min: {min(confidences):.2f}")
        print(f"  Max: {max(confidences):.2f}")

    # Save results
    output_path = Path("experiments/baselines/baseline_b3_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")

    return results, accuracy


if __name__ == "__main__":
    data_path = "data/processed/labeled_research_data_improved.json"

    # Run on a larger sample for meaningful comparison
    # Adjust sample_size based on API budget
    results, accuracy = run_baseline_b3(data_path, sample_size=100)
