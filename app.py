"""
Snore Analysis Assistant — Streamlit front-end
==============================================
Mirrors the lecturer's sample pattern:
Streamlit -> n8n Webhook -> (FastAPI prediction + AI agent) -> response back.

Run locally:
    pip install streamlit requests
    streamlit run app.py
"""

import requests
import streamlit as st

# copy your n8n webhook PRODUCTION url here
N8N = "https://corrwong.app.n8n.cloud/webhook/snore-analysis"

st.title("Snore Analysis Assistant")
st.caption("Upload a sleep recording to analyze snoring patterns and get "
           "personalized recommendations. Screening aid only — not a "
           "medical diagnosis.")
 
# ---- User information (Trigger Layer inputs) ----
name = st.text_input("Name", "Jane Tan")
email = st.text_input("Email (for the report and alerts)", "jane@example.com")
age = st.slider("Age", 18, 90, 35)
gender = st.selectbox("Gender", ["Female", "Male"])
weight = st.number_input("Weight (kg)", 30.0, 200.0, 65.0)
height = st.number_input("Height (cm)", 120.0, 220.0, 165.0)
 
# ---- Sleep recording upload ----
audio = st.file_uploader("Sleep recording",
                         type=["wav", "mp3", "ogg", "m4a"])
 
if st.button("Analyze & recommend"):
    if audio is None:
        st.error("Please upload a WAV recording first.")
        st.stop()
 
    bmi = round(weight / ((height / 100) ** 2), 1)
 
    data = {
        "name": name,
        "email": email,
        "age": age,
        "gender": gender,
        "bmi": bmi,
    }
    files = {"file": (audio.name, audio.getvalue(),
                      audio.type or "application/octet-stream")}
 
    with st.spinner("Analyzing your recording... this can take a minute."):
        # long timeout: Render free tier wake-up + audio analysis + Gemini
        r = requests.post(N8N, data=data, files=files, timeout=180)
        r.raise_for_status()
        d = r.json()
 
    # ---- Analysis results ----
    st.subheader("Analysis results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Snoring duration",
              f"{d['snore_duration_seconds']} s",
              f"{d['snore_percentage']}% of recording")
    c2.metric("Events per hour", f"{d['events_per_hour']}")
    loud = d.get("avg_loudness_db")
    c3.metric("Avg loudness", f"{loud} dBFS" if loud is not None else "n/a")
 
    severity = d.get("severity", "unknown")
    if severity == "severe":
        st.error(f"Severity: {severity.upper()} — an alert email has been sent.")
    elif severity == "moderate":
        st.warning(f"Severity: {severity}")
    else:
        st.success(f"Severity: {severity}")
 
    # ---- AI recommendations ----
    st.subheader("Personalized recommendations")
    st.write(d.get("recommendation", "No recommendation returned."))
