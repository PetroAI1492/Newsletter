import json
from datetime import datetime, UTC
import asyncio
import httpx

# =========================================================
# CONFIG: PORT LIST
# =========================================================

PORTS = [
    {"name": "Port of Rotterdam", "lat": 51.9526, "lon": 4.1339},
    {"name": "Port of Antwerp", "lat": 51.2637, "lon": 4.4125},
    {"name": "Port of Hamburg", "lat": 53.5461, "lon": 9.9661},
    {"name": "Port of Marseille", "lat": 43.3521, "lon": 5.3378},
    {"name": "Port of Fujairah", "lat": 25.1557, "lon": 56.3340},
    {"name": "Port of Jeddah", "lat": 21.4612, "lon": 39.1768},
    {"name": "Port of Sohar", "lat": 24.5000, "lon": 56.6667},
    {"name": "Port of Singapore", "lat": 1.2644, "lon": 103.8222},
    {"name": "Port of Shanghai", "lat": 31.2304, "lon": 121.4737},
    {"name": "Port of Busan", "lat": 35.0951, "lon": 129.0403},
    {"name": "Port of Hong Kong", "lat": 22.3080, "lon": 114.2250},
    {"name": "Port of Los Angeles", "lat": 33.7329, "lon": -118.2673},
    {"name": "Port of Long Beach", "lat": 33.7542, "lon": -118.2160},
    {"name": "Port of Houston", "lat": 29.7280, "lon": -95.2620},
    {"name": "Port of New York/New Jersey", "lat": 40.6681, "lon": -74.0451},
    {"name": "Port of Santos", "lat": -23.9520, "lon": -46.3280},
    {"name": "Port of Buenos Aires", "lat": -34.6037, "lon": -58.3816},
    {"name": "Port of Durban", "lat": -29.8710, "lon": 31.0456},
    {"name": "Port of Lagos (Apapa)", "lat": 6.4483, "lon": 3.3635},
    {"name": "Port of Tangier-Med", "lat": 35.8844, "lon": -5.5023},
    {"name": "Port of Melbourne", "lat": -37.8140, "lon": 144.9633},
    {"name": "Port of Sydney", "lat": -33.8688, "lon": 151.2093},
]


# =========================================================
# DATA FETCHING
# =========================================================

async def fetch_forecast(lat: float, lon: float) -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,windspeed_10m,visibility,precipitation"
    )
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


# =========================================================
# HELPERS
# =========================================================

def extract_24h(hourly: dict) -> list:
    """Slice the first 24 hours into a simple list of dicts."""
    out = []
    for i in range(24):
        out.append({
            "time": hourly["time"][i],
            "temp": hourly["temperature_2m"][i],
            "wind": hourly["windspeed_10m"][i],
            "vis": hourly["visibility"][i],
            "precip": hourly["precipitation"][i],
        })
    return out


def compute_risk(hourly: dict) -> dict:
    """Refined port risk model with weighted wind/vis/precip."""
    wind = hourly["windspeed_10m"][0]
    vis = hourly["visibility"][0]
    precip = hourly["precipitation"][0]

    # WIND SCORE (0–50)
    if wind <= 15:
        wind_score = 0
    elif wind <= 25:
        wind_score = 10
    elif wind <= 35:
        wind_score = 20
    elif wind <= 45:
        wind_score = 35
    else:
        wind_score = 50

    # VISIBILITY SCORE (0–30)
    if vis > 10000:
        vis_score = 0
    elif vis > 5000:
        vis_score = 5
    elif vis > 2000:
        vis_score = 10
    elif vis > 500:
        vis_score = 20
    else:
        vis_score = 30

    # PRECIP SCORE (0–20)
    if precip <= 0.5:
        precip_score = 0
    elif precip <= 2:
        precip_score = 5
    elif precip <= 5:
        precip_score = 10
    elif precip <= 10:
        precip_score = 15
    else:
        precip_score = 20

    score = min(wind_score + vis_score + precip_score, 100)

    if score < 30:
        level = "low"
        color = "#2ECC71"
    elif score < 60:
        level = "moderate"
        color = "#F1C40F"
    else:
        level = "high"
        color = "#E74C3C"

    drivers = {
        "wind": wind_score,
        "visibility": vis_score,
        "precipitation": precip_score,
    }
    dominant = max(drivers, key=drivers.get)

    wind_future = hourly["windspeed_10m"][6]
    trend = wind_future - wind
    if trend > 5:
        outlook = "Deteriorating"
    elif trend < -5:
        outlook = "Improving"
    else:
        outlook = "Stable"

    strip = []
    for i in range(24):
        w = hourly["windspeed_10m"][i]
        v = hourly["visibility"][i]
        p = hourly["precipitation"][i]

        # reuse same scoring logic
        if w <= 15:
            ws = 0
        elif w <= 25:
            ws = 10
        elif w <= 35:
            ws = 20
        elif w <= 45:
            ws = 35
        else:
            ws = 50

        if v > 10000:
            vs = 0
        elif v > 5000:
            vs = 5
        elif v > 2000:
            vs = 10
        elif v > 500:
            vs = 20
        else:
            vs = 30

        if p <= 0.5:
            ps = 0
        elif p <= 2:
            ps = 5
        elif p <= 5:
            ps = 10
        elif p <= 10:
            ps = 15
        else:
            ps = 20

        s = ws + vs + ps
        if s < 30:
            strip.append("low")
        elif s < 60:
            strip.append("moderate")
        else:
            strip.append("high")

    return {
        "score": int(score),
        "level": level,
        "color": color,
        "dominant_driver": dominant,
        "outlook_6h": outlook,
        "hourly_risk_strip": strip,
        "tdi_score": int(score),
        "tdi_category": level.capitalize(),
    }


def assess_operational_impact(entry: dict) -> str:
    """Port‑specific operational impact text."""
    wind = entry["current"]["wind_kmh"]
    vis = entry["current"]["visibility_m"]
    precip = entry["current"]["precip_mm"]

    impacts = []

    # WIND IMPACTS
    if wind > 45:
        impacts.append(
            "High winds may halt STS crane operations, delay pilotage, and require tug assistance for berthing."
        )
    elif wind > 35:
        impacts.append(
            "Elevated winds may reduce crane speeds, affect mooring integrity, and slow berthing operations."
        )
    elif wind > 25:
        impacts.append(
            "Moderate winds may require caution during cargo handling and vessel maneuvering."
        )
    elif wind > 15:
        impacts.append(
            "Light to moderate winds with minor operational impact."
        )

    # VISIBILITY IMPACTS
    if vis < 500:
        impacts.append(
            "Severely reduced visibility may suspend pilotage and restrict vessel movements."
        )
    elif vis < 2000:
        impacts.append(
            "Reduced visibility may slow pilot boarding and inbound traffic."
        )

    # PRECIPITATION IMPACTS
    if precip > 10:
        impacts.append(
            "Heavy precipitation may halt container and bulk cargo operations."
        )
    elif precip > 5:
        impacts.append(
            "Rain may reduce cargo handling efficiency and slow yard operations."
        )
    elif precip > 1:
        impacts.append(
            "Light precipitation with minor operational impact."
        )

    if not impacts:
        return "Normal operating conditions with no significant weather‑related restrictions."

    return " ".join(impacts)


def compute_global_metrics(ports: list) -> dict:
    max_score = -1
    highest = None
    counts = {"low": 0, "moderate": 0, "high": 0}

    for p in ports:
        lvl = p["risk"]["level"]
        score = p["risk"]["score"]
        counts[lvl] += 1
        if score > max_score:
            max_score = score
            highest = p

    if max_score < 30:
        global_level = "low"
    elif max_score < 60:
        global_level = "moderate"
    else:
        global_level = "high"

    return {
        "global_level": global_level,
        "global_index": max_score,
        "highest": highest["name"] if highest else "N/A",
        "counts": counts,
    }


def save_json(data: dict) -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    fn = f"port_ops_{ts}.json"
    with open(fn, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved JSON: {fn}")
    return fn


# =========================================================
# HTML GENERATION
# =========================================================

def generate_html(data: dict, filename: str = "port_dashboard.html") -> None:
    metrics = compute_global_metrics(data["ports"])
    updated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Port Operations Weather Dashboard</title>
<style>
body {{
  font-family: Arial, sans-serif;
  background: #f4f4f4;
  padding: 20px;
}}
h1 {{
  text-align: center;
  margin-bottom: 10px;
}}
.summary-block {{
  background: #ffffff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  margin-bottom: 25px;
}}
.summary-line {{
  margin: 4px 0;
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}}
.card {{
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}}
.risk {{
  font-weight: bold;
  padding: 6px 10px;
  border-radius: 4px;
  color: white;
  display: inline-block;
  margin-top: 10px;
}}
details {{
  margin-top: 10px;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 13px;
}}
th, td {{
  padding: 4px 6px;
  border-bottom: 1px solid #ddd;
  text-align: left;
}}
th {{
  background: #eee;
}}
footer {{
  margin-top: 40px;
  padding: 18px 0;
  border-top: 1px solid #ccc;
  font-size: 12px;
  text-align: center;
  color: #444;
}}
</style>
</head>

<body>

<h1>Port Operations Weather Dashboard</h1>

<div class="summary-block">
  <p class="summary-line"><strong>Overall operational risk:</strong> {metrics["global_level"].upper()}</p>
  <p class="summary-line"><strong>Highest‑risk port:</strong> {metrics["highest"]}</p>
  <p class="summary-line"><strong>Risk distribution:</strong> {metrics["counts"]["low"]} low, {metrics["counts"]["moderate"]} moderate, {metrics["counts"]["high"]} high</p>
  <p class="summary-line"><strong>Last updated:</strong> {updated}</p>
  <p class="summary-line">Short‑term weather intelligence for berthing, pilotage, and cargo operations.</p>
</div>

<div class="grid">
"""

    for p in data["ports"]:
        c = p["current"]
        summary = (
            f"{c['temperature_c']}°C, "
            f"{c['wind_kmh']} km/h wind, "
            f"{c['visibility_m']} m visibility, "
            f"{c['precip_mm']} mm precip"
        )

        strip_html = ""
        for lvl in p["risk"]["hourly_risk_strip"]:
            color = "#2ECC71" if lvl == "low" else "#F1C40F" if lvl == "moderate" else "#E74C3C"
            strip_html += f"<div style='width:12px;height:12px;background:{color};border-radius:2px;'></div>"

        rows_html = ""
        for h in p["forecast_24h"]:
            rows_html += f"""
      <tr>
        <td>{h['time']}</td>
        <td>{h['temp']}°C</td>
        <td>{h['wind']} km/h</td>
        <td>{h['vis']} m</td>
        <td>{h['precip']} mm</td>
      </tr>"""

        html += f"""
  <div class="card">
    <h2>{p['name']}</h2>

    <p><strong>Current conditions:</strong> {summary}</p>

    <p class="risk" style="background:{p['risk']['color']}">
      {p['risk']['level'].upper()} (Score: {p['risk']['score']})
    </p>

    <p><strong>Port Operations Difficulty Index:</strong> {p['risk']['tdi_score']} ({p['risk']['tdi_category']})</p>

    <p><strong>Next 6 hours:</strong> {p['risk']['outlook_6h']}</p>

    <p><strong>Dominant operational constraint:</strong> {p['risk']['dominant_driver']}</p>

    <p><strong>Operational impact assessment:</strong> {p['impact']}</p>

    <div style="display:flex; gap:2px; margin:10px 0;">{strip_html}</div>

    <details>
      <summary>24‑Hour Forecast</summary>
      <table>
        <tr>
          <th>Time</th>
          <th>Temp</th>
          <th>Wind</th>
          <th>Vis</th>
          <th>Precip</th>
        </tr>
        {rows_html}
      </table>
    </details>
  </div>
"""

    html += """
</div>

<footer>
  <div><strong>Port Operations Weather Dashboard</strong></div>
  <div>Short‑term weather intelligence for global port activity and operational planning.</div>
  <div style="margin-top:6px;">
    Forecast data is for situational awareness only and should be used alongside official port authority guidance.
  </div>
</footer>

</body>
</html>
"""

    with open(filename, "w") as f:
        f.write(html)

    print(f"Saved HTML: {filename}")


# =========================================================
# MAIN
# =========================================================

async def main():
    ports_output = []

    for port in PORTS:
        data = await fetch_forecast(port["lat"], port["lon"])
        h = data["hourly"]

        entry = {
            "name": port["name"],
            "coords": {"lat": port["lat"], "lon": port["lon"]},
            "current": {
                "temperature_c": h["temperature_2m"][0],
                "wind_kmh": h["windspeed_10m"][0],
                "visibility_m": h["visibility"][0],
                "precip_mm": h["precipitation"][0],
            },
            "forecast_24h": extract_24h(h),
            "risk": compute_risk(h),
        }

        entry["impact"] = assess_operational_impact(entry)
        ports_output.append(entry)

    response = {"ports": ports_output}

    save_json(response)
    generate_html(response)


if __name__ == "__main__":
    asyncio.run(main())

