"""Mock CRM tools simulating MCP-based CRM integration.

This implements a fake CRM database for testing the agent pipeline.
In production, this would be replaced with actual MCP tool calls.
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from ..models.crm_entities import Company, Contact, Opportunity, CalendarEvent
from fuzzywuzzy import fuzz
import unicodedata
import re


class MockCRMTools:
    """Mock CRM database with search capabilities."""

    def __init__(self):
        """Initialize mock CRM with sample data."""
        self._companies = self._create_mock_companies()
        self._contacts = self._create_mock_contacts()
        self._opportunities = self._create_mock_opportunities()
        self._calendar_events = self._create_mock_calendar()

    def _create_mock_companies(self) -> Dict[str, Company]:
        """Create mock company records."""
        return {
            "comp_123": Company(
                company_id="comp_123",
                name="Nextera",
                domain="nextera.com",
                industry="Technology",
            ),
            "comp_124": Company(
                company_id="comp_124",
                name="Occurent Systems",
                domain="occurent.com",
                industry="Software",
            ),
            "comp_125": Company(
                company_id="comp_125",
                name="TechCorp International",
                domain="techcorp.com",
                industry="Technology",
            ),
        }

    def _create_mock_contacts(self) -> Dict[str, Contact]:
        """Create mock contact records."""
        return {
            "cont_456": Contact(
                contact_id="cont_456",
                name="Patrick Dubois",
                email="patrick.dubois@nextera.com",
                role="Sales Director",
                company_id="comp_123",
                company_name="Nextera",
            ),
            "cont_789": Contact(
                contact_id="cont_789",
                name="Pierre Lefevre",
                email="pierre.lefevre@nextera.com",
                role="IT Director",
                company_id="comp_123",
                company_name="Nextera",
            ),
            "cont_790": Contact(
                contact_id="cont_790",
                name="Pierre Dubois",
                email="pierre.dubois@nextera.com",
                role="Technical Lead",
                company_id="comp_123",
                company_name="Nextera",
            ),
            "cont_791": Contact(
                contact_id="cont_791",
                name="Marie Laurent",
                email="marie.laurent@techcorp.com",
                role="CEO",
                company_id="comp_125",
                company_name="TechCorp International",
            ),
        }

    def _create_mock_opportunities(self) -> Dict[str, Opportunity]:
        """Create mock opportunity records."""
        return {
            "opp_321": Opportunity(
                opportunity_id="opp_321",
                title="Nextera - CRM Implementation 2026",
                company_id="comp_123",
                company_name="Nextera",
                stage="proposal",
                amount=150000.0,
                expected_close_date=datetime(2026, 3, 31),
                contacts=["cont_456", "cont_789"],
                last_activity=datetime.now() - timedelta(days=14),
            ),
            "opp_322": Opportunity(
                opportunity_id="opp_322",
                title="TechCorp - Digital Transformation",
                company_id="comp_125",
                company_name="TechCorp International",
                stage="negotiate",
                amount=500000.0,
                expected_close_date=datetime(2026, 6, 30),
                contacts=["cont_791"],
                last_activity=datetime.now() - timedelta(days=5),
            ),
        }

    def _create_mock_calendar(self) -> Dict[str, CalendarEvent]:
        """Create mock calendar events."""
        return {
            "evt_001": CalendarEvent(
                event_id="evt_001",
                title="Nextera - Proposal Discussion",
                date=datetime(2026, 1, 15, 14, 0),
                participants=["cont_456"],
                company_id="comp_123",
                opportunity_id="opp_321",
                notes="Discussed pricing and timeline",
            ),
            "evt_002": CalendarEvent(
                event_id="evt_002",
                title="TechCorp Quarterly Review",
                date=datetime(2026, 1, 14, 10, 0),
                participants=["cont_791"],
                company_id="comp_125",
                opportunity_id="opp_322",
                notes="Progress update on digital transformation",
            ),
        }

    @staticmethod
    def _normalize_string(s: str) -> str:
        """Normalize string for fuzzy matching (remove accents, lowercase)."""
        # Remove accents
        nfkd = unicodedata.normalize('NFKD', s)
        normalized = ''.join([c for c in nfkd if not unicodedata.combining(c)])
        # Lowercase and strip
        return normalized.lower().strip()

    def get_user_calendar(
        self, user_id: str, date_range: tuple[datetime, datetime]
    ) -> List[Dict[str, Any]]:
        """Retrieve calendar events for a user within date range.

        Args:
            user_id: User identifier
            date_range: Tuple of (start_date, end_date)

        Returns:
            List of calendar events with linked CRM entities
        """
        start, end = date_range
        events = []

        for event in self._calendar_events.values():
            if start <= event.date <= end:
                events.append(event.model_dump())

        return events

    def search_company(
        self, query: str
    ) -> List[Dict[str, Any]]:
        """Search for companies in CRM.

        Args:
            query: Company name to search

        Returns:
            List of matched companies with confidence scores
        """
        results = []
        query_norm = self._normalize_string(query)

        for company in self._companies.values():
            name_norm = self._normalize_string(company.name)

            # Calculate confidence score
            confidence = 0.0

            # Exact match
            if query_norm == name_norm:
                confidence = 1.0
            else:
                # Fuzzy match
                confidence = fuzz.ratio(query_norm, name_norm) / 100.0

            # # Boost if in calendar context
            # TODO: Use calendar context to boost scores
            # Not implemented in this mock version because wasn't sure of 
            # how it would look  but the code could be something like this
            # if context:
            #     for event in context:
            #         if event.get("company_id") == company.company_id:
            #             confidence = min(1.0, confidence + 0.15)
            #             break

            if confidence > 0.2:  # Threshold for returning results
                result = company.model_dump()
                result["confidence"] = confidence
                results.append(result)

        # Sort by confidence descending
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def search_contact(
        self,
        query: str,
        role_context: Optional[str] = None,
        company_context: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for contacts in CRM.

        Args:
            query: Contact name to search
            role_context: Optional role hint from notes
            company_context: Optional company name from notes

        Returns:
            List of matched contacts with confidence scores
        """
        results = []
        query_norm = self._normalize_string(query)

        for contact in self._contacts.values():
            name_norm = self._normalize_string(contact.name)

            # Calculate confidence score
            confidence = 0.0

            # Name matching (exact, partial, or fuzzy)
            if query_norm == name_norm:
                confidence = 0.9
            elif query_norm in name_norm or name_norm in query_norm:
                confidence = 0.6
            else:
                # Fuzzy match on name
                confidence = fuzz.ratio(query_norm, name_norm) / 100.0 * 0.7
                
            # Boost for company match
            # This boost emulates what's done by the real DB in case of search
            if company_context and contact.company_name:
                company_norm = self._normalize_string(company_context)
                contact_company_norm = self._normalize_string(contact.company_name)
                if fuzz.ratio(company_norm, contact_company_norm) > 80:
                    confidence = min(1.0, confidence + 0.2)


            if confidence > 0.2:
                result = contact.model_dump()
                result["confidence"] = confidence
                results.append(result)

        # Sort by confidence descending
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def search_opportunity(
        self,
        keywords: List[str],
        company_context: Optional[str] = None,
        stage_hint: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for opportunities in CRM.

        Args:
            keywords: Keywords from meeting notes
            company_context: Optional company name
            stage_hint: Optional stage indicator (proposal, negotiate, etc.)

        Returns:
            List of matched opportunities with confidence scores
        """
        results = []

        for opp in self._opportunities.values():
            confidence = 0.0

            # Keyword matching in title
            title_norm = self._normalize_string(opp.title)
            for keyword in keywords:
                keyword_norm = self._normalize_string(keyword)
                if keyword_norm in title_norm:
                    confidence = min(1.0, confidence + 0.3)

            # Company match
            if company_context and opp.company_name:
                company_norm = self._normalize_string(company_context)
                opp_company_norm = self._normalize_string(opp.company_name)
                if fuzz.ratio(company_norm, opp_company_norm) > 80:
                    confidence = min(1.0, confidence + 0.3)

            # Stage hint matching
            if stage_hint:
                stage_map = {
                    "proposal": ["proposal", "propose"],
                    "negotiate": ["negotiate", "negotiation", "pricing"],
                    "approach": ["approach", "initial", "interest"],
                }
                for stage, hints in stage_map.items():
                    if any(h in self._normalize_string(stage_hint) for h in hints):
                        if opp.stage == stage:
                            confidence = min(1.0, confidence + 0.2)

            if confidence > 0.2:
                result = opp.model_dump()
                result["confidence"] = confidence
                results.append(result)

        # Sort by confidence descending
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    # Write tools (mock implementations)
    def create_company(self, name: str, **kwargs) -> str:
        """Create new company."""
        company_id = f"comp_{len(self._companies) + 1000}"
        company = Company(company_id=company_id, name=name, **kwargs)
        self._companies[company_id] = company
        return company_id

    def create_contact(self, name: str, **kwargs) -> str:
        """Create new contact."""
        contact_id = f"cont_{len(self._contacts) + 1000}"
        contact = Contact(contact_id=contact_id, name=name, **kwargs)
        self._contacts[contact_id] = contact
        return contact_id

    def create_opportunity(self, title: str, **kwargs) -> str:
        """Create new opportunity."""
        opp_id = f"opp_{len(self._opportunities) + 1000}"
        opportunity = Opportunity(opportunity_id=opp_id, title=title, **kwargs)
        self._opportunities[opp_id] = opportunity
        return opp_id

    def log_meeting_interaction(self, **kwargs) -> str:
        """Log meeting interaction."""
        event_id = f"evt_{len(self._calendar_events) + 1000}"
        return event_id

    def update_opportunity(self, opportunity_id: str, fields_to_update: Dict) -> bool:
        """Update opportunity fields."""
        if opportunity_id in self._opportunities:
            for field, value in fields_to_update.items():
                setattr(self._opportunities[opportunity_id], field, value)
            return True
        return False

    def create_follow_up_task(self, **kwargs) -> str:
        """Create follow-up task."""
        task_id = f"task_{datetime.now().timestamp()}"
        return task_id
