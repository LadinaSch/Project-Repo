import streamlit as st
from datetime import datetime, time

st.title('Arbeitsplan ')
st.divider()

#kalender welcher angezeigt wird 
date_selected = st.date_input("Datum auswählen:")
time_selected = st.time_input("Zeit auswählen:", value=time(12, 0))

datetime_selected = datetime.combine(date_selected, time_selected)

st.write("Gewählter Zeitpunkt:", datetime_selected)




