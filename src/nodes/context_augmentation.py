"""Phase 1: Context augmentation - retrieve calendar events."""
from datetime import datetime, timedelta
from typing import Dict, Any
from ..models.state import AgentState
from ..tools.mock_crm import MockCRMTools


def context_augmentation_node(state: AgentState) -> Dict[str, Any]:
    """Retrieve calendar events to establish meeting context.

    This node fetches recent meetings to help identify which meeting
    the notes refer to by matching dates, participants, and companies.

    """
    print("📅 Phase 1: Context Augmentation")

    # Initialize CRM tools
    crm_tools = MockCRMTools()

    # Get date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Retrieve calendar events
    try:
        calendar_events = crm_tools.get_user_calendar(
            user_id=state["user_id"],
            date_range=(start_date, end_date)
        )

        print(f"   Found {len(calendar_events)} recent calendar events")

        return {
            "calendar_events": calendar_events
        }
    except Exception as e:
        print(f"   ⚠️  Error retrieving calendar: {e}")
        return {
            "calendar_events": [],
            "warnings": [f"Calendar retrieval failed: {e}"]
        }
