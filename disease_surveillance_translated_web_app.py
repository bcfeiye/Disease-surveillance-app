
import streamlit as st
import re
import json
import geocoder
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
st.title("Disease Surveillance Web App with Auto-Translation")

st.write("This app scans your message in any language and detects possible illness symptoms.")

user_input = st.text_area("Type your post (in any language):")

if st.button("Scan for symptoms"):
    # Get user's city via IP
    g = geocoder.ip('me')
    location = g.city or "Unknown"

    # Translate input to English
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(user_input)
        st.write("Translated Text:", translated_text)
    except Exception as e:
        translated_text = user_input
        st.warning("Translation failed. Using original text.")

    # Run symptom detection on translated text
    result = detect_symptoms(translated_text, location)

    if result:
        st.success("Potential symptoms detected!")
        st.json(result)
    else:
        st.info("No illness symptoms found.")
