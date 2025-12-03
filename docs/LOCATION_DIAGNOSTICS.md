# Location Card Diagnostics Guide

This guide explains how the location card generation system detects and reports failures, and how to troubleshoot common issues.

## Overview

The location card generation process involves three main steps:

1. **Fetching location data** from GitHub profile
2. **Geocoding location** to coordinates using Nominatim API
3. **Downloading static map** from OpenStreetMap
4. **Generating SVG card** with embedded map image

Each step now includes comprehensive diagnostics to help identify and resolve issues.

## Diagnostic Files

When failures occur, diagnostic information is saved to the `location/` directory:

> **⚠️ Privacy Note:** Diagnostic files contain your location query and are automatically excluded from git commits via `.gitignore`. Do not share these files publicly if your location information is sensitive.

### `location/debug_nominatim.json`
Contains the raw JSON response from the Nominatim geocoding API. This helps identify:
- Invalid JSON responses
- Empty responses (rate limiting)
- Unexpected response structure

### `location/debug_nominatim_response.txt`
Contains detailed request/response information including:
- The full URL requested
- Location query string
- HTTP status code
- Curl exit code
- Response headers
- Response body

### `location/debug_map_response.txt`
Contains information about the static map download:
- Map service URL
- HTTP status code
- Curl exit code
- Response headers
- File size of downloaded image

## Common Failure Scenarios

### 1. Nominatim Rate Limiting

**Symptoms:**
```
❌ FAILURE: Nominatim API returned error (HTTP Code: 429)
   → Rate limiting detected
   → Nominatim has strict rate limits (1 request per second)
   → Wait at least 1 hour before retrying or use caching
```

**Cause:** Nominatim enforces a strict rate limit of 1 request per second and blocks IPs that make excessive requests.

**Solutions:**
- Use the built-in caching mechanism (responses are cached for 7 days)
- Wait at least 1 hour before retrying
- Consider using a commercial geocoding service for production use
- Review Nominatim usage policy: https://operations.osmfoundation.org/policies/nominatim/

**Check diagnostics:**
```bash
cat location/debug_nominatim_response.txt
# Look for HTTP Code: 429 or 403
```

### 2. Nominatim Invalid JSON

**Symptoms:**
```
❌ FAILURE: Nominatim returned invalid JSON
   → Response is not valid JSON format
   → See location/debug_nominatim.json for raw response
```

**Cause:** Nominatim returned an error page or rate limit message instead of JSON.

**Solutions:**
- Check `location/debug_nominatim.json` for the actual response
- If it contains HTML, you're likely rate-limited or blocked
- Wait before retrying

### 3. Nominatim No Results

**Symptoms:**
```
❌ FAILURE: Nominatim returned no results for location: XYZ
   → The location string may be too vague or invalid
   → Try a more specific location (e.g., 'New York, NY, USA' instead of 'NYC')
```

**Cause:** The location string in your GitHub profile is not recognized by Nominatim.

**Solutions:**
- Update your GitHub profile location to be more specific
- Use a format like "City, State, Country" (e.g., "San Francisco, CA, USA")
- Avoid abbreviations or informal names

### 4. Map Download Failure

**Symptoms:**
```
❌ FAILURE: Map retrieval failed (HTTP Code: 403)
   → Authentication required or access forbidden
   → Map service may require API key or token
```

**Cause:** The static map service returned an error.

**Solutions:**
- Check `location/debug_map_response.txt` for details
- If HTTP 429: Rate limit exceeded, wait before retrying
- If HTTP 403/401: Service may now require authentication
- If HTTP 404: Service endpoint may have changed
- Consider using an alternative map service

### 5. Map Image Not Found

**Symptoms:**
```
❌ FAILURE: Map image not found: location/location-map.png
   → The map download may have failed
   → Check debug_map_response.txt in the location directory
```

**Cause:** The map download step failed before card generation.

**Solutions:**
- Check `location/debug_map_response.txt` for the HTTP error code
- Review the error messages from the map download step
- Verify network connectivity

### 6. Invalid Metadata

**Symptoms:**
```
❌ FAILURE: Cannot read location metadata
   → Invalid JSON in Metadata file: ...
```

**Cause:** The `location.json` file is corrupted or contains invalid JSON.

**Solutions:**
- Delete `location/location.json` to force regeneration
- Check for partial file writes
- Verify disk space is available

### 7. Map Embedding Failure

**Symptoms:**
```
❌ FAILURE: SVG does not contain embedded map image
   → The map image failed to embed in the SVG
```

**Cause:** The map image file is corrupted or in an unsupported format.

**Solutions:**
- Verify the map image is a valid PNG file
- Check `location/location-map.png` file size (should be > 0 bytes)
- Regenerate the map by deleting the existing file

## Diagnostic Output Format

All error messages follow this format:

```
❌ FAILURE: <Brief description of what failed>
   → <Specific cause or symptom>
   → <Actionable step to resolve>
   → <Additional context or documentation link>
```

Success messages use this format:

```
✅ <What succeeded>
   → <Additional diagnostic info>
```

## Workflow Integration

The GitHub Actions workflow automatically runs these checks and will:

1. Continue with fallback SVG card if one exists
2. Skip card generation if no fallback exists
3. Display actionable error messages in workflow logs

To view diagnostics in GitHub Actions:

1. Go to the workflow run
2. Check the "Fetch location data and static map" step
3. Look for ❌ FAILURE messages
4. Download artifacts to see `debug_*.json` and `debug_*.txt` files

## Testing Diagnostics

Run the diagnostic tests locally:

```bash
# Python tests for card generation
python -m pytest tests/test_location_diagnostics.py -v

# Shell tests for location fetching
bash tests/test_location_shell_diagnostics.sh
```

## Caching Behavior

The system uses multiple layers of caching to reduce API calls:

1. **Nominatim cache**: Geocoding results cached for 7 days in `cache/nominatim_*.json`
2. **Location fallback**: Last successful GitHub location cached in `cached/location.json`
3. **SVG fallback**: Last successful card preserved if new generation fails

Caches are automatically cleaned up after their TTL expires.

## Best Practices

1. **Set a specific location** in your GitHub profile (e.g., "San Francisco, CA, USA")
2. **Monitor workflow runs** for rate limiting warnings
3. **Don't delete cache files** unless troubleshooting specific issues
4. **Review diagnostic files** when workflow fails
5. **Wait 1 hour** between manual workflow triggers to avoid rate limits

## Troubleshooting Checklist

If the location card is not rendering:

- [ ] Check if location is set in GitHub profile
- [ ] Review workflow logs for ❌ FAILURE messages
- [ ] Check `location/debug_nominatim.json` for API response
- [ ] Check `location/debug_map_response.txt` for map download status
- [ ] Verify `location/location-map.png` exists and is > 0 bytes
- [ ] Check if rate limit messages appear in logs
- [ ] Verify `location/location-card.svg` was generated
- [ ] Confirm README.md includes the location card marker

## Getting Help

If diagnostics don't clearly identify the issue:

1. Enable workflow debugging: Set `ACTIONS_STEP_DEBUG` secret to `true`
2. Download workflow artifacts with diagnostic files
3. Share diagnostic files and workflow logs when reporting issues
4. Include the specific error messages from stderr logs

## Related Documentation

- [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)
- [OpenStreetMap Static Maps](https://staticmap.openstreetmap.de/)
- [GitHub Actions Workflow Debugging](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/enabling-debug-logging)
