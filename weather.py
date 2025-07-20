import requests
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd


def get_coordinates(city_name):
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
    headers = {"User-Agent": "WeatherDashboardApp/1.0 (satvikbaranwal07@gmail.com)"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        location_data = response.json()
        if location_data:
            location = location_data[0]
            return float(location['lat']), float(location['lon'])
        else:
            st.warning("City not found. Try adding the country name (e.g., 'Paris, France').")
            return None, None
    else:
        st.error(f"API request failed with status code {response.status_code}: {response.text}")
        return None, None
def get_weather_data(lat, lon, hours):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m&forecast_days=2"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve weather data.")
        return None
st.title("Real-Time Weather Dashboard 🌤️")
st.write("Get live weather updates and forecasts.")

city_name = st.text_input("Enter City Name", value="San Francisco")
forecast_duration = st.slider("Select forecast duration (hours)", min_value=12, max_value=48, value=24, step=12)
parameter_options = st.multiselect(
    "Choose weather parameters to display:",
    options=["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)"],
    default=["Temperature (°C)", "Humidity (%)"]
)
if st.button("Get Weather Data"):
    lat, lon = get_coordinates(city_name)
    if lat and lon:
        data = get_weather_data(lat, lon, forecast_duration)
        if data:
            times = [datetime.now() + timedelta(hours=i) for i in range(forecast_duration)] # type: ignore
            df = pd.DataFrame({"Time": times}) # type: ignore

            if "Temperature (°C)" in parameter_options:
                df["Temperature (°C)"] = data['hourly']['temperature_2m'][:forecast_duration]
                st.subheader(f"Temperature Forecast")
                st.line_chart(df.set_index("Time")["Temperature (°C)"])

            if "Humidity (%)" in parameter_options:
                df["Humidity (%)"] = data['hourly']['relative_humidity_2m'][:forecast_duration]
                st.subheader(f"HumidityForecast")
                st.line_chart(df.set_index("Time")["Humidity (%)"])

            if "Wind Speed (m/s)" in parameter_options:
                df["Wind Speed (m/s)"] = data['hourly']['wind_speed_10m'][:forecast_duration]
                st.subheader(f"Wind SpeedForecast")
                st.line_chart(df.set_index("Time")["Wind Speed (m/s)"])
            st.subheader("Current Weather Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ Temperature", f"{data['hourly']['temperature_2m'][0]}°C")
            col2.metric("💧 Humidity", f"{data['hourly']['relative_humidity_2m'][0]}%")
            col3.metric("🌬️ Wind Speed", f"{data['hourly']['wind_speed_10m'][0]} m/s")