
import streamlit as st
import re
import json
from datetime import datetime
from deep_translator import GoogleTranslator
from streamlit_js_eval import streamlit_js_eval
import requests

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

# Reverse geocoding to get city from lat/lon
def get_city_from_coords(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            data = response.json()
            return data.get("address", {}).get("city", "Unknown")
    except:
        return "Unknown"
    return "Unknown"

# Streamlit UI
st.title("Disease Surveillance Web App with GPS Location & Translation")

st.write("This app scans your message in any language and detects possible illness symptoms.")

# Try to get GPS location via browser
location_data = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition((pos) => ({latitude: pos.coords.latitude, longitude: pos.coords.longitude}))",
    key="get_user_location", want_return=True
)

# User message
user_input = st.text_area("Type your post (in any language):")

if st.button("Scan for symptoms"):
    if not user_input.strip():
        st.warning("Please enter a message first.")
    else:
        # Use real GPS-based location if available
        if location_data and "latitude" in location_data and "longitude" in location_data:
            lat = location_data["latitude"]
            lon = location_data["longitude"]
            city = get_city_from_coords(lat, lon)
            st.write(f"Detected location: {city} (Lat: {lat}, Lon: {lon})")
        else:
            city = "Unknown"
            st.warning("Unable to fetch your location. Please allow location access.")

        # Translate text to English
        try:
            translated_text = GoogleTranslator(source='auto', target='en').translate(user_input)
            st.write("Translated Text:", translated_text)
        except:
            translated_text = user_input
            st.warning("Translation failed. Using original text.")

        # Analyze symptoms
        result = detect_symptoms(translated_text, city)
        if result:
            st.success("Potential symptoms detected!")
            st.json(result)
        else:
            st.info("No illness symptoms found.")
