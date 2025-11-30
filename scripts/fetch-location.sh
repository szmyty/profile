#!/bin/bash
# Script to fetch location data and static map from OpenStreetMap
# This script:
# 1. Gets the GitHub user's location
# 2. Converts location to coordinates via Nominatim
# 3. Downloads a static map centered on coordinates
# 4. Outputs location data as JSON

set -euo pipefail

GITHUB_OWNER="${GITHUB_OWNER:-szmyty}"
OUTPUT_DIR="${OUTPUT_DIR:-location}"

# Function to get GitHub user location
get_github_location() {
    echo "Fetching GitHub profile location for ${GITHUB_OWNER}..." >&2
    
    local user_data
    user_data=$(curl -sf "https://api.github.com/users/${GITHUB_OWNER}" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "User-Agent: GitHub-Profile-Location-Card") || {
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
    
    # URL encode the location
    local encoded_location
    encoded_location=$(echo "$location" | sed 's/ /%20/g; s/,/%2C/g')
    
    # Add delay to respect Nominatim rate limits
    sleep 1
    
    local nominatim_data
    nominatim_data=$(curl -sf "https://nominatim.openstreetmap.org/search?q=${encoded_location}&format=json&limit=1" \
        -H "User-Agent: GitHub-Profile-Location-Card/1.0") || {
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
    local lat lon display_name
    lat=$(echo "$nominatim_data" | jq -r '.[0].lat')
    lon=$(echo "$nominatim_data" | jq -r '.[0].lon')
    display_name=$(echo "$nominatim_data" | jq -r '.[0].display_name')
    
    if [ -z "$lat" ] || [ -z "$lon" ] || [ "$lat" = "null" ] || [ "$lon" = "null" ]; then
        echo "Error: Could not extract coordinates from Nominatim response" >&2
        return 1
    fi
    
    echo "Found coordinates: ${lat}, ${lon}" >&2
    echo "Display name: ${display_name}" >&2
    
    # Output JSON with coordinates
    jq -n \
        --arg lat "$lat" \
        --arg lon "$lon" \
        --arg display_name "$display_name" \
        '{lat: $lat, lon: $lon, display_name: $display_name}'
}

# Function to download static map from OpenStreetMap
download_static_map() {
    local lat=$1
    local lon=$2
    local output_path=$3
    
    echo "Downloading static map centered on ${lat}, ${lon}..." >&2
    
    # OpenStreetMap static map API
    local map_url="https://staticmap.openstreetmap.de/staticmap.php?center=${lat},${lon}&zoom=12&size=600x400&markers=${lat},${lon},blue"
    
    curl -sf -o "$output_path" "$map_url" || {
        echo "Error: Failed to download static map" >&2
        return 1
    }
    
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
    
    # Get current UTC time for update timestamp
    local updated_at
    updated_at=$(date -u +"%Y-%m-%d %H:%M UTC")
    
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
