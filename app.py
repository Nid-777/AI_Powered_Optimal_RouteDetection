import streamlit as st
import requests
import json
from jinja2 import Template

# Your Google Maps API Key
API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

# Function to get all routes using Google Maps Directions API
def get_routes(origin, destination, mode):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "alternatives": "true",
        "departure_time": "now",
        "mode": mode,
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

# Function to estimate fuel consumption
def estimate_fuel(distance_km, mileage):
    return distance_km / mileage

# Streamlit UI
st.set_page_config(page_title="Route Optimizer", layout="wide")
st.title("🚗 Smart Route & Fuel Optimizer with Traffic and Heatmap")

# Inputs
origin = st.text_input("Enter Origin (e.g., Durgapur, India)")
destination = st.text_input("Enter Destination (e.g., Delhi, India)")
mode = st.selectbox("Select Vehicle Type", ["driving", "bicycling", "walking", "transit"])
mileage = st.slider("Vehicle Mileage (km per litre)", 5, 30, 15)
fuel_price = st.number_input("Enter Fuel Price per Litre (INR)", value=100)

# Button to compute routes
if st.button("Compute Optimal Route"):
    data = get_routes(origin, destination, mode)

    if data["status"] != "OK":
        st.error("Failed to fetch routes. Check input and API key.")
    else:
        heat_pts = []
        scores = []
        st.markdown("---")
        st.subheader("Available Routes")

        for i, route in enumerate(data["routes"]):
            leg = route["legs"][0]
            distance_km = leg["distance"]["value"] / 1000
            duration = leg.get("duration_in_traffic", leg["duration"])["text"]
            fuel_used = estimate_fuel(distance_km, mileage)
            cost = fuel_used * fuel_price

            for step in leg["steps"]:
                heat_pts.append(step["start_location"])

            score = distance_km + cost / 10
            scores.append((i, score))

            st.markdown(f"### Route {i+1}")
            st.write(f"📏 Distance: **{distance_km:.2f} km**")
            st.write(f"⏱️ Duration (with traffic): **{duration}**")
            st.write(f"⛽ Estimated Fuel Used: **{fuel_used:.2f} litres**")
            st.write(f"💸 Estimated Fuel Cost: **₹{cost:.2f}**")
            st.markdown("---")

        best_route_index = min(scores, key=lambda x: x[1])[0]
        st.success(f"✅ Optimal Route: Route {best_route_index + 1}")

        # Display map
        with open("templates/map.html") as f:
            template = Template(f.read())
            html_content = template.render(api_key=API_KEY)
            st.components.v1.html(html_content, height=600)

        # Send heat points and route data to JS
        js_data = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "heat_points": heat_pts
        }

        # For browser-based communication (if needed later)
        st.json(js_data)
