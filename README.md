#
<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 🎯 HERO SECTION                                                            -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

<!-- markdownlint-disable MD033 -->
<div align="center">

<!-- Branded Header Banner -->
<img src="branding/header.svg" alt="Alan Szmyt - Software Engineer • DevOps & Cloud • AI-Assisted Systems" width="100%"/>

<br/><br/>

<!-- Badges Row -->
[![GitHub followers](https://img.shields.io/github/followers/szmyty?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=4a4e69)](https://github.com/szmyty?tab=followers)
![Profile Views](https://komarev.com/ghpvc/?username=szmyty&style=for-the-badge&color=4a4e69&labelColor=1a1a2e)
[![GitHub Stars](https://img.shields.io/github/stars/szmyty?style=for-the-badge&logo=github&logoColor=white&labelColor=1a1a2e&color=4a4e69)](https://github.com/szmyty?tab=repositories)
[![CI](https://img.shields.io/github/actions/workflow/status/szmyty/szmyty/metrics.yml?style=for-the-badge&logo=github-actions&logoColor=white&labelColor=1a1a2e&color=4a4e69&label=CI)](https://github.com/szmyty/szmyty/actions)

</div>

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 👤 ABOUT ME                                                                 -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

<div align="center">

## 👤 About Me

</div>

<p align="center" width="90%">
🚀 Software engineer focusing on cloud-native systems, developer experience, creative automation, and AI-assisted tooling.  
I build high-quality, scalable platforms with strong emphasis on automation, security, and clarity.
</p>

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 💡 DEVELOPER EXPERIENCE                                                      -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

<div align="center">

## 💡 Developer Experience

</div>

<div align="center">

### 🎯 DX Philosophy

⚡ Automate the mundane • 🔄 Fast feedback loops  
📚 Self-documenting code • 🧩 Composable architectures

</div>

<br/>

<div align="center">

### 🏛️ Engineering Pillars

🔒 Secure by default • 📈 Scalable by design  
🧪 Test-driven quality • 🔧 Continuous improvement

</div>

<br/>

<div align="center">

### 🚀 What I Build

🛠 Developer tooling & CLIs • ☁ Cloud-native platforms  
🤖 AI-augmented workflows • 🔁 CI/CD & automation systems

</div>

<br/>

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 📊 DYNAMIC DASHBOARD CARDS                                                 -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

<div align="center">

![Weather](https://github.com/szmyty/profile/actions/workflows/weather.yml/badge.svg)
![Location](https://github.com/szmyty/profile/actions/workflows/location-card.yml/badge.svg)
![SoundCloud](https://github.com/szmyty/profile/actions/workflows/soundcloud-card.yml/badge.svg)
![Oura](https://github.com/szmyty/profile/actions/workflows/oura.yml/badge.svg)
![Developer](https://github.com/szmyty/profile/actions/workflows/developer.yml/badge.svg)

</div>

<br/>

<div align="center">

## 💻 Developer Dashboard

</div>

<p align="center">
<!-- DEVELOPER-DASHBOARD:START -->
![Developer Dashboard](./developer/developer_dashboard.svg)
<!-- DEVELOPER-DASHBOARD:END -->
</p>

<br/>

<div align="center">

## 📍 My Location

</div>

<p align="center">
<!-- LOCATION-CARD:START -->
![My Location](./location/location-card.svg)
<!-- LOCATION-CARD:END -->
</p>

<br/>

<div align="center">

## 🌦️ Today's Weather

</div>

<p align="center">
<!-- WEATHER-CARD:START -->
![Today's Weather](./weather/weather-today.svg)
<!-- WEATHER-CARD:END -->
</p>

<br/>

<div align="center">

## 🎵 Latest SoundCloud Release

</div>

<p align="center">
<!-- SOUNDCLOUD-CARD:START -->
[![SoundCloud Latest Track](assets/soundcloud-card.svg)](https://soundcloud.com/playfunction/prescience_v2)
<!-- SOUNDCLOUD-CARD:END -->
</p>

<br/>

<div align="center">

## 🧬 Oura Health Dashboard

</div>

<p align="center">
<!-- OURA-HEALTH-CARD:START -->
![Oura Health Dashboard](./oura/health_dashboard.svg)
<!-- OURA-HEALTH-CARD:END -->
</p>

<br/>

<div align="center">

## 💫 Oura Mood Dashboard

</div>

<p align="center">
<!-- OURA-MOOD-CARD:START -->
![Oura Mood Dashboard](./oura/mood_dashboard.svg)
<!-- OURA-MOOD-CARD:END -->
</p>

<br/>

---

<br/>

<div align="center">

## 📊 System Status

</div>

<p align="center">
<!-- STATUS-PAGE:START -->
![System Status](./data/status/status-page.svg)
<!-- STATUS-PAGE:END -->
</p>

<p align="center">
<a href="docs/MONITORING.md">📖 View detailed monitoring documentation</a>
</p>

<br/>

---

<br/>

<div align="center">

## ⚡ Performance Optimizations

</div>

This repository implements several performance optimizations to improve speed and reduce GitHub Actions usage:

- **🔄 Parallel API Fetching** - Fetch Oura, Weather, and SoundCloud data simultaneously (3x faster)
- **📊 Incremental SVG Generation** - Skip regeneration when data hasn't changed (50-80% time savings)
- **📦 Python Dependency Caching** - Reuse installed packages with Poetry lock file (6x faster setup)
- **🎨 Enhanced SVG Optimization** - Advanced compression with path simplification (30-50% smaller files)
- **💾 Multi-Level Caching** - Cache API responses, client IDs, and geocoding results

**Results**: 60-75% faster workflows, 60-70% lower GitHub Actions usage

<p align="center">
📖 <a href="docs/OPTIMIZATION_GUIDE.md">View Optimization Guide</a>
</p>

<br/>

---

<br/>

<div align="center">

## 🔍 Monitoring & Observability

</div>

This repository includes comprehensive monitoring features:

- **📈 Workflow Metrics** - Track run times, success/failure rates, and API call counts
- **🎯 Status Dashboard** - Visual display of system health and recent updates
- **🚨 Automated Alerts** - Automatic issue creation for repeated failures (3+ consecutive)
- **✅ Data Quality Checks** - Detection of missing fields, NaN values, and out-of-range metrics

<p align="center">
📖 <a href="docs/MONITORING.md">View Monitoring Guide</a>
</p>

<br/>

---

<br/>

<div align="center">

## 📜 Logs

</div>

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

<br/>

---

<br/>

<div align="center">

## 🛠️ Development

</div>

### Quick Start

<details>
<summary><b>🚀 Using GitHub Codespaces (Recommended)</b></summary>

<br/>

1. Click "Code" → "Create codespace on main"
2. Wait for the environment to set up automatically
3. Start developing!

</details>

<details>
<summary><b>💻 Local Development</b></summary>

<br/>

```bash
# Install dependencies with Poetry (recommended)
pip install poetry
poetry install

# Or use pip with requirements.txt (alternative)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
poetry run pre-commit install  # if using Poetry
# or
pre-commit install              # if using pip

# Generate cards with mock data (no API keys needed)
./scripts/dev-mode.sh all
```

</details>

<br/>

<details>
<summary><b>📋 Code Conventions</b></summary>

<br/>

**Script Naming**: All Python scripts use dash-case naming (e.g., `generate-card.py`, `update-readme.py`).

**Script Permissions**: Python scripts that are directly executed by workflows are marked as executable. Library modules in `scripts/lib/` are not executable.

**Dependencies**: Install required Python packages with Poetry (recommended) or pip:

```bash
# Using Poetry (pinned dependencies in poetry.lock for reproducibility)
pip install poetry
poetry install

# Or using pip (alternative)
pip install -r requirements.txt        # Core dependencies
pip install -r requirements-dev.txt    # Development tools
```

All dependencies are pinned to exact versions in `pyproject.toml` and `poetry.lock` to ensure reproducible builds and prevent breakage from upstream changes.

**Theme Configuration**: All visual styling (colors, fonts, spacing, dimensions) is centralized in `config/theme.json`.

**Pre-commit Hooks**: Run `pre-commit run --all-files` before committing to validate:

- JSON schemas
- SVG formatting
- Python linting (black, flake8, isort)
- Shell script validation (shellcheck)
- File permissions

</details>

<br/>

<details>
<summary><b>🧪 Development Mode</b></summary>

<br/>

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

</details>

<br/>

<details>
<summary><b>📚 Documentation</b></summary>

<br/>

- **[Monitoring Guide](docs/MONITORING.md)**: Monitoring, observability, and alerting features
- **[Optimization Guide](docs/OPTIMIZATION_GUIDE.md)**: Performance optimizations and caching strategies
- **[Workflows](docs/WORKFLOWS.md)**: Complete guide to GitHub Actions workflows and their dependencies
- **[Mock Data](data/mock/README.md)**: Information about development mode and mock data

</details>

<details>
<summary><b>🧪 Testing</b></summary>

<br/>

Run the test suite:

```bash
python -m pytest tests/ -v
```

</details>

<br/>

---

<br/>

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 📫 FOOTER - Open Source Community & Contact                               -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

<div align="center">

<img src="branding/footer.svg" alt="Footer" width="100%"/>

<br/><br/>

## 🤝 Open Source Community

Supporting and contributing to open-source initiatives

<br/>

[![Open Collective](https://img.shields.io/badge/Open%20Collective-Supporter-7fadf2?style=for-the-badge&logo=opencollective&logoColor=white)](https://opencollective.com)
[![Linux Foundation](https://img.shields.io/badge/Linux%20Foundation-Member-003366?style=for-the-badge&logo=linux&logoColor=white)](https://www.linuxfoundation.org/)
[![CNCF](https://img.shields.io/badge/CNCF-Cloud%20Native-436fb5?style=for-the-badge&logo=cncf&logoColor=white)](https://www.cncf.io/)

<br/>

[![Mozilla](https://img.shields.io/badge/Mozilla-Contributor-000000?style=for-the-badge&logo=mozilla&logoColor=white)](https://www.mozilla.org/)
[![FSF](https://img.shields.io/badge/FSF-Free%20Software-0d47a1?style=for-the-badge&logo=gnu&logoColor=white)](https://www.fsf.org/)
[![Creative Commons](https://img.shields.io/badge/Creative%20Commons-Supporter-ef9421?style=for-the-badge&logo=creativecommons&logoColor=white)](https://creativecommons.org/)

<br/>

[![EFF](https://img.shields.io/badge/EFF-Digital%20Rights-d32027?style=for-the-badge&logo=eff&logoColor=white)](https://www.eff.org/)
[![Apache](https://img.shields.io/badge/Apache-Foundation-d22128?style=for-the-badge&logo=apache&logoColor=white)](https://www.apache.org/)
[![Open Source Initiative](https://img.shields.io/badge/OSI-Open%20Source-3da639?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](https://opensource.org/)

<br/><br/>

---

<br/>

## 📬 Get In Touch

[![GitHub](https://img.shields.io/badge/GitHub-szmyty-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/szmyty)
[![Email](https://img.shields.io/badge/Email-Contact-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:szmyty@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/szmyty)

<br/>

### *Built with ❤️ and open-source tools*

<br/>

![Powered by GitHub Actions](https://img.shields.io/badge/Powered%20by-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)
![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Automated with Poetry](https://img.shields.io/badge/Automated%20with-Poetry-60A5FA?style=flat-square&logo=poetry&logoColor=white)

</div>
