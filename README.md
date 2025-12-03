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

### Code Conventions

**Script Naming**: All Python scripts use dash-case naming (e.g., `generate-card.py`, `update-readme.py`).

**Script Permissions**: Python scripts that are directly executed by workflows are marked as executable. Library modules in `scripts/lib/` are not executable.

**Dependencies**: Install required Python packages with:
```bash
pip install -r requirements.txt
```

**Theme Configuration**: All visual styling (colors, fonts, spacing, dimensions) is centralized in `config/theme.json`.