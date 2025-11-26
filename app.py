import streamlit as st
from datetime import datetime, timedelta, timezone
from streamlit_calendar import calendar

# ----------------------------------------
# TEMPORARY: GOOGLE LOGIN DISABLED
# ----------------------------------------

st.warning("Google Login is temporarily disabled to fix deployment errors.")

creds = None   # prevents NameError

google_events = []   # keep an empty list so the rest of your app works

# ----------------------------------------
# Excel loading (your function should exist below)
# ----------------------------------------

try:
    excel_events = load_excel_events()
except:
    excel_events = []
    st.error("Excel appointments could not be loaded.")

# Merge both event sources
all_events = google_events + excel_events
all_events.sort(key=lambda x: x["start"] if "start" in x else "")

# CALENDAR VIEW
st.subheader("Calendar Overview")
formatting = {
    "initialView": "timeGridWeek",
    "height": 650,
    "locale": "en",
    "weekNumbers": True,
    "selectable": True,
    "nowIndicator": True,
}

calendar(all_events, formatting)
