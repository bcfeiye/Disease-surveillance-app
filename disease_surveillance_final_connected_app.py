
import streamlit as st
import re
import json
from datetime import datetime
from deep_translator import GoogleTranslator
import pandas as pd
from collections import Counter

# ---------- SYMPTOM DETECTION SETUP ----------
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

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="Disease Surveillance System", layout="wide")

st.title("LUNA Disease Surveillance App")
st.markdown("Track and visualize user-reported illness symptoms in real-time.")

# Initialize reports storage
if "reports" not in st.session_state:
    st.session_state.reports = []

# ---------- TABS ----------
tab1, tab2 = st.tabs(["Submit a Report", "View Dashboard"])

# ---------- TAB 1: Report Submission ----------
with tab1:
    st.header("Submit a Report")

    user_input = st.text_area("Type your post (in any language):")
    user_location = st.text_input("Enter your location (city, area, or country):")

    if st.button("Scan and Submit"):
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
                st.success("Symptoms detected and report saved!")
                st.json(result)
                st.session_state.reports.append(result)
            else:
                st.info("No symptoms detected.")

# ---------- TAB 2: Dashboard ----------
with tab2:
    st.header("Live Outbreak Dashboard")

    if len(st.session_state.reports) == 0:
        st.info("No reports submitted yet.")
    else:
        df = pd.DataFrame(st.session_state.reports)

        st.subheader("All Reports")
        st.dataframe(df[["timestamp", "location", "symptoms"]])

        # Symptoms Frequency Chart
        all_symptoms = []
        for symptoms in df["symptoms"]:
            if isinstance(symptoms, list):
                all_symptoms.extend(symptoms)

        symptom_counts = Counter(all_symptoms)
        symptom_df = pd.DataFrame(symptom_counts.items(), columns=["Symptom", "Count"]).sort_values(by="Count", ascending=False)

        st.subheader("Symptoms Frequency")
        st.bar_chart(symptom_df.set_index("Symptom"))

        # Location Breakdown
        if "location" in df.columns:
            st.subheader("Reports by Location")
            location_counts = df["location"].value_counts()
            st.bar_chart(location_counts)
