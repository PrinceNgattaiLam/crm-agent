"""Phase 2: Information extraction - LLM-based structured extraction."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from ..models.state import AgentState, ExtractedInfo
from ..models.crm_entities import Contact, Company, Opportunity


# For follow-ups, we need a custom schema
class FollowUp(BaseModel):
    """Follow-up action item."""
    type: str = Field(description="Type: meeting, task, or validation")
    with_person: str = Field(description="Person to follow up with", alias="with")
    timing: str = Field(description="When to follow up (e.g., 'next week', 'January 15')")
    topic: str = Field(description="What to discuss or accomplish")


class ExtractionOutput(BaseModel):
    """Structured output for meeting notes extraction."""
    meeting_date: Optional[str] = Field(default=None, description="Meeting date in ISO format (YYYY-MM-DD) if mentioned")
    participants: List[Contact] = Field(default_factory=list, description="List of meeting participants - Contact objects with name, role, email, company_name")
    companies: List[Company] = Field(default_factory=list, description="List of companies mentioned - Company objects with name, domain, industry")
    opportunities: List[Opportunity] = Field(default_factory=list, description="Business opportunities discussed - Opportunity objects with title, stage, amount")
    follow_ups: List[FollowUp] = Field(default_factory=list, description="Follow-up actions and commitments")
    key_points: List[str] = Field(default_factory=list, description="Key discussion points")
    sentiment: str = Field(description="Overall sentiment: positive, neutral, or negative")


EXTRACTION_PROMPT = """
You are an AI assistant that extracts structured information from meeting notes.
Your responses should be in french if the meeting notes are in French.

Extract the following information from the meeting notes:
1. Meeting date (if mentioned)
2. Participants with their names, roles, and companies
3. Companies/organizations mentioned
4. Opportunities or deals discussed (existing or new)
5. Follow-up actions and commitments
6. Key discussion points
7. Overall sentiment (positive, neutral, negative)

Meeting notes:
{meeting_notes}

Be thorough and extract all entities, even if some information is incomplete.
"""


def information_extraction_node(state: AgentState) -> Dict[str, Any]:
    """Extract structured information from meeting notes using LLM.

    Args:
        state: Current agent state with meeting_notes
        crm_tools: CRM integration tools
    Returns:
        Updated state with extracted_info
    """
    print("🔍 Phase 2: Information Extraction")

    meeting_notes = state["meeting_notes"]

    # Initialize LLM with structured output
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        temperature=0,
    )

    # Use structured output to constrain the response
    llm_with_structure = llm.with_structured_output(ExtractionOutput)

    # Prepare messages
    messages = [
        SystemMessage(content="You are a helpful AI assistant that extracts structured information from meeting notes."),
        HumanMessage(content=EXTRACTION_PROMPT.format(
            meeting_notes=meeting_notes
        ))
    ]

    try:
        # Call LLM with structured output - this guarantees valid schema
        structured_output: ExtractionOutput = llm_with_structure.invoke(messages)

        print("   ✓ LLM response received (structured)")
        print(f"   Extracted {len(structured_output.participants)} participants")
        print(f"   Found {len(structured_output.companies)} companies")

        # Convert structured output to dict for compatibility
        extracted_data = structured_output.model_dump()

        # Convert follow_ups field (handle the 'with' -> 'with_person' alias)
        follow_ups_converted = []
        for fu in extracted_data.get("follow_ups", []):
            follow_ups_converted.append({
                "type": fu.get("type"),
                "with": fu.get("with_person") or fu.get("with"),
                "timing": fu.get("timing"),
                "topic": fu.get("topic")
            })

        # Convert to ExtractedInfo model
        extracted_info = ExtractedInfo(
            meeting_date=datetime.fromisoformat(extracted_data["meeting_date"]) if extracted_data.get("meeting_date") else None,
            participants=extracted_data.get("participants", []),
            companies=extracted_data.get("companies", []),
            opportunities=extracted_data.get("opportunities", []),
            follow_ups=follow_ups_converted,
            key_points=extracted_data.get("key_points", []),
            sentiment=extracted_data.get("sentiment"),
        )

        print(f"   ✓ Extracted {len(extracted_info.participants)} participants")
        print(f"   ✓ Found {len(extracted_info.companies)} companies")
        print(f"   ✓ Identified {len(extracted_info.opportunities)} opportunities")
        print(f"   ✓ {len(extracted_info.follow_ups)} follow-up actions")

        return {
            "extracted_info": extracted_info
        }

    except Exception as e:
        print(f"   ⚠️  Extraction error: {e}")
        return {
            "errors": [f"Information extraction failed: {e}"]
        }
