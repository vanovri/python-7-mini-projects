import os
from pathlib import Path
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

WMO_CODE_MAP = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    51: "light drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "snow fall",
    80: "rain showers",
    95: "thunderstorm",
}


def fetch_openweather(city: str, api_key: str) -> Dict[str, Any]:
    url = "https://api.openweathermap.org/data/2.5/weather"
    resp = requests.get(
        url, params={"q": city, "appid": api_key, "units": "metric"}, timeout=10
    )
    resp.raise_for_status()
    data = resp.json()

    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    f_resp = requests.get(
        forecast_url,
        params={"q": city, "appid": api_key, "units": "metric", "cnt": 5},
        timeout=10,
    )
    forecast_list: List[Dict[str, Any]] = []
    if f_resp.ok:
        for item in f_resp.json().get("list", [])[:5]:
            forecast_list.append(
                {
                    "time": item.get("dt_txt", ""),
                    "temp": round(float(item["main"]["temp"]), 1),
                    "sky": item["weather"][0]["description"],
                }
            )

    return {
        "city": data.get("name", city),
        "country": data.get("sys", {}).get("country", ""),
        "temp": round(float(data["main"]["temp"]), 1),
        "feels_like": round(float(data["main"].get("feels_like", data["main"]["temp"])), 1),
        "humidity": int(data["main"]["humidity"]),
        "wind_kmh": round(float(data.get("wind", {}).get("speed", 0.0)) * 3.6, 1),
        "sky": data["weather"][0]["description"],
        "source": "OpenWeather API",
        "forecast": forecast_list,
    }


def fetch_open_meteo_live(city: str) -> Dict[str, Any]:
    geo_resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    geo_resp.raise_for_status()
    results = geo_resp.json().get("results")
    if not results:
        raise ValueError(f"City '{city}' not found.")

    loc = results[0]
    lat, lon = loc["latitude"], loc["longitude"]

    w_resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
            "forecast_days": 5,
        },
        timeout=10,
    )
    w_resp.raise_for_status()
    w_data = w_resp.json()
    curr = w_data["current"]
    code = int(curr.get("weather_code", 0))

    daily = w_data.get("daily", {})
    forecast_list = []
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    codes = daily.get("weather_code", [])
    for idx in range(min(5, len(dates))):
        forecast_list.append(
            {
                "time": dates[idx],
                "temp": round((max_temps[idx] + min_temps[idx]) / 2, 1),
                "temp_max": max_temps[idx],
                "temp_min": min_temps[idx],
                "sky": WMO_CODE_MAP.get(int(codes[idx]), "clear"),
            }
        )

    return {
        "city": loc.get("name", city),
        "country": loc.get("country_code", ""),
        "temp": round(float(curr["temperature_2m"]), 1),
        "feels_like": round(float(curr.get("apparent_temperature", curr["temperature_2m"])), 1),
        "humidity": int(curr["relative_humidity_2m"]),
        "wind_kmh": round(float(curr.get("wind_speed_10m", 0.0)), 1),
        "sky": WMO_CODE_MAP.get(code, "clear"),
        "source": "Open-Meteo Live API (Zero-Key Fallback)",
        "forecast": forecast_list,
    }


def get_weather(city: str) -> Dict[str, Any]:
    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if api_key and api_key != "your_openweather_api_key_here":
        try:
            return fetch_openweather(city, api_key)
        except Exception:
            pass
    return fetch_open_meteo_live(city)
