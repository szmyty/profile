#!/usr/bin/env python3
"""
Generate a holistic health dashboard SVG from Oura Ring metrics.
This script reads the health snapshot JSON and creates a comprehensive SVG dashboard
with personal stats, sleep, readiness, activity panels, and optional HR trend chart.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List

from lib.utils import escape_xml, safe_value, load_json, generate_sparkline_path


def format_temp(value: Optional[float]) -> str:
    """Format temperature deviation value."""
    if value is None:
        return "—"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}°C"


def generate_score_ring(value: Optional[int], cx: int, cy: int, radius: int, color: str, label: str) -> str:
    """Generate a circular score indicator."""
    score = value if value is not None else 0
    score = min(100, max(0, score))
    circumference = 2 * 3.14159 * radius
    dash_offset = circumference * (1 - score / 100)
    
    return f"""
    <g transform="translate({cx}, {cy})">
      <circle r="{radius}" fill="none" stroke="#2d3748" stroke-width="4"/>
      <circle r="{radius}" fill="none" stroke="{color}" stroke-width="4"
              stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}"
              stroke-linecap="round" transform="rotate(-90)"/>
      <text y="5" font-family="'Segoe UI', Arial, sans-serif" font-size="14" fill="#ffffff" 
            font-weight="bold" text-anchor="middle">{score}</text>
      <text y="{radius + 14}" font-family="'Segoe UI', Arial, sans-serif" font-size="8" 
            fill="#8892b0" text-anchor="middle">{escape_xml(label)}</text>
    </g>"""


def generate_metric_row(label: str, value: str, x: int, y: int, icon: str = "") -> str:
    """Generate a single metric row."""
    return f"""
    <g transform="translate({x}, {y})">
      <text font-family="'Segoe UI', Arial, sans-serif" font-size="9" fill="#8892b0">
        {icon} {escape_xml(label)}
      </text>
      <text x="100" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#ffffff" 
            text-anchor="end" font-weight="500">{escape_xml(value)}</text>
    </g>"""


def generate_svg(snapshot: dict) -> str:
    """Generate the holistic health dashboard SVG."""
    
    # Extract data sections
    personal = snapshot.get("personal", {})
    sleep = snapshot.get("sleep", {})
    readiness = snapshot.get("readiness", {})
    activity = snapshot.get("activity", {})
    heart_rate = snapshot.get("heart_rate", {})
    updated_at = snapshot.get("updated_at", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    
    # Personal stats
    age = personal.get("age")
    height_cm = personal.get("height_cm")
    weight_kg = personal.get("weight_kg")
    weight_lbs = personal.get("weight_lbs")
    bmi = personal.get("bmi")
    sex = personal.get("sex")
    
    # Scores
    sleep_score = sleep.get("score")
    readiness_score = readiness.get("score")
    activity_score = activity.get("score")
    
    # Sleep metrics
    deep_sleep = sleep.get("deep_sleep")
    rem_sleep = sleep.get("rem_sleep")
    total_sleep = sleep.get("total_sleep")
    efficiency = sleep.get("efficiency")
    
    # Readiness metrics
    recovery_index = readiness.get("recovery_index")
    hrv_balance = readiness.get("hrv_balance")
    temp_deviation = readiness.get("temperature_deviation")
    
    # Activity metrics
    steps = activity.get("steps")
    total_calories = activity.get("total_calories")
    active_calories = activity.get("active_calories")
    inactivity_alerts = activity.get("inactivity_alerts")
    avg_met = activity.get("average_met_minutes")
    
    # Heart rate - use heart_rate.resting_bpm as primary, fallback to readiness
    latest_bpm = heart_rate.get("latest_bpm")
    hr_trend = heart_rate.get("trend_values", [])
    resting_hr = heart_rate.get("resting_bpm") or readiness.get("resting_heart_rate")
    
    # Generate sparkline for HR trend
    sparkline_path = generate_sparkline_path(hr_trend, 90, 22)
    
    # Generate score rings
    sleep_ring = generate_score_ring(sleep_score, 55, 45, 30, "#4facfe", "Sleep")
    readiness_ring = generate_score_ring(readiness_score, 135, 45, 30, "#38ef7d", "Ready")
    activity_ring = generate_score_ring(activity_score, 215, 45, 30, "#f5576c", "Active")
    
    # Format weight display
    weight_display = "—"
    if weight_kg is not None:
        weight_display = f"{weight_kg}kg"
        if weight_lbs is not None:
            weight_display += f" ({weight_lbs}lb)"
    
    # Format height display
    height_display = safe_value(height_cm, suffix="cm") if height_cm else "—"
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="500" height="380" viewBox="0 0 500 380">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f0f23"/>
      <stop offset="100%" style="stop-color:#1a1a2e"/>
    </linearGradient>
    <linearGradient id="sleep-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#667eea"/>
      <stop offset="100%" style="stop-color:#764ba2"/>
    </linearGradient>
    <linearGradient id="readiness-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#11998e"/>
      <stop offset="100%" style="stop-color:#38ef7d"/>
    </linearGradient>
    <linearGradient id="activity-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#f093fb"/>
      <stop offset="100%" style="stop-color:#f5576c"/>
    </linearGradient>
    <linearGradient id="hr-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ff6b6b"/>
      <stop offset="100%" style="stop-color:#feca57"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="500" height="380" rx="12" fill="url(#bg-gradient)"/>
  <rect width="500" height="380" rx="12" fill="none" stroke="#64ffda" stroke-width="1" stroke-opacity="0.3"/>

  <!-- Header -->
  <g transform="translate(20, 20)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="14" fill="#64ffda" font-weight="600">
      🧬 OURA HEALTH DASHBOARD
    </text>
  </g>

  <!-- Score Rings Row -->
  <g transform="translate(20, 45)">
    {sleep_ring}
    {readiness_ring}
    {activity_ring}
  </g>

  <!-- Personal Stats Panel (grey/white) -->
  <g transform="translate(280, 45)">
    <rect width="200" height="75" rx="6" fill="#1e1e2e" stroke="#4a5568" stroke-width="1"/>
    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#64ffda" font-weight="600">
      👤 Personal Stats
    </text>
    {generate_metric_row("Age", safe_value(age, suffix=" yrs") if age else "—", 10, 35)}
    {generate_metric_row("Height", height_display, 10, 50)}
    {generate_metric_row("Weight", weight_display, 10, 65)}
    <text x="180" y="65" font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
      BMI: {safe_value(bmi)}
    </text>
  </g>

  <!-- Sleep Panel (blue/purple) -->
  <g transform="translate(20, 130)">
    <rect width="145" height="105" rx="6" fill="#1a1a3e" stroke="#667eea" stroke-width="1" stroke-opacity="0.5"/>
    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#4facfe" font-weight="600">
      😴 Sleep
    </text>
    {generate_metric_row("Deep Sleep", safe_value(deep_sleep), 10, 35)}
    {generate_metric_row("REM Sleep", safe_value(rem_sleep), 10, 50)}
    {generate_metric_row("Total Sleep", safe_value(total_sleep), 10, 65)}
    {generate_metric_row("Efficiency", safe_value(efficiency, suffix="%") if efficiency else "—", 10, 80)}
    {generate_metric_row("Timing", safe_value(sleep.get("timing")), 10, 95)}
  </g>

  <!-- Readiness Panel (teal/green) -->
  <g transform="translate(175, 130)">
    <rect width="145" height="105" rx="6" fill="#1a2e2e" stroke="#38ef7d" stroke-width="1" stroke-opacity="0.5"/>
    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#38ef7d" font-weight="600">
      💪 Readiness
    </text>
    {generate_metric_row("Recovery", safe_value(recovery_index), 10, 35)}
    {generate_metric_row("HRV Balance", safe_value(hrv_balance), 10, 50)}
    {generate_metric_row("Resting HR", safe_value(resting_hr), 10, 65)}
    {generate_metric_row("Temp Dev", format_temp(temp_deviation), 10, 80)}
    {generate_metric_row("Sleep Bal", safe_value(readiness.get("sleep_balance")), 10, 95)}
  </g>

  <!-- Activity Panel (orange/yellow) -->
  <g transform="translate(330, 130)">
    <rect width="150" height="105" rx="6" fill="#2e2a1a" stroke="#f5576c" stroke-width="1" stroke-opacity="0.5"/>
    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#f5576c" font-weight="600">
      🏃 Activity
    </text>
    {generate_metric_row("Steps", safe_value(steps, default="0"), 10, 35)}
    {generate_metric_row("Total Cal", safe_value(total_calories, suffix=" kcal") if total_calories else "—", 10, 50)}
    {generate_metric_row("Active Cal", safe_value(active_calories, suffix=" kcal") if active_calories else "—", 10, 65)}
    {generate_metric_row("Inact Alerts", safe_value(inactivity_alerts, default="0"), 10, 80)}
    {generate_metric_row("Avg MET", f"{avg_met:.2f}" if avg_met is not None else "—", 10, 95)}
  </g>

  <!-- Heart Rate Mini Chart -->
  <g transform="translate(20, 245)">
    <rect width="225" height="70" rx="6" fill="#1e1e2e" stroke="#ff6b6b" stroke-width="1" stroke-opacity="0.3"/>
    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#ff6b6b" font-weight="600">
      ❤️ Heart Rate Trend
    </text>
    <text x="200" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="12" fill="#ffffff" font-weight="bold" text-anchor="end">
      {safe_value(latest_bpm, suffix=" bpm") if latest_bpm else "— bpm"}
    </text>
    <g transform="translate(10, 38)">
      <rect width="100" height="25" rx="3" fill="#0f0f23"/>
      <g transform="translate(5, 1)">
        <path d="{sparkline_path}" fill="none" stroke="url(#hr-gradient)" stroke-width="1.5" stroke-linecap="round"/>
      </g>
    </g>
    <g transform="translate(120, 35)">
      <text font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        Latest: {safe_value(latest_bpm, default="—")} bpm
      </text>
      <text y="14" font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        Resting: {safe_value(resting_hr, default="—")}
      </text>
      <text y="28" font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        HRV: {safe_value(hrv_balance, default="—")}
      </text>
    </g>
  </g>

  <!-- Additional Metrics Panel -->
  <g transform="translate(255, 245)">
    <rect width="225" height="70" rx="6" fill="#1e1e2e" stroke="#64ffda" stroke-width="1" stroke-opacity="0.3"/>
    <text x="10" y="18" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#64ffda" font-weight="600">
      📊 Contributors
    </text>
    <g transform="translate(10, 32)">
      <text font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        Training Freq: {safe_value(activity.get("training_frequency"))}
      </text>
      <text y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        Recovery Time: {safe_value(activity.get("recovery_time"))}
      </text>
      <text y="24" font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        Previous Night: {safe_value(readiness.get("previous_night"))}
      </text>
    </g>
    <g transform="translate(120, 32)">
      <text font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        Move/Hour: {safe_value(activity.get("move_every_hour"))}
      </text>
      <text y="12" font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        Stay Active: {safe_value(activity.get("stay_active"))}
      </text>
      <text y="24" font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#8892b0">
        Activity Bal: {safe_value(readiness.get("activity_balance"))}
      </text>
    </g>
  </g>

  <!-- Footer: Updated timestamp -->
  <g transform="translate(20, 340)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#4a5568">
      Updated: {escape_xml(str(updated_at))}
    </text>
  </g>

  <!-- Sex indicator if available -->
  <g transform="translate(465, 340)">
    <text font-family="'Segoe UI', Arial, sans-serif" font-size="8" fill="#4a5568" text-anchor="end">
      {escape_xml(sex) if sex else ""}
    </text>
  </g>

  <!-- Decorative accent -->
  <rect x="484" y="15" width="4" height="350" rx="2" fill="#64ffda" fill-opacity="0.3"/>
</svg>"""

    return svg


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: generate-health-dashboard.py <health_snapshot.json> [output_path]",
            file=sys.stderr,
        )
        sys.exit(1)

    snapshot_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "oura/health_dashboard.svg"

    # Read health snapshot
    snapshot = load_json(snapshot_path, "Health snapshot file")

    # Generate SVG
    svg = generate_svg(snapshot)

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        f.write(svg)

    print(f"Generated Oura health dashboard SVG: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
