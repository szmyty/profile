# profile

![Weather](https://github.com/szmyty/profile/actions/workflows/weather.yml/badge.svg)
![Location](https://github.com/szmyty/profile/actions/workflows/location-card.yml/badge.svg)
![SoundCloud](https://github.com/szmyty/profile/actions/workflows/soundcloud-card.yml/badge.svg)
![Oura](https://github.com/szmyty/profile/actions/workflows/oura.yml/badge.svg)
![Developer](https://github.com/szmyty/profile/actions/workflows/developer.yml/badge.svg)

## 💻 Developer Dashboard

<!-- DEVELOPER-DASHBOARD:START -->
![Developer Dashboard](./developer/developer_dashboard.svg)
<!-- DEVELOPER-DASHBOARD:END -->

## 📍 My Location

<!-- LOCATION-CARD:START -->
![My Location](./location/location-card.svg)
<!-- LOCATION-CARD:END -->

## 🌦️ Today's Weather

<!-- WEATHER-CARD:START -->
![Today's Weather](./weather/weather-today.svg)
<!-- WEATHER-CARD:END -->

## 🎵 Latest SoundCloud Release

<!-- SOUNDCLOUD-CARD:START -->
[![SoundCloud Latest Track](assets/soundcloud-card.svg)](https://soundcloud.com/playfunction/prescience_v2)
<!-- SOUNDCLOUD-CARD:END -->

## 🧬 Oura Health Dashboard

<!-- OURA-HEALTH-CARD:START -->
![Oura Health Dashboard](./oura/health_dashboard.svg)
<!-- OURA-HEALTH-CARD:END -->

## 💫 Oura Mood Dashboard

<!-- OURA-MOOD-CARD:START -->
![Oura Mood Dashboard](./oura/mood_dashboard.svg)
<!-- OURA-MOOD-CARD:END -->

---

## 📊 System Status

<!-- STATUS-PAGE:START -->
![System Status](./data/status/status-page.svg)
<!-- STATUS-PAGE:END -->

[View detailed monitoring documentation](docs/MONITORING.md)

---

## ⚡ Performance Optimizations

This repository implements several performance optimizations to improve speed and reduce GitHub Actions usage:

- **🔄 Parallel API Fetching** - Fetch Oura, Weather, and SoundCloud data simultaneously (3x faster)
- **📊 Incremental SVG Generation** - Skip regeneration when data hasn't changed (50-80% time savings)
- **📦 Python Dependency Caching** - Reuse installed packages between runs (6x faster setup)
- **🎨 Enhanced SVG Optimization** - Advanced compression with path simplification (30-50% smaller files)
- **💾 Multi-Level Caching** - Cache API responses, client IDs, and geocoding results

**Results**: 60-75% faster workflows, 60-70% lower GitHub Actions usage

See [OPTIMIZATION_GUIDE.md](docs/OPTIMIZATION_GUIDE.md) for detailed documentation.

---

## 🔍 Monitoring & Observability

This repository includes comprehensive monitoring features:

- **📈 Workflow Metrics** - Track run times, success/failure rates, and API call counts
- **🎯 Status Dashboard** - Visual display of system health and recent updates
- **🚨 Automated Alerts** - Automatic issue creation for repeated failures (3+ consecutive)
- **✅ Data Quality Checks** - Detection of missing fields, NaN values, and out-of-range metrics

See [MONITORING.md](docs/MONITORING.md) for detailed documentation.

---

## 📜 Logs

All workflow logs are stored in the `logs/` directory with automatic rotation to prevent excessive file growth.

- **`logs/location/`** - Location card workflow logs
- **`logs/weather/`** - Weather card workflow logs
- **`logs/oura/`** - Oura health workflow logs
- **`logs/developer/`** - Developer dashboard workflow logs
- **`logs/soundcloud/`** - SoundCloud card workflow logs
- **`logs/avatar/`** - Avatar workflow logs (if applicable)
- **`logs/ai/`** - AI workflow logs (if applicable)

### Log Features

- **Persistent Logging**: All logs are committed on every workflow run, even if the workflow fails
- **Automatic Rotation**: Logs automatically rotate when they exceed 5MB
- **Timestamped Entries**: Each log entry includes UTC timestamps and severity levels (INFO, WARN, ERROR)
- **Command Tracking**: All API calls, script executions, and their exit codes are logged
- **Troubleshooting**: Use logs to debug workflow failures and track historical execution

---

## 🛠️ Development

### Quick Start

#### Using GitHub Codespaces (Recommended)
1. Click "Code" → "Create codespace on main"
2. Wait for the environment to set up automatically
3. Start developing!

#### Local Development
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Generate cards with mock data (no API keys needed)
./scripts/dev-mode.sh all
```

### Code Conventions

**Script Naming**: All Python scripts use dash-case naming (e.g., `generate-card.py`, `update-readme.py`).

**Script Permissions**: Python scripts that are directly executed by workflows are marked as executable. Library modules in `scripts/lib/` are not executable.

**Dependencies**: Install required Python packages with:
```bash
pip install -r requirements.txt        # Core dependencies
pip install -r requirements-dev.txt    # Development tools
```

**Theme Configuration**: All visual styling (colors, fonts, spacing, dimensions) is centralized in `config/theme.json`.

**Pre-commit Hooks**: Run `pre-commit run --all-files` before committing to validate:
- JSON schemas
- SVG formatting
- Python linting (black, flake8, isort)
- Shell script validation (shellcheck)
- File permissions

### Development Mode

Test card generation locally without API keys using mock data:

```bash
# Generate all cards
./scripts/dev-mode.sh all

# Generate specific cards
./scripts/dev-mode.sh soundcloud
./scripts/dev-mode.sh weather
./scripts/dev-mode.sh developer
./scripts/dev-mode.sh oura
```

Output is saved to `dev-output/` directory. See [`data/mock/README.md`](data/mock/README.md) for details on mock data.

### Documentation

- **[Monitoring Guide](docs/MONITORING.md)**: Monitoring, observability, and alerting features
- **[Optimization Guide](docs/OPTIMIZATION_GUIDE.md)**: Performance optimizations and caching strategies
- **[Workflows](docs/WORKFLOWS.md)**: Complete guide to GitHub Actions workflows and their dependencies
- **[Mock Data](data/mock/README.md)**: Information about development mode and mock data

### Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```