import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

st.title("Unisport HSG – Pilates Termine (robust)")

url = "https://www.sportprogramm.unisg.ch/unisg/angebote/aktueller_zeitraum/_Pilates.html"
response = requests.get(url)
if response.status_code != 200:
    st.error(f"Fehler beim Laden der Seite: {response.status_code}")
    st.stop()

soup = BeautifulSoup(response.text, "html.parser")

# Tabelle auf der Seite finden
table = soup.find("table")
if table is None:
    st.error("Keine Tabelle auf der Seite gefunden.")
    st.stop()

rows = []
for tr in table.find_all("tr"):
    cols = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
    if cols:
        rows.append(cols)

# DataFrame erstellen
df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])

st.write("Rohdaten:")
st.dataframe(df)

# Prüfen, ob "Buchung"-Spalte existiert
buchung_col = None
for col in df.columns:
    if "Buchung" in col:
        buchung_col = col
        break

# Datum aus "Buchung" extrahieren
def parse_buchung(buchung_text):
    if not buchung_text:
        return pd.NaT
    # z.B. "ab 23.11., 12:30"
    match = re.search(r"ab (\d{1,2}\.\d{1,2}\.)?,? ?(\d{1,2}:\d{2})?", buchung_text)
    if match:
        date_part = match.group(1)
        time_part = match.group(2)
        if date_part:
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

if buchung_col:
    df["Datum_dt"] = df[buchung_col].apply(parse_buchung)
else:
    df["Datum_dt"] = pd.NaT
    st.warning("Keine 'Buchung'-Spalte gefunden. Datum wird leer bleiben.")

# Sortieren nach Datum
df = df.sort_values("Datum_dt")

# Sidebar Filter
st.sidebar.header("Filter")
selected_date = st.sidebar.date_input("Zeige Termine ab", datetime.today())
df_filtered = df[df["Datum_dt"] >= pd.to_datetime(selected_date, errors="coerce")]

# Anzeige: nur existierende Spalten zeigen
columns_to_show = ["Details", "Datum_dt", "Zeit", "Ort", "Buchung"]
columns_exist = [c for c in columns_to_show if c in df_filtered.columns]

st.subheader("Gefilterte Termine")
st.dataframe(df_filtered[columns_exist].reset_index(drop=True))


         
