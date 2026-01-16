"""Utility functions for the CRM agent."""
from datetime import datetime
from typing import Any, List


def json_serializer(obj: Any) -> str:
    """Custom JSON serializer for objects not serializable by default.

    Handles:
    - datetime objects -> ISO format strings
    - Any other objects -> string representation

    Args:
        obj: Object to serialize

    Returns:
        String representation of the object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)