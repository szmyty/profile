# Archived Workflows

This directory contains workflows that have been consolidated into the unified `build-profile.yml` workflow.

## Consolidation Date
December 5, 2024

## Archived Workflows

### Core Data Fetching & Card Generation
- **developer.yml** - Developer Dashboard — GitHub Metrics + Visualization
- **soundcloud-card.yml** - SoundCloud Latest Release Card
- **weather.yml** - Weather Card — Daily Conditions + Forecast
- **location-card.yml** - Location Map Card — Mapbox Static Map with Day/Night Theme
- **oura.yml** - Oura Health Dashboard — Full Metrics + Unified Snapshot
- **parallel-fetch.yml** - Parallel Data Fetch & Card Generation

### Infrastructure & CI/CD
- **megalinter.yml** - MegaLinter Diagnostic (Report-Only)
- **deploy-dashboard.yml** - Deploy Dashboard to GitHub Pages

## Unified Workflow

All functionality from these workflows has been consolidated into:

**`.github/workflows/build-profile.yml`** - Build Profile — Unified Orchestration Pipeline

This unified workflow:
- Fetches all data sources (Developer, Weather, Location, SoundCloud, Oura)
- Validates all JSON data
- Generates all SVG cards with fallback handling
- Updates README with all cards
- Builds and deploys the React dashboard
- Runs MegaLinter in report-only mode
- Commits and pushes all changes atomically
- Never fails due to partial errors (uses continue-on-error strategy)

## Why Consolidate?

1. **Reduced Complexity** - One workflow to maintain instead of 8+
2. **Better Orchestration** - Sequential phases with proper dependencies
3. **Atomic Updates** - All cards updated in a single commit
4. **Error Resilience** - Continues on partial failures with fallbacks
5. **Easier Debugging** - All logs in one place
6. **Resource Efficiency** - Single environment setup for all operations

## Restoration

If you need to restore any of these workflows, they are preserved here and can be copied back to the parent directory. However, the unified workflow is recommended for production use.
