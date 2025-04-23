import streamlit as st
import re
import json
from datetime import datetime
from deep_translator import GoogleTranslator

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

# Streamlit UI
st.title("Disease Surveillance Web App with Manual Location Entry")

st.markdown("This app scans your message in any language, detects illness symptoms, and lets you enter your location manually.")

if "reports" not in st.session_state:
    st.session_state.reports = []

user_input = st.text_area("Type your post (in any language):")
user_location = st.text_input("Enter your location (city, area, or country):")

if st.button("Scan"):
    if not user_input.strip():
        st.warning("Please enter a message.")
    elif not user_location.strip():
        st.warning("Please enter your location.")
    else:
        try:
            translated_text = GoogleTranslator(source='auto', target='en').translate(user_input)
            st.write("Translated Text:", translated_text)
        except:
            translated_text = user_input
            st.warning("Translation failed. Using original.")

        result = detect_symptoms(translated_text, user_location)
        if result:
            st.success("Symptoms detected!")
            st.json(result)
            st.session_state.reports.append(result)
        else:
            st.info("No symptoms detected.")

# Summary table
if st.session_state.reports:
    st.subheader("Summary of Your Reports")
    st.json(st.session_state.reports)
