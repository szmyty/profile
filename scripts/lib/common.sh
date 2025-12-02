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
