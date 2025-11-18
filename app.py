import streamlit as st
from datetime import datetime
import pandas as pd
import requests
from ics import Calendar
pip install ics

# Titel der App
st.title("Uni-Sport Termine")

# ====== Konfiguration ======
ical_url = "https://www.sportprogramm.unisg.ch/unisg/angebote/aktueller_zeitraum/_Pilates.html"  # z. B. https://unisport.uni.de/termine.ics

# ====== ICS-Datei laden ======
try:
    response = requests.get(ical_url)
    response.raise_for_status()  # Fehler bei Verbindung werfen
    calendar = Calendar(response.text)
except Exception as e:
    st.error(f"Fehler beim Laden des Kalenders: {e}")
    st.stop()

# ====== Termine sortieren ======
events = sorted(calendar.events, key=lambda e: e.begin)

# ====== Termine anzeigen ======
if events:
    for event in events:
        start = event.begin.to('local').format('YYYY-MM-DD HH:mm')
        end = event.end.to('local').format('HH:mm')
        st.markdown(f"**{event.name}**  \n{start} – {end}  \n{event.location if event.location else ''}")
else:
    st.info("Keine Termine gefunden.")

# ====== Filter nach Datum (optional) ======
st.sidebar.header("Filter")
selected_date = st.sidebar.date_input("Zeige Termine ab diesem Datum", datetime.today())

filtered_events = [e for e in events if e.begin.date() >= selected_date]

st.sidebar.subheader("Gefilterte Termine")
for e in filtered_events:
    start = e.begin.to('local').format('YYYY-MM-DD HH:mm')
    st.sidebar.markdown(f"- {e.name} ({start})")

