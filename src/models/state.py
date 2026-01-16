"""LangGraph state models for the agent workflow."""
from typing import TypedDict, Annotated, Optional, List, Literal
from pydantic import BaseModel, Field
from operator import add
from datetime import datetime
from ..models.crm_entities import Contact, Company, Opportunity


class ExtractedInfo(BaseModel):
    """Structured information extracted from meeting notes."""
    meeting_date: Optional[datetime] = None
    participants: List[Contact] = Field(default_factory=list)  # name, role, company
    companies: List[Company] = Field(default_factory=list)
    opportunities: List[Opportunity] = Field(default_factory=list)
    follow_ups: list[dict] = Field(default_factory=list)  # type, with, timing, topic
    key_points: list[str] = Field(default_factory=list)
    sentiment: Optional[str] = None


class MatchedEntity(BaseModel):
    """Entity matched in CRM with confidence score."""
    entity_type: Literal["company", "contact", "opportunity"]
    name: str
    entity_id: Optional[str] = None
    confidence: float
    action: Literal["use_existing", "validate", "create"]
    alternatives: list[dict] = Field(default_factory=list)
    details: dict = Field(default_factory=dict)


class ActionItem(BaseModel):
    """Planned CRM action to be executed."""
    action_id: int
    action_type: str  # log_meeting, create_contact, create_opportunity, etc.
    tool_name: str
    params: dict
    rationale: str
    dependencies: list[int] = Field(default_factory=list)
    status: str = "pending"  # pending, approved, rejected, executed


class AgentState(TypedDict, total=False):
    """State object for the LangGraph agent."""
    # Input
    meeting_notes: str
    user_id: str

    # Phase 1: Context augmentation
    calendar_events: list[dict]

    # Phase 2: Information extraction
    extracted_info: Optional[ExtractedInfo]

    # Phase 3: Entity resolution (parallel)
    matched_companies: Annotated[list[MatchedEntity], add]
    matched_contacts: Annotated[list[MatchedEntity], add]
    matched_opportunities: Annotated[list[MatchedEntity], add]

    # Phase 4: Validation
    entities_needing_validation: list[MatchedEntity]
    validated_entities: list[MatchedEntity]

    # Phase 5: Action planning
    action_plan: list[ActionItem]

    # Errors and warnings
    errors: Annotated[list[str], add]
    warnings: Annotated[list[str], add]
