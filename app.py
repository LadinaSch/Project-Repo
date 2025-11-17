import streamlit as st
from datetime import datetime, time
import pandas as pd

st.title('Dienstplan Sonntagsteam')
st.divider()

#sonntage berechnen

import calendar
from datetime import date

def get_sundays(year, month):
    sundays = []
    month_calendar = calendar.monthcalendar(year, month)

    for week in month_calendar:
        sunday = week[calendar.SUNDAY]
        if sunday != 0:                 # 0 bedeutet: kein Sonntag in dieser Woche
            sundays.append(date(year, month, sunday))

    return sundays

#input


# ---- Benutzereingaben ----
year = st.number_input("Jahr", min_value=2020, max_value=2030, value=2025)
month = st.number_input("Monat", min_value=1, max_value=12, value=4)

employees = ["Shpresa", "Hümeysa", "Semi", "Janine", "Dona", "Ladina", "Matthias", "Saskia", "Julia"]  # deine Mitarbeitenden

# ---- Sonntage holen ----
sundays = get_sundays(year, month)

# ---- DataFrame erzeugen ----
# Spalten sind Sonntage, Zeilen sind Mitarbeiter
df = pd.DataFrame(index=employees, columns=[d.strftime("%d.%m.%Y") for d in sundays])

# Leere Zellen mit "" befüllen, damit die Tabelle sauber aussieht
df = df.fillna("")

st.subheader("Dienstplan")
st.dataframe(df)

