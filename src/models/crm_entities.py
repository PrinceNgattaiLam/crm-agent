"""CRM entity data models."""
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime


class Company(BaseModel):
    """Company entity in CRM."""
    name: str
    company_id: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None


class Contact(BaseModel):
    """Contact entity in CRM."""
    name: str
    contact_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None

class Opportunity(BaseModel):
    """Opportunity (deal) entity in CRM."""
    
    title: str
    opportunity_id: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    stage: Literal["approach", "proposal", "negotiate", "closed_won", "closed_lost"]
    amount: Optional[float] = None
    expected_close_date: Optional[datetime] = None
    contacts: list[str] = Field(default_factory=list)
    last_activity: Optional[datetime] = None


class CalendarEvent(BaseModel):
    """Calendar event with CRM linkage."""
    event_id: str
    title: str
    date: datetime
    participants: List[str] = Field(default_factory=list)
    company_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    notes: Optional[str] = None
