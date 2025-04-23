
import streamlit as st
import pandas as pd
import json
from collections import Counter

st.title("Disease Surveillance Data Dashboard")

st.markdown("This dashboard visualizes collected data from user reports.")

uploaded_file = st.file_uploader("Upload JSON file with user reports", type=["json"])

if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)

        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            st.error("The file format must be a list of reports.")
            st.stop()

        st.subheader("Raw Data")
        st.dataframe(df)

        # Count symptom frequency
        all_symptoms = []
        for symptoms in df["symptoms"]:
            if isinstance(symptoms, list):
                all_symptoms.extend(symptoms)

        symptom_counts = Counter(all_symptoms)
        symptom_df = pd.DataFrame(symptom_counts.items(), columns=["Symptom", "Count"]).sort_values(by="Count", ascending=False)

        st.subheader("Symptoms Frequency")
        st.bar_chart(symptom_df.set_index("Symptom"))

        # Location breakdown
        if "location" in df.columns:
            location_counts = df["location"].value_counts()
            st.subheader("Reports per Location")
            st.bar_chart(location_counts)

    except Exception as e:
        st.error(f"Error reading file: {e}")
