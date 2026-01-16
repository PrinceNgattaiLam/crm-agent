# CRM Meeting Notes Agent

A LangGraph-based agent that processes meeting notes and generates structured action suggestions for CRM operations with intelligent entity resolution and disambiguation.

## Features

### Phase 1: Context Augmentation
- **Calendar Integration**: Retrieves recent calendar events (last 7 days) to provide context
- **Meeting Context**: Links meeting notes to calendar events for better entity matching

### Phase 2: Information Extraction
- **Structured Output**: Uses Claude with Pydantic schemas for guaranteed valid JSON
- **Comprehensive Extraction**:
  - Meeting date and participants (with roles and companies if possible)
  - Companies mentioned
  - Opportunities and deals discussed
  - Follow-up actions and commitments
  - Key discussion points and sentiment analysis

### Phase 3: Entity Resolution
  Fuzzy matching with confidence scoring for:
  - Companies (confidence threshold: 85%)
  - Contacts (confidence threshold: 85%)
  - Opportunities (confidence threshold: 85%)


### Phase 4: Confidence Validation & Disambiguation
Shows alternatives with confidence scores to user if necessary or automatically select top matches

### Phase 5: Action Planning
Generate action plan

### Key Technologies

- **LangGraph**: State-based workflow orchestration with parallel execution
- **Claude Sonnet 4.5**: Latest model with structured output support
- **Pydantic**: Schema validation and type safety
- **Fuzzy Matching**: Entity resolution with confidence scoring

## Installation

### Prerequisites
- Python 3.10+
- Anthropic API key
- uv

### Setup

1. Install `uv`
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
2. Run the following command in the root directory:
```bash
uv sync
```
3. Add an ANTHOPIC_API_KEY in `.env` file

## Usage

### Run the Main Test

```bash
uv run main.py
```

## Mock CRM Database

The agent includes a comprehensive mock CRM database for testing:

### Companies
- **Nextera**: Technology company (ID: comp_123)
- **Occurent Systems**: Software company (ID: comp_124)
- **TechCorp International**: Technology company (ID: comp_125)

### Contacts
- **Patrick Dubois**: Sales Director at Nextera
- **Pierre Lefevre**: IT Director at Nextera
- **Pierre Dubois**: Technical Lead at Nextera
- **Marie Laurent**: CEO at TechCorp International

### Opportunities
- **Nextera - CRM Implementation 2026**: €150,000 proposal stage
- **TechCorp - Digital Transformation**: €500,000 negotiation stage



## Project Structure

```
crm-agent/
├── src/
│   ├── agent.py                    # LangGraph workflow definition
│   ├── utils.py                    # Utility functions (JSON serialization)
│   ├── models/
│   │   ├── state.py               # State models (AgentState, ExtractedInfo)
│   │   └── crm_entities.py        # CRM entity models (Company, Contact, etc.)
│   ├── nodes/
│   │   ├── context_augmentation.py        # Phase 1: Calendar retrieval
│   │   ├── information_extraction.py      # Phase 2: LLM extraction
│   │   ├── entity_resolution.py           # Phase 3: Entity matching
│   │   ├── validation.py                  # Phase 4: Disambiguation
│   │   └── action_planning.py             # Phase 5: Action generation
│   └── tools/
│       ├── mock_crm.py            # Mock CRM database
│       └── crm_tools.py           # LangChain tools for CRM operations
├── main.py                        # Main test script
├── test_simple.py                 # Simple tests (no API key)
├── pyproject.toml                 # Dependencies
└── README.md                      # This file
```
