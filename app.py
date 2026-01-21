import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Live Weather Dashboard",
    page_icon="🌦",
    layout="centered"
)

API_KEY = "rQHkkGK3sfNWHPpU2yuUvA1uSAHbjsSq"

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=300000, key="weather_refresh")  # 5 minutes
if st.button("🔄 Refresh Now"):
    st.rerun()

# ---------------- TITLE ----------------
st.title("🌦 Live Weather Dashboard")
st.caption("Real-time weather data using Tomorrow.io API")

# ---------------- INPUT ----------------
city = st.text_input("Enter City Name", "Ranchi")

# ---------------- GEO CODING ----------------
def get_lat_lon(city):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{city}, India",
        "format": "json"
    }
    headers = {
        "User-Agent": "live-weather-app/1.0 (educational-use)"
    }

    response = requests.get(url, params=params, headers=headers)

    try:
        data = response.json()
    except ValueError:
        return None, None

    if len(data) == 0:
        return None, None

    return data[0]["lat"], data[0]["lon"]

# ---------------- WEATHER FUNCTIONS ----------------
def get_current_weather(lat, lon):
    url = "https://api.tomorrow.io/v4/weather/realtime"
    params = {
        "location": f"{lat},{lon}",
        "apikey": API_KEY,
        "units": "metric"
    }
    try:
        return requests.get(url, params=params).json()
    except ValueError:
        return None


def get_forecast(lat, lon):
    url = "https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": f"{lat},{lon}",
        "apikey": API_KEY,
        "units": "metric"
    }
    try:
        return requests.get(url, params=params).json()
    except ValueError:
        return None

# ---------------- MAIN LOGIC ----------------
if city:
    lat, lon = get_lat_lon(city)

    if lat is None:
        st.error("City not found ❌")
        st.stop()

    weather = get_current_weather(lat, lon)

    if weather is None or "data" not in weather:
        st.error("Unable to fetch weather data ❌")
        st.stop()

    values = weather["data"]["values"]

    # -------- CURRENT WEATHER --------
    st.subheader(f"📍 {city.title()}, India")

    col1, col2, col3 = st.columns(3)

    col1.metric("🌡 Temp (°C)", values.get("temperature", "N/A"))
    col1.metric("💧 Humidity (%)", values.get("humidity", "N/A"))
    col1.metric("🌬 Wind (m/s)", values.get("windSpeed", "N/A"))

    col2.metric("🌧 Rain (mm/hr)", values.get("precipitationIntensity", "N/A"))
    col2.metric("☀️ UV Index", values.get("uvIndex", "N/A"))
    col2.metric("🌡 Pressure (hPa)", values.get("pressureSurfaceLevel", "N/A"))

    col3.metric("🧭 Weather Code", values.get("weatherCode", "N/A"))
    col3.metric("📍 Latitude", lat)
    col3.metric("📍 Longitude", lon)

    st.divider()

    # -------- 5 DAY FORECAST --------
    forecast = get_forecast(lat, lon)

    if forecast is None or "timelines" not in forecast:
        st.error("Forecast data unavailable ❌")
        st.stop()

    daily = forecast["timelines"]["daily"][:5]

    forecast_data = []
    for day in daily:
        forecast_data.append({
            "Date": datetime.fromisoformat(day["time"].replace("Z", "")).date(),
            "Min Temp (°C)": day["values"].get("temperatureMin", "N/A"),
            "Max Temp (°C)": day["values"].get("temperatureMax", "N/A"),
            "Rain (%)": day["values"].get("precipitationProbabilityAvg", "N/A"),
            "UV Index": day["values"].get("uvIndexAvg", "N/A"),
            "Pressure (hPa)": day["values"].get("pressureSurfaceLevelAvg", "N/A"),
            "Wind (m/s)": day["values"].get("windSpeedAvg", "N/A"),
            "Weather Code": day["values"].get("weatherCodeMax", "N/A")
        })

    df = pd.DataFrame(forecast_data)

    st.subheader("📅 5-Day Weather Forecast")
    st.dataframe(df, use_container_width=True)

    st.success("Auto-refresh enabled (every 5 minutes)")
