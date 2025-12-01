#!/usr/bin/env python3
"""
Generate a styled SVG card for Oura Ring mood dashboard.
This script reads mood and metrics data from JSON and creates an SVG card
with mood visualization, key metrics, and a sparkline chart.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


def escape_xml(text: str) -> str:
    """Escape special characters for XML/SVG."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def safe_value(value: Any, default: str = "—") -> str:
    """Return value or default placeholder if None."""
    if value is None:
        return default
    return str(value)


def generate_sparkline_path(values: list, width: int = 120, height: int = 30) -> str:
    """
    Generate SVG path data for a sparkline visualization.
    """
    if not values or len(values) < 2:
        # Default flat line if no data
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


def generate_radial_bars(scores: dict, cx: int = 60, cy: int = 50, radius: int = 40) -> str:
    """
    Generate SVG elements for radial progress bars showing scores.
    """
    elements = []
    metrics = [
        ("sleep_score", "#4facfe", "Sleep"),
        ("readiness_score", "#667eea", "Ready"),
        ("activity_score", "#f093fb", "Active"),
    ]

    for i, (key, color, _) in enumerate(metrics):
        value = scores.get(key, 50) or 50
        # Normalize to 0-100
        value = min(100, max(0, value))
        circumference = 2 * 3.14159 * radius
        dash_offset = circumference * (1 - value / 100)

        # Each bar is offset by rotation
        rotation = -90 + (i * 120)

        elements.append(f"""
    <circle cx="{cx}" cy="{cy}" r="{radius - (i * 8)}"
            fill="none" stroke="{color}" stroke-width="6"
            stroke-dasharray="{circumference * 0.33} {circumference}"
            stroke-dashoffset="{dash_offset * 0.33}"
            stroke-linecap="round" opacity="0.8"
            transform="rotate({rotation} {cx} {cy})"/>""")

    return "".join(elements)


def generate_score_bar(value: Any, x: int, y: int, width: int = 80, label: str = "") -> str:
    """Generate a horizontal score bar."""
    score = value if value is not None else 0
    score = min(100, max(0, score))
    fill_width = int((score / 100) * width)

    # Color based on score
    if score >= 75:
        color = "#4ade80"  # Green
    elif score >= 50:
        color = "#fbbf24"  # Yellow
    else:
        color = "#f87171"  # Red

    return f"""
    <g transform="translate({x}, {y})">
      <text font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#8892b0" y="-3">{escape_xml(label)}</text>
      <rect width="{width}" height="6" rx="3" fill="#2d3748"/>
      <rect width="{fill_width}" height="6" rx="3" fill="{color}"/>
      <text x="{width + 8}" y="5" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#ffffff">{score}</text>
    </g>"""


def generate_svg(mood: dict, metrics: dict) -> str:
    """Generate SVG card markup."""

    # Extract mood data
    mood_name = escape_xml(mood.get("mood_name", "Unknown"))
    mood_icon = mood.get("mood_icon", "🌙")
    mood_score = mood.get("mood_score", 50)
    gradient = mood.get("mood_color_gradient", ["#1a1a2e", "#16213e"])
    mood_description = escape_xml(mood.get("mood_description", ""))

    # Extract raw scores
    raw_scores = mood.get("raw_scores", {})
    sleep_score = raw_scores.get("sleep_score")
    readiness_score = raw_scores.get("readiness_score")
    activity_score = raw_scores.get("activity_score")
    hrv = raw_scores.get("hrv")
    resting_hr = raw_scores.get("resting_hr")
    temp_deviation = raw_scores.get("temp_deviation")

    # Get interpretations
    interpreted = mood.get("interpreted_metrics", {})

    # Get timestamp
    updated_at = mood.get("computed_at", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    # Generate sparkline from available scores
    sparkline_values = [sleep_score, readiness_score, activity_score, hrv or 50]
    sparkline_path = generate_sparkline_path(sparkline_values)

    # Generate score bars
    sleep_bar = generate_score_bar(sleep_score, 200, 75, 100, "😴 Sleep")
    readiness_bar = generate_score_bar(readiness_score, 200, 105, 100, "💪 Readiness")
    activity_bar = generate_score_bar(activity_score, 200, 135, 100, "🏃 Activity")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="220" viewBox="0 0 420 220">
  <defs>
    <linearGradient id="mood-bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{gradient[0]}"/>
      <stop offset="100%" style="stop-color:{gradient[1]}"/>
    </linearGradient>
    <linearGradient id="sparkline-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{gradient[0]}"/>
      <stop offset="100%" style="stop-color:{gradient[1]}"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="soft-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>

  <!-- Background with mood gradient -->
  <rect width="420" height="220" rx="12" fill="url(#mood-bg-gradient)"/>
  <rect width="420" height="220" rx="12" fill="none" stroke="#64ffda" stroke-width="1" stroke-opacity="0.3"/>

  <!-- Header: Oura Ring badge -->
  <g transform="translate(20, 25)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#64ffda" font-weight="500">
      ⭕ OURA RING
    </text>
  </g>

  <!-- Mood icon and name -->
  <g transform="translate(20, 55)">
    <text font-family="Arial, sans-serif" font-size="32" filter="url(#glow)">
      {mood_icon}
    </text>
    <text x="45" y="5" font-family="'Segoe UI', Arial, sans-serif" font-size="22" fill="#ffffff" font-weight="bold" filter="url(#glow)">
      {mood_name}
    </text>
    <text x="45" y="22" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#8892b0">
      {mood_description}
    </text>
  </g>

  <!-- Score bars -->
  {sleep_bar}
  {readiness_bar}
  {activity_bar}

  <!-- HRV and Resting HR display -->
  <g transform="translate(20, 95)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#8892b0">
      ❤️ HRV Balance
    </text>
    <text y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="16" fill="#ffffff" font-weight="600">
      {safe_value(hrv)}
    </text>
  </g>

  <g transform="translate(100, 95)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#8892b0">
      💓 Rest HR
    </text>
    <text y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="16" fill="#ffffff" font-weight="600">
      {safe_value(resting_hr)}
    </text>
  </g>

  <!-- Mood Score indicator -->
  <g transform="translate(20, 145)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#8892b0">
      🎯 Mood Score
    </text>
    <text y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="24" fill="#64ffda" font-weight="bold" filter="url(#glow)">
      {mood_score}
    </text>
    <text x="45" y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#4a5568">
      / 100
    </text>
  </g>

  <!-- Sparkline visualization -->
  <g transform="translate(280, 165)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="9" fill="#4a5568" y="-5">
      Metrics Trend
    </text>
    <rect width="120" height="35" rx="4" fill="#1a1a2e" fill-opacity="0.5"/>
    <g transform="translate(5, 2)">
      <path d="{sparkline_path}" fill="none" stroke="url(#sparkline-gradient)" stroke-width="2" stroke-linecap="round"/>
    </g>
  </g>

  <!-- Footer: Updated timestamp -->
  <g transform="translate(20, 205)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#4a5568">
      Updated: {updated_at}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="400" y="15" width="4" height="190" rx="2" fill="#64ffda" fill-opacity="0.3"/>
</svg>"""

    return svg


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: generate-oura-mood-card.py <mood.json> [metrics.json] [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    mood_path = sys.argv[1]
    metrics_path = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else "oura/mood_dashboard.svg"

    # Read mood data
    try:
        with open(mood_path, "r") as f:
            mood = json.load(f)
    except FileNotFoundError:
        print(f"Error: Mood file not found: {mood_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in mood file: {e}", file=sys.stderr)
        sys.exit(1)

    # Read metrics data (optional, for additional visualizations)
    metrics = {}
    if metrics_path:
        try:
            with open(metrics_path, "r") as f:
                metrics = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Continue without metrics

    # Generate SVG
    svg = generate_svg(mood, metrics)

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write(svg)

    print(f"Generated Oura mood dashboard SVG: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
