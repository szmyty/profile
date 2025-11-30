#!/bin/bash
# Script to fetch the latest SoundCloud track data
# This script:
# 1. Extracts the client_id from SoundCloud's JavaScript assets
# 2. Fetches the user's latest track metadata
# 3. Downloads the track artwork
# 4. Outputs track metadata as JSON

set -euo pipefail

SOUNDCLOUD_USER="${SOUNDCLOUD_USER:-playfunction}"
OUTPUT_DIR="${OUTPUT_DIR:-assets}"

# Function to extract client_id from SoundCloud
get_client_id() {
    echo "Fetching SoundCloud client_id..." >&2
    
    # Fetch the main page HTML
    local html
    html=$(curl -sf "https://soundcloud.com/${SOUNDCLOUD_USER}" \
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36") || {
        echo "Error: Failed to fetch SoundCloud profile page" >&2
        return 1
    }
    
    if [ -z "$html" ]; then
        echo "Error: Empty response from SoundCloud" >&2
        return 1
    fi
    
    # Extract JS asset URLs
    local js_urls
    js_urls=$(echo "$html" | grep -oE 'https://a-v2\.sndcdn\.com/assets/[^"]+\.js' | head -10)
    
    if [ -z "$js_urls" ]; then
        echo "Error: No JavaScript assets found in SoundCloud page" >&2
        return 1
    fi
    
    # Search each JS file for client_id
    for url in $js_urls; do
        local js_content
        js_content=$(curl -sf "$url") || continue
        
        # Look for client_id patterns
        local client_id
        client_id=$(echo "$js_content" | grep -oE 'client_id[=:]["'"'"'][a-zA-Z0-9]+' | grep -oE '[a-zA-Z0-9]{20,}' | head -1 || true)
        
        if [ -n "$client_id" ]; then
            echo "$client_id"
            return 0
        fi
    done
    
    echo "Error: Failed to extract client_id from any JavaScript asset" >&2
    return 1
}

# Function to get user ID from username
get_user_id() {
    local client_id=$1
    echo "Fetching user ID for ${SOUNDCLOUD_USER}..." >&2
    
    local user_data
    user_data=$(curl -sf "https://api-v2.soundcloud.com/resolve?url=https://soundcloud.com/${SOUNDCLOUD_USER}&client_id=${client_id}") || {
        echo "Error: Failed to resolve SoundCloud user" >&2
        return 1
    }
    
    local user_id
    user_id=$(echo "$user_data" | jq -r '.id')
    
    if [ -z "$user_id" ] || [ "$user_id" = "null" ]; then
        echo "Error: Invalid user data received from SoundCloud API" >&2
        return 1
    fi
    
    echo "$user_id"
}

# Function to fetch latest track
fetch_latest_track() {
    local client_id=$1
    local user_id=$2
    echo "Fetching latest track..." >&2
    
    local tracks
    tracks=$(curl -sf "https://api-v2.soundcloud.com/users/${user_id}/tracks?representation=&client_id=${client_id}&limit=1&offset=0") || {
        echo "Error: Failed to fetch tracks from SoundCloud API" >&2
        return 1
    }
    
    local track
    track=$(echo "$tracks" | jq '.collection[0]')
    
    if [ -z "$track" ] || [ "$track" = "null" ]; then
        echo "Error: No tracks found for user" >&2
        return 1
    fi
    
    echo "$track"
}

# Function to download artwork
download_artwork() {
    local artwork_url=$1
    local output_path=$2
    
    echo "Downloading artwork..." >&2
    
    # Replace size placeholder with larger size
    local large_url
    large_url=$(echo "$artwork_url" | sed 's/-large\./-t500x500./')
    
    curl -s -o "$output_path" "$large_url" || curl -s -o "$output_path" "$artwork_url"
    echo "Artwork saved to $output_path" >&2
}

# Main execution
main() {
    # Get client_id
    local client_id
    client_id=$(get_client_id)
    echo "Got client_id: ${client_id:0:10}..." >&2
    
    # Get user ID
    local user_id
    user_id=$(get_user_id "$client_id")
    echo "Got user_id: $user_id" >&2
    
    # Fetch latest track
    local track_data
    track_data=$(fetch_latest_track "$client_id" "$user_id")
    
    # Extract track info
    local title
    title=$(echo "$track_data" | jq -r '.title')
    local artwork_url
    artwork_url=$(echo "$track_data" | jq -r '.artwork_url // .user.avatar_url')
    local permalink_url
    permalink_url=$(echo "$track_data" | jq -r '.permalink_url')
    local genre
    genre=$(echo "$track_data" | jq -r '.genre // "Electronic"')
    local duration
    duration=$(echo "$track_data" | jq -r '.duration')
    local playback_count
    playback_count=$(echo "$track_data" | jq -r '.playback_count // 0')
    local created_at
    created_at=$(echo "$track_data" | jq -r '.created_at')
    local user_username
    user_username=$(echo "$track_data" | jq -r '.user.username')
    
    # Download artwork
    mkdir -p "$OUTPUT_DIR"
    download_artwork "$artwork_url" "${OUTPUT_DIR}/soundcloud-artwork.jpg"
    
    # Output track metadata as JSON using jq for proper escaping
    jq -n \
        --arg title "$title" \
        --arg artist "$user_username" \
        --arg artwork_url "$artwork_url" \
        --arg permalink_url "$permalink_url" \
        --arg genre "$genre" \
        --argjson duration_ms "$duration" \
        --argjson playback_count "$playback_count" \
        --arg created_at "$created_at" \
        '{
            title: $title,
            artist: $artist,
            artwork_url: $artwork_url,
            permalink_url: $permalink_url,
            genre: $genre,
            duration_ms: $duration_ms,
            playback_count: $playback_count,
            created_at: $created_at
        }'
}

main "$@"
