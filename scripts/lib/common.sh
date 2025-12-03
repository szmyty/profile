#!/bin/bash
# Common shell script utilities for profile scripts.
# This module provides shared helper functions used across multiple scripts.

# Default cache configuration
CACHE_DIR="${CACHE_DIR:-cache}"
CACHE_TTL_DAYS="${CACHE_TTL_DAYS:-7}"

# Default retry configuration
MAX_RETRIES="${MAX_RETRIES:-3}"
INITIAL_RETRY_DELAY="${INITIAL_RETRY_DELAY:-5}"

# Retry a command with exponential backoff.
# Executes the given command, retrying on failure with increasing delays.
# The delay follows an exponential backoff pattern: 5s → 10s → 20s
#
# Usage:
#   retry_with_backoff "curl -sf https://api.example.com/data"
#   retry_with_backoff wget -q -O output.json https://api.example.com/data
#
# Arguments:
#   $@ - Command and arguments to execute
#
# Environment variables:
#   MAX_RETRIES - Maximum number of retry attempts (default: 3)
#   INITIAL_RETRY_DELAY - Initial delay in seconds (default: 5)
#
# Returns:
#   Exit code of the command if successful, 1 if all retries exhausted
retry_with_backoff() {
    local max_attempts=$((MAX_RETRIES + 1))  # +1 for initial attempt
    local attempt=1
    local delay=$INITIAL_RETRY_DELAY
    local exit_code=0
    
    while [ $attempt -le $max_attempts ]; do
        # Execute the command
        if "$@"; then
            return 0
        fi
        exit_code=$?
        
        # Don't sleep after the last attempt
        if [ $attempt -lt $max_attempts ]; then
            echo "Attempt $attempt/$max_attempts failed, retrying in ${delay}s..." >&2
            sleep $delay
            # Exponential backoff: double the delay
            delay=$((delay * 2))
        else
            echo "All $max_attempts attempts failed" >&2
        fi
        
        attempt=$((attempt + 1))
    done
    
    return $exit_code
}

# Initialize cache directory.
# Creates the cache directory if it doesn't exist.
#
# Environment variables:
#   CACHE_DIR - Directory to store cache files (default: cache)
#
# Returns:
#   0 on success
init_cache() {
    mkdir -p "$CACHE_DIR"
}

# Generate a cache key from a string.
# Converts the input to a safe filename using base64 encoding.
#
# Usage:
#   generate_cache_key "New York, NY"
#
# Arguments:
#   $1 - The string to convert to a cache key
#
# Output:
#   The cache key to stdout
generate_cache_key() {
    local input="${1:-}"
    # Use base64 encoding to create a safe filename, replace / with _
    echo -n "$input" | base64 | tr '/' '_' | tr '+' '-'
}

# Get cached response if valid.
# Checks if a cached response exists and is not expired.
#
# Usage:
#   get_cached_response "nominatim" "New_York_NY"
#
# Arguments:
#   $1 - Cache type (e.g., "nominatim")
#   $2 - Cache key
#
# Output:
#   Cached content to stdout if valid, empty otherwise
#
# Returns:
#   0 if cache hit, 1 if cache miss or expired
get_cached_response() {
    local cache_type=$1
    local cache_key=$2
    local cache_file="${CACHE_DIR}/${cache_type}_${cache_key}.json"
    
    # Check if cache file exists
    if [ ! -f "$cache_file" ]; then
        return 1
    fi
    
    # Check if cache is expired
    # Use portable stat command (works on both Linux and macOS)
    local file_mtime
    if stat -c %Y "$cache_file" > /dev/null 2>&1; then
        # Linux
        file_mtime=$(stat -c %Y "$cache_file")
    elif stat -f %m "$cache_file" > /dev/null 2>&1; then
        # macOS/BSD
        file_mtime=$(stat -f %m "$cache_file")
    else
        # Fallback: treat as expired if stat fails
        file_mtime=0
    fi
    
    local file_age_days
    file_age_days=$(( ( $(date +%s) - file_mtime ) / 86400 ))
    
    if [ "$file_age_days" -ge "$CACHE_TTL_DAYS" ]; then
        echo "Cache expired for ${cache_type}:${cache_key}" >&2
        return 1
    fi
    
    # Validate JSON
    if ! jq -e . "$cache_file" > /dev/null 2>&1; then
        echo "Invalid cache entry for ${cache_type}:${cache_key}" >&2
        rm -f "$cache_file"
        return 1
    fi
    
    echo "Cache hit for ${cache_type}:${cache_key}" >&2
    cat "$cache_file"
    return 0
}

# Save response to cache.
#
# Usage:
#   echo '{"lat": "40.7", "lon": "-74.0"}' | save_cached_response "nominatim" "New_York_NY"
#
# Arguments:
#   $1 - Cache type (e.g., "nominatim")
#   $2 - Cache key
#
# Input:
#   Response content via stdin
#
# Returns:
#   0 on success
save_cached_response() {
    local cache_type=$1
    local cache_key=$2
    local cache_file="${CACHE_DIR}/${cache_type}_${cache_key}.json"
    
    init_cache
    cat > "$cache_file"
    echo "Cached response for ${cache_type}:${cache_key}" >&2
}

# Validate JSON response from an API.
# Checks if the response is valid JSON and optionally validates structure.
#
# Usage:
#   validate_api_response "$response_data" "temperature"
#
# Arguments:
#   $1 - JSON response data to validate
#   $2 - Optional: required field name to check for
#
# Returns:
#   0 if valid, 1 if invalid
validate_api_response() {
    local response=$1
    local required_field="${2:-}"
    
    # Check if response is non-empty
    if [ -z "$response" ]; then
        echo "Error: Empty API response" >&2
        return 1
    fi
    
    # Validate JSON structure
    if ! echo "$response" | jq empty 2>/dev/null; then
        echo "Error: Invalid JSON in API response" >&2
        return 1
    fi
    
    # Check for required field if specified
    if [ -n "$required_field" ]; then
        if ! echo "$response" | jq -e ".$required_field" >/dev/null 2>&1; then
            echo "Error: Required field '$required_field' not found in API response" >&2
            return 1
        fi
    fi
    
    return 0
}

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

# Get the GitHub user's location from their profile with fallback support.
# Uses the GitHub API to fetch the user's profile and extract the location.
# If the API fails or returns no location, tries to use cached location.
#
# Environment variables:
#   GITHUB_OWNER - GitHub username (default: szmyty)
#   GITHUB_TOKEN - Optional GitHub token for authentication
#   LOCATION_CACHE_FILE - Path to fallback location cache (default: cached/location.json)
#
# Output:
#   The location string to stdout
#
# Returns:
#   0 on success, 1 on failure
get_github_location() {
    local github_owner="${GITHUB_OWNER:-szmyty}"
    local location_cache="${LOCATION_CACHE_FILE:-cached/location.json}"
    
    echo "Fetching GitHub profile location for ${github_owner}..." >&2
    
    local user_data location
    
    # Try to fetch from GitHub API
    if user_data=$(curl -sf --max-time 10 "https://api.github.com/users/${github_owner}" \
        -H "Accept: application/vnd.github.v3+json" \
        ${GITHUB_TOKEN:+-H "Authorization: Bearer ${GITHUB_TOKEN}"} \
        -H "User-Agent: GitHub-Profile-Scripts/1.0" 2>/dev/null); then
        
        location=$(echo "$user_data" | jq -r '.location // empty')
        
        if [ -n "$location" ] && [ "$location" != "null" ]; then
            # Save successful location to cache
            mkdir -p "$(dirname "$location_cache")"
            jq -n --arg location "$location" --arg updated_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
                '{location: $location, updated_at: $updated_at}' > "$location_cache"
            echo "Location saved to cache: ${location}" >&2
            echo "$location"
            return 0
        fi
    fi
    
    # Try fallback to cached location
    echo "GitHub location not available, trying cached location..." >&2
    if [ -f "$location_cache" ]; then
        # Validate cache file once
        if jq -e . "$location_cache" >/dev/null 2>&1; then
            location=$(jq -r '.location // empty' "$location_cache")
            if [ -n "$location" ] && [ "$location" != "null" ]; then
                echo "Using cached location: ${location}" >&2
                echo "$location"
                return 0
            fi
        fi
    fi
    
    echo "Warning: No location found in GitHub profile or cache" >&2
    return 1
}

# Convert a location string to coordinates using the Nominatim API.
# Uses OpenStreetMap's Nominatim geocoding service to convert a location
# string to latitude/longitude coordinates.
# Responses are cached to reduce API calls.
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
# Environment variables:
#   OUTPUT_DIR - Directory for diagnostic output (default: location)
#
# Returns:
#   0 on success, 1 on failure
get_coordinates() {
    local location=$1
    local debug_dir="${OUTPUT_DIR:-location}"
    
    echo "Converting location to coordinates: ${location}" >&2
    
    # Generate cache key from location
    local cache_key
    cache_key=$(generate_cache_key "$location")
    
    # Try to get cached response
    local cached_data
    if cached_data=$(get_cached_response "nominatim" "$cache_key"); then
        echo "Using cached coordinates" >&2
        echo "$cached_data"
        return 0
    fi
    
    # URL encode the location using the shared encode_uri function
    local encoded_location
    encoded_location=$(encode_uri "$location")
    
    # Add delay to respect Nominatim rate limits
    sleep 1
    
    # Fetch from Nominatim with detailed error capture
    local nominatim_data http_code temp_response temp_headers
    temp_response=$(mktemp)
    temp_headers=$(mktemp)
    
    http_code=$(curl -w "%{http_code}" \
        --max-time 10 \
        -o "$temp_response" \
        -D "$temp_headers" \
        -s "https://nominatim.openstreetmap.org/search?q=${encoded_location}&format=json&limit=1" \
        -H "User-Agent: GitHub-Profile-Scripts/1.0")
    local curl_exit=$?
    
    nominatim_data=$(cat "$temp_response")
    
    # Save diagnostic information
    # Note: These files contain the location query and may be sensitive.
    # They are excluded from git commits via .gitignore
    mkdir -p "$debug_dir"
    echo "$nominatim_data" > "${debug_dir}/debug_nominatim.json"
    echo "URL: https://nominatim.openstreetmap.org/search?q=${encoded_location}&format=json&limit=1
Location Query: $location
HTTP Code: $http_code
Curl Exit Code: $curl_exit
Response Headers:
$(cat "$temp_headers")
Response Body:
$nominatim_data" > "${debug_dir}/debug_nominatim_response.txt"
    
    echo "Diagnostic info saved to ${debug_dir}/debug_nominatim.json" >&2
    echo "Note: Debug files contain location data and are excluded from git commits" >&2
    
    rm -f "$temp_response" "$temp_headers"
    
    # Check curl exit code
    if [ $curl_exit -ne 0 ]; then
        echo "❌ FAILURE: Nominatim API request failed (Curl exit code: ${curl_exit})" >&2
        echo "   → Network error or DNS resolution failure" >&2
        return 1
    fi
    
    # Check HTTP status code
    if [ "$http_code" -ge 400 ]; then
        echo "❌ FAILURE: Nominatim API returned error (HTTP Code: ${http_code})" >&2
        case "$http_code" in
            429)
                echo "   → Rate limiting detected" >&2
                echo "   → Nominatim has strict rate limits (1 request per second)" >&2
                echo "   → Wait at least 1 hour before retrying or use caching" >&2
                echo "   → Consider using a commercial geocoding service for production" >&2
                ;;
            403)
                echo "   → Access forbidden" >&2
                echo "   → Your IP may be blocked due to excessive requests" >&2
                echo "   → Check Nominatim usage policy: https://operations.osmfoundation.org/policies/nominatim/" >&2
                ;;
            500|502|503|504)
                echo "   → Nominatim service error" >&2
                echo "   → Try again later" >&2
                ;;
        esac
        return 1
    fi
    
    # Check if response is empty
    if [ -z "$nominatim_data" ]; then
        echo "❌ FAILURE: Nominatim returned empty response" >&2
        echo "   → This may indicate rate limiting or service issues" >&2
        return 1
    fi
    
    # Validate the JSON response
    if ! echo "$nominatim_data" | jq empty 2>/dev/null; then
        echo "❌ FAILURE: Nominatim returned invalid JSON" >&2
        echo "   → Response is not valid JSON format" >&2
        echo "   → See ${debug_dir}/debug_nominatim.json for raw response" >&2
        return 1
    fi
    
    # Check if we got results
    local result_count
    result_count=$(echo "$nominatim_data" | jq 'length' 2>/dev/null || echo "0")
    
    if [ "$result_count" -eq 0 ]; then
        echo "❌ FAILURE: Nominatim returned no results for location: ${location}" >&2
        echo "   → The location string may be too vague or invalid" >&2
        echo "   → Try a more specific location (e.g., 'New York, NY, USA' instead of 'NYC')" >&2
        return 1
    fi
    
    # Extract lat/lon
    local lat lon display_name
    lat=$(echo "$nominatim_data" | jq -r '.[0].lat')
    lon=$(echo "$nominatim_data" | jq -r '.[0].lon')
    display_name=$(echo "$nominatim_data" | jq -r '.[0].display_name')
    
    if [ -z "$lat" ] || [ -z "$lon" ] || [ "$lat" = "null" ] || [ "$lon" = "null" ]; then
        echo "❌ FAILURE: Could not extract coordinates from Nominatim response" >&2
        echo "   → Response structure is unexpected" >&2
        echo "   → See ${debug_dir}/debug_nominatim.json for details" >&2
        return 1
    fi
    
    echo "✅ Found coordinates: ${lat}, ${lon}" >&2
    echo "   Display name: ${display_name}" >&2
    
    # Build result JSON
    local result
    result=$(jq -n \
        --arg lat "$lat" \
        --arg lon "$lon" \
        --arg display_name "$display_name" \
        '{lat: $lat, lon: $lon, display_name: $display_name}')
    
    # Cache the result
    echo "$result" | save_cached_response "nominatim" "$cache_key"
    
    # Output JSON with coordinates
    echo "$result"
}
