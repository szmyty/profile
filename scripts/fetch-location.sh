#!/bin/bash
# Script to fetch location data and static map from OpenStreetMap
# This script:
# 1. Gets the GitHub user's location
# 2. Converts location to coordinates via Nominatim
# 3. Downloads a static map centered on coordinates
# 4. Outputs location data as JSON

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

GITHUB_OWNER="${GITHUB_OWNER:-szmyty}"
OUTPUT_DIR="${OUTPUT_DIR:-location}"

# Function to download static map from OpenStreetMap
download_static_map() {
    local lat=$1
    local lon=$2
    local output_path=$3
    
    echo "Downloading static map centered on ${lat}, ${lon}..." >&2
    
    # OpenStreetMap static map API
    local map_url="https://staticmap.openstreetmap.de/staticmap.php?center=${lat},${lon}&zoom=12&size=600x400&markers=${lat},${lon},blue"
    
    if ! retry_with_backoff curl -sf -o "$output_path" "$map_url"; then
        echo "Error: Failed to download static map after retries" >&2
        return 1
    fi
    
    # Verify the downloaded file is not empty
    if [ ! -s "$output_path" ]; then
        echo "Error: Downloaded map file is empty" >&2
        return 1
    fi
    
    echo "Static map saved to ${output_path}" >&2
}

# Main execution
main() {
    # Get GitHub location
    local location
    location=$(get_github_location) || {
        echo "Skipping location card generation: No location found" >&2
        exit 1
    }
    echo "GitHub location: ${location}" >&2
    
    # Get coordinates
    local coord_data
    coord_data=$(get_coordinates "$location") || {
        echo "Skipping location card generation: Could not get coordinates" >&2
        exit 1
    }
    
    local lat lon display_name
    lat=$(echo "$coord_data" | jq -r '.lat')
    lon=$(echo "$coord_data" | jq -r '.lon')
    display_name=$(echo "$coord_data" | jq -r '.display_name')
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Download static map
    download_static_map "$lat" "$lon" "${OUTPUT_DIR}/location-map.png" || {
        echo "Skipping location card generation: Could not download map" >&2
        exit 1
    }
    
    # Get current UTC time for update timestamp in ISO 8601 format
    local updated_at
    updated_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Output combined JSON
    jq -n \
        --arg location "$location" \
        --arg display_name "$display_name" \
        --arg lat "$lat" \
        --arg lon "$lon" \
        --arg map_path "${OUTPUT_DIR}/location-map.png" \
        --arg updated_at "$updated_at" \
        '{
            location: $location,
            display_name: $display_name,
            coordinates: {lat: ($lat | tonumber), lon: ($lon | tonumber)},
            map_path: $map_path,
            updated_at: $updated_at
        }'
}

main "$@"
