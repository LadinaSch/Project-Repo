import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from streamlit_calendar import calendar
import urllib.parse
from google.oauth2.credentials import Credentials

# Excel import (correct path!)
from appointment_data.excel_data import load_excel_events, add_appointment


# Google OAuth settings
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
APP_URL = "https://projectrepo-nelb9xkappkqy6bhbwcmqwp.streamlit.app"


# -------------------------------
# GOOGLE LOGIN SYSTEM
# -------------------------------
def get_google_creds():
    # If token exists in session storage → use it
    if "gcal_token" in st.session_state:
        return Credentials.from_authorized_user_info(
            st.session_state["gcal_token"], SCOPES
        )

    # OAuth flow
    flow = Flow.from_client_config(
        st.secrets["GOOGLE_OAUTH_CLIENT"],
        scopes=SCOPES,
        redirect_uri=APP_URL
    )

    qp = st.query_params

    # Check if Google redirected back with an auth code
    if "code" in qp:
        current_url = APP_URL
        if qp:
            current_url += "?" + urllib.parse.urlencode(qp, doseq=True)

        flow.fetch_token(authorization_response=current_url)
        creds = flow.credentials

        # Save token in session
        st.session_state["gcal_token"] = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }

        st.query_params.clear()
        return creds

    else:
        # Show login button
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        st.link_button("Connect with Google", auth_url)
        st.stop()


# Run login flow
try:
    creds = get_google_creds()
except Exception as e:
    st.error("Google Login is temporarily disabled to fix deployment errors.")
    creds = None


# -------------------------------
# LOAD CALENDAR DATA
# -------------------------------
google_events = []

if creds:
    try:
        service = build("calendar", "v3", credentials=creds)

        time_min = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        time_max = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        cal_list = service.calendarList().list().execute()
        calendars = cal_list.get("items", [])

        for cal in calendars:
            cal_id = cal["id"]
            cal_summary = cal.get("summaryOverride", cal.get("summary", "Unknown calendar"))

            try:
                events_result = service.events().list(
                    calendarId=cal_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=100,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()

                events = events_result.get("items", [])

                for event in events:
                    title = f"{cal_summary}: {event.get('summary', 'without title')}"
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    end = event["end"].get("dateTime", event["end"].get("date"))

                    google_events.append({
                        "title": title,
                        "start": start,
                        "end": end,
                    })

            except Exception as e:
                st.warning(f"Could not read calendar '{cal_summary}': {e}")

        google_events.sort(key=lambda x: x["start"])

    except Exception as e:
        st.error(f"Error loading Google Calendar: {e}")


# -------------------------------
# LOAD EXCEL APPOINTMENTS
# -------------------------------
try:
    excel_events = load_excel_events()
except Exception:
    excel_events = []
    st.error("Excel appointments could not be loaded.")


# -------------------------------
# MERGE ALL EVENTS
# -------------------------------
all_events = google_events + excel_events
all_events.sort(key=lambda x: x["start"])


# -------------------------------
# DISPLAY CALENDAR
# -------------------------------
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

