from typing import Optional, List, Dict, Any, Annotated
from langchain_core.tools import tool
from datetime import datetime, timedelta
from .mock_crm import MockCRMTools

# Initialize mock CRM instance (singleton for the module)
crm = MockCRMTools()
@tool
def get_user_calendar(
    user_id: str,
    days_back: int = 7
) -> List[Dict[str, Any]]:
    """Retrieve recent calendar events for a user.

    Args:
        user_id: User identifier
        days_back: Number of days to look back (default: 7)

    Returns:
        List of calendar events with linked CRM entities
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return crm.get_user_calendar(user_id, (start_date, end_date))

@tool
def search_company(
    query: Annotated[str, "Company name to search for"],
) -> List[Dict[str, Any]]:
    """Search for companies in the CRM database.

    Use this tool to find existing companies that match the query.
    Returns matches with confidence scores.

    Args:
        query: Company name to search for
        use_calendar_context: Boost scores for companies in recent meetings

    Returns:
        List of matched companies with confidence scores, sorted by relevance
    """
    print(f"Searching companies with query: {query}")
    # Get calendar context if requested

    return crm.search_company(query)

@tool
def search_contact(
    query: Annotated[str, "Contact name to search for"],
    role: Annotated[Optional[str], "Role or title hint (e.g., 'IT Director', 'Marketing')"] = None,
    company: Annotated[Optional[str], "Company name hint"] = None,
) -> List[Dict[str, Any]]:
    """Search for contacts in the CRM database.

    Use this tool to find existing contacts that match the query.
    Provide role_hint and company_hint to improve matching accuracy.

    Args:
        query: Contact name to search for
        role_hint: Optional role/title to improve matching (e.g., "Director", "Manager")
        company_hint: Optional company name to narrow search

    Returns:
        List of matched contacts with confidence scores, sorted by relevance
    """
    print(f"Searching contacts with query: {query}, role: {role}, company: {company}")  
    # Get calendar context if requested
    return crm.search_contact(
        query=query,
        role_context=role,
        company_context=company
    )

@tool
def search_opportunity(
    keywords: Annotated[List[str], "Keywords to search for in opportunity titles/descriptions"],
    company_hint: Annotated[Optional[str], "Company name associated with the opportunity"] = None,
    stage_hint: Annotated[Optional[str], "Stage indicator (e.g., 'proposal', 'negotiate', 'approach')"] = None
) -> List[Dict[str, Any]]:
    """Search for opportunities (deals) in the CRM database.

    Use this tool to find existing opportunities that match the search criteria.
    Provide company_hint and stage_hint to improve matching accuracy.

    Args:
        keywords: List of keywords to search for (e.g., ["CRM", "implementation"], ["marketing", "automation"])
        company_hint: Optional company name to narrow search
        stage_hint: Optional stage indicator to improve matching

    Returns:
        List of matched opportunities with confidence scores, sorted by relevance
    """
    print(f"Searching opportunities with keywords: {keywords}, company_hint: {company_hint}, stage_hint: {stage_hint}")
    return crm.search_opportunity(
        keywords=keywords,
        company_context=company_hint,
        stage_hint=stage_hint
    )

@tool
def create_company(
    name: Annotated[str, "Company name"],
    domain: Annotated[Optional[str], "Company website domain"] = None,
    industry: Annotated[Optional[str], "Industry/sector"] = None
) -> str:
    """Create a new company in the CRM.

    Args:
        name: Company name (required)
        domain: Company website domain (optional)
        industry: Industry or sector (optional)

    Returns:
        Created company ID
    """
    return crm.create_company(name=name, domain=domain, industry=industry)

@tool
def create_contact(
    name: Annotated[str, "Contact full name"],
    company_id: Annotated[str, "Company ID to associate with"],
    role: Annotated[Optional[str], "Job title/role"] = None,
    email: Annotated[Optional[str], "Email address"] = None
) -> str:
    """Create a new contact in the CRM.

    Args:
        name: Contact full name (required)
        company_id: ID of the company this contact belongs to (required)
        role: Job title or role (optional)
        email: Email address (optional)

    Returns:
        Created contact ID
    """
    return crm.create_contact(
        name=name,
        company_id=company_id,
        role=role,
        email=email
    )

@tool
def create_opportunity(
    title: Annotated[str, "Opportunity title"],
    company_id: Annotated[str, "Company ID"],
    stage: Annotated[str, "Current stage (approach/proposal/negotiate/closed)"],
    amount: Annotated[Optional[float], "Deal amount"] = None
) -> str:
    """Create a new opportunity (deal) in the CRM.

    Args:
        title: Opportunity title (required)
        company_id: ID of the company (required)
        stage: Current stage: approach, proposal, negotiate, or closed (required)
        amount: Expected deal amount in dollars (optional)

    Returns:
        Created opportunity ID
    """
    return crm.create_opportunity(
        title=title,
        company_id=company_id,
        stage=stage,
        amount=amount
    )

@tool
def log_meeting_interaction(
    date: Annotated[str, "Meeting date (ISO format)"],
    participants: Annotated[List[str], "List of contact IDs who participated"],
    company_id: Annotated[str, "Company ID"],
    opportunity_id: Annotated[Optional[str], "Related opportunity ID"] = None,
    notes: Annotated[str, "Meeting notes/summary"] = ""
) -> str:
    """Log a meeting interaction in the CRM.

    Args:
        date: Meeting date in ISO format (e.g., "2026-01-15")
        participants: List of contact IDs who participated
        company_id: Company ID
        opportunity_id: Related opportunity ID if applicable
        notes: Meeting notes or summary

    Returns:
        Created interaction ID
    """
    return crm.log_meeting_interaction(
        type="meeting",
        date=date,
        participants=participants,
        company_id=company_id,
        opportunity_id=opportunity_id,
        notes=notes
    )

@tool
def update_opportunity(
    opportunity_id: Annotated[str, "Opportunity ID to update"],
    stage: Annotated[Optional[str], "New stage"] = None,
    amount: Annotated[Optional[float], "New amount"] = None,
    notes: Annotated[Optional[str], "Additional notes to append"] = None
) -> bool:
    """Update an existing opportunity in the CRM.

    Args:
        opportunity_id: ID of the opportunity to update (required)
        stage: New stage (optional)
        amount: New amount (optional)
        notes: Additional notes (optional)

    Returns:
        True if successful, False otherwise
    """
    fields_to_update = {}
    if stage:
        fields_to_update["stage"] = stage
    if amount is not None:
        fields_to_update["amount"] = amount
    if notes:
        fields_to_update["notes"] = notes

    return crm.update_opportunity(opportunity_id, fields_to_update)

@tool
def create_follow_up_task(
    title: Annotated[str, "Task title"],
    description: Annotated[str, "Task description"],
    due_date: Annotated[Optional[str], "Due date (ISO format)"] = None,
    contact_id: Annotated[Optional[str], "Related contact ID"] = None,
    opportunity_id: Annotated[Optional[str], "Related opportunity ID"] = None
) -> str:
    """Create a follow-up task in the CRM.

    Args:
        title: Task title (required)
        description: Task description (required)
        due_date: Due date in ISO format (optional)
        contact_id: Related contact ID (optional)
        opportunity_id: Related opportunity ID (optional)

    Returns:
        Created task ID
    """
    linked_entities = {}
    if contact_id:
        linked_entities["contact_id"] = contact_id
    if opportunity_id:
        linked_entities["opportunity_id"] = opportunity_id

    return crm.create_follow_up_task(
        title=title,
        description=description,
        due_date=due_date,
        assigned_to="current_user",
        linked_entities=linked_entities
    )

# List of all tools available to the agent
CRM_TOOLS = [
    get_user_calendar,
    search_company,
    search_contact,
    search_opportunity,
    create_company,
    create_contact,
    create_opportunity,
    log_meeting_interaction,
    update_opportunity,
    create_follow_up_task,
]

__all__ = ["CRM_TOOLS"]