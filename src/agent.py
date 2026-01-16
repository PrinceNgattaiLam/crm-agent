"""LangGraph agent setup and workflow definition."""
from langgraph.graph import StateGraph, END, START
from .nodes.entity_resolution import resolve_companies_node, resolve_contacts_node, resolve_opportunities_node
from .models.state import AgentState
from .nodes.information_extraction import information_extraction_node
from .nodes.validation import validation_node, should_skip_validation
from .nodes.action_planning import action_planning_node
from .nodes.context_augmentation import context_augmentation_node


# ============================================================================
# LangGraph Setup
# ============================================================================

def create_agent_graph():
    """Create and compile the LangGraph agent."""
    # Initialize graph
    workflow = StateGraph(AgentState)

    # Add nodes with CRM tools bound
    workflow.add_node("context_augmentation", context_augmentation_node)
    workflow.add_node("information_extraction", information_extraction_node)

    # Phase 3: Parallel entity resolution
    workflow.add_node("resolve_companies", resolve_companies_node)
    workflow.add_node("resolve_contacts", resolve_contacts_node)
    workflow.add_node("resolve_opportunities",resolve_opportunities_node)

    # Add a checkpoint node to check if validation is needed
    workflow.add_node("validation_check", lambda state: state)

    # Phase 4: Validation
    workflow.add_node("validation", validation_node)

    # Phase 5: Action planning
    workflow.add_node("action_planning", action_planning_node)
    
    # Set entry point
    workflow.set_entry_point("context_augmentation")
    
    # Define edges
    
    # Phase 1 → Phase 2
    workflow.add_edge("context_augmentation", "information_extraction")

    # Phase 2 → Phase 3 (parallel)
    # All three resolution nodes run in parallel
    workflow.add_edge("information_extraction", "resolve_companies")
    workflow.add_edge("information_extraction", "resolve_contacts")
    workflow.add_edge("information_extraction", "resolve_opportunities")

    # Phase 3 → Validation checkpoint
    # All parallel nodes converge to the validation checkpoint
    workflow.add_edge("resolve_companies", "validation_check")
    workflow.add_edge("resolve_contacts", "validation_check")
    workflow.add_edge("resolve_opportunities", "validation_check")

    # Validation checkpoint → conditional edge
    # Check if validation is needed and route accordingly
    workflow.add_conditional_edges(
        "validation_check",
        should_skip_validation,
        {
            "validate": "validation",       # Go to validation if needed
            "skip": "action_planning"       # Skip directly to action planning
        }
    )

    # Phase 4 → Phase 5 (after validation)
    workflow.add_edge("validation", "action_planning")

    # Phase 5 → END
    workflow.add_edge("action_planning", END)

    

    # Compile the graph
    return workflow.compile()

