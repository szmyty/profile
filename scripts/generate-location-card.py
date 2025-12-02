#!/usr/bin/env python3
"""
Generate a styled SVG card for location display with embedded map.
This script reads location metadata from JSON and creates an SVG card
with the static map image embedded.
"""

import base64
import sys
from pathlib import Path

from lib.utils import escape_xml, load_json


def encode_image_base64(image_path: str) -> str:
    """Encode an image file to base64 for embedding in SVG."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_svg(
    location: str,
    display_name: str,
    lat: float,
    lon: float,
    map_image_base64: str,
    updated_at: str,
) -> str:
    """Generate SVG card markup with embedded map."""

    # Escape text for XML
    location_escaped = escape_xml(location)

    # Truncate location if too long
    display_location = (
        location_escaped[:35] + "..." if len(location_escaped) > 35 else location_escaped
    )

    # Format coordinates for display
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    coords_display = f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="600" height="480" viewBox="0 0 600 480">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#16213e"/>
    </linearGradient>
    <clipPath id="map-clip">
      <rect x="20" y="70" width="560" height="350" rx="8"/>
    </clipPath>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="600" height="480" rx="12" fill="url(#bg-gradient)"/>
  <rect width="600" height="480" rx="12" fill="none" stroke="#64ffda" stroke-width="1" stroke-opacity="0.3"/>

  <!-- Header: Location title -->
  <g transform="translate(20, 35)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="18" fill="#64ffda" font-weight="600" filter="url(#glow)">
      📍 My Location
    </text>
  </g>

  <!-- Location name -->
  <g transform="translate(20, 58)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="14" fill="#ffffff">
      {display_location}
    </text>
  </g>

  <!-- Map image -->
  <g clip-path="url(#map-clip)">
    <image x="20" y="70" width="560" height="350" preserveAspectRatio="xMidYMid slice"
           xlink:href="data:image/png;base64,{map_image_base64}"/>
  </g>

  <!-- Map border -->
  <rect x="20" y="70" width="560" height="350" rx="8" fill="none" stroke="#64ffda" stroke-width="1" stroke-opacity="0.5"/>

  <!-- Coordinates display -->
  <g transform="translate(20, 445)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#8892b0">
      🌐 {coords_display}
    </text>
  </g>

  <!-- Footer: Updated timestamp -->
  <g transform="translate(20, 465)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#4a5568">
      Updated: {updated_at}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="580" y="15" width="4" height="450" rx="2" fill="#64ffda" fill-opacity="0.3"/>
</svg>"""

    return svg


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(
            "Usage: generate-location-card.py <location.json> <map.png> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    metadata_path = sys.argv[1]
    map_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "location/location-card.svg"

    # Read metadata
    metadata = load_json(metadata_path, "Metadata file")

    # Read and encode map image
    try:
        map_image_base64 = encode_image_base64(map_path)
    except FileNotFoundError:
        print(f"Error: Map image not found: {map_path}", file=sys.stderr)
        sys.exit(1)
    except (IOError, OSError, PermissionError) as e:
        print(f"Error: Failed to read map image: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate SVG
    svg = generate_svg(
        location=metadata.get("location", "Unknown Location"),
        display_name=metadata.get("display_name", ""),
        lat=metadata.get("coordinates", {}).get("lat", 0),
        lon=metadata.get("coordinates", {}).get("lon", 0),
        map_image_base64=map_image_base64,
        updated_at=metadata.get("updated_at", ""),
    )

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write(svg)

    print(f"Generated location SVG card: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
