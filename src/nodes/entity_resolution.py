"""Phase 3: Entity resolution - parallel search across CRM entities.

All entity searches (companies, contacts, opportunities) execute in parallel
for maximum speed, with confidence-based decision making.
"""
from typing import Dict, Any, List
from ..models.state import AgentState, MatchedEntity
from ..tools.mock_crm import MockCRMTools

# Confidence thresholds from architecture
COMPANY_HIGH_THRESHOLD = 0.85
CONTACT_HIGH_THRESHOLD = 0.85
OPPORTUNITY_HIGH_THRESHOLD = 0.85
CREATION_THRESHOLD = 0.2


def determine_action(confidence: float, high_threshold: float) -> str:
    """Determine action based on confidence score.

    Args:
        confidence: Match confidence score (0-1)
        high_threshold: High confidence threshold for this entity type

    Returns:
        Action: "use_existing", "validate", or "create"
    """
    #TODO Action should be StrEnum
    if confidence >= high_threshold:
        return "use_existing"
    elif confidence >= CREATION_THRESHOLD:
        return "validate"
    else:
        return "create"


def resolve_companies_node(state: AgentState) -> Dict[str, Any]:
    """Resolve company entities in parallel.

    Args:
        state: Current agent state with extracted_info

    Returns:
        State update with matched_companies
    """
    print("🏢 Phase 3a: Resolving Companies (parallel)")

    # Initialize CRM tools
    crm_tools = MockCRMTools()

    extracted_info = state.get("extracted_info")
    if not extracted_info:
        return {"matched_companies": []}

    companies = extracted_info.companies
    matched_companies = []

    for company in companies:
        company_name = company.name

        try:
            # Search CRM
            results = crm_tools.search_company(
                query=company_name,
            )

            if results:
                # Take top match
                top_match = results[0]
                confidence = top_match["confidence"]
                action = determine_action(confidence, COMPANY_HIGH_THRESHOLD)

                matched = MatchedEntity(
                    entity_type="company",
                    name=top_match.get("company_name"),
                    entity_id=top_match.get("company_id") if action != "create" else None,
                    confidence=confidence,
                    action=action,
                    alternatives=results[1:4] if action == "validate" else [],
                    details=top_match if action != "create" else {}
                )
                matched_companies.append(matched)
                print(f"   {company_name}: {action} (confidence: {confidence:.2f})")
            else:
                # No matches - create new
                matched = MatchedEntity(
                    entity_type="company",
                    name=company_name,
                    entity_id=None,
                    confidence=0.0,
                    action="create",
                    alternatives=[],
                    details={}
                )
                matched_companies.append(matched)
                print(f"   {company_name}: create (no matches)")

        except Exception as e:
            print(f"   ⚠️  Error resolving {company_name}: {e}")
    return {"matched_companies": matched_companies}


def resolve_contacts_node(state: AgentState) -> Dict[str, Any]:
    """Resolve contact entities in parallel.

    Args:
        state: Current agent state with extracted_info

    Returns:
        State update with matched_contacts
    """
    print("👤 Phase 3b: Resolving Contacts (parallel)")

    # Initialize CRM tools
    crm_tools = MockCRMTools()

    extracted_info = state.get("extracted_info")
    if not extracted_info:
        return {"matched_contacts": []}

    participants = extracted_info.participants
    matched_contacts = []

    for participant in participants:
        # Extract Contact object fields
        name = participant.name
        role = participant.role
        company = participant.company_name
        participant_dict = participant.model_dump()

        try:
            # Search CRM
            results = crm_tools.search_contact(
                query=name,
                role_context=role,
                company_context=company,
            )

            if results:
                # Take top match
                top_match = results[0]
                confidence = top_match["confidence"]
                action = determine_action(confidence, CONTACT_HIGH_THRESHOLD)

                matched = MatchedEntity(
                    entity_type="contact",
                    name=top_match.get("name", name),
                    entity_id=top_match.get("contact_id") if action != "create" else None,
                    confidence=confidence,
                    action=action,
                    alternatives=results[1:4] if action == "validate" else [],
                    details={**top_match, **participant_dict} if action != "create" else participant_dict
                )
                matched_contacts.append(matched)
                print(f"   {name}: {action} (confidence: {confidence:.2f})")
            else:
                # No matches - create new
                matched = MatchedEntity(
                    entity_type="contact",
                    name=name,
                    entity_id=None,
                    confidence=0.0,
                    action="create",
                    alternatives=[],
                    details=participant_dict
                )
                matched_contacts.append(matched)
                print(f"   {name}: create (no matches)")

        except Exception as e:
            print(f"   ⚠️  Error resolving {name}: {e}")
    return {"matched_contacts": matched_contacts}


def resolve_opportunities_node(state: AgentState) -> Dict[str, Any]:
    """Resolve opportunity entities in parallel.

    Args:
        state: Current agent state with extracted_info

    Returns:
        State update with matched_opportunities
    """
    print("💼 Phase 3c: Resolving Opportunities (parallel)")

    # Initialize CRM tools
    crm_tools = MockCRMTools()

    extracted_info = state.get("extracted_info")
    if not extracted_info:
        return {"matched_opportunities": []}

    opportunities = extracted_info.opportunities
    companies = extracted_info.companies
    matched_opportunities = []

    for opp in opportunities:
        # Extract Opportunity object fields
        opp_title = opp.title
        opp_stage = opp.stage
        opp_dict = opp.model_dump()

        # Extract keywords for search
        keywords = [opp_title, opp_stage]

        # Get company context from Company object
        company_context = None
        if companies:
            first_company = companies[0]
            company_context = first_company.name

        try:
            # Search CRM
            results = crm_tools.search_opportunity(
                keywords=keywords,
                company_context=company_context,
                stage_hint=opp_stage
            )

            if results:
                # Take top match
                top_match = results[0]
                confidence = top_match["confidence"]
                action = determine_action(confidence, OPPORTUNITY_HIGH_THRESHOLD)

                matched = MatchedEntity(
                    entity_type="opportunity",
                    name=top_match.get("title", opp_title),
                    entity_id=top_match.get("opportunity_id") if action != "create" else None,
                    confidence=confidence,
                    action=action,
                    alternatives=results[1:4] if action == "validate" else [],
                    details={**top_match, **opp_dict} if action != "create" else opp_dict
                )
                matched_opportunities.append(matched)
                print(f"   {matched.name}: {action} (confidence: {confidence:.2f})")
            else:
                # No matches - create new
                matched = MatchedEntity(
                    entity_type="opportunity",
                    name=opp_title or "New Opportunity",
                    entity_id=None,
                    confidence=0.0,
                    action="create",
                    alternatives=[],
                    details=opp_dict
                )
                matched_opportunities.append(matched)
                print(f"   {matched.name}: create (no matches)")

        except Exception as e:
            print(f"   ⚠️  Error resolving opportunity: {e}")

    return {"matched_opportunities": matched_opportunities}
