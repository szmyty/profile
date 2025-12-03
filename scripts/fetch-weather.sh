#!/bin/bash
# Script to fetch weather data from Open-Meteo API
# This script:
# 1. Gets the GitHub user's location
# 2. Converts location to coordinates via Nominatim
# 3. Fetches weather data from Open-Meteo API
# 4. Outputs weather data as JSON

set -euo pipefail

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

GITHUB_OWNER="${GITHUB_OWNER:-szmyty}"
OUTPUT_DIR="${OUTPUT_DIR:-weather}"

# Function to fetch weather from Open-Meteo
fetch_weather() {
    local lat=$1
    local lon=$2
    echo "Fetching weather data from Open-Meteo..." >&2
    
    # Generate cache key from coordinates
    local cache_key
    cache_key=$(generate_cache_key "${lat},${lon}")
    
    # Try to get cached weather (cache for 1 hour by setting CACHE_TTL_DAYS=0.042)
    local cached_weather
    if CACHE_TTL_DAYS=0.042 cached_weather=$(get_cached_response "weather" "$cache_key"); then
        echo "Using cached weather data" >&2
        echo "$cached_weather"
        return 0
    fi
    
    local weather_data
    if ! weather_data=$(retry_with_backoff curl -sf "https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=auto"); then
        echo "Error: Failed to fetch weather from Open-Meteo API after retries" >&2
        return 1
    fi
    
    # Validate JSON response
    if ! validate_api_response "$weather_data" "current_weather"; then
        echo "Error: Invalid weather data from Open-Meteo API" >&2
        return 1
    fi
    
    # Cache the weather data
    echo "$weather_data" | save_cached_response "weather" "$cache_key"
    
    echo "$weather_data"
}

# Function to map weathercode to condition and emoji
get_weather_condition() {
    local code=$1
    local is_day=$2
    
    local condition emoji
    
    case $code in
        0)
            condition="Clear sky"
            if [ "$is_day" -eq 1 ]; then
                emoji="☀️"
            else
                emoji="🌙"
            fi
            ;;
        1)
            condition="Mainly clear"
            if [ "$is_day" -eq 1 ]; then
                emoji="🌤️"
            else
                emoji="🌙"
            fi
            ;;
        2)
            condition="Partly cloudy"
            emoji="⛅"
            ;;
        3)
            condition="Overcast"
            emoji="☁️"
            ;;
        45|48)
            condition="Fog"
            emoji="🌫️"
            ;;
        51|53|55)
            condition="Drizzle"
            emoji="🌦️"
            ;;
        56|57)
            condition="Freezing drizzle"
            emoji="🌧️"
            ;;
        61|63|65)
            condition="Rain"
            emoji="🌧️"
            ;;
        66|67)
            condition="Freezing rain"
            emoji="🌧️"
            ;;
        71|73|75)
            condition="Snow"
            emoji="❄️"
            ;;
        77)
            condition="Snow grains"
            emoji="🌨️"
            ;;
        80|81|82)
            condition="Rain showers"
            emoji="🌧️"
            ;;
        85|86)
            condition="Snow showers"
            emoji="🌨️"
            ;;
        95)
            condition="Thunderstorm"
            emoji="⛈️"
            ;;
        96|99)
            condition="Thunderstorm with hail"
            emoji="⛈️"
            ;;
        *)
            condition="Unknown"
            emoji="🌡️"
            ;;
    esac
    
    jq -n \
        --arg condition "$condition" \
        --arg emoji "$emoji" \
        '{condition: $condition, emoji: $emoji}'
}

# Main execution
main() {
    # Get GitHub location
    local location
    location=$(get_github_location) || {
        echo "Skipping weather card generation: No location found" >&2
        exit 1
    }
    echo "GitHub location: ${location}" >&2
    
    # Get coordinates
    local coord_data
    coord_data=$(get_coordinates "$location") || {
        echo "Skipping weather card generation: Could not get coordinates" >&2
        exit 1
    }
    
    local lat lon display_name
    lat=$(echo "$coord_data" | jq -r '.lat')
    lon=$(echo "$coord_data" | jq -r '.lon')
    display_name=$(echo "$coord_data" | jq -r '.display_name')
    
    # Fetch weather data
    local weather_data
    weather_data=$(fetch_weather "$lat" "$lon") || {
        echo "Skipping weather card generation: Could not fetch weather" >&2
        exit 1
    }
    
    # Extract current weather
    local current_temp wind_speed weathercode is_day
    current_temp=$(echo "$weather_data" | jq -r '.current_weather.temperature')
    wind_speed=$(echo "$weather_data" | jq -r '.current_weather.windspeed')
    weathercode=$(echo "$weather_data" | jq -r '.current_weather.weathercode')
    is_day=$(echo "$weather_data" | jq -r '.current_weather.is_day')
    
    # Extract daily forecast
    local temp_max temp_min sunrise sunset daily_weathercode timezone
    temp_max=$(echo "$weather_data" | jq -r '.daily.temperature_2m_max[0]')
    temp_min=$(echo "$weather_data" | jq -r '.daily.temperature_2m_min[0]')
    sunrise=$(echo "$weather_data" | jq -r '.daily.sunrise[0]')
    sunset=$(echo "$weather_data" | jq -r '.daily.sunset[0]')
    daily_weathercode=$(echo "$weather_data" | jq -r '.daily.weathercode[0]')
    timezone=$(echo "$weather_data" | jq -r '.timezone')
    
    # Get weather condition
    local condition_data
    condition_data=$(get_weather_condition "$weathercode" "$is_day")
    local condition emoji
    condition=$(echo "$condition_data" | jq -r '.condition')
    emoji=$(echo "$condition_data" | jq -r '.emoji')
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Get current UTC time for update timestamp in ISO 8601 format
    local updated_at
    updated_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Output combined JSON
    jq -n \
        --arg location "$location" \
        --arg display_name "$display_name" \
        --arg lat "$lat" \
        --arg lon "$lon" \
        --argjson current_temp "$current_temp" \
        --argjson wind_speed "$wind_speed" \
        --argjson weathercode "$weathercode" \
        --argjson is_day "$is_day" \
        --argjson temp_max "$temp_max" \
        --argjson temp_min "$temp_min" \
        --arg sunrise "$sunrise" \
        --arg sunset "$sunset" \
        --argjson daily_weathercode "$daily_weathercode" \
        --arg timezone "$timezone" \
        --arg condition "$condition" \
        --arg emoji "$emoji" \
        --arg updated_at "$updated_at" \
        '{
            location: $location,
            display_name: $display_name,
            coordinates: {lat: ($lat | tonumber), lon: ($lon | tonumber)},
            current: {
                temperature: $current_temp,
                wind_speed: $wind_speed,
                weathercode: $weathercode,
                is_day: $is_day,
                condition: $condition,
                emoji: $emoji
            },
            daily: {
                temperature_max: $temp_max,
                temperature_min: $temp_min,
                sunrise: $sunrise,
                sunset: $sunset,
                weathercode: $daily_weathercode
            },
            timezone: $timezone,
            updated_at: $updated_at
        }'
}

main "$@"
