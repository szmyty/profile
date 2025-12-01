#!/bin/bash
# Script to fetch Oura Ring health metrics from Oura Cloud API
# This script:
# 1. Authenticates with Oura API using OURA_PAT secret
# 2. Fetches daily sleep, readiness, activity metrics
# 3. Optionally fetches heart rate data
# 4. Outputs combined metrics as JSON

set -euo pipefail

OURA_PAT="${OURA_PAT:-}"
OUTPUT_DIR="${OUTPUT_DIR:-oura}"

# Validate that we have the Oura Personal Access Token
if [ -z "$OURA_PAT" ]; then
    echo "Error: OURA_PAT environment variable is not set" >&2
    exit 1
fi

# Calculate date range (last 7 days to ensure we get most recent data)
END_DATE=$(date -u +"%Y-%m-%d")
START_DATE=$(date -u -d "7 days ago" +"%Y-%m-%d" 2>/dev/null || date -u -v-7d +"%Y-%m-%d")

# Logging: Show date range being used
echo "Start date: $START_DATE" >&2
echo "End date: $END_DATE" >&2

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to make Oura API request with retry logic
oura_api_request() {
    local endpoint=$1
    local params="${2:-}"
    local max_retries=3
    local retry_delay=5
    
    local url="https://api.ouraring.com/v2/usercollection/${endpoint}"
    if [ -n "$params" ]; then
        url="${url}?${params}"
    fi
    
    echo "Fetching from: ${url}" >&2
    
    local response
    local attempt
    for attempt in $(seq 1 $max_retries); do
        response=$(curl -sf "$url" \
            -H "Authorization: Bearer ${OURA_PAT}" \
            -H "Content-Type: application/json" \
            -H "User-Agent: GitHub-Profile-Oura-Card/1.0" 2>/dev/null) || response=""
        
        # Check if response is valid JSON
        if [ -n "$response" ] && echo "$response" | jq empty 2>/dev/null; then
            echo "$response"
            return 0
        fi
        
        if [ "$attempt" -lt "$max_retries" ]; then
            echo "Attempt $attempt failed for endpoint: ${endpoint}. Retrying in ${retry_delay}s..." >&2
            sleep $retry_delay
        fi
    done
    
    echo "Error: Failed to fetch valid JSON from Oura API endpoint after $max_retries attempts: ${endpoint}" >&2
    if [ -n "$response" ]; then
        echo "Invalid response saved for debugging" >&2
        echo "$response" > "${OUTPUT_DIR}/debug_invalid_response_${endpoint}.txt"
    fi
    return 1
}

# Fetch daily sleep data
fetch_daily_sleep() {
    echo "Fetching daily sleep data..." >&2
    local response
    response=$(oura_api_request "daily_sleep" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_sleep.json"
    echo "Sleep JSON saved to raw_sleep.json" >&2
    
    # Check if items array is empty
    local item_count
    item_count=$(echo "$response" | jq '.data | length')
    if [ "$item_count" -eq 0 ]; then
        echo "::warning::No data returned for daily_sleep" >&2
        echo "{}"
        return 0
    fi
    
    # Get the most recent entry
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch daily readiness data
fetch_daily_readiness() {
    echo "Fetching daily readiness data..." >&2
    local response
    response=$(oura_api_request "daily_readiness" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_readiness.json"
    echo "Readiness JSON saved to raw_readiness.json" >&2
    
    # Check if items array is empty
    local item_count
    item_count=$(echo "$response" | jq '.data | length')
    if [ "$item_count" -eq 0 ]; then
        echo "::warning::No data returned for daily_readiness" >&2
        echo "{}"
        return 0
    fi
    
    # Get the most recent entry
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch daily activity data
fetch_daily_activity() {
    echo "Fetching daily activity data..." >&2
    local response
    response=$(oura_api_request "daily_activity" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_activity.json"
    echo "Activity JSON saved to raw_activity.json" >&2
    
    # Check if items array is empty
    local item_count
    item_count=$(echo "$response" | jq '.data | length')
    if [ "$item_count" -eq 0 ]; then
        echo "::warning::No data returned for daily_activity" >&2
        echo "{}"
        return 0
    fi
    
    # Get the most recent entry
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch heart rate data (optional, may fail)
fetch_heart_rate() {
    echo "Fetching heart rate data..." >&2
    local response
    # Note: Correct endpoint is "heart_rate" not "heartrate"
    response=$(oura_api_request "heart_rate" "start_datetime=${START_DATE}T00:00:00&end_datetime=${END_DATE}T23:59:59") || {
        echo "Warning: Could not fetch heart rate data, continuing without it" >&2
        echo "{}"
        return 0
    }
    
    # Save raw response for debugging
    echo "$response" > "${OUTPUT_DIR}/raw_heart_rate.json"
    echo "Heart rate JSON saved to raw_hr.json" >&2
    
    # Get avg resting heart rate from recent data
    echo "$response" | jq '{
        data: (.data // []),
        avg_bpm: (if (.data | length) > 0 then (.data | map(.bpm) | add / length | floor) else null end)
    }'
}

# Main execution
main() {
    echo "Starting Oura data fetch..." >&2
    echo "Date range: ${START_DATE} to ${END_DATE}" >&2
    
    # Fetch all data types
    local sleep_data readiness_data activity_data hr_data
    
    sleep_data=$(fetch_daily_sleep) || sleep_data="{}"
    readiness_data=$(fetch_daily_readiness) || readiness_data="{}"
    activity_data=$(fetch_daily_activity) || activity_data="{}"
    hr_data=$(fetch_heart_rate) || hr_data="{}"
    
    # Ensure all data variables contain valid JSON (default to empty object)
    if [ -z "$sleep_data" ] || ! echo "$sleep_data" | jq empty 2>/dev/null; then
        echo "Warning: sleep_data is invalid, defaulting to empty object" >&2
        sleep_data="{}"
    fi
    if [ -z "$readiness_data" ] || ! echo "$readiness_data" | jq empty 2>/dev/null; then
        echo "Warning: readiness_data is invalid, defaulting to empty object" >&2
        readiness_data="{}"
    fi
    if [ -z "$activity_data" ] || ! echo "$activity_data" | jq empty 2>/dev/null; then
        echo "Warning: activity_data is invalid, defaulting to empty object" >&2
        activity_data="{}"
    fi
    if [ -z "$hr_data" ] || ! echo "$hr_data" | jq empty 2>/dev/null; then
        echo "Warning: hr_data is invalid, defaulting to empty object" >&2
        hr_data="{}"
    fi
    
    # Log what data was received
    echo "Sleep data received: $(echo "$sleep_data" | jq -c '.')" >&2
    echo "Readiness data received: $(echo "$readiness_data" | jq -c '.')" >&2
    echo "Activity data received: $(echo "$activity_data" | jq -c '.')" >&2
    echo "Heart rate data received: $(echo "$hr_data" | jq -c '.')" >&2
    
    # Check if we got any meaningful data (don't fail if some categories are empty)
    if [ "$sleep_data" = "{}" ] && [ "$readiness_data" = "{}" ] && [ "$activity_data" = "{}" ]; then
        echo "Warning: No data returned from any Oura API endpoint. Check if your token is valid and you have data available." >&2
        # Don't exit, continue with empty data to allow workflow to complete
    fi
    
    # Extract key metrics with null-safe defaults
    local sleep_score readiness_score activity_score hrv resting_hr temp_deviation
    
    sleep_score=$(echo "$sleep_data" | jq '.score // null')
    readiness_score=$(echo "$readiness_data" | jq '.score // null')
    activity_score=$(echo "$activity_data" | jq '.score // null')
    
    # HRV from readiness contributors
    hrv=$(echo "$readiness_data" | jq '.contributors.hrv_balance // null')
    
    # Resting HR from readiness
    resting_hr=$(echo "$readiness_data" | jq '.contributors.resting_heart_rate // null')
    
    # Temperature deviation from readiness
    temp_deviation=$(echo "$readiness_data" | jq '.contributors.body_temperature // null')
    
    # Get current UTC time for update timestamp
    local updated_at
    updated_at=$(date -u +"%Y-%m-%d %H:%M UTC")
    
    # Output combined JSON - always include all categories
    jq -n \
        --argjson sleep_score "$sleep_score" \
        --argjson readiness_score "$readiness_score" \
        --argjson activity_score "$activity_score" \
        --argjson hrv "$hrv" \
        --argjson resting_hr "$resting_hr" \
        --argjson temp_deviation "$temp_deviation" \
        --argjson sleep "$sleep_data" \
        --argjson readiness "$readiness_data" \
        --argjson activity "$activity_data" \
        --argjson heart_rate "$hr_data" \
        --arg updated_at "$updated_at" \
        '{
            sleep_score: $sleep_score,
            readiness_score: $readiness_score,
            activity_score: $activity_score,
            hrv: $hrv,
            resting_hr: $resting_hr,
            temp_deviation: $temp_deviation,
            sleep: $sleep,
            readiness: $readiness,
            activity: $activity,
            heart_rate: $heart_rate,
            updated_at: $updated_at
        }'
}

main "$@"
