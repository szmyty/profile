#!/usr/bin/env python3
"""
Shared utility functions for profile card generators.

This module provides common helper functions used across multiple card generator
scripts, including XML escaping, safe dictionary access, JSON loading, and
SVG visualization helpers.
"""

import json
import sys
from typing import Any, List, Optional


def escape_xml(text: str) -> str:
    """
    Escape special characters for XML/SVG.

    Args:
        text: The text string to escape.

    Returns:
        The escaped string safe for use in XML/SVG content.
    """
    if not text:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def safe_get(data: dict, *keys, default: Any = None) -> Any:
    """
    Safely get nested dictionary values.

    Args:
        data: The dictionary to traverse.
        *keys: Variable number of keys to traverse.
        default: Default value if key path not found.

    Returns:
        The value at the key path, or default if not found.
    """
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, default)
        else:
            return default
    return value if value is not None else default


def safe_value(value: Any, default: str = "—", suffix: str = "") -> str:
    """
    Return value or default placeholder if None.

    Args:
        value: The value to format.
        default: Default string if value is None.
        suffix: Optional suffix to append to the value.

    Returns:
        Formatted string value or default.
    """
    if value is None:
        return default
    return f"{value}{suffix}"


def load_json(path: str, description: str = "file") -> dict:
    """
    Load and parse a JSON file with error handling.

    Args:
        path: Path to the JSON file.
        description: Human-readable description for error messages.

    Returns:
        Parsed JSON as a dictionary.

    Raises:
        SystemExit: If file not found or JSON is invalid.
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {description} not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {description}: {e}", file=sys.stderr)
        sys.exit(1)


def generate_sparkline_path(
    values: List[Optional[float]], width: int = 100, height: int = 25
) -> str:
    """
    Generate SVG path data for a sparkline visualization.

    Args:
        values: List of numeric values (None values are filtered out).
        width: Width of the sparkline in pixels.
        height: Height of the sparkline in pixels.

    Returns:
        SVG path data string (e.g., "M0,10 L5,15 L10,8").
    """
    if not values or len(values) < 2:
        return f"M0,{height // 2} L{width},{height // 2}"

    # Filter out None values and convert to floats
    clean_values = [v for v in values if v is not None]
    if len(clean_values) < 2:
        return f"M0,{height // 2} L{width},{height // 2}"

    min_val = min(clean_values)
    max_val = max(clean_values)
    val_range = max_val - min_val if max_val != min_val else 1

    step = width / (len(clean_values) - 1)
    points = []

    for i, val in enumerate(clean_values):
        x = i * step
        # Normalize to height (invert Y axis for SVG)
        y = height - ((val - min_val) / val_range * height)
        points.append(f"{x:.1f},{y:.1f}")

    return f"M{' L'.join(points)}"
