#!/usr/bin/env python3
"""
Global Maritime Chokepoint Risk Dashboard
Monitors weather and geopolitical risks at major shipping chokepoints
Generates professional HTML dashboard with real-time risk assessments
"""

import os
import json
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from enum import Enum


class RiskLevel(Enum):
    """Risk level classifications"""
    LOW = ("LOW", 5, "#28a745")
    MODERATE = ("MODERATE", 30, "#ffc107")
    HIGH = ("HIGH", 70, "#dc3545")
    CRITICAL = ("CRITICAL", 100, "#8b0000")
    
    def __init__(self, label: str, threshold: int, color: str):
        self.label = label
        self.threshold = threshold
        self.color = color


class TransitDifficulty(Enum):
    """Transit difficulty classifications"""
    ROUTINE = ("Routine", 10, "#28a745")
    CAUTION = ("Caution", 30, "#ffc107")
    HAZARDOUS = ("Hazardous", 60, "#dc3545")
    
    def __init__(self, label: str, threshold: int, color: str):
        self.label = label
        self.threshold = threshold
        self.color = color


@dataclass
class ChokePointWeather:
    """Weather data for a chokepoint"""
    temperature: float  # Celsius
    wind_speed: float   # km/h
    visibility: float   # meters
    precipitation: float  # mm


@dataclass
class ChokePointForecast:
    """Forecast data for a chokepoint"""
    next_6_hours: str   # "Stable" or "Deteriorating"
    dominant_driver: str  # Wind, Precipitation, Geopolitical, etc.
    operational_impact: str


@dataclass
class ChokePoint:
    """Maritime chokepoint data"""
    name: str
    risk_score: int  # 0-100
    weather: ChokePointWeather
    forecast: ChokePointForecast
    transit_difficulty: int  # 0-100
    
    def get_risk_level(self) -> RiskLevel:
        """Get risk level based on score"""
        for level in RiskLevel:
            if self.risk_score <= level.threshold:
                return level
        return RiskLevel.CRITICAL
    
    def get_difficulty_level(self) -> TransitDifficulty:
        """Get transit difficulty based on score"""
        for difficulty in TransitDifficulty:
            if self.transit_difficulty <= difficulty.threshold:
                return difficulty
        return TransitDifficulty.HAZARDOUS


class MaritimeDashboard:
    """Generate Global Maritime Chokepoint Risk Dashboard"""
    
    def __init__(self):
        """Initialize dashboard"""
        self.current_date = datetime.now().strftime("%B %d, %Y")
        self.current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.chokepoints: List[ChokePoint] = []
        
    def add_chokepoint(self, chokepoint: ChokePoint) -> None:
        """Add a chokepoint to the dashboard"""
        self.chokepoints.append(chokepoint)
    
    def get_global_risk_index(self) -> int:
        """Calculate global risk index as average of all chokepoints"""
        if not self.chokepoints:
            return 0
        return int(sum(cp.risk_score for cp in self.chokepoints) / len(self.chokepoints))
    
    def get_global_risk_level(self) -> RiskLevel:
        """Get global risk level"""
        global_risk = self.get_global_risk_index()
        for level in RiskLevel:
            if global_risk <= level.threshold:
                return level
        return RiskLevel.CRITICAL
    
    def get_risk_distribution(self) -> Dict[str, int]:
        """Get distribution of risk levels across chokepoints"""
        distribution = {
            "low": 0,
            "moderate": 0,
            "high": 0,
            "critical": 0
        }
        
        for cp in self.chokepoints:
            level = cp.get_risk_level()
            if level == RiskLevel.LOW:
                distribution["low"] += 1
            elif level == RiskLevel.MODERATE:
                distribution["moderate"] += 1
            elif level == RiskLevel.HIGH:
                distribution["high"] += 1
            else:
                distribution["critical"] += 1
        
        return distribution
    
    def get_highest_risk_chokepoint(self) -> Optional[ChokePoint]:
        """Get the chokepoint with highest risk"""
        if not self.chokepoints:
            return None
        return max(self.chokepoints, key=lambda cp: cp.risk_score)
    
    def load_sample_data(self) -> None:
        """Load sample chokepoint data"""
        
        # Strait of Hormuz
        self.add_chokepoint(ChokePoint(
            name="Strait of Hormuz",
            risk_score=20,
            weather=ChokePointWeather(
                temperature=21.8,
                wind_speed=2.5,
                visibility=24140.0,
                precipitation=0.0
            ),
            forecast=ChokePointForecast(
                next_6_hours="Deteriorating",
                dominant_driver="Wind-driven risk",
                operational_impact="Elevated winds could require increased caution during transits. Precipitation may reduce situational awareness and increase workload on bridge teams."
            ),
            transit_difficulty=25
        ))
        
        # Strait of Malacca
        self.add_chokepoint(ChokePoint(
            name="Strait of Malacca",
            risk_score=15,
            weather=ChokePointWeather(
                temperature=26.6,
                wind_speed=8.5,
                visibility=24140.0,
                precipitation=0.7
            ),
            forecast=ChokePointForecast(
                next_6_hours="Stable",
                dominant_driver="Heavy precipitation",
                operational_impact="Heavy precipitation may degrade sensor performance and complicate navigation."
            ),
            transit_difficulty=19
        ))
        
        # Suez Canal
        self.add_chokepoint(ChokePoint(
            name="Suez Canal",
            risk_score=5,
            weather=ChokePointWeather(
                temperature=17.0,
                wind_speed=6.6,
                visibility=62260.0,
                precipitation=0.0
            ),
            forecast=ChokePointForecast(
                next_6_hours="Deteriorating",
                dominant_driver="Wind-driven risk",
                operational_impact="No significant weather-driven operational impacts are expected at this chokepoint."
            ),
            transit_difficulty=6
        ))
        
        # Bab el-Mandeb
        self.add_chokepoint(ChokePoint(
            name="Bab el-Mandeb",
            risk_score=30,
            weather=ChokePointWeather(
                temperature=22.3,
                wind_speed=31.6,
                visibility=24140.0,
                precipitation=0.0
            ),
            forecast=ChokePointForecast(
                next_6_hours="Stable",
                dominant_driver="Wind-driven risk",
                operational_impact="High winds may affect vessel maneuverability and transit safety."
            ),
            transit_difficulty=38
        ))
        
        # Panama Canal
        self.add_chokepoint(ChokePoint(
            name="Panama Canal",
            risk_score=10,
            weather=ChokePointWeather(
                temperature=25.0,
                wind_speed=14.3,
                visibility=24140.0,
                precipitation=0.0
            ),
            forecast=ChokePointForecast(
                next_6_hours="Stable",
                dominant_driver="Heavy precipitation",
                operational_impact="Precipitation may reduce situational awareness and increase workload on bridge teams."
            ),
            transit_difficulty=12
        ))
        
        # Danish Straits
        self.add_chokepoint(ChokePoint(
            name="Danish Straits",
            risk_score=30,
            weather=ChokePointWeather(
                temperature=-0.3,
                wind_speed=25.9,
                visibility=5120.0,
                precipitation=0.1
            ),
            forecast=ChokePointForecast(
                next_6_hours="Deteriorating",
                dominant_driver="Wind-driven risk",
                operational_impact="Elevated winds could require increased caution during transits. Reduced visibility may slow traffic and increase collision risk. Precipitation may reduce situational awareness and increase workload on bridge teams."
            ),
            transit_difficulty=38
        ))
    
    def generate_html(self, output_path: str = "maritime_risk_dashboard.html") -> str:
        """
        Generate HTML dashboard
        
        Args:
            output_path: Path where HTML file will be saved
            
        Returns:
            Path to generated HTML file
        """
        
        global_risk = self.get_global_risk_index()
        global_level = self.get_global_risk_level()
        highest_risk = self.get_highest_risk_chokepoint()
        distribution = self.get_risk_distribution()
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Maritime Chokepoint Risk Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-bottom: 25px;
            border-left: 6px solid #667eea;
        }}
        
        .header h1 {{
            color: #1a1a1a;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header-meta {{
            color: #666;
            font-size: 0.95em;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        
        .header-meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .timestamp {{
            color: #999;
            font-size: 0.85em;
            font-style: italic;
        }}
        
        .global-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border-left: 6px solid;
        }}
        
        .summary-card.low {{
            border-left-color: #28a745;
        }}
        
        .summary-card.moderate {{
            border-left-color: #ffc107;
        }}
        
        .summary-card.high {{
            border-left-color: #dc3545;
        }}
        
        .summary-card.critical {{
            border-left-color: #8b0000;
        }}
        
        .summary-card h2 {{
            color: #1a1a1a;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
            color: #666;
        }}
        
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        
        .summary-card .label {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .risk-index {{
            font-size: 3em;
            font-weight: bold;
            color: {global_level.color};
        }}
        
        .risk-gauge {{
            display: flex;
            gap: 5px;
            margin-top: 10px;
        }}
        
        .gauge-segment {{
            flex: 1;
            height: 8px;
            border-radius: 4px;
            background: #e0e0e0;
        }}
        
        .gauge-segment.active {{
            background: {global_level.color};
        }}
        
        .distribution {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            margin-top: 15px;
        }}
        
        .distribution-item {{
            text-align: center;
        }}
        
        .distribution-count {{
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .distribution-label {{
            font-size: 0.75em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .chokepoints-section {{
            margin-top: 30px;
        }}
        
        .section-title {{
            background: white;
            padding: 20px 25px;
            border-radius: 8px 8px 0 0;
            border-left: 6px solid #667eea;
            color: #1a1a1a;
            font-size: 1.8em;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .chokepoints-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .chokepoint-card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            overflow: hidden;
            border-left: 6px solid;
        }}
        
        .chokepoint-card.low {{
            border-left-color: #28a745;
        }}
        
        .chokepoint-card.moderate {{
            border-left-color: #ffc107;
        }}
        
        .chokepoint-card.high {{
            border-left-color: #dc3545;
        }}
        
        .chokepoint-card.critical {{
            border-left-color: #8b0000;
        }}
        
        .chokepoint-header {{
            padding: 20px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: start;
        }}
        
        .chokepoint-name {{
            font-size: 1.3em;
            font-weight: 600;
            color: #1a1a1a;
        }}
        
        .chokepoint-risk {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .risk-score {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .risk-badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: white;
        }}
        
        .risk-badge.low {{
            background: #28a745;
        }}
        
        .risk-badge.moderate {{
            background: #ffc107;
            color: #1a1a1a;
        }}
        
        .risk-badge.high {{
            background: #dc3545;
        }}
        
        .risk-badge.critical {{
            background: #8b0000;
        }}
        
        .chokepoint-body {{
            padding: 20px;
        }}
        
        .weather-section {{
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .weather-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 12px;
        }}
        
        .weather-item {{
            background: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
        }}
        
        .weather-label {{
            font-size: 0.75em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .weather-value {{
            font-size: 1.2em;
            font-weight: 600;
            color: #1a1a1a;
        }}
        
        .forecast-section {{
            margin-bottom: 15px;
        }}
        
        .forecast-label {{
            font-size: 0.75em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .forecast-value {{
            font-size: 0.95em;
            color: #333;
        }}
        
        .transit-difficulty {{
            background: #f0f7ff;
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 12px;
            border-left: 3px solid #667eea;
        }}
        
        .transit-label {{
            font-size: 0.75em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .transit-bar {{
            background: #e0e0e0;
            height: 6px;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 8px;
        }}
        
        .transit-fill {{
            height: 100%;
            background: #667eea;
        }}
        
        .operational-impact {{
            background: #fff8e1;
            padding: 12px;
            border-radius: 4px;
            border-left: 3px solid #ffc107;
            font-size: 0.9em;
            color: #333;
        }}
        
        .footer {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .footer-divider {{
            border-top: 1px solid #e0e0e0;
            margin-top: 15px;
            padding-top: 15px;
        }}
        
        .copyright {{
            color: #999;
            font-size: 0.85em;
            margin-top: 10px;
        }}
        
        @media (max-width: 768px) {{
            .chokepoints-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .weather-grid {{
                grid-template-columns: 1fr;
            }}
            
            .distribution {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌊 Global Maritime Chokepoint Risk Dashboard</h1>
            <div class="header-meta">
                <span>📅 {self.current_date}</span>
                <span class="timestamp">Generated: {self.current_timestamp}</span>
            </div>
        </div>
        
        <div class="global-summary">
            <div class="summary-card {global_level.name.lower()}">
                <h2>Global Risk Index</h2>
                <div class="risk-index">{global_risk}</div>
                <div class="label">{global_level.label} RISK</div>
                <div class="risk-gauge">
                    {''.join(f'<div class="gauge-segment {"active" if i < global_risk/25 else ""}"></div>' for i in range(4))}
                </div>
                <div class="distribution">
                    <div class="distribution-item">
                        <div class="distribution-count" style="color: #28a745;">{distribution['low']}</div>
                        <div class="distribution-label">Low</div>
                    </div>
                    <div class="distribution-item">
                        <div class="distribution-count" style="color: #ffc107;">{distribution['moderate']}</div>
                        <div class="distribution-label">Moderate</div>
                    </div>
                    <div class="distribution-item">
                        <div class="distribution-count" style="color: #dc3545;">{distribution['high']}</div>
                        <div class="distribution-label">High</div>
                    </div>
                    <div class="distribution-item">
                        <div class="distribution-count" style="color: #8b0000;">{distribution['critical']}</div>
                        <div class="distribution-label">Critical</div>
                    </div>
                </div>
            </div>
            
            <div class="summary-card {highest_risk.get_risk_level().name.lower() if highest_risk else 'low'}">
                <h2>Highest Operational Risk</h2>
                <div class="value" style="font-size: 1.5em;">{highest_risk.name if highest_risk else 'N/A'}</div>
                <div class="label">Risk Score: <strong>{highest_risk.risk_score if highest_risk else 0}</strong></div>
                <div class="label">{highest_risk.get_risk_level().label if highest_risk else 'N/A'}</div>
            </div>
            
            <div class="summary-card low">
                <h2>Global Assessment</h2>
                <div class="forecast-value" style="font-size: 1em; line-height: 1.5;">
                    Global chokepoint risk is elevated to {global_level.label.lower()}. Weather-driven constraints may impact operations at select locations. No widespread high-risk disruptions are currently assessed.
                </div>
            </div>
        </div>
        
        <div class="chokepoints-section">
            <div class="section-title">Chokepoint Analysis</div>
            <div class="chokepoints-grid">
                {self._generate_chokepoint_cards_html()}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Global Maritime Chokepoint Risk Dashboard</strong></p>
            <p>Data based on forecast conditions; for situational awareness only and not a substitute for official navigation guidance.</p>
            <div class="footer-divider">
                <p class="copyright">© 2026 Randy Hinton. All rights reserved.</p>
            </div>
        </div>
    </div>
</body>
</html>"""
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Maritime Risk Dashboard generated: {output_path}")
        return output_path
    
    def _generate_chokepoint_cards_html(self) -> str:
        """Generate HTML cards for each chokepoint"""
        
        html = ""
        for cp in self.chokepoints:
            risk_level = cp.get_risk_level()
            difficulty = cp.get_difficulty_level()
            
            html += f"""            <div class="chokepoint-card {risk_level.name.lower()}">
                <div class="chokepoint-header">
                    <div>
                        <div class="chokepoint-name">{cp.name}</div>
                    </div>
                    <div class="chokepoint-risk">
                        <div class="risk-score">{cp.risk_score}</div>
                        <div class="risk-badge {risk_level.name.lower()}">{risk_level.label}</div>
                    </div>
                </div>
                
                <div class="chokepoint-body">
                    <div class="weather-section">
                        <strong>Current Conditions</strong>
                        <div class="weather-grid">
                            <div class="weather-item">
                                <div class="weather-label">Temperature</div>
                                <div class="weather-value">{cp.weather.temperature:.1f}°C</div>
                            </div>
                            <div class="weather-item">
                                <div class="weather-label">Wind Speed</div>
                                <div class="weather-value">{cp.weather.wind_speed:.1f} km/h</div>
                            </div>
                            <div class="weather-item">
                                <div class="weather-label">Visibility</div>
                                <div class="weather-value">{cp.weather.visibility:,.0f} m</div>
                            </div>
                            <div class="weather-item">
                                <div class="weather-label">Precipitation</div>
                                <div class="weather-value">{cp.weather.precipitation:.1f} mm</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="forecast-section">
                        <div class="forecast-label">6-Hour Outlook</div>
                        <div class="forecast-value">{cp.forecast.next_6_hours}</div>
                    </div>
                    
                    <div class="forecast-section">
                        <div class="forecast-label">Dominant Driver</div>
                        <div class="forecast-value">{cp.forecast.dominant_driver}</div>
                    </div>
                    
                    <div class="transit-difficulty">
                        <div class="transit-label">Transit Difficulty: {difficulty.label} ({cp.transit_difficulty}/100)</div>
                        <div class="transit-bar">
                            <div class="transit-fill" style="width: {cp.transit_difficulty}%; background: {difficulty.color};"></div>
                        </div>
                    </div>
                    
                    <div class="operational-impact">
                        <strong>⚠ Operational Impact:</strong> {cp.forecast.operational_impact}
                    </div>
                </div>
            </div>
"""
        
        return html


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate Global Maritime Chokepoint Risk Dashboard"
    )
    parser.add_argument(
        "-o", "--output",
        default="maritime_risk_dashboard.html",
        help="Output HTML file path"
    )
    
    args = parser.parse_args()
    
    # Create dashboard and load sample data
    dashboard = MaritimeDashboard()
    dashboard.load_sample_data()
    
    # Generate HTML
    output_file = dashboard.generate_html(output_path=args.output)
    print(f"✓ Dashboard saved to: {output_file}")
    
    # Print summary statistics
    print(f"\n📊 Dashboard Summary:")
    print(f"   Global Risk Index: {dashboard.get_global_risk_index()} ({dashboard.get_global_risk_level().label})")
    print(f"   Chokepoints monitored: {len(dashboard.chokepoints)}")
    print(f"   Risk distribution: {dashboard.get_risk_distribution()}")


if __name__ == "__main__":
    main()
