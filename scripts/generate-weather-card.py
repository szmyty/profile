#!/usr/bin/env python3
"""
Generate a styled SVG card for daily weather conditions and forecast.
This script reads weather metadata from JSON and creates an SVG card.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def format_time(time_str: str) -> str:
    """Format ISO time string to readable format (HH:MM AM/PM)."""
    try:
        dt = datetime.fromisoformat(time_str)
        return dt.strftime("%-I:%M %p")
    except (ValueError, AttributeError):
        return time_str


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def kmh_to_mph(kmh: float) -> float:
    """Convert km/h to mph."""
    return kmh * 0.621371


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


def get_background_gradient(is_day: int, weathercode: int) -> tuple:
    """Get background gradient colors based on time of day and weather."""
    if is_day:
        if weathercode in [0, 1]:  # Clear/Mainly clear
            return ("#1e3a5f", "#2d5a7b")  # Clear day blue
        elif weathercode in [2, 3]:  # Cloudy
            return ("#3d4f5f", "#4a5d6e")  # Cloudy gray-blue
        elif weathercode in [45, 48]:  # Fog
            return ("#4a5568", "#5a6578")  # Foggy gray
        elif weathercode in range(51, 68) or weathercode in range(80, 83):  # Rain
            return ("#2d3748", "#3d4758")  # Rainy dark blue
        elif weathercode in range(71, 78) or weathercode in range(85, 87):  # Snow
            return ("#4a5568", "#6b7280")  # Snowy gray
        elif weathercode in range(95, 100):  # Thunderstorm
            return ("#1a202c", "#2d3748")  # Stormy dark
        else:
            return ("#1a1a2e", "#16213e")  # Default
    else:
        return ("#0f0f23", "#1a1a2e")  # Night theme


def generate_svg(
    location: str,
    condition: str,
    emoji: str,
    current_temp: float,
    temp_max: float,
    temp_min: float,
    wind_speed: float,
    sunrise: str,
    sunset: str,
    updated_at: str,
    is_day: int,
    weathercode: int,
) -> str:
    """Generate SVG card markup."""

    # Convert units (API returns Celsius and km/h by default)
    current_temp_f = celsius_to_fahrenheit(current_temp)
    temp_max_f = celsius_to_fahrenheit(temp_max)
    temp_min_f = celsius_to_fahrenheit(temp_min)
    wind_mph = kmh_to_mph(wind_speed)

    # Format times
    sunrise_formatted = format_time(sunrise)
    sunset_formatted = format_time(sunset)

    # Escape text for XML
    location_escaped = escape_xml(location)
    condition_escaped = escape_xml(condition)
    emoji_escaped = escape_xml(emoji)

    # Truncate location if too long
    display_location = (
        location_escaped[:30] + "..." if len(location_escaped) > 30 else location_escaped
    )

    # Get background colors
    bg_start, bg_end = get_background_gradient(is_day, weathercode)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="420" height="200" viewBox="0 0 420 200">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_start}"/>
      <stop offset="100%" style="stop-color:{bg_end}"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="420" height="200" rx="12" fill="url(#bg-gradient)"/>
  <rect width="420" height="200" rx="12" fill="none" stroke="#64ffda" stroke-width="1" stroke-opacity="0.3"/>

  <!-- Header: Location + Weather Icon -->
  <g transform="translate(20, 30)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="14" fill="#64ffda" font-weight="600">
      {emoji_escaped} {display_location}
    </text>
  </g>

  <!-- Current Condition -->
  <g transform="translate(20, 60)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="36" fill="#ffffff" font-weight="bold" filter="url(#glow)">
      {current_temp_f:.0f}°F
    </text>
    <text x="110" y="0" font-family="'Segoe UI', Arial, sans-serif" font-size="16" fill="#8892b0">
      {condition_escaped}
    </text>
  </g>

  <!-- High/Low -->
  <g transform="translate(20, 95)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="13" fill="#8892b0">
      <tspan fill="#ff6b6b">High: {temp_max_f:.0f}°F</tspan>
      <tspan fill="#4a5568">  •  </tspan>
      <tspan fill="#4ecdc4">Low: {temp_min_f:.0f}°F</tspan>
    </text>
  </g>

  <!-- Wind -->
  <g transform="translate(20, 120)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#8892b0">
      💨 Wind: {wind_mph:.0f} mph
    </text>
  </g>

  <!-- Sunrise/Sunset -->
  <g transform="translate(20, 145)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#8892b0">
      🌅 {sunrise_formatted}
      <tspan fill="#4a5568">  •  </tspan>
      🌇 {sunset_formatted}
    </text>
  </g>

  <!-- Footer: Updated timestamp -->
  <g transform="translate(20, 180)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#4a5568">
      Updated: {updated_at}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="400" y="15" width="4" height="170" rx="2" fill="#64ffda" fill-opacity="0.3"/>
</svg>"""

    return svg


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: generate-weather-card.py <weather.json> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    metadata_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "weather/weather-today.svg"

    # Read metadata
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        print(f"Error: Metadata file not found: {metadata_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in metadata file: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate SVG
    svg = generate_svg(
        location=metadata.get("location", "Unknown Location"),
        condition=metadata.get("current", {}).get("condition", "Unknown"),
        emoji=metadata.get("current", {}).get("emoji", "🌡️"),
        current_temp=metadata.get("current", {}).get("temperature", 0),
        temp_max=metadata.get("daily", {}).get("temperature_max", 0),
        temp_min=metadata.get("daily", {}).get("temperature_min", 0),
        wind_speed=metadata.get("current", {}).get("wind_speed", 0),
        sunrise=metadata.get("daily", {}).get("sunrise", ""),
        sunset=metadata.get("daily", {}).get("sunset", ""),
        updated_at=metadata.get("updated_at", ""),
        is_day=metadata.get("current", {}).get("is_day", 1),
        weathercode=metadata.get("current", {}).get("weathercode", 0),
    )

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write(svg)

    print(f"Generated weather SVG card: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
