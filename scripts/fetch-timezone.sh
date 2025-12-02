#!/bin/bash
# Script to fetch timezone data based on GitHub profile location
# This script:
# 1. Gets the GitHub user's location
# 2. Converts location to coordinates via Nominatim
# 3. Gets timezone info from Open-Meteo timezone API
# 4. Outputs timezone data as JSON to data/timezone.json

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

GITHUB_OWNER="${GITHUB_OWNER:-szmyty}"
OUTPUT_DIR="${OUTPUT_DIR:-data}"

# Function to get GitHub user location
get_github_location() {
    echo "Fetching GitHub profile location for ${GITHUB_OWNER}..." >&2
    
    local user_data
    user_data=$(curl -sf "https://api.github.com/users/${GITHUB_OWNER}" \
        -H "Accept: application/vnd.github.v3+json" \
        ${GITHUB_TOKEN:+-H "Authorization: Bearer ${GITHUB_TOKEN}"} \
        -H "User-Agent: GitHub-Profile-Timezone") || {
        echo "Error: Failed to fetch GitHub profile" >&2
        return 1
    }
    
    local location
    location=$(echo "$user_data" | jq -r '.location // empty')
    
    if [ -z "$location" ] || [ "$location" = "null" ]; then
        echo "Warning: No location found in GitHub profile" >&2
        return 1
    fi
    
    echo "$location"
}

# Function to convert location to coordinates via Nominatim
get_coordinates() {
    local location=$1
    echo "Converting location to coordinates: ${location}" >&2
    
    # URL encode the location using the shared encode_uri function
    local encoded_location
    encoded_location=$(encode_uri "$location")
    
    # Add delay to respect Nominatim rate limits
    sleep 1
    
    local nominatim_data
    nominatim_data=$(curl -sf "https://nominatim.openstreetmap.org/search?q=${encoded_location}&format=json&limit=1" \
        -H "User-Agent: GitHub-Profile-Timezone/1.0") || {
        echo "Error: Failed to query Nominatim API" >&2
        return 1
    }
    
    # Check if we got results
    local result_count
    result_count=$(echo "$nominatim_data" | jq 'length')
    
    if [ "$result_count" -eq 0 ]; then
        echo "Error: Nominatim returned no results for location: ${location}" >&2
        return 1
    fi
    
    # Extract lat/lon
    local lat lon
    lat=$(echo "$nominatim_data" | jq -r '.[0].lat')
    lon=$(echo "$nominatim_data" | jq -r '.[0].lon')
    
    if [ -z "$lat" ] || [ -z "$lon" ] || [ "$lat" = "null" ] || [ "$lon" = "null" ]; then
        echo "Error: Could not extract coordinates from Nominatim response" >&2
        return 1
    fi
    
    echo "Found coordinates: ${lat}, ${lon}" >&2
    
    # Output JSON with coordinates
    jq -n \
        --arg lat "$lat" \
        --arg lon "$lon" \
        '{lat: $lat, lon: $lon}'
}

# Function to fetch timezone from Open-Meteo
fetch_timezone() {
    local lat=$1
    local lon=$2
    echo "Fetching timezone from Open-Meteo..." >&2
    
    local timezone_data
    timezone_data=$(curl -sf "https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&timezone=auto&forecast_days=1") || {
        echo "Error: Failed to fetch timezone from Open-Meteo API" >&2
        return 1
    }
    
    local timezone utc_offset_seconds
    timezone=$(echo "$timezone_data" | jq -r '.timezone // "UTC"')
    utc_offset_seconds=$(echo "$timezone_data" | jq -r '.utc_offset_seconds // 0')
    
    # Convert seconds to hours
    local utc_offset_hours
    utc_offset_hours=$(echo "scale=1; $utc_offset_seconds / 3600" | bc)
    
    # Get abbreviation using date command with TZ
    local abbreviation
    abbreviation=$(TZ="$timezone" date +"%Z" 2>/dev/null || echo "UTC")
    
    echo "Timezone: ${timezone}, UTC offset: ${utc_offset_hours}h, Abbreviation: ${abbreviation}" >&2
    
    # Output JSON with timezone info
    jq -n \
        --arg timezone "$timezone" \
        --argjson utc_offset_hours "$utc_offset_hours" \
        --arg abbreviation "$abbreviation" \
        '{
            timezone: $timezone,
            utc_offset_hours: $utc_offset_hours,
            abbreviation: $abbreviation
        }'
}

# Main execution
main() {
    # Get GitHub location
    local location
    location=$(get_github_location) || {
        echo "Skipping timezone detection: No location found" >&2
        exit 1
    }
    echo "GitHub location: ${location}" >&2
    
    # Get coordinates
    local coord_data
    coord_data=$(get_coordinates "$location") || {
        echo "Skipping timezone detection: Could not get coordinates" >&2
        exit 1
    }
    
    local lat lon
    lat=$(echo "$coord_data" | jq -r '.lat')
    lon=$(echo "$coord_data" | jq -r '.lon')
    
    # Fetch timezone data
    local timezone_json
    timezone_json=$(fetch_timezone "$lat" "$lon") || {
        echo "Skipping timezone detection: Could not fetch timezone" >&2
        exit 1
    }
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Write timezone.json
    echo "$timezone_json" > "${OUTPUT_DIR}/timezone.json"
    echo "Timezone data written to ${OUTPUT_DIR}/timezone.json" >&2
    
    # Also output to stdout
    echo "$timezone_json"
}

main "$@"
