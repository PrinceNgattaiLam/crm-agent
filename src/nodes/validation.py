"""Phase 4: Confidence validation - handle ambiguous matches.

Only entities with action="validate" need user input.
This is a simplified version - in production, this would present
interactive prompts to the user.
"""
from typing import Dict, Any, List
from ..models.state import AgentState, MatchedEntity


def visualize_disambiguation(entities_needing_validation: List[MatchedEntity]) -> None:
    """Print disambiguation information in a user-friendly format.

    Format:
    [DISAMBIGUATION] "Pierre" - CTO
    Found 2 contacts named Pierre at Nextera. Which one?

    Args:
        entities_needing_validation: List of MatchedEntity objects needing validation
    """
    if not entities_needing_validation:
        return

    print(f"\n   Found {len(entities_needing_validation)} entities needing disambiguation:\n")
    print("="*70)

    for i, entity in enumerate(entities_needing_validation, 1):
        # Get role or additional context
        context = ""
        if entity.details:
            if entity.entity_type == "contact" and entity.details.get("role"):
                context = f" - {entity.details['role']}"
            elif entity.entity_type == "opportunity" and entity.details.get("type"):
                context = f" - {entity.details['type']}"

        # Print disambiguation header
        print(f"\n[DISAMBIGUATION] \"{entity.name}\"{context}")

        # Describe the ambiguity
        num_alternatives = len(entity.alternatives) + 1  # +1 for the top match

        if entity.entity_type == "contact":
            company_name = entity.details.get("company", "unknown company")
            print(f"Found {num_alternatives} contacts named \"{entity.name}\" at {company_name}. Which one?")
        elif entity.entity_type == "company":
            print(f"Found {num_alternatives} companies matching \"{entity.name}\". Which one?")
        elif entity.entity_type == "opportunity":
            company_name = entity.details.get("company", "unknown company")
            print(f"Found {num_alternatives} opportunities for {company_name}. Which one?")

        # Show top match (current selection)
        print(f"\n   ✓ Selected (confidence: {entity.confidence:.0%}):")
        if entity.name:
            print(f"      Name: {entity.name}")
        if entity.entity_id:
            print(f"      ID: {entity.entity_id}")
        if entity.details:
            for key, value in entity.details.items():
                if key not in ["name", "confidence"] and value:
                    print(f"      {key.replace('_', ' ').title()}: {value}")

        # Show alternatives
        if entity.alternatives and len(entity.alternatives) > 0:
            print(f"\n   Other options ({len(entity.alternatives)}):")
            for j, alt in enumerate(entity.alternatives[:3], 1):  # Show max 3
                alt_confidence = alt.get("confidence", 0)
                print(f"      {j}. {alt.get('name', 'N/A')} (confidence: {alt_confidence:.0%})")
                if alt.get("email"):
                    print(f"         Email: {alt['email']}")
                if alt.get("role"):
                    print(f"         Role: {alt['role']}")
                if alt.get("company_name"):
                    print(f"         Company: {alt['company_name']}")

        print()

    print("="*70)


def validation_node(state: AgentState) -> Dict[str, Any]:
    """Filter and prepare entities that need user validation.

    Args:
        state: Current agent state with matched entities

    Returns:
        State update with entities_needing_validation
    """
    print("⚠️  Phase 4: Confidence Validation")

    # Collect all matched entities
    all_entities = []
    all_entities.extend(state.get("matched_companies", []))
    all_entities.extend(state.get("matched_contacts", []))
    all_entities.extend(state.get("matched_opportunities", []))

    # Filter entities needing validation
    entities_needing_validation = [
        entity for entity in all_entities
        if entity.action == "validate"
    ]

    if entities_needing_validation:
        # Display disambiguation information in a user-friendly format
        visualize_disambiguation(entities_needing_validation)

        # In a real implementation, we would:
        # . Present these to the user via UI
        # . Maybe Use LLM reranking to improve alternative ordering
        # . Wait for user selection
        # . Update entity.action to "use_existing" or "create"

        # For now, we auto-select the top match (simulating user approval)
        validated_entities = []
        for entity in entities_needing_validation:
            entity.action = "use_existing"  # Auto-approve top match
            validated_entities.append(entity)

        print(f"\n   ✓ Auto-validated {len(validated_entities)} entities (using top matches)\n")

        return {
            "entities_needing_validation": entities_needing_validation,
            "validated_entities": validated_entities
        }
    else:
        print("   ✓ No validation needed - all entities have clear actions")
        return {
            "entities_needing_validation": [],
            "validated_entities": []
        }


def should_skip_validation(state: AgentState) -> str:
    """Conditional edge: skip validation if not needed.

    Returns:
        "skip" if no entities need validation, "validate" otherwise
    """
    all_entities = []
    all_entities.extend(state.get("matched_companies", []))
    all_entities.extend(state.get("matched_contacts", []))
    all_entities.extend(state.get("matched_opportunities", []))

    needs_validation = any(entity.action == "validate" for entity in all_entities)

    return "validate" if needs_validation else "skip"
