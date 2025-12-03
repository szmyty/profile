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

- **[Workflows](docs/WORKFLOWS.md)**: Complete guide to GitHub Actions workflows and their dependencies
- **[Mock Data](data/mock/README.md)**: Information about development mode and mock data

### Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```