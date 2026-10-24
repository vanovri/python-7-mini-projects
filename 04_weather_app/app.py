import argparse
import json
from weather_service import get_weather


def run_cli_demo(city: str = "Delhi") -> None:
    data = get_weather(city)
    compact = {"temp": data["temp"], "humidity": data["humidity"], "sky": data["sky"]}
    print(f"[04 Weather App] GET /weather?q={city} ({data['source']})")
    print(f"  -> {json.dumps(compact)}")
    print(
        f"  Details: {data['city']}, {data['country']} | Feels like {data['feels_like']}°C | Wind {data['wind_kmh']} km/h"
    )
    if data.get("forecast"):
        print("  5-Day Forecast:")
        for day in data["forecast"]:
            print(f"    - {day['time']}: {day['temp']}°C ({day['sky']})")


def run_streamlit_ui() -> None:
    import streamlit as st

    st.set_page_config(page_title="04 - Weather App", page_icon="⛅", layout="centered")
    st.title("⛅ Project 04: Live Weather App")
    st.caption("Python + Requests + Weather API + JSON + python-dotenv + Streamlit")

    city = st.text_input("Enter City Name", value="Delhi")
    if st.button("Get Live Weather", type="primary") or city:
        try:
            with st.spinner(f"Fetching live weather for {city}..."):
                data = get_weather(city)
            st.success(f"Live Weather for **{data['city']}, {data['country']}** ({data['source']})")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Temperature", f"{data['temp']} °C")
            c2.metric("Feels Like", f"{data['feels_like']} °C")
            c3.metric("Humidity", f"{data['humidity']}%")
            c4.metric("Wind", f"{data['wind_kmh']} km/h")
            st.info(f"**Condition:** {data['sky'].title()}")

            if data.get("forecast"):
                st.subheader("📅 5-Day / Upcoming Forecast")
                st.table(data["forecast"])
        except Exception as err:
            st.error(f"Could not fetch weather: {err}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Project 04: Weather App")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument("--city", type=str, default="Delhi", help="City name to query")
    args, _ = parser.parse_known_args()
    if args.cli:
        run_cli_demo(city=args.city)
    else:
        run_streamlit_ui()
