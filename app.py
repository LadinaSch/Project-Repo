import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re

st.title("Unisport HSG – Pilates Termine")

url = "https://www.sportprogramm.unisg.ch/unisg/angebote/aktueller_zeitraum/_Pilates.html"
response = requests.get(url)
if response.status_code != 200:
    st.error(f"Fehler beim Laden der Seite: {response.status_code}")
    st.stop()

soup = BeautifulSoup(response.text, "html.parser")

# Alle Kursboxen finden
kurs_boxen = soup.find_all("div", class_="angebotbox")

kurse = []

for box in kurs_boxen:
    # Kursname
    kursname_tag = box.find("h3")
    kursname = kursname_tag.get_text(strip=True) if kursname_tag else "Kein Kursname"

    # Details: Datum, Zeit, Raum, Leiter
    details = box.find_all("p")
    detail_texts = [d.get_text(strip=True) for d in details]

    # Versuche Datum, Zeit, Raum, Leiter zu extrahieren
    datum = ""
    zeit = ""
    raum = ""
    leiter = ""

    for text in detail_texts:
        # Datum: z.B. "Montag, 18.11.2025"
        match_datum = re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", text)
        if match_datum:
            datum = match_datum.group(0)
        # Zeit: z.B. "18:15 – 19:15 Uhr"
        match_zeit = re.search(r"\d{1,2}:\d{2}\s*–\s*\d{1,2}:\d{2}", text)
        if match_zeit:
            zeit = match_zeit.group(0)
        # Raum: oft "Raum XY"
        match_raum = re.search(r"Raum\s.*", text)
        if match_raum:
            raum = match_raum.group(0)
        # Leiter: z.B. "Leitung: Name"
        match_leiter = re.search(r"Leitung:\s*.*", text)
        if match_leiter:
            leiter = match_leiter.group(0)

    kurse.append({
        "Kurs": kursname,
        "Datum": datum,
        "Zeit": zeit,
        "Raum": raum,
        "Leiter": leiter
    })

# In DataFrame umwandeln
df = pd.DataFrame(kurse)

# Datum in datetime umwandeln, um zu sortieren
def parse_datum(d):
    try:
        return datetime.strptime(d, "%d.%m.%Y")
    except:
        return None

df["Datum_dt"] = df["Datum"].apply(parse_datum)
df = df.sort_values("Datum_dt")

# Sidebar-Filter: ab Datum
st.sidebar.header("Filter")
selected_date = st.sidebar.date_input("Zeige Termine ab diesem Datum", datetime.today())
df_filtered = df[df["Datum_dt"] >= pd.to_datetime(selected_date)]

# Anzeige
st.dataframe(df_filtered[["Kurs", "Datum", "Zeit", "Raum", "Leiter"]])

