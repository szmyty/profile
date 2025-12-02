#!/usr/bin/env python3
"""
Generate a styled SVG card for location display with embedded map.
This script reads location metadata from JSON and creates an SVG card
with the static map image embedded.
"""

import base64
import sys
from pathlib import Path

from lib.utils import (
    escape_xml,
    load_json,
    try_load_json,
    load_theme,
    get_theme_color,
    get_theme_gradient,
    get_theme_typography,
    get_theme_font_size,
    get_theme_card_dimension,
    get_theme_border_radius,
    format_timestamp_local,
    optimize_image_file,
    fallback_exists,
    log_fallback_used,
)


def encode_image_base64(image_path: str) -> str:
    """Encode and optimize an image file to base64 for embedding in SVG.
    
    The image is optimized by:
    - Reducing resolution to fit the map display area
    - Compressing PNG with color quantization from theme settings
    """
    # Get theme settings for map dimensions
    theme = load_theme()
    card_width = get_theme_card_dimension("widths", "location")
    map_config = theme.get("cards", {}).get("map", {})
    map_margin = map_config.get("margin", 20)
    map_width = card_width - (map_margin * 2)  # Match the SVG map width
    map_height = map_config.get("height", 350)  # Match the SVG map height
    
    # Optimize the image before encoding
    optimized_data = optimize_image_file(
        image_path,
        max_width=map_width,
        max_height=map_height,
    )
    return base64.b64encode(optimized_data).decode("utf-8")


def generate_svg(
    location: str,
    display_name: str,
    lat: float,
    lon: float,
    map_image_base64: str,
    updated_at: str,
) -> str:
    """Generate SVG card markup with embedded map."""
    
    # Load theme values
    theme = load_theme()
    bg_gradient = get_theme_gradient("background.default")
    font_family = get_theme_typography("font_family")
    
    # Colors from theme
    bg_primary = bg_gradient[0]
    bg_secondary = bg_gradient[1]
    text_primary = get_theme_color("text", "primary")
    text_secondary = get_theme_color("text", "secondary")
    text_muted = get_theme_color("text", "muted")
    accent_teal = get_theme_color("text", "accent")
    
    # Card dimensions from theme
    card_width = get_theme_card_dimension("widths", "location")
    card_height = get_theme_card_dimension("heights", "location")
    border_radius = get_theme_border_radius("xl")
    border_radius_lg = get_theme_border_radius("lg")
    
    # Font sizes from theme
    font_size_base = get_theme_font_size("base")
    font_size_lg = get_theme_font_size("lg")
    font_size_xl = get_theme_font_size("xl")
    font_size_3xl = get_theme_font_size("3xl")
    
    # Card stroke settings from theme
    stroke_width = theme.get("cards", {}).get("stroke_width", 1)
    stroke_opacity = theme.get("cards", {}).get("stroke_opacity", 0.3)
    
    # Effect settings from theme
    glow = theme.get("effects", {}).get("glow", {})
    glow_std = glow.get("stdDeviation", 2)

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
    
    # Calculate map dimensions from theme settings
    map_config = theme.get("cards", {}).get("map", {})
    map_margin = map_config.get("margin", 20)
    map_width = card_width - (map_margin * 2)
    map_height = map_config.get("height", 350)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{card_width}" height="{card_height}" viewBox="0 0 {card_width} {card_height}">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_primary}"/>
      <stop offset="100%" style="stop-color:{bg_secondary}"/>
    </linearGradient>
    <clipPath id="map-clip">
      <rect x="{map_margin}" y="70" width="{map_width}" height="{map_height}" rx="{border_radius_lg}"/>
    </clipPath>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="{glow_std}" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="url(#bg-gradient)"/>
  <rect width="{card_width}" height="{card_height}" rx="{border_radius}" fill="none" stroke="{accent_teal}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}"/>

  <!-- Header: Location title -->
  <g transform="translate({map_margin}, 35)">
    <text font-family="{font_family}" font-size="{font_size_3xl}" fill="{accent_teal}" font-weight="600" filter="url(#glow)">
      📍 My Location
    </text>
  </g>

  <!-- Location name -->
  <g transform="translate({map_margin}, 58)">
    <text font-family="{font_family}" font-size="{font_size_xl}" fill="{text_primary}">
      {display_location}
    </text>
  </g>

  <!-- Map image -->
  <g clip-path="url(#map-clip)">
    <image x="{map_margin}" y="70" width="{map_width}" height="{map_height}" preserveAspectRatio="xMidYMid slice"
           xlink:href="data:image/png;base64,{map_image_base64}"/>
  </g>

  <!-- Map border -->
  <rect x="{map_margin}" y="70" width="{map_width}" height="{map_height}" rx="{border_radius_lg}" fill="none" stroke="{accent_teal}" stroke-width="{stroke_width}" stroke-opacity="0.5"/>

  <!-- Coordinates display -->
  <g transform="translate({map_margin}, 445)">
    <text font-family="{font_family}" font-size="{font_size_lg}" fill="{text_secondary}">
      🌐 {coords_display}
    </text>
  </g>

  <!-- Footer: Updated timestamp -->
  <g transform="translate({map_margin}, 465)">
    <text font-family="{font_family}" font-size="{font_size_base}" fill="{text_muted}">
      Updated: {updated_at}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="{card_width - 20}" y="15" width="4" height="450" rx="2" fill="{accent_teal}" fill-opacity="{stroke_opacity}"/>
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

    # Check if fallback exists before attempting generation
    has_fallback = fallback_exists(output_path)

    # Try to read metadata
    metadata, error = try_load_json(metadata_path, "Metadata file")
    if error:
        if has_fallback:
            log_fallback_used("location", error, output_path)
            print(f"Using fallback location SVG card: {output_path}", file=sys.stderr)
            return
        else:
            print(f"Error: {error}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Try to read and encode map image
    try:
        map_image_base64 = encode_image_base64(map_path)
    except FileNotFoundError:
        error_msg = f"Map image not found: {map_path}"
        if has_fallback:
            log_fallback_used("location", error_msg, output_path)
            print(f"Using fallback location SVG card: {output_path}", file=sys.stderr)
            return
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)
    except (IOError, OSError, PermissionError) as e:
        error_msg = f"Failed to read map image: {e}"
        if has_fallback:
            log_fallback_used("location", error_msg, output_path)
            print(f"Using fallback location SVG card: {output_path}", file=sys.stderr)
            return
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Format updated_at to local time for display
    updated_at_raw = metadata.get("updated_at", "")
    updated_at_display = format_timestamp_local(updated_at_raw) if updated_at_raw else ""

    # Try to generate SVG
    try:
        svg = generate_svg(
            location=metadata.get("location", "Unknown Location"),
            display_name=metadata.get("display_name", ""),
            lat=metadata.get("coordinates", {}).get("lat", 0),
            lon=metadata.get("coordinates", {}).get("lon", 0),
            map_image_base64=map_image_base64,
            updated_at=updated_at_display,
        )
    except Exception as e:
        error_msg = f"SVG generation failed: {e}"
        if has_fallback:
            log_fallback_used("location", error_msg, output_path)
            print(f"Using fallback location SVG card: {output_path}", file=sys.stderr)
            return
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Validate SVG looks correct
    if not svg or not svg.strip().startswith("<svg"):
        error_msg = "Generated SVG appears invalid (missing <svg> tag)"
        if has_fallback:
            log_fallback_used("location", error_msg, output_path)
            print(f"Using fallback location SVG card: {output_path}", file=sys.stderr)
            return
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)

    # Try to write output
    try:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            f.write(svg)
        print(f"Generated location SVG card: {output_path}", file=sys.stderr)
    except (IOError, OSError) as e:
        error_msg = f"Failed to write SVG: {e}"
        if has_fallback:
            log_fallback_used("location", error_msg, output_path)
            print(f"Using fallback location SVG card: {output_path}", file=sys.stderr)
        else:
            print(f"Error: {error_msg}", file=sys.stderr)
            print(
                f"No fallback SVG available at {output_path}. Cannot recover.",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
