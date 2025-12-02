#!/bin/bash
# Common shell script utilities for profile scripts.
# This module provides shared helper functions used across multiple scripts.

# Encode a string for use in URLs.
# Uses jq's @uri filter for proper RFC 3986 percent-encoding.
#
# Usage:
#   encode_uri "New York, NY"
#   # Output: New%20York%2C%20NY
#
# Arguments:
#   $1 - The string to encode
#
# Output:
#   The URL-encoded string to stdout
encode_uri() {
    local input="${1:-}"
    if [ -z "$input" ]; then
        echo ""
        return 0
    fi
    echo "$input" | jq -rR @uri
}

# Get the GitHub user's location from their profile.
# Uses the GitHub API to fetch the user's profile and extract the location.
#
# Environment variables:
#   GITHUB_OWNER - GitHub username (default: szmyty)
#   GITHUB_TOKEN - Optional GitHub token for authentication
#
# Output:
#   The location string to stdout
#
# Returns:
#   0 on success, 1 on failure
get_github_location() {
    local github_owner="${GITHUB_OWNER:-szmyty}"
    echo "Fetching GitHub profile location for ${github_owner}..." >&2
    
    local user_data
    user_data=$(curl -sf "https://api.github.com/users/${github_owner}" \
        -H "Accept: application/vnd.github.v3+json" \
        ${GITHUB_TOKEN:+-H "Authorization: Bearer ${GITHUB_TOKEN}"} \
        -H "User-Agent: GitHub-Profile-Scripts") || {
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

# Convert a location string to coordinates using the Nominatim API.
# Uses OpenStreetMap's Nominatim geocoding service to convert a location
# string to latitude/longitude coordinates.
#
# Usage:
#   get_coordinates "New York, NY"
#
# Arguments:
#   $1 - The location string to geocode
#
# Output:
#   JSON object with lat, lon, and display_name fields to stdout
#
# Returns:
#   0 on success, 1 on failure
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
        -H "User-Agent: GitHub-Profile-Scripts/1.0") || {
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
