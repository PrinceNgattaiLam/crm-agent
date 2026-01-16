"""Phase 5: Action planning - generate CRM action plan with dependencies."""
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from ..models.state import AgentState, ActionItem
from ..utils import json_serializer
from ..tools.crm_tools import CRM_TOOLS


# Structured output schema for action planning
class ActionParams(BaseModel):
    """Parameters for a CRM action."""
    # This allows any fields since different actions have different params
    class Config:
        extra = "allow"


class PlannedAction(BaseModel):
    """A single planned CRM action with dependencies."""
    action_id: int = Field(description="Unique action ID (1, 2, 3, ...)")
    action_type: str = Field(description="Type of action (create_contact, create_opportunity, log_meeting_interaction, etc.)")
    tool_name: str = Field(description="Name of the CRM tool to call")
    params: Dict[str, Any] = Field(description="Parameters to pass to the tool")
    rationale: str = Field(description="Why this action is needed")
    dependencies: List[int] = Field(default_factory=list, description="List of action_ids this action depends on")


class ActionPlanOutput(BaseModel):
    """Complete action plan for CRM updates."""
    actions: List[PlannedAction] = Field(description="Ordered list of actions to execute")


ACTION_PLANNING_PROMPT = """You are an AI assistant that creates CRM action plans based on meeting analysis.
Your responses should always be in french if the meeting notes are in French.

You have analyzed a meeting and resolved the following entities:

COMPANIES:
{companies}

CONTACTS:
{contacts}

OPPORTUNITIES:
{opportunities}

EXTRACTED INFORMATION:
{extracted_info}

You have access to CRM tools (bound to this conversation) that you can reference in your action plan.
Use the exact tool names and parameters as defined in the tool schemas.

For each action, specify:
- action_id: Sequential number (1, 2, 3, ...)
- action_type: Type of action (create_contact, create_opportunity, log_meeting_interaction, create_follow_up_task, update_opportunity, etc.)
- tool_name: Name of the CRM tool to call
- params: Parameters to pass to the tool
- rationale: Why this action is needed
- dependencies: List of action_ids this action depends on (use empty list if no dependencies)

Use placeholder values like "[DEPENDS_ON:1]" in params when you need the result of a previous action.

Be thorough and include all necessary actions to update the CRM.
"""


def action_planning_node(state: AgentState) -> Dict[str, Any]:
    """Generate structured action plan with dependencies.

    Args:
        state: Current agent state with all resolved entities

    Returns:
        State update with action_plan
    """
    print("📋 Phase 5: Action Planning")

    # Collect all resolved entities
    companies = state.get("matched_companies", [])
    contacts = state.get("matched_contacts", [])
    opportunities = state.get("matched_opportunities", [])
    extracted_info = state.get("extracted_info")

    # Format entities for prompt (use custom serializer for datetime objects)
    companies_str = json.dumps([c.model_dump() for c in companies], indent=2, default=json_serializer)
    contacts_str = json.dumps([c.model_dump() for c in contacts], indent=2, default=json_serializer)
    opportunities_str = json.dumps([o.model_dump() for o in opportunities], indent=2, default=json_serializer)
    extracted_str = json.dumps(extracted_info.model_dump(), indent=2, default=json_serializer) if extracted_info else "{}"

    # Initialize LLM with tools bound (for awareness) and structured output
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0,
    )

    # Bind CRM tools so LLM knows what tools are available, then force structured output
    # The LLM will see the tools but will return ActionPlanOutput instead of calling them
    llm_with_structure = llm.bind_tools(CRM_TOOLS).with_structured_output(ActionPlanOutput)

    # Prepare messages
    messages = [
        SystemMessage(content="You are a helpful AI assistant that creates CRM action plans."),
        HumanMessage(content=ACTION_PLANNING_PROMPT.format(
            companies=companies_str,
            contacts=contacts_str,
            opportunities=opportunities_str,
            extracted_info=extracted_str
        ))
    ]

    try:
        # Call LLM with structured output - this guarantees valid schema
        structured_output: ActionPlanOutput = llm_with_structure.invoke(messages)

        print(f"   ✓ Action plan generated (structured)")
        print(f"   Found {len(structured_output.actions)} actions")

        # Convert to ActionItem models
        action_plan = []
        for action_data in structured_output.actions:
            action = ActionItem(
                action_id=action_data.action_id,
                action_type=action_data.action_type,
                tool_name=action_data.tool_name,
                params=action_data.params,
                rationale=action_data.rationale,
                dependencies=action_data.dependencies,
                status="pending"
            )
            action_plan.append(action)

        print(f"   ✓ Generated {len(action_plan)} actions")
        print("\n" + "="*70)
        print("  ACTION PLAN")
        print("="*70)
        visualize_action_plan(action_plan)

        print("\n" + "="*70)

        return {
            "action_plan": action_plan
        }

    except Exception as e:
        print(f"   ⚠️  Action planning error: {e}")
        return {
            "action_plan": [],
            "errors": [f"Action planning failed: {e}"]
        }

def visualize_action_plan(action_plan: List[ActionItem]) -> None:
    """Print a simple visualization of the action plan.

    Args:
        action_plan: List of planned actions
    """
    for action in action_plan:
        # Format action type as readable label
        action_label = action.action_type.upper().replace("_", " ")

        # Print action header
        print(f"\n{action.action_id}. [{action_label}]", end="")

        # Extract and display key information based on action type
        params = action.params

        if "create_contact" in action.action_type.lower():
            print(f" {params.get('name', 'N/A')}")
            if params.get('company_id'):
                print(f"   Company: {params.get('company_id')}")
            if params.get('role'):
                print(f"   Role: {params['role']}")
            if params.get('email'):
                print(f"   Email: {params['email']}")

        elif "create_opportunity" in action.action_type.lower():
            print(f" {params.get('title', 'N/A')}")
            if params.get('company_id'):
                print(f"   Company: {params['company_id']}")
            if params.get('stage'):
                print(f"   Stage: {params['stage'].title()}")
            if params.get('amount'):
                print(f"   Amount: ${params['amount']:,.2f}")

        elif "log_meeting" in action.action_type.lower():
            print(f" {params.get('notes', 'Meeting interaction')}")
            if params.get('date'):
                print(f"   Date: {params['date']}")
            if params.get('company_id'):
                print(f"   Company: {params['company_id']}")
            if params.get('participants'):
                print(f"   Participants: {len(params['participants'])} contact(s)")

        elif "update_opportunity" in action.action_type.lower():
            print(f" Update opportunity {params.get('opportunity_id', 'N/A')}")
            if params.get('stage'):
                print(f"   New stage: {params['stage'].title()}")
            if params.get('amount'):
                print(f"   New amount: ${params['amount']:,.2f}")
            if params.get('notes'):
                print(f"   Note: {params['notes']}")

        elif "create_follow_up_task" in action.action_type.lower() or "task" in action.action_type.lower():
            print(f" {params.get('title', 'N/A')}")
            if params.get('description'):
                print(f"   {params['description']}")
            if params.get('due_date'):
                print(f"   Due: {params['due_date']}")
            if params.get('contact_id'):
                print(f"   Contact: {params['contact_id']}")
        else:
            # Generic display for other action types
            print(f" {params}")

        # Show rationale
        print(f"   Rationale: {action.rationale}")

        # Show dependencies if any
        if action.dependencies:
            dep_str = ", ".join([f"#{d}" for d in action.dependencies])
            print(f"   Dependencies: Depends on action(s) {dep_str}")