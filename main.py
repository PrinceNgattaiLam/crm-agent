"""CRM Agent Main Entry Point - Test Script

hub-crm-agent-meeting-report

This script demonstrates the CRM meeting notes agent by processing
sample meeting notes through the LangGraph pipeline.
"""
import os
from datetime import datetime, timedelta
from src.agent import create_agent_graph, AgentState
from src.tools.mock_crm import MockCRMTools

# Initialize mock CRM
crm = MockCRMTools()

from dotenv import load_dotenv

load_dotenv()

# Sample meeting notes for testing
SAMPLE_MEETING_NOTES = """
Meeting notes –Jan 10
Hier, j’ai rencontré Patrick comme prévu. Nous avons discuté de la propal en cours, et il me
demande de faire un effort sur le prix. Je dois revenir vers lui la semaine prochaine.
Il en a profité pour me présenté Sophie Martin, qui vient de chez Occurent Systems, leur nouvelle
directrice marketing. Elle m’a indiqué commencer de son côté la recherche d’une solution pour
optimiser ses campagnes d’e-mail pour Q2
Il faut valider avec Pierre leur Directeur informatique, les aspects techniques de notre solution
marketing automation.
"""


def run_agent_test():
    """Run the agent on sample meeting notes."""

    print("📝 Sample Meeting Notes:")
    print("-" * 60)
    print(SAMPLE_MEETING_NOTES)
    print("-" * 60)

    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("   Please set your API key:")
        print("   export ANTHROPIC_API_KEY='your-api-key-here'")
        return

    # Initialize the agent graph
    print("\n🔧 Initializing agent graph...")
    graph = create_agent_graph()
    print("✓ Agent graph compiled successfully")

    # Prepare initial state
    print("\n🚀 Starting agent execution...")
    initial_state = {
        "meeting_notes": SAMPLE_MEETING_NOTES,
        "user_id": "test_user_001",
        "calendar_events": [],
        "extracted_info": None,
        "matched_companies": [],
        "matched_contacts": [],
        "matched_opportunities": [],
        "entities_needing_validation": [],
        "validated_entities": [],
        "action_plan": [],
        "user_approved": False,
        "approved_actions": [],
        "execution_results": [],
        "errors": [],
        "warnings": [],
    }

    try:
        # Run the agent
        result = graph.invoke(initial_state)

    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()



if __name__ == "__main__":
    # Test CRM tools first
    # test_crm_tools()

    # Run the full agent
    run_agent_test()


