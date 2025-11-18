


import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("Unisport HSG – Pilates Termine")

url = "https://www.sportprogramm.unisg.ch/unisg/angebote/aktueller_zeitraum/_Pilates.html"
response = requests.get(url)
if response.status_code != 200:
    st.error(f"Fehler beim Laden der Seite: {response.status_code}")
    st.stop()

soup = BeautifulSoup(response.text, "html.parser")

# Nun musst du die Struktur der Seite analysieren – z. B. sind die Kurszeiten vielleicht in <table>, <ul> oder <div>-Elementen

# Beispiel: Angenommen, die Kurse sind in einer Tabelle so aufgebaut:
kurs_table = soup.find("table")  # Beispiel: erste Tabelle nehmen
if not kurs_table:
    st.error("Keine Tabelle mit Kursdaten gefunden")
    st.stop()

# Dann jede Zeile durchgehen:
for row in kurs_table.find_all("tr"):
    cols = row.find_all(["td", "th"])
    texts = [col.get_text(strip=True) for col in cols]
    if texts:
        # Das hängt stark davon ab, wie viele Spalten die Tabelle hat
        # Beispiel: Spalte 1 = Datum, Spalte 2 = Uhrzeit, Spalte 3 = Kursname
        if len(texts) >= 3:
            datum = texts[0]
            zeit = texts[1]
            kursname = texts[2]
            st.write(f"**{kursname}** – {datum} {zeit}")
        else:
            # Falls weniger Spalten
            st.write(" · ".join(texts))

