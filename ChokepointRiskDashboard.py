import httpx
import json
from datetime import datetime, UTC
import asyncio

# -----------------------------------------
# Chokepoint coordinates
# -----------------------------------------
CHOKEPOINTS = [
    {"name": "Strait of Hormuz", "lat": 26.625, "lon": 56.250},
    {"name": "Strait of Malacca", "lat": 2.550, "lon": 101.000},
    {"name": "Suez Canal", "lat": 30.585, "lon": 32.265},
    {"name": "Bab el-Mandeb", "lat": 12.640, "lon": 43.330},
    {"name": "Panama Canal", "lat": 9.101, "lon": -79.700},
    {"name": "Danish Straits", "lat": 55.670, "lon": 12.590}
]

# -----------------------------------------
# Save JSON to file
# -----------------------------------------
def save_json_to_file(data, filename_prefix="chokepoints"):
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved JSON to {filename}")

# -----------------------------------------
# Operational impact assessment
# -----------------------------------------
def assess_operational_impact(cp):
    r = cp["risk"]
    wind = r["factors"]["wind"]
    vis = r["factors"]["visibility"]
    precip = r["factors"]["precipitation"]
    level = r["level"]

    impacts = []

    # Wind impacts
    if wind >= 30:
        impacts.append("High winds may affect vessel maneuverability and transit safety.")
    elif wind >= 15:
        impacts.append("Elevated winds could require increased caution during transits.")

    # Visibility impacts
    if vis >= 10:
        impacts.append("Reduced visibility may slow traffic and increase collision risk.")
    elif vis >= 5:
        impacts.append("Visibility degradation may require speed reductions and tighter traffic control.")

    # Precipitation impacts
    if precip >= 10:
        impacts.append("Heavy precipitation may degrade sensor performance and complicate navigation.")
    elif precip >= 5:
        impacts.append("Precipitation may reduce situational awareness and increase workload on bridge teams.")

    if not impacts:
        if level == "low":
            return "No significant weather-driven operational impacts are expected at this chokepoint."
        else:
            return "Weather conditions may require routine caution but are not assessed as significantly disruptive."

    return " ".join(impacts)

# -----------------------------------------
# Global risk + summary (operational style)
# -----------------------------------------
def compute_global_metrics(chokepoints):
    max_score = -1
    highest_cp = None
    counts = {"low": 0, "moderate": 0, "high": 0}

    for cp in chokepoints:
        level = cp["risk"]["level"]
        score = cp["risk"]["score"]
        counts[level] += 1
        if score > max_score:
            max_score = score
            highest_cp = cp

    if max_score < 30:
        global_level = "low"
    elif max_score < 60:
        global_level = "moderate"
    else:
        global_level = "high"

    global_index = max_score

    if global_level == "low":
        posture_line = (
            "Overall chokepoint risk remains low. "
            "Moderate conditions are limited and localized. "
            "No high-risk weather disruptions are expected within the next 24 hours."
        )
    elif global_level == "moderate":
        posture_line = (
            "Global chokepoint risk is elevated to moderate. "
            "Weather-driven constraints may impact operations at select locations. "
            "No widespread high-risk disruptions are currently assessed."
        )
    else:
        posture_line = (
            "Global chokepoint risk is high. "
            "Weather conditions at one or more locations may significantly impact maritime operations "
            "within the next 24 hours."
        )

    if highest_cp:
        highest_line = (
            f"Highest operational risk: {highest_cp['name']} "
            f"(Score {highest_cp['risk']['score']}, {highest_cp['risk']['level']} risk)."
        )
    else:
        highest_line = "No chokepoints currently assessed."

    counts_line = (
        f"Risk distribution: {counts['low']} low, "
        f"{counts['moderate']} moderate, {counts['high']} high."
    )

    return {
        "global_index": global_index,
        "global_level": global_level,
        "posture_line": posture_line,
        "highest_line": highest_line,
        "counts_line": counts_line,
    }

# -----------------------------------------
# Generate HTML dashboard (no JavaScript)
# -----------------------------------------
def generate_html_dashboard(data, filename="dashboard.html"):
    metrics = compute_global_metrics(data["chokepoints"])

    html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Chokepoint Risk Dashboard</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f4f4f4;
      padding: 20px;
    }
    h1 {
      text-align: center;
      margin-bottom: 10px;
    }
    h2 {
      margin-top: 0;
    }
    .summary-block {
      background: #ffffff;
      border-radius: 10px;
      padding: 20px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
      margin-bottom: 25px;
    }
    .summary-title {
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 8px;
    }
    .summary-line {
      margin: 4px 0;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
      gap: 20px;
    }
    .card {
      background: white;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .risk {
      font-weight: bold;
      padding: 6px 10px;
      border-radius: 4px;
      color: white;
      display: inline-block;
      margin-top: 10px;
    }
    summary {
      cursor: pointer;
      font-weight: bold;
      margin-top: 10px;
      color: #333;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 13px;
    }
    th, td {
      padding: 4px 6px;
      border-bottom: 1px solid #ddd;
      text-align: left;
    }
    th {
      background: #eee;
    }
  </style>
</head>
<body>

<h1>Global Maritime Chokepoint Risk Dashboard</h1>

<div class="summary-block">
  <div class="summary-title">Global Maritime Summary</div>
"""

    html += (
        f"  <p class=\"summary-line\"><strong>Global risk index:</strong> "
        f"{metrics['global_index']} ({metrics['global_level'].upper()} risk)</p>\n"
        f"  <p class=\"summary-line\">{metrics['posture_line']}</p>\n"
        f"  <p class=\"summary-line\">{metrics['highest_line']}</p>\n"
        f"  <p class=\"summary-line\">{metrics['counts_line']}</p>\n"
        "</div>\n\n"
        "<div class=\"grid\">\n"
    )

    for cp in data["chokepoints"]:
        summary_line = (
            f"{cp['current']['temperature_c']}°C, "
            f"{cp['current']['wind_kmh']} km/h wind, "
            f"{cp['current']['visibility_m']} m vis, "
            f"{cp['current']['precip_mm']} mm precip"
        )

        impact_text = assess_operational_impact(cp)

        html += (
            "  <div class=\"card\">\n"
            f"    <h2>{cp['name']}</h2>\n\n"
            f"    <p><strong>Summary:</strong> {summary_line}</p>\n\n"
            f"    <p class=\"risk\" style=\"background:{cp['risk']['color']}\">\n"
            f"      {cp['risk']['level'].upper()} (Score: {cp['risk']['score']})\n"
            "    </p>\n\n"
            f"    <p><strong>Transit difficulty index:</strong> "
            f"{cp['risk']['tdi_score']} ({cp['risk']['tdi_category']})</p>\n\n"
            f"    <p><strong>Next 6 hours outlook:</strong> "
            f"{cp['risk']['outlook_6h']}</p>\n\n"
            f"    <p><strong>Dominant driver:</strong> "
            f"{cp['risk']['dominant_driver']}</p>\n\n"
            f"    <p><strong>Operational impact assessment:</strong> {impact_text}</p>\n\n"
        )

        # 24-hour risk strip
        html += "    <div style='display:flex; gap:2px; margin:10px 0;'>\n"
        for level in cp["risk"]["hourly_risk_strip"]:
            color = "#2ECC71" if level == "low" else "#F1C40F" if level == "moderate" else "#E74C3C"
            html += (
                f"      <div style='width:12px; height:12px; background:{color}; "
                "border-radius:2px;'></div>\n"
            )
        html += "    </div>\n"

        html += (
            "    <details>\n"
            "      <summary>24‑Hour Forecast</summary>\n"
            "      <table>\n"
            "        <tr>\n"
            "          <th>Time</th>\n"
            "          <th>Temp</th>\n"
            "          <th>Wind</th>\n"
            "          <th>Vis</th>\n"
            "          <th>Precip</th>\n"
            "        </tr>\n"
        )

        for hour in cp["forecast_24h"]:
            html += (
                "        <tr>\n"
                f"          <td>{hour['time']}</td>\n"
                f"          <td>{hour['temp']}°C</td>\n"
                f"          <td>{hour['wind']} km/h</td>\n"
                f"          <td>{hour['vis']} m</td>\n"
                f"          <td>{hour['precip']} mm</td>\n"
                "        </tr>\n"
            )

        html += (
            "      </table>\n"
            "    </details>\n"
            "  </div>\n"
        )

    html += "</div>\n</body>\n</html>\n"

    with open(filename, "w") as f:
        f.write(html)

    print(f"Saved HTML dashboard to {filename}")

# -----------------------------------------
# Fetch Open-Meteo forecast
# -----------------------------------------
async def fetch_forecast(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,windspeed_10m,visibility,precipitation"
    )
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.json()

# -----------------------------------------
# Extract 24-hour forecast
# -----------------------------------------
def extract_24h(hourly):
    return [
        {
            "time": hourly["time"][i],
            "temp": hourly["temperature_2m"][i],
            "wind": hourly["windspeed_10m"][i],
            "vis": hourly["visibility"][i],
            "precip": hourly["precipitation"][i]
        }
        for i in range(24)
    ]

# -----------------------------------------
# Risk scoring + TDI + 6h outlook + driver + strip
# -----------------------------------------
def compute_risk(hourly):
    winds = hourly["windspeed_10m"][:24]
    vis = hourly["visibility"][:24]
    precip = hourly["precipitation"][:24]

    max_wind = max(winds)
    min_vis = min(vis)
    max_precip = max(precip)

    # Wind risk
    if max_wind < 20:
        wind_risk = 5
    elif max_wind < 40:
        wind_risk = 15
    elif max_wind < 60:
        wind_risk = 30
    else:
        wind_risk = 40

    # Visibility risk
    if min_vis > 10000:
        vis_risk = 0
    elif min_vis > 5000:
        vis_risk = 5
    elif min_vis > 1000:
        vis_risk = 10
    else:
        vis_risk = 20

    # Precipitation risk
    if max_precip == 0:
        precip_risk = 0
    elif max_precip < 2:
        precip_risk = 5
    elif max_precip < 10:
        precip_risk = 10
    else:
        precip_risk = 20

    score = wind_risk + vis_risk + precip_risk

    if score < 30:
        level = "low"
        color = "#2ECC71"   # green
    elif score < 60:
        level = "moderate"
        color = "#F1C40F"   # yellow
    else:
        level = "high"
        color = "#E74C3C"   # red

    # Transit Difficulty Index (0–100, scaled from max 80)
    max_possible = 40 + 20 + 20  # 80
    tdi_score = round((score / max_possible) * 100)
    if tdi_score < 20:
        tdi_category = "Routine"
    elif tdi_score < 40:
        tdi_category = "Caution"
    elif tdi_score < 60:
        tdi_category = "Challenging"
    elif tdi_score < 80:
        tdi_category = "Hazardous"
    else:
        tdi_category = "Severe"

    # Dominant risk driver
    driver_map = {
        wind_risk: "Wind-driven risk",
        vis_risk: "Visibility degradation",
        precip_risk: "Heavy precipitation"
    }
    dominant_driver = driver_map[max(driver_map.keys())]

    # Next 6 hours outlook
    def avg(seq):
        return sum(seq) / len(seq) if seq else 0.0

    first_3_wind = avg(winds[0:3])
    next_3_wind = avg(winds[3:6])
    first_3_vis = avg(vis[0:3])
    next_3_vis = avg(vis[3:6])
    first_3_precip = avg(precip[0:3])
    next_3_precip = avg(precip[3:6])

    d_wind = next_3_wind - first_3_wind
    d_vis = next_3_vis - first_3_vis
    d_precip = next_3_precip - first_3_precip

    worsening = (d_wind > 5) or (d_vis < -2000) or (d_precip > 2)
    improving = (d_wind < -5) or (d_vis > 2000) or (d_precip < -2)

    if worsening and not improving:
        outlook_6h = "Conditions deteriorating over the next 6 hours."
    elif improving and not worsening:
        outlook_6h = "Conditions improving over the next 6 hours."
    elif worsening and improving:
        outlook_6h = "Mixed signals: some factors improving, others deteriorating."
    else:
        outlook_6h = "Stable conditions expected over the next 6 hours."

    # 24-hour risk strip (hour-by-hour)
    hourly_risk_strip = []
    for i in range(24):
        w = winds[i]
        v = vis[i]
        p = precip[i]

        if w < 20:
            hr_w = 5
        elif w < 40:
            hr_w = 15
        elif w < 60:
            hr_w = 30
        else:
            hr_w = 40

        if v > 10000:
            hr_v = 0
        elif v > 5000:
            hr_v = 5
        elif v > 1000:
            hr_v = 10
        else:
            hr_v = 20

        if p == 0:
            hr_p = 0
        elif p < 2:
            hr_p = 5
        elif p < 10:
            hr_p = 10
        else:
            hr_p = 20

        hr_score = hr_w + hr_v + hr_p

        if hr_score < 30:
            hr_level = "low"
        elif hr_score < 60:
            hr_level = "moderate"
        else:
            hr_level = "high"

        hourly_risk_strip.append(hr_level)

    return {
        "score": score,
        "level": level,
        "color": color,
        "tdi_score": tdi_score,
        "tdi_category": tdi_category,
        "outlook_6h": outlook_6h,
        "dominant_driver": dominant_driver,
        "hourly_risk_strip": hourly_risk_strip,
        "factors": {
            "wind": wind_risk,
            "visibility": vis_risk,
            "precipitation": precip_risk
        }
    }

# -----------------------------------------
# Main program
# -----------------------------------------
async def main():
    results = []

    for cp in CHOKEPOINTS:
        data = await fetch_forecast(cp["lat"], cp["lon"])
        h = data["hourly"]

        entry = {
            "name": cp["name"],
            "coords": {"lat": cp["lat"], "lon": cp["lon"]},
            "current": {
                "temperature_c": h["temperature_2m"][0],
                "wind_kmh": h["windspeed_10m"][0],
                "visibility_m": h["visibility"][0],
                "precip_mm": h["precipitation"][0]
            },
            "forecast_24h": extract_24h(h),
            "risk": compute_risk(h)
        }

        results.append(entry)

    response = {"chokepoints": results}

    save_json_to_file(response)
    generate_html_dashboard(response)
    print(json.dumps(response, indent=2))

asyncio.run(main())

