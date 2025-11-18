import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re

st.title("Unisport HSG – Pilates Termine (robust)")

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
    kursname_tag = box.find("h3")
    kursname = kursname_tag.get_text(strip=True) if kursname_tag else "Kein Kursname"

    # Details: Datum, Zeit, Raum, Leiter
    details = box.find_all("p")
    detail_texts = [d.get_text(strip=True) for d in details]

    # Initialisiere Felder
    datum = ""
    zeit = ""
    raum = ""
    leiter = ""

    for text in detail_texts:
        # Datum (z.B. "Montag, 18.11.2025" oder "18.11.2025")
        match_datum = re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", text)
        if match_datum:
            datum = match_datum.group(0)
        # Zeit (z.B. "18:15 – 19:15")
        match_zeit = re.search(r"\d{1,2}:\d{2}\s*–\s*\d{1,2}:\d{2}", text)
        if match_zeit:
            zeit = match_zeit.group(0)
        # Raum (z.B. "Raum XY")
        match_raum = re.search(r"Raum\s*.*", text)
        if match_raum:
            raum = match_raum.group(0)
        # Leiter (z.B. "Leitung: Name")
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

# Datum in datetime konvertieren, falls vorhanden
def parse_datum(d):
    try:
        return datetime.strptime(d, "%d.%m.%Y")
    except:
        return pd.NaT

if "Datum" in df.columns:
    df["Datum_dt"] = df["Datum"].apply(parse_datum)
else:
    df["Datum_dt"] = pd.NaT

# Sortieren nach Datum
df = df.sort_values("Datum_dt")

# Sidebar-Filter: ab Datum
st.sidebar.header("Filter")
selected_date = st.sidebar.date_input("Zeige Termine ab diesem Datum", datetime.today())
df_filtered = df[df["Datum_dt"] >= pd.to_datetime(selected_date)]

# Robust: nur existierende Spalten anzeigen
columns_to_show = ["Kurs", "Datum", "Zeit", "Raum", "Leiter"]
columns_exist = [col for col in columns_to_show if col in df_filtered.columns]

st.dataframe(df_filtered[columns_exist])

# Optional: Debugging
# st.write(df.head())


