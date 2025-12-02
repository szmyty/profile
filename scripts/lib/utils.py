#!/usr/bin/env python3
"""
Shared utility functions for profile card generators.

This module provides common helper functions used across multiple card generator
scripts, including XML escaping, safe dictionary access, JSON loading, and
SVG visualization helpers.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

try:
    import jsonschema
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    ValidationError = Exception  # Fallback type for type hints

# Cache for loaded theme to avoid re-reading file
_theme_cache: Optional[Dict] = None
# Cache for loaded schemas to avoid re-reading files
_schema_cache: Dict[str, Dict] = {}


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


def load_schema(schema_name: str) -> Dict:
    """
    Load a JSON schema from the schemas directory.

    Args:
        schema_name: Name of the schema file. Can be provided with the full
                     '.schema.json' suffix (e.g., 'weather.schema.json') or
                     without it (e.g., 'weather'), in which case the suffix
                     will be automatically appended.

    Returns:
        Parsed schema as a dictionary.

    Raises:
        SystemExit: If schema file not found or invalid.
    """
    global _schema_cache

    # Normalize schema name
    if not schema_name.endswith('.schema.json'):
        schema_name = f"{schema_name}.schema.json"

    if schema_name in _schema_cache:
        return _schema_cache[schema_name]

    # Find schema relative to this file's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    schema_path = os.path.join(repo_root, "schemas", schema_name)

    schema = load_json(schema_path, f"Schema file '{schema_name}'")
    _schema_cache[schema_name] = schema
    return schema


def validate_json(data: Dict, schema_name: str, description: str = "data") -> None:
    """
    Validate JSON data against a schema.

    Args:
        data: The data dictionary to validate.
        schema_name: Name of the schema file (e.g., 'weather' or 'weather.schema.json').
        description: Human-readable description for error messages.

    Raises:
        SystemExit: If validation fails or jsonschema is not available.
    """
    if not JSONSCHEMA_AVAILABLE:
        print(
            "Warning: jsonschema not installed, skipping validation",
            file=sys.stderr,
        )
        return

    schema = load_schema(schema_name)

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        print(
            f"Error: {description} validation failed: {e.message}",
            file=sys.stderr,
        )
        # Provide more context for nested errors
        if e.absolute_path:
            path = ".".join(str(p) for p in e.absolute_path)
            print(f"  At path: {path}", file=sys.stderr)
        sys.exit(1)


def load_and_validate_json(
    path: str, schema_name: str, description: str = "file"
) -> Dict:
    """
    Load a JSON file and validate it against a schema.

    Args:
        path: Path to the JSON file.
        schema_name: Name of the schema to validate against.
        description: Human-readable description for error messages.

    Returns:
        Parsed and validated JSON as a dictionary.

    Raises:
        SystemExit: If file not found, JSON invalid, or validation fails.
    """
    data = load_json(path, description)
    validate_json(data, schema_name, description)
    return data


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


def load_theme(theme_path: Optional[str] = None) -> Dict:
    """
    Load theme configuration from JSON file.

    Args:
        theme_path: Optional path to theme.json. If not provided,
                   defaults to config/theme.json relative to the repository root.

    Returns:
        Theme configuration dictionary.

    Note:
        The theme is cached after first load to avoid repeated file reads.
    """
    global _theme_cache

    if _theme_cache is not None:
        return _theme_cache

    if theme_path is None:
        # Find theme.json relative to this file's location
        # scripts/lib/utils.py -> scripts/lib -> scripts -> repo root -> config/theme.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        theme_path = os.path.join(repo_root, "config", "theme.json")

    _theme_cache = load_json(theme_path, "Theme configuration file")
    return _theme_cache


def get_theme_color(category: str, name: str, fallback: str = "#ffffff") -> str:
    """
    Get a color value from the theme.

    Args:
        category: Color category (e.g., 'background', 'text', 'accent').
        name: Color name within the category.
        fallback: Default color if not found.

    Returns:
        Hex color string.
    """
    theme = load_theme()
    return safe_get(theme, "colors", category, name, default=fallback)


def get_theme_gradient(name: str, fallback: Optional[List[str]] = None) -> List[str]:
    """
    Get a gradient definition from the theme.

    Args:
        name: Gradient name (e.g., 'sleep', 'readiness', 'activity').
        fallback: Default gradient if not found.

    Returns:
        List of two hex color strings [start, end].
    """
    if fallback is None:
        fallback = ["#1a1a2e", "#16213e"]

    theme = load_theme()
    gradients = theme.get("gradients", {})

    # Check for nested gradient (e.g., weather.clear_day)
    if "." in name:
        parts = name.split(".", 1)
        return safe_get(gradients, parts[0], parts[1], default=fallback)

    return gradients.get(name, fallback)


def get_theme_typography(key: str, fallback: Any = None) -> Any:
    """
    Get a typography value from the theme.

    Args:
        key: Typography key (e.g., 'font_family', 'sizes').
        fallback: Default value if not found.

    Returns:
        Typography value (string for font_family, dict for sizes).
    """
    theme = load_theme()
    return safe_get(theme, "typography", key, default=fallback)


def get_theme_font_size(size_name: str, fallback: int = 12) -> int:
    """
    Get a font size from the theme.

    Args:
        size_name: Size name (e.g., 'xs', 'sm', 'base', 'lg', 'xl', '2xl').
        fallback: Default size if not found.

    Returns:
        Font size in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "typography", "sizes", size_name, default=fallback)


def get_theme_spacing(size_name: str, fallback: int = 10) -> int:
    """
    Get a spacing value from the theme.

    Args:
        size_name: Size name (e.g., 'xs', 'sm', 'md', 'lg', 'xl').
        fallback: Default spacing if not found.

    Returns:
        Spacing value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "spacing", size_name, default=fallback)


def get_theme_card_dimension(dimension: str, card_type: str, fallback: int = 400) -> int:
    """
    Get a card dimension from the theme.

    Args:
        dimension: 'widths' or 'heights'.
        card_type: Card type name (e.g., 'soundcloud', 'weather').
        fallback: Default dimension if not found.

    Returns:
        Dimension value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", dimension, card_type, default=fallback)


def get_theme_border_radius(size: str = "xl", fallback: int = 12) -> int:
    """
    Get a border radius from the theme.

    Args:
        size: Size name (e.g., 'sm', 'md', 'lg', 'xl').
        fallback: Default radius if not found.

    Returns:
        Border radius value in pixels.
    """
    theme = load_theme()
    return safe_get(theme, "cards", "border_radius", size, default=fallback)


# Cache for loaded timezone to avoid re-reading file
_timezone_cache: Optional[Dict] = None


def load_timezone(timezone_path: Optional[str] = None) -> Dict:
    """
    Load timezone configuration from JSON file.

    Args:
        timezone_path: Optional path to timezone.json. If not provided,
                      defaults to data/timezone.json relative to the repository root.

    Returns:
        Timezone configuration dictionary with keys:
        - timezone: Timezone identifier (e.g., "America/New_York")
        - utc_offset_hours: UTC offset in hours (e.g., -5)
        - abbreviation: Timezone abbreviation (e.g., "EST")

    Note:
        The timezone is cached after first load to avoid repeated file reads.
        Returns default UTC timezone if file not found.
    """
    global _timezone_cache

    if _timezone_cache is not None:
        return _timezone_cache

    if timezone_path is None:
        # Find timezone.json relative to this file's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        timezone_path = os.path.join(repo_root, "data", "timezone.json")

    try:
        with open(timezone_path, "r") as f:
            _timezone_cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default to UTC if timezone file not found
        _timezone_cache = {
            "timezone": "UTC",
            "utc_offset_hours": 0,
            "abbreviation": "UTC"
        }

    return _timezone_cache


def format_timestamp_local(dt_utc_str: str, tzinfo_str: Optional[str] = None) -> str:
    """
    Convert ISO 8601 UTC timestamp to local time display format.

    Args:
        dt_utc_str: UTC timestamp string in ISO 8601 format (e.g., "2025-12-01T06:22:41Z")
        tzinfo_str: Optional timezone identifier (e.g., "America/New_York").
                   If not provided, uses timezone from data/timezone.json.

    Returns:
        Human-readable local time string in format "YYYY-MM-DD HH:MM AM/PM"

    Example:
        >>> format_timestamp_local("2025-12-01T06:22:41Z", "America/New_York")
        "2025-12-01 01:22 AM"
    """
    try:
        # Parse the UTC timestamp
        # Handle various ISO 8601 formats
        dt_utc_str = dt_utc_str.strip()
        if dt_utc_str.endswith('Z'):
            dt_utc_str = dt_utc_str[:-1] + '+00:00'
        elif len(dt_utc_str) >= 6 and '+' not in dt_utc_str and '-' not in dt_utc_str[-6:]:
            # No timezone info, assume UTC
            dt_utc_str = dt_utc_str + '+00:00'

        dt_utc = datetime.fromisoformat(dt_utc_str)

        # Ensure it's UTC
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)

        # Get timezone info - always use loaded timezone offset as the source of truth
        tz_data = load_timezone()
        loaded_timezone = tz_data.get("timezone", "UTC")
        loaded_offset = tz_data.get("utc_offset_hours", 0)

        if tzinfo_str is None:
            # Use loaded timezone
            offset_hours = loaded_offset
        elif tzinfo_str == loaded_timezone:
            # Requested timezone matches loaded, use loaded offset
            offset_hours = loaded_offset
        else:
            # Requested timezone differs - use loaded timezone offset as fallback
            # This ensures consistent behavior even if the requested timezone differs
            offset_hours = loaded_offset

        # Apply timezone offset manually (since zoneinfo may not be available)
        offset = timedelta(hours=offset_hours)
        dt_local = dt_utc + offset

        # Format as "YYYY-MM-DD HH:MM AM/PM"
        formatted = dt_local.strftime("%Y-%m-%d %I:%M %p")

        return formatted

    except (ValueError, AttributeError, TypeError):
        # Return original string if parsing fails
        return dt_utc_str


def format_timestamp_iso(dt: Optional[datetime] = None) -> str:
    """
    Format a datetime object to ISO 8601 UTC format with Zulu time.

    Args:
        dt: datetime object to format. If None, uses current UTC time.

    Returns:
        ISO 8601 formatted string (e.g., "2025-12-01T06:22:41Z")
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
