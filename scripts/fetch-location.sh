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
DEBUG_DIR="${OUTPUT_DIR}"

# Function to save diagnostic information
save_diagnostic() {
    local filename=$1
    local content=$2
    
    mkdir -p "$DEBUG_DIR"
    echo "$content" > "${DEBUG_DIR}/${filename}"
    echo "Diagnostic info saved to ${DEBUG_DIR}/${filename}" >&2
}

# Function to download static map from OpenStreetMap
download_static_map() {
    local lat=$1
    local lon=$2
    local output_path=$3
    
    echo "Downloading static map centered on ${lat}, ${lon}..." >&2
    
    # OpenStreetMap static map API
    local map_url="https://staticmap.openstreetmap.de/staticmap.php?center=${lat},${lon}&zoom=12&size=600x400&markers=${lat},${lon},blue"
    
    # Capture HTTP response with headers
    local http_code response_headers temp_file
    temp_file=$(mktemp)
    response_headers=$(mktemp)
    
    http_code=$(curl -w "%{http_code}" -o "$temp_file" -D "$response_headers" -s "$map_url")
    local curl_exit=$?
    
    # Save diagnostic information
    save_diagnostic "debug_map_response.txt" "URL: $map_url
HTTP Code: $http_code
Curl Exit Code: $curl_exit
Response Headers:
$(cat "$response_headers")
File Size: $(stat -f%z "$temp_file" 2>/dev/null || stat -c%s "$temp_file" 2>/dev/null || echo "unknown")"
    
    # Check curl exit code
    if [ $curl_exit -ne 0 ]; then
        echo "❌ FAILURE: Map retrieval failed (Curl exit code: ${curl_exit})" >&2
        echo "   → This usually indicates a network error or DNS resolution failure" >&2
        echo "   → Check your network connection and try again" >&2
        rm -f "$temp_file" "$response_headers"
        return 1
    fi
    
    # Check HTTP status code
    if [ "$http_code" -ge 400 ]; then
        echo "❌ FAILURE: Map retrieval failed (HTTP Code: ${http_code})" >&2
        case "$http_code" in
            401|403)
                echo "   → Authentication required or access forbidden" >&2
                echo "   → Map service may require API key or token" >&2
                echo "   → Check if the service has changed its authentication requirements" >&2
                ;;
            404)
                echo "   → Map service endpoint not found" >&2
                echo "   → The static map service URL may have changed" >&2
                ;;
            429)
                echo "   → Rate limit exceeded" >&2
                echo "   → Wait before retrying or use a different service" >&2
                ;;
            500|502|503|504)
                echo "   → Map service is experiencing issues" >&2
                echo "   → Try again later or use an alternative service" >&2
                ;;
            *)
                echo "   → Unexpected HTTP error" >&2
                echo "   → Check debug_map_response.txt for details" >&2
                ;;
        esac
        rm -f "$temp_file" "$response_headers"
        return 1
    fi
    
    # Verify the downloaded file is not empty
    if [ ! -s "$temp_file" ]; then
        echo "❌ FAILURE: Downloaded map file is empty" >&2
        echo "   → The map service returned an empty response" >&2
        echo "   → This may indicate rate limiting, service issues, or invalid parameters" >&2
        rm -f "$temp_file" "$response_headers"
        return 1
    fi
    
    # Move temp file to final location
    mv "$temp_file" "$output_path"
    rm -f "$response_headers"
    
    echo "✅ Static map saved to ${output_path}" >&2
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
