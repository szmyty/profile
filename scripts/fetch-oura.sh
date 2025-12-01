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

# Function to make Oura API request
oura_api_request() {
    local endpoint=$1
    local params="${2:-}"
    
    local url="https://api.ouraring.com/v2/usercollection/${endpoint}"
    if [ -n "$params" ]; then
        url="${url}?${params}"
    fi
    
    echo "Fetching from: ${url}" >&2
    
    curl -sf "$url" \
        -H "Authorization: Bearer ${OURA_PAT}" \
        -H "Content-Type: application/json" \
        -H "User-Agent: GitHub-Profile-Oura-Card/1.0" || {
        echo "Error: Failed to fetch from Oura API endpoint: ${endpoint}" >&2
        return 1
    }
}

# Fetch daily sleep data
fetch_daily_sleep() {
    echo "Fetching daily sleep data..." >&2
    local response
    response=$(oura_api_request "daily_sleep" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Get the most recent entry
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch daily readiness data
fetch_daily_readiness() {
    echo "Fetching daily readiness data..." >&2
    local response
    response=$(oura_api_request "daily_readiness" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Get the most recent entry
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch daily activity data
fetch_daily_activity() {
    echo "Fetching daily activity data..." >&2
    local response
    response=$(oura_api_request "daily_activity" "start_date=${START_DATE}&end_date=${END_DATE}") || return 1
    
    # Get the most recent entry
    echo "$response" | jq '.data | sort_by(.day) | last // empty'
}

# Fetch heart rate data (optional, may fail)
fetch_heart_rate() {
    echo "Fetching heart rate data..." >&2
    local response
    response=$(oura_api_request "heartrate" "start_datetime=${START_DATE}T00:00:00&end_datetime=${END_DATE}T23:59:59") || {
        echo "Warning: Could not fetch heart rate data, continuing without it" >&2
        echo "{}"
        return 0
    }
    
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
    
    # Validate we got some data
    if [ "$sleep_data" = "{}" ] && [ "$readiness_data" = "{}" ] && [ "$activity_data" = "{}" ]; then
        echo "Error: No data returned from Oura API. Check if your token is valid and you have data available." >&2
        exit 1
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
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Output combined JSON
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
