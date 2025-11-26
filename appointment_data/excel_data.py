import pandas as pd
import streamlit as st
from pathlib import Path

# FIXED PATH — this is where your file actually is
EXCEL_PATH = Path(__file__).parent / "appointments.xlsx"

def load_excel_events():
    """Load appointments from Excel and convert them into calendar events."""
    try:
        st.write("🔍 Loading Excel from:", EXCEL_PATH)

        df = pd.read_excel(EXCEL_PATH)

        required_cols = {"title", "start", "end"}
        if not required_cols.issubset(df.columns):
            st.error("appointments.xlsx must contain: title, start, end")
            return []

        df["start"] = pd.to_datetime(df["start"]).astype(str)
        df["end"] = pd.to_datetime(df["end"]).astype(str)

        return df.to_dict(orient="records")

    except Exception as e:
        st.error(f"Error loading Excel data: {e}")
        return []


def add_appointment(title, start, end):
    """Add a new appointment to the Excel file easily."""
    try:
        df = pd.read_excel(EXCEL_PATH)
    except:
        df = pd.DataFrame(columns=["title", "start", "end"])

    new_row = pd.DataFrame([{
        "title": title,
        "start": start,
        "end": end
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False)






