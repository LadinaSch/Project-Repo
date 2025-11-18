import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

st.title("Unisport HSG – Pilates Termine")

url = "https://www.sportprogramm.unisg.ch/unisg/angebote/aktueller_zeitraum/_Pilates.html"
response = requests.get(url)
if response.status_code != 200:
    st.error(f"Fehler beim Laden der Seite: {response.status_code}")
    st.stop()

soup = BeautifulSoup(response.text, "html.parser")

# Erste Tabelle auf der Seite nehmen
table = soup.find("table")
rows = []
for tr in table.find_all("tr"):
    cols = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
    if cols:
        rows.append(cols)

# DataFrame erstellen
df = pd.DataFrame(rows[1:], columns=rows[0])  # erste Zeile als Header

# Datum aus Spalte "Buchung" extrahieren
def parse_buchung(buchung_text):
    # z.B. "ab 23.11., 12:30"
    match = re.search(r"ab (\d{1,2}\.\d{1,2}\.)?,? ?(\d{1,2}:\d{2})?", buchung_text)
    if match:
        date_part = match.group(1)
        time_part = match.group(2)
        if date_part:
            # Jahr ergänzen: aktuelle Saison nehmen
            year = datetime.today().year
            datum_str = f"{date_part}{year}"
            try:
                datum = datetime.strptime(datum_str, "%d.%m.%Y")
                if time_part:
                    h, m = map(int, time_part.split(":"))
                    datum = datum.replace(hour=h, minute=m)
                return datum
            except:
                return pd.NaT
    return pd.NaT

df["Datum_dt"] = df["Buchung"].apply(parse_buchung)

# Sortieren nach Datum
df = df.sort_values("Datum_dt")

# Sidebar Filter
st.sidebar.header("Filter")
selected_date = st.sidebar.date_input("Zeige Termine ab", datetime.today())
df_filtered = df[df["Datum_dt"] >= pd.to_datetime(selected_date)]

# Anzeige: Nur relevante Spalten
columns_to_show = ["Details", "Datum_dt", "Zeit", "Ort", "Buchung"]
columns_exist = [c for c in columns_to_show if c in df_filtered.columns]
st.dataframe(df_filtered[columns_exist].reset_index(drop=True))
