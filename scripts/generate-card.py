#!/usr/bin/env python3
"""
Generate a styled SVG card for SoundCloud latest release.
This script reads track metadata from JSON and creates an SVG card.
"""

import sys
import base64
from pathlib import Path
from datetime import datetime

from lib.utils import escape_xml, load_json


def format_duration(duration_ms: int) -> str:
    """Convert milliseconds to MM:SS format."""
    seconds = duration_ms // 1000
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"


def format_playcount(count: int) -> str:
    """Format play count with K/M suffixes."""
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except (ValueError, AttributeError):
        return date_str


def get_artwork_base64(artwork_path: str) -> str:
    """Read artwork file and return base64 encoded data URI."""
    try:
        path = Path(artwork_path)
        if path.exists():
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                # Determine MIME type
                suffix = path.suffix.lower()
                mime = "image/jpeg" if suffix in [".jpg", ".jpeg"] else "image/png"
                return f"data:{mime};base64,{data}"
    except (OSError, IOError) as e:
        print(f"Warning: Could not load artwork: {e}", file=sys.stderr)
    return ""


def generate_svg(
    title: str,
    artist: str,
    genre: str,
    duration_ms: int,
    playback_count: int,
    created_at: str,
    permalink_url: str,
    artwork_data_uri: str,
) -> str:
    """Generate SVG card markup."""

    # Format values
    duration = format_duration(duration_ms)
    plays = format_playcount(playback_count)
    date = format_date(created_at)

    # Escape text for XML
    title_escaped = escape_xml(title)
    artist_escaped = escape_xml(artist)
    genre_escaped = escape_xml(genre)
    permalink_escaped = escape_xml(permalink_url)

    # Truncate title if too long
    display_title = title_escaped[:35] + "..." if len(title_escaped) > 35 else title_escaped

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="400" height="120" viewBox="0 0 400 120">
  <defs>
    <clipPath id="artwork-clip">
      <rect x="10" y="10" width="100" height="100" rx="8"/>
    </clipPath>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#16213e"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-opacity="0.3"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="400" height="120" rx="12" fill="url(#bg-gradient)"/>
  <rect width="400" height="120" rx="12" fill="none" stroke="#ff5500" stroke-width="1" stroke-opacity="0.3"/>

  <!-- Artwork -->
  <g clip-path="url(#artwork-clip)">
    <image x="10" y="10" width="100" height="100" preserveAspectRatio="xMidYMid slice" href="{artwork_data_uri}"/>
  </g>
  <rect x="10" y="10" width="100" height="100" rx="8" fill="none" stroke="#ff5500" stroke-width="2" stroke-opacity="0.5"/>

  <!-- SoundCloud Logo/Icon -->
  <g transform="translate(370, 10)">
    <circle cx="10" cy="10" r="10" fill="#ff5500"/>
    <text x="10" y="14" font-family="Arial, sans-serif" font-size="10" fill="white" text-anchor="middle" font-weight="bold">SC</text>
  </g>

  <!-- Track Info -->
  <g transform="translate(125, 25)">
    <!-- Title -->
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="16" font-weight="bold" fill="#ffffff">
      {display_title}
    </text>

    <!-- Artist -->
    <text y="22" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#ff5500">
      {artist_escaped}
    </text>

    <!-- Genre & Duration -->
    <text y="42" font-family="'Segoe UI', Arial, sans-serif" font-size="11" fill="#8892b0">
      <tspan fill="#64ffda">{genre_escaped}</tspan>
      <tspan fill="#4a5568"> · </tspan>
      <tspan>{duration}</tspan>
    </text>

    <!-- Stats -->
    <g transform="translate(0, 58)">
      <!-- Play count icon -->
      <polygon points="0,0 0,10 8,5" fill="#8892b0"/>
      <text x="12" y="9" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#8892b0">{plays} plays</text>

      <!-- Date -->
      <text x="80" y="9" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#8892b0">Released {date}</text>
    </g>
  </g>

  <!-- Clickable overlay (for GitHub markdown) -->
  <a href="{permalink_escaped}" target="_blank">
    <rect width="400" height="120" fill="transparent" style="cursor: pointer;"/>
  </a>
</svg>"""

    return svg


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: generate-card.py <metadata.json> [artwork_path] [output_path]", file=sys.stderr)
        sys.exit(1)

    metadata_path = sys.argv[1]
    artwork_path = sys.argv[2] if len(sys.argv) > 2 else "assets/soundcloud-artwork.jpg"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "assets/soundcloud-card.svg"

    # Read metadata
    metadata = load_json(metadata_path, "Metadata file")

    # Get artwork as base64
    artwork_data_uri = get_artwork_base64(artwork_path)

    # Generate SVG
    svg = generate_svg(
        title=metadata.get("title", "Unknown Track"),
        artist=metadata.get("artist", "Unknown Artist"),
        genre=metadata.get("genre", "Music"),
        duration_ms=metadata.get("duration_ms", 0),
        playback_count=metadata.get("playback_count", 0),
        created_at=metadata.get("created_at", ""),
        permalink_url=metadata.get("permalink_url", "https://soundcloud.com"),
        artwork_data_uri=artwork_data_uri,
    )

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write(svg)

    print(f"Generated SVG card: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
