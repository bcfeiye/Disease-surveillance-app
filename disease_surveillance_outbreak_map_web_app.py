
import streamlit as st
import re
import json
from datetime import datetime
from deep_translator import GoogleTranslator
from streamlit_js_eval import streamlit_js_eval
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

# Keywords and phrases
keywords = [
    "sick", "fever", "tired", "dizzy", "headache", "flu", "cough",
    "vomiting", "nausea", "cold", "chills", "sore throat", "weak",
    "pain", "congested", "sneezing", "runny nose", "body ache", "exhausted",
    "diarrhea", "infected", "unwell", "soreness", "fatigue", "burning throat"
]

phrases = [
    "I feel tired", "not feeling well", "I am dizzy", "have a fever", "down with flu",
    "can't get out of bed", "feel like death", "my body aches",
    "I think I’m sick", "my head is pounding", "throat is killing me",
    "I'm burning up", "I feel horrible", "been vomiting", "sick again",
    "my stomach hurts", "I'm exhausted today"
]

# Function to detect symptoms
def detect_symptoms(text, location):
    detected = {
        "text": text,
        "location": location,
        "timestamp": datetime.now().isoformat(),
        "symptoms": []
    }

    for word in keywords:
        if re.search(rf"\b{re.escape(word)}\b", text.lower()):
            detected["symptoms"].append(word)

    for phrase in phrases:
        if phrase.lower() in text.lower():
            detected["symptoms"].append(phrase)

    return detected if detected["symptoms"] else None

# Reverse geocoding to get detailed location info
def get_location_details(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            return ", ".join(filter(None, [
                address.get("road"),
                address.get("neighbourhood"),
                address.get("suburb"),
                address.get("city"),
                address.get("town"),
                address.get("village"),
                address.get("state"),
                address.get("country")
            ]))
    except:
        return "Unknown"
    return "Unknown"

# Streamlit UI
st.title("Disease Surveillance Web App with GPS, Translation & Live Map")

st.markdown("This app scans your message in any language, detects symptoms, and shows them on a live map.")
st.markdown("**Note:** Allow your browser to access your location. If blocked, change it in your browser's site settings.")

if "reports" not in st.session_state:
    st.session_state.reports = []

location_data = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition((pos) => ({latitude: pos.coords.latitude, longitude: pos.coords.longitude}))",
    key="get_user_location", want_return=True
)

user_input = st.text_area("Type your post (in any language):")

if st.button("Scan and Report"):
    if not user_input.strip():
        st.warning("Please enter a message.")
    else:
        lat, lon = 0, 0
        if location_data and "latitude" in location_data and "longitude" in location_data:
            lat = location_data["latitude"]
            lon = location_data["longitude"]
            location_string = get_location_details(lat, lon)
            st.write(f"GPS Coordinates: {lat}, {lon}")
            st.write(f"Detected Location: {location_string}")
        else:
            location_string = "Unknown"
            st.warning("Could not fetch your exact GPS location. Your report will still be stored.")

        try:
            translated_text = GoogleTranslator(source='auto', target='en').translate(user_input)
            st.write("Translated Text:", translated_text)
        except:
            translated_text = user_input
            st.warning("Translation failed. Using original.")

        result = detect_symptoms(translated_text, location_string)
        if result:
            result["lat"] = lat
            result["lon"] = lon
            st.session_state.reports.append(result)
            st.success("Symptoms detected and report added.")
            st.json(result)
        else:
            st.info("No symptoms detected.")

# Map Section
st.subheader("Live Outbreak Map")
default_center = [25.276987, 55.296249]  # Default: Dubai
last_valid = next((r for r in reversed(st.session_state.reports) if r["lat"] != 0), None)
center = [last_valid["lat"], last_valid["lon"]] if last_valid else default_center

m = folium.Map(location=center, zoom_start=5)
for report in st.session_state.reports:
    if report["lat"] != 0:
        popup_info = f"{report['location']}<br>{', '.join(report['symptoms'])}<br>{report['timestamp']}"
        folium.Marker([report["lat"], report["lon"]], popup=popup_info, icon=folium.Icon(color='red')).add_to(m)
st_folium(m, width=700, height=500)

# Outbreak Report Table
if st.session_state.reports:
    st.subheader("Summary of Reported Outbreaks")
    df = pd.DataFrame(st.session_state.reports)
    st.dataframe(df[["timestamp", "location", "symptoms"]])
