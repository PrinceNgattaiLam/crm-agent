"""Data models for the CRM agent."""
from .state import AgentState, ExtractedInfo, MatchedEntity, ActionItem
from .crm_entities import Company, Contact, Opportunity, CalendarEvent

__all__ = [
    "AgentState",
    "ExtractedInfo",
    "MatchedEntity",
    "ActionItem",
    "Company",
    "Contact",
    "Opportunity",
    "CalendarEvent",
]
